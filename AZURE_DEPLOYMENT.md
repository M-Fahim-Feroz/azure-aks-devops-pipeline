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
  "clientId": "value-from-appId",
  "clientSecret": "value-from-password",
  "subscriptionId": "value-from-az-account-show",
  "tenantId": "value-from-tenant"
}
```

> **Note**: The Azure service principal command may output appId/password/tenant. For GitHub Actions, you must convert it to the exact JSON format shown above with `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` keys.

---

## Step 3: Configure GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Required Secrets:

| Secret Name | Value |
|-------------|-------|
| `AZURE_CREDENTIALS` | Entire JSON block from Step 2 |
| `ACR_LOGIN_SERVER` | `fahimaksdevopsacr.azurecr.io` |
| `ACR_NAME` | `fahimaksdevopsacr` |
| `AKS_CLUSTER_NAME` | `azure-aks-devops-cluster` |
| `AZURE_RESOURCE_GROUP` | `azure-aks-devops-rg` |
| `POSTGRES_DB` | `appdb` |
| `POSTGRES_USER` | `admin` |
| `POSTGRES_PASSWORD` | `<secure-password>` |
| `WEATHER_API_KEY` | `demo` (or your real API key) |

> **Note**: Storage account credentials are automatically fetched securely via the Azure CLI during deployment - no manual setup or Terraform state exposure needed!

---

## Step 4: Deploy! 🚀

```bash
# Commit and push to main branch
git add .
git commit -m "Fix Azure deployment configuration alignment"
git push origin main
```

The GitHub Actions pipeline will automatically:
1. ✅ **Build & Test** - Lint, security scan, unit tests
2. ✅ **Terraform Apply** - Create Resource Group, VNet, AKS, ACR, Storage
3. ✅ **Docker Build** - Build and push images to Azure Container Registry
4. ✅ **Ansible Deploy** - Create secrets securely, apply K8s manifests, install monitoring
5. ✅ **Smoke Test** - Verify application is accessible

---

## Step 5: Access Your Application

```bash
# Get AKS credentials
az aks get-credentials --resource-group azure-aks-devops-rg --name azure-aks-devops-cluster

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
```

---

## 🧹 Cleanup (Teardown)

> [!CAUTION]
> This project creates real Azure resources. Destroy the infrastructure after screenshots to avoid charges.

```bash
# Delete all Azure resources
cd infra
terraform destroy

# Or delete entire resource group manually
az group delete --name azure-aks-devops-rg --yes --no-wait
```

---

## Troubleshooting

### Pipeline Fails at Terraform
- Verify `AZURE_CREDENTIALS` JSON is properly formatted.
- Check Azure subscription has sufficient quota.

### Pods in CrashLoopBackOff
```bash
kubectl logs <pod-name> -n fastapi
kubectl describe pod <pod-name> -n fastapi
```

### ACR Login Fails
```bash
az acr login --name fahimaksdevopsacr
```

### Can't Access External IP
```bash
# Wait for LoadBalancer provisioning (can take 2-5 minutes)
kubectl get svc -n fastapi -w
```
