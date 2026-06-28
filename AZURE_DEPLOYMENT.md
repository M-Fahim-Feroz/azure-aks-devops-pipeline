# Azure Deployment Guide

Complete step-by-step guide to deploy this Azure AKS DevOps pipeline project.

> **Deployment Status:**  Successfully deployed and validated through GitHub Actions.
> FastAPI endpoint responded with `{"status":"ok"}`. Prometheus/Grafana monitoring stack confirmed UP.
> Screenshots are stored under `docs/screenshots/`.

---

## Prerequisites

1. **Azure Account** with active subscription ([Azure for Students](https://azure.microsoft.com/en-us/free/students/) works)
2. **Azure CLI** installed ([Download](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
3. **GitHub Account** with this repo forked/cloned
4. **Docker Desktop** (for local testing only)

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

**Save the JSON output** — you will need it for the `AZURE_CREDENTIALS` GitHub Secret:

```json
{
  "clientId": "value-from-appId",
  "clientSecret": "value-from-password",
  "subscriptionId": "value-from-az-account-show",
  "tenantId": "value-from-tenant"
}
```

> **Note:** The Azure CLI may output `appId`/`password`/`tenant`. For GitHub Actions, convert to the exact JSON format above with `clientId`, `clientSecret`, `subscriptionId`, and `tenantId` keys.

---

## Step 3: Configure GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Required Secrets

| Secret Name | Example / Notes |
|---|---|
| `AZURE_CREDENTIALS` | Entire JSON block from Step 2 |
| `ACR_LOGIN_SERVER` | `fahimaksdevopsacr.azurecr.io` |
| `ACR_NAME` | `fahimaksdevopsacr` |
| `AKS_CLUSTER_NAME` | `azure-aks-devops-cluster` |
| `AZURE_RESOURCE_GROUP` | `azure-aks-devops-rg` |
| `POSTGRES_DB` | `appdb` |
| `POSTGRES_USER` | `admin` |
| `POSTGRES_PASSWORD` | `<your-secure-password>` |
| `WEATHER_API_KEY` | `demo` (or your real API key) |

> **Security note:** Do not commit secret values. Storage account credentials are automatically fetched during the pipeline run using Azure CLI — no manual setup needed.

---

## Step 4: Trigger the Pipeline

Push to main branch to trigger the GitHub Actions workflow:

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

### What the pipeline does automatically

1.  **Secret validation** — preflight check for all 9 required secrets
2.  **Build & Test** — Flake8 lint, Bandit security scan, Pytest unit tests
3.  **Terraform Apply** — provisions Resource Group, VNet, AKS, ACR, Storage Account
4.  **Docker Build** — builds and pushes `api` and `worker` images to ACR
5.  **Ansible Deploy** — creates Kubernetes secrets, applies manifests, installs Prometheus/Grafana via Helm
6.  **Smoke Test** — verifies the public FastAPI endpoint returns the expected JSON response

---

## Step 5: Access Your Application

```bash
# Get AKS credentials locally
az aks get-credentials --resource-group azure-aks-devops-rg --name azure-aks-devops-cluster

# Get all workloads and services
kubectl get all -n fastapi

# Get external LoadBalancer IP
kubectl get svc -n fastapi

# Example output:
# NAME              TYPE           CLUSTER-IP     EXTERNAL-IP       PORT(S)
# fastapi-service   LoadBalancer   10.0.217.28    40.119.215.246    80:31876/TCP
```

**Access URLs** (replace `<EXTERNAL-IP>` with the IP from above):
- 🌐 API root: `http://<EXTERNAL-IP>/`
- 📚 API Docs: `http://<EXTERNAL-IP>/docs`
- 🖥️ Web UI: `http://<EXTERNAL-IP>/ui`

---

## Step 6: Access Monitoring (Grafana + Prometheus)

```bash
# List monitoring services
kubectl get svc -n monitoring

# Port-forward Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

- **Grafana URL:** `http://localhost:3000`
- **Login:** `admin` / `<your-GRAFANA_ADMIN_PASSWORD>` (configured via GitHub Secrets)
- **Dashboards available:** Kubernetes Cluster, Namespace Pods, Node Exporter, Kubelet

```bash
# Port-forward Prometheus
kubectl port-forward svc/monitoring-kube-prometheus-prometheus -n monitoring 9090:9090
```

- **Prometheus URL:** `http://localhost:9090`
- Check **Status → Targets** to confirm all targets are UP

---

## Validation Commands

```bash
# Check all fastapi namespace pods
kubectl get pods -n fastapi

# Check services and LoadBalancer IP
kubectl get svc -n fastapi

# Check monitoring pods
kubectl get pods -n monitoring

# Check Helm releases
helm list -A

# Verify endpoint manually
curl http://<EXTERNAL-IP>/
```

---

## Deployment Notes

- Deployed on **Azure for Students** subscription in **Southeast Asia** region
- AKS cluster uses a **single demo node** (Standard_DS2_v2)
- Terraform state is managed remotely using an **Azure Storage backend**, ensuring idempotency across pipeline runs.
- Failed partial pipeline runs can be safely retried because Terraform remote state handles drift and existing resources automatically.

---

## Troubleshooting

### Pipeline fails at Terraform Apply

- Verify `AZURE_CREDENTIALS` JSON is correctly formatted (all 4 fields present)
- Check Azure subscription quota for AKS nodes (at least 2 vCPUs needed)
- Ensure the service principal has `Contributor` role on the subscription

### Pods in CrashLoopBackOff

```bash
kubectl logs <pod-name> -n fastapi
kubectl describe pod <pod-name> -n fastapi
```

### ACR Login Fails

```bash
az acr login --name fahimaksdevopsacr
```

### Cannot Access External IP

```bash
# Wait for LoadBalancer provisioning (can take 2–5 minutes after deployment)
kubectl get svc -n fastapi -w
```

### Smoke Test Fails with Connection Refused

The LoadBalancer IP may take 2–5 minutes to become active after provisioning. The smoke test includes a wait loop — if it times out, check pod readiness first:

```bash
kubectl get pods -n fastapi
```

---

## Cleanup

> [!CAUTION]
> This project provisions real Azure resources (AKS, ACR, LoadBalancers, Storage Account) which incur ongoing cost. Always destroy infrastructure after testing/demo.

```bash
# Delete the entire resource group (fastest cleanup method)
az group delete --name azure-aks-devops-rg --yes --no-wait
```

This removes: AKS cluster, ACR, virtual network, storage account, and all associated resources.

---

## Screenshots

Deployment proof screenshots are stored in [`docs/screenshots/`](docs/screenshots/).

See the [screenshot index](docs/screenshots/README.md) for a categorized view of all CI/CD, Azure infrastructure, Kubernetes workload, and monitoring screenshots.
