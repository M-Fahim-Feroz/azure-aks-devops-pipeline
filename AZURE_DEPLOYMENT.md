# 🚀 Azure Deployment Guide

Complete step-by-step guide to deploy this DevOps project on Azure.

---

## Prerequisites

1. **Azure Account** with active subscription
2. **Azure CLI** installed ([Download](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
3. **GitHub Account** with this repo forked/cloned
4. **Docker Desktop** (for local testing)

---

## Step 1: Azure CLI Setup

```bash
# Login to Azure
az login

# Verify subscription
az account show

# Set subscription (if you have multiple)
az account set --subscription "<YOUR_SUBSCRIPTION_ID>"
```

---

## Step 2: Create Service Principal

This gives GitHub Actions permission to manage Azure resources.

```bash
# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "github-devops-sp" \
  --role contributor \
  --scopes /subscriptions/<YOUR_SUBSCRIPTION_ID> \
  --sdk-auth
```

**Save the JSON output** - you'll need it for GitHub Secrets:
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

---

## Step 3: Configure GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Required Secrets:

| Secret Name | Value | Source |
|-------------|-------|--------|
| `AZURE_CREDENTIALS` | Entire JSON from Step 2 | Service Principal output |
| `ARM_CLIENT_ID` | `clientId` field | Service Principal JSON |
| `ARM_CLIENT_SECRET` | `clientSecret` field | Service Principal JSON |
| `ARM_SUBSCRIPTION_ID` | `subscriptionId` field | Service Principal JSON |
| `ARM_TENANT_ID` | `tenantId` field | Service Principal JSON |
| `ACR_LOGIN_SERVER` | `fastapiacr123456789.azurecr.io` | From `infra/variables.tf` |
| `ACR_NAME` | `fastapiacr123456789` | From `infra/variables.tf` |
| `AKS_CLUSTER_NAME` | `fastapi-aks` | From `infra/variables.tf` |
| `AZURE_RESOURCE_GROUP` | `fastapi-rg` | From `infra/variables.tf` |
| `POSTGRES_DB` | `appdb` | Your choice |
| `POSTGRES_USER` | `admin` | Your choice |
| `POSTGRES_PASSWORD` | `<secure-password>` | Your choice |
| `WEATHER_API_KEY` | `<your-api-key>` | From weather API provider |

> **Note**: Storage account credentials are automatically fetched from Terraform - no manual setup needed!

---

## Step 4: Deploy! 🚀

```bash
# Commit and push to main branch
git add .
git commit -m "Deploy to Azure"
git push origin main
```

The GitHub Actions pipeline will automatically:
1. ✅ **Build & Test** - Lint, security scan, unit tests
2. ✅ **Docker Build** - Push images to Azure Container Registry
3. ✅ **Terraform Apply** - Create AKS, VNet, ACR, Storage
4. ✅ **Ansible Deploy** - Apply K8s manifests, install monitoring
5. ✅ **Smoke Test** - Verify application is accessible

---

## Step 5: Access Your Application

```bash
# Get AKS credentials
az aks get-credentials --resource-group fastapi-rg --name fastapi-aks

# Get external IP
kubectl get svc -n fastapi

# Output:
# NAME              TYPE           EXTERNAL-IP     PORT(S)
# fastapi-service   LoadBalancer   20.xxx.xxx.xxx  80:xxxxx/TCP
```

**Access URLs:**
- 🌐 Web UI: `http://<EXTERNAL-IP>/ui`
- 📚 API Docs: `http://<EXTERNAL-IP>/docs`

---

## Step 6: Access Monitoring (Grafana)

```bash
# Get Grafana service
kubectl get svc -n monitoring

# Port-forward if no external IP
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

- **URL**: `http://localhost:3000`
- **Login**: `admin` / `admin`
- **Import Dashboard**: Use `grafana_template.json`

---

## 📸 Validation Commands

```bash
# Kubernetes
kubectl get pods -n fastapi
kubectl get svc -n fastapi
kubectl describe pod fastapi-api-<hash> -n fastapi
kubectl get pods -n monitoring

# Terraform
cd infra
terraform output

# After all screenshots, cleanup:
terraform destroy -auto-approve
```

---

## 🧹 Cleanup (Teardown)

```bash
# Delete all Azure resources
cd infra
terraform destroy -auto-approve

# Or delete entire resource group manually
az group delete --name fastapi-rg --yes --no-wait
```

---

## Troubleshooting

### Pipeline Fails at Terraform
- Verify all `ARM_*` secrets are correctly set
- Check Azure subscription has sufficient quota

### Pods in CrashLoopBackOff
```bash
kubectl logs <pod-name> -n fastapi
kubectl describe pod <pod-name> -n fastapi
```

### ACR Login Fails
```bash
az acr login --name fastapiacr123456789
```

### Can't Access External IP
```bash
# Wait for LoadBalancer provisioning (can take 2-5 minutes)
kubectl get svc -n fastapi -w
```
