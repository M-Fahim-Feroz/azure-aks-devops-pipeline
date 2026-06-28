# Azure AKS DevOps Pipeline

A production-style, end-to-end DevOps portfolio project that provisions Azure infrastructure with Terraform, builds and pushes Docker images to ACR, deploys a FastAPI microservice stack to Azure Kubernetes Service, automates deployment with Ansible, and validates the rollout through a fully automated GitHub Actions pipeline with Prometheus and Grafana observability.

> **Deployment Status:**  Successfully deployed and smoke-tested. Public FastAPI endpoint returned `{"status":"ok"}`.

---

## Overview

This project demonstrates a complete production-style DevOps workflow on Azure. It integrates infrastructure automation, container orchestration, background task processing, monitoring, and automated CI/CD smoke testing — all driven from a single GitHub Actions pipeline.

Key highlights:
- **Zero manual Azure steps** after secrets are configured — the pipeline provisions everything
- **Ansible-driven Kubernetes deployment** including Helm-based monitoring stack
- **Live smoke test** validates the public FastAPI endpoint at the end of every run
- **kube-prometheus-stack** provides cluster-wide Prometheus metrics and Grafana dashboards
- **Azure Storage remote backend** for Terraform state — idempotent and safe on repeated runs

---

## Architecture

```
Developer push to GitHub
        │
        ▼
GitHub Actions CI/CD
        │
        ├─ 1. Secret Validation (preflight check)
        ├─ 2. Build & Test (lint, security scan, unit tests)
        │
        ├─ 3. Terraform Provision  ← only when infra/** changes or workflow_dispatch
        │      └─ Azure Resource Group
        │      └─ Azure Virtual Network / Subnet
        │      └─ Azure Container Registry (ACR)
        │      └─ Azure Kubernetes Service (AKS)
        │      └─ Azure Storage Account / File Share
        │
        ├─ 4. Docker Build & Push → ACR
        │      └─ fastapi-api image
        │      └─ fastapi-worker image
        │
        ├─ 5. AKS Deploy (Ansible Playbook)
        │      └─ Apply Kubernetes manifests (namespace, secrets, configmaps)
        │      └─ Deploy FastAPI, Worker, PostgreSQL, Redis
        │      └─ Install kube-prometheus-stack via Helm
        │
        └─ 6. Smoke Test
               └─ Wait for LoadBalancer IP
               └─ curl public endpoint → validate JSON response
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Cloud | Azure (AKS, ACR, Storage, VNet) |
| Infrastructure as Code | Terraform |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Orchestration | Kubernetes |
| Deployment Automation | Ansible, Helm |
| API Framework | FastAPI (Python) |
| Background Tasks | Celery |
| Message Broker | Redis |
| Database | PostgreSQL |
| Monitoring | Prometheus, Grafana (kube-prometheus-stack) |
| Code Quality | Flake8, Bandit, Pytest |

---

## CI/CD Pipeline

The `.github/workflows/aks-cicd.yml` workflow runs on every push to `main`.

### Jobs

| # | Job | Description |
|---|---|---|
| 1 | `build-and-test` | Secret preflight validation, Python lint (Flake8), security scan (Bandit), unit tests (Pytest) |
| 2 | `detect-changes` | Uses `dorny/paths-filter@v3` to detect whether `infra/**` changed |
| 3 | `provision-infra` | Azure Login, Terraform Init (remote backend), Terraform Apply — only runs when infra changes or `workflow_dispatch` |
| 4 | `docker-build` | ACR login, multi-stage Docker build, push `api` and `worker` images with commit-SHA tags |
| 5 | `deploy-app` | Set AKS context, fetch storage key, create Kubernetes secrets, run Ansible playbook, force-restart deployments |
| 6 | `smoke-test` | Wait for pods, retrieve LoadBalancer IP, curl endpoint, validate JSON response |

All credentials are stored as **GitHub Actions repository secrets** and are never logged or committed.

---

## Infrastructure Provisioned

Terraform (`infra/`) provisions the following on Azure (Southeast Asia region):

- **Resource Group:** `azure-aks-devops-rg`
- **Virtual Network:** `fastapi-vnet` with node subnet
- **Azure Container Registry:** `fahimaksdevopsacr` (ACR with AcrPull role on AKS)
- **AKS Cluster:** `azure-aks-devops-cluster` — single node pool, OIDC + Workload Identity enabled
- **Azure Storage Account:** with file share mounted for PostgreSQL persistent storage

---

## Kubernetes Workloads

All workloads run in the **`fastapi`** namespace.

| Workload | Type | Description |
|---|---|---|
| `fastapi-api` | Deployment (2 replicas) | FastAPI REST API with liveness/readiness probes |
| `fastapi-worker` | Deployment | Celery background task worker |
| `postgres` | StatefulSet | PostgreSQL with Azure Files persistent volume |
| `redis` | Deployment | Redis message broker for Celery |
| `fastapi-service` | Service (LoadBalancer) | Public Azure LoadBalancer exposing port 80 |

Kubernetes Secrets and ConfigMaps are injected dynamically by Ansible and GitHub Actions — no credentials are stored in manifests.

---

## Ansible Automation

Ansible (`ansible/playbook.yaml`) is used in the `deploy-app` stage to:

1. Ensure the `fastapi` Kubernetes namespace exists
2. Apply all Kubernetes manifests idempotently (ConfigMaps, Secrets, Deployments, Services)
3. Add and update the `prometheus-community` Helm repository
4. Install the `kube-prometheus-stack` Helm chart into the `monitoring` namespace
5. Verify running pods after deployment

---

## Monitoring and Observability

The **kube-prometheus-stack** is installed via Helm into the `monitoring` namespace:

- **Prometheus** scrapes metrics from all cluster targets
- **Grafana** provides pre-built dashboards for cluster compute resources, namespace-level pods, node metrics, kubelet, and node exporter
- FastAPI pod CPU and memory metrics are visible in the Grafana **Namespace (Pods)** dashboard

Access Grafana locally:
```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
# Open http://localhost:3000  (login: admin / your-GRAFANA_ADMIN_PASSWORD from GitHub Secrets)
```

---

## Deployment Proof / Screenshots

Full screenshot index: [docs/screenshots/README.md](docs/screenshots/README.md)

### CI/CD Pipeline

![GitHub Actions Overall Success](docs/screenshots/01-github-actions-overall-success.png)

![Terraform Provision Success](docs/screenshots/03-github-actions-terraform-provision-success.png)

![Docker Build and Push Success](docs/screenshots/04-github-actions-docker-build-push-success.png)

![Ansible Playbook Success](docs/screenshots/06-github-actions-ansible-playbook-success.png)

![Smoke Test Success](docs/screenshots/07-github-actions-smoke-test-success.png)

---

### Azure Infrastructure

![Azure Resource Group Overview](docs/screenshots/08-azure-resource-group-overview.png)

![AKS Cluster Overview](docs/screenshots/09-azure-aks-cluster-overview.png)

![ACR Repositories](docs/screenshots/12-azure-acr-repositories.png)

---

### Kubernetes Workloads

![kubectl all fastapi namespace](docs/screenshots/15-kubectl-all-fastapi.png)

![kubectl services LoadBalancer](docs/screenshots/16-kubectl-services-loadbalancer.png)

![FastAPI Public Endpoint](docs/screenshots/17-fastapi-public-endpoint.png)

---

### Monitoring and Observability

![Monitoring Stack Helm Running](docs/screenshots/19-monitoring-stack-helm-running.png)

![Grafana Cluster Dashboard](docs/screenshots/20-grafana-cluster-dashboard.png)

![Grafana FastAPI Namespace Pods](docs/screenshots/21-grafana-fastapi-namespace-pods.png)

![Prometheus Targets UP](docs/screenshots/25-prometheus-targets-up.png)

---

## Local Setup

### Required Tools

| Tool | Purpose |
|---|---|
| Azure CLI | Azure authentication and resource management |
| Terraform | Infrastructure provisioning |
| Docker | Container image build and local testing |
| kubectl | Kubernetes cluster management |
| Helm | Monitoring stack installation |
| Python 3.11+ | FastAPI and Celery application |
| Git | Source control |

### Local Development with Docker Compose

```bash
# Start the full stack locally (no Azure required)
docker compose up --build

# Access the API at http://localhost:81
# API docs at http://localhost:81/docs

# Tear down
docker compose down -v
```

---

## Required GitHub Secrets

> [!IMPORTANT]
> Configure ALL of these secrets in your GitHub repo under **Settings → Secrets and variables → Actions** before triggering the workflow. Missing secrets will cause the pipeline to fail with a clear error message identifying which secret is missing.

| Secret | Required | Description |
|---|---|---|
| `AZURE_CREDENTIALS` | Yes | Azure Service Principal JSON (`clientId`, `clientSecret`, `subscriptionId`, `tenantId`) |
| `AZURE_RESOURCE_GROUP` | Yes | Azure resource group name for the application (e.g. `azure-aks-devops-rg`) |
| `AKS_CLUSTER_NAME` | Yes | AKS cluster name (e.g. `azure-aks-devops-cluster`) |
| `ACR_NAME` | Yes | ACR name without `.azurecr.io` — set to: `fahimaksdevopsacr` |
| `ACR_LOGIN_SERVER` | Yes | ACR login server — set to: `fahimaksdevopsacr.azurecr.io` |
| `POSTGRES_DB` | Yes | PostgreSQL database name |
| `POSTGRES_USER` | Yes | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes | PostgreSQL password |
| `WEATHER_API_KEY` | Yes | Weather API key (use `demo` for testing) |
| `GRAFANA_ADMIN_PASSWORD` | Yes | Grafana admin password for the monitoring stack |
| `AZURE_STORAGE_ACCOUNT_NAME` | Yes | Azure Storage Account name used for PostgreSQL file share (e.g. `fastapiaksstore`) |
| `TF_STATE_RG` | Yes | Resource Group containing the Terraform remote state storage account (e.g. `terraform-state-rg`) |
| `TF_STATE_STORAGE_ACCOUNT` | Yes | Azure Storage Account for Terraform remote state (e.g. `tfstate12345678`) |

> [!NOTE]
> `TF_STATE_RG` and `TF_STATE_STORAGE_ACCOUNT` are required for `terraform init` to connect to the Azure Storage remote backend. Create them by following the **Terraform Remote State Setup** guide below.

---

## Terraform Remote State Setup

> [!IMPORTANT]
> This is a **one-time setup** that must be completed before the GitHub Actions pipeline can run Terraform. The remote backend stores Terraform state in Azure Blob Storage so that state persists across pipeline runs and is not lost when runners restart.

### Step 1: Create the Backend Storage Account

Run these commands from your local machine (requires `az login`):

```bash
# Choose a unique name for the Terraform state storage account (3-24 lowercase alphanumeric chars)
TF_STATE_RG="terraform-state-rg"
TF_STATE_SA="tfstate$(openssl rand -hex 4)"   # e.g. tfstate3a7f2b9c
TF_STATE_CONTAINER="tfstate"

# Create resource group for Terraform state (separate from app RG)
az group create --name "$TF_STATE_RG" --location southeastasia

# Create storage account
az storage account create \
  --name "$TF_STATE_SA" \
  --resource-group "$TF_STATE_RG" \
  --sku Standard_LRS \
  --encryption-services blob \
  --allow-blob-public-access false

# Create the blob container
az storage container create \
  --name "$TF_STATE_CONTAINER" \
  --account-name "$TF_STATE_SA"

echo "TF_STATE_RG=$TF_STATE_RG"
echo "TF_STATE_STORAGE_ACCOUNT=$TF_STATE_SA"
```

### Step 2: Add GitHub Secrets

Add the following two secrets to your GitHub repository:
- `TF_STATE_RG` = value of `$TF_STATE_RG` (e.g. `terraform-state-rg`)
- `TF_STATE_STORAGE_ACCOUNT` = value of `$TF_STATE_SA` (e.g. `tfstate3a7f2b9c`)

### Step 3: Initialize Terraform with the Remote Backend (Local)

```bash
cd infra/

# Export credentials
export ARM_CLIENT_ID="<from AZURE_CREDENTIALS clientId>"
export ARM_CLIENT_SECRET="<from AZURE_CREDENTIALS clientSecret>"
export ARM_SUBSCRIPTION_ID="<from AZURE_CREDENTIALS subscriptionId>"
export ARM_TENANT_ID="<from AZURE_CREDENTIALS tenantId>"

terraform init \
  -backend-config="resource_group_name=terraform-state-rg" \
  -backend-config="storage_account_name=<TF_STATE_STORAGE_ACCOUNT>" \
  -backend-config="container_name=tfstate" \
  -backend-config="key=azure-aks-devops-pipeline.tfstate" \
  -input=false
```

### Step 4: Import Existing Azure Resources into Remote State

If your infrastructure already exists in Azure, import it so Terraform won't try to recreate it.

#### Windows / PowerShell Migration Script

If you are on Windows, you can use the included PowerShell script. Open a PowerShell terminal and run:

```powershell
$SUBSCRIPTION_ID="98f80b4a-c870-4a33-be5d-911ce933a22c"
$RESOURCE_GROUP="azure-aks-devops-rg"
$AKS_NAME="azure-aks-devops-cluster"
$ACR_NAME="fahimaksdevopsacr"
$STORAGE_ACCOUNT_NAME="fastapi5b3fd32c"
$TF_STATE_RG="terraform-state-rg"
$TF_STATE_STORAGE_ACCOUNT="<your tfstate storage account name>"

.\scripts\import-terraform-state.ps1 `
  -SubscriptionId $SUBSCRIPTION_ID `
  -ResourceGroup $RESOURCE_GROUP `
  -AksName $AKS_NAME `
  -AcrName $ACR_NAME `
  -StorageAccountName $STORAGE_ACCOUNT_NAME `
  -TfStateRg $TF_STATE_RG `
  -TfStateStorageAccount $TF_STATE_STORAGE_ACCOUNT
```

> **Note on Storage Account Update:** The old Kubernetes secret for PostgreSQL previously pointed to a deleted storage account (`fastapi00d37c175744e902`). The correct app storage account to use now is **`fastapi5b3fd32c`** as shown in the script above.

#### Manual Bash Import Commands

If you prefer to run the import manually in Bash:

```bash
# Set your values
SUBSCRIPTION_ID="98f80b4a-c870-4a33-be5d-911ce933a22c"
RESOURCE_GROUP="azure-aks-devops-rg"
ACR_NAME="fahimaksdevopsacr"
AKS_NAME="azure-aks-devops-cluster"
STORAGE_ACCOUNT="fastapi5b3fd32c"

# 1. Resource Group
terraform import azurerm_resource_group.rg \
  "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}"

# 2. Virtual Network
terraform import azurerm_virtual_network.vnet \
  "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Network/virtualNetworks/fastapi-vnet"

# 3. Subnet
terraform import azurerm_subnet.subnet \
  "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Network/virtualNetworks/fastapi-vnet/subnets/fastapi-subnet"

# 4. Container Registry
terraform import azurerm_container_registry.acr \
  "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.ContainerRegistry/registries/${ACR_NAME}"

# 5. AKS Cluster
terraform import azurerm_kubernetes_cluster.aks \
  "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.ContainerService/managedClusters/${AKS_NAME}"

# 6. Storage Account
terraform import azurerm_storage_account.storage \
  "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT}"

# 7. File Share
terraform import azurerm_storage_share.postgres_share \
  "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Storage/storageAccounts/${STORAGE_ACCOUNT}/fileServices/default/shares/postgres-data"

# 8. AKS-to-ACR role assignment (get the role assignment ID first)
ROLE_ASSIGNMENT_ID=$(az role assignment list \
  --scope "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.ContainerRegistry/registries/${ACR_NAME}" \
  --role "AcrPull" \
  --query "[0].id" -o tsv)
terraform import azurerm_role_assignment.aks_acr_pull "$ROLE_ASSIGNMENT_ID"
```

### Step 5: Verify — Run terraform plan

```bash
terraform plan \
  -var="aks_name=<AKS_CLUSTER_NAME>" \
  -var="resource_group_name=<RESOURCE_GROUP_NAME>" \
  -var="acr_name=<ACR_NAME>" \
  -var="storage_account_name=<STORAGE_ACCOUNT_NAME>"
```

> [!IMPORTANT]
> The expected output should be **`No changes. Your infrastructure matches the configuration.`**  
> If you see any destructive changes (`-/+` or `-`), **do not apply** and investigate the diff before proceeding.

---

## Troubleshooting

### `TF_STATE_RG is missing`
Create the secret in GitHub Repository → Settings → Secrets and variables → Actions. See [Terraform Remote State Setup](#terraform-remote-state-setup) above.

### `TF_STATE_STORAGE_ACCOUNT is missing`
Same as above. This is the storage account that holds your `terraform.tfstate` blob.

### `AZURE_STORAGE_ACCOUNT_NAME is missing`
This is the application storage account for the PostgreSQL Azure Files persistent volume (separate from the Terraform state storage account). Set it to the name of the storage account in your app resource group (e.g. `fastapiaksstore`).

### Terraform wants to recreate existing resources
This means existing resources are not in the Terraform state file. Run the import commands in [Step 4](#step-4-import-existing-azure-resources-into-remote-state) above.

### ACR name mismatch
Ensure the GitHub secret `ACR_NAME` is set to `fahimaksdevopsacr` and `ACR_LOGIN_SERVER` is set to `fahimaksdevopsacr.azurecr.io`.

### Terraform init asks for input interactively
All `terraform init` and `terraform apply` calls use `-input=false`. If you see an interactive prompt, ensure all `-backend-config` values are being passed correctly.

---

## Local Setup

---

## Security Notes

- No secrets are committed to this repository
- `terraform.tfstate` is in `.gitignore`
- `terraform.tfvars` is in `.gitignore`
- All credentials are managed through GitHub Actions repository secrets
- Screenshots containing passwords or credentials are not committed (excluded to `docs/screenshots/_excluded/`)
- Azure resources should be destroyed after demo use to avoid exposure of public IPs

---

## Release & Changelog
### Suggested First Release
- **v1.0.0**: Initial portfolio-ready release.
  - Includes full CI/CD pipeline, security cleanup, and structured deployment documentation.
- See `CHANGELOG.md` for a complete history of updates.
- It is highly recommended to leverage [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) to bundle version tags cleanly.

## Clean Up

> [!CAUTION]
> This project provisions real Azure resources (AKS, ACR, LoadBalancers, Storage) which incur cost. Always destroy infrastructure after testing.

```bash
# Delete all application Azure resources
az group delete --name azure-aks-devops-rg --yes --no-wait

# Optionally also delete the Terraform state storage
az group delete --name terraform-state-rg --yes --no-wait
```

---

## Related Portfolio Projects

This project builds on the foundations demonstrated in my other DevOps portfolio repositories:

- [FastAPI DevSecOps Pipeline](https://github.com/M-Fahim-Feroz/fastapi-devsecops-pipeline) — Application containerization, testing, security scanning, and Docker image publishing
- [Kubernetes Application Deployment](https://github.com/M-Fahim-Feroz/kubernetes-application-deployment) — Kubernetes manifests, Helm, probes, resource limits, autoscaling, and CI validation
- [Terraform AWS Infrastructure](https://github.com/M-Fahim-Feroz/terraform-aws-infrastructure) — Infrastructure as Code, secure networking, private compute/database tiers, remote state, and state locking

---

## For Detailed Deployment Steps

See [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for step-by-step Azure setup, service principal creation, and pipeline trigger instructions.
