# Terraform State Management

## Current Behavior (Stateless CI)

In this portfolio project, Terraform runs inside GitHub Actions using an uncommitted local state. Because GitHub-hosted runners are ephemeral, the state is **not persisted** between pipeline runs.

Why this is risky:
- Terraform assumes a blank slate on every run.
- It attempts to create resources that already exist, causing pipeline failures.
- If an `apply` fails mid-way, you get "partial apply" resources orphaned in Azure.

To make the pipeline robust without forcing a remote state backend immediately, the `.github/workflows/aks-cicd.yml` workflow includes a pre-flight "import script". It uses `az cli` to discover existing resources (like the Resource Group, VNet, Subnet, ACR, and AKS) and runs `terraform import` to dynamically pull them into the ephemeral state before `terraform apply`.

## Roadmap Item: Migrate Terraform state to Azure Storage remote backend

For true idempotency and safety, this project will eventually migrate to a remote backend.

### 1. Create the Backend Resources

```bash
# Create resource group
az group create --name tf-state-rg --location southeastasia

# Create storage account
az storage account create \
  --name tfstate$RANDOM \
  --resource-group tf-state-rg \
  --sku Standard_LRS \
  --encryption-services blob

# Create container
az storage container create \
  --name tfstate \
  --account-name <STORAGE_ACCOUNT_NAME>
```

### 2. Configure the Backend in Terraform

Update `infra/providers.tf` to initialize the backend:

```hcl
terraform {
  backend "azurerm" {
    # resource_group_name  = "<state-rg>"
    # storage_account_name = "<state-storage-account>"
    # container_name       = "tfstate"
    # key                  = "azure-aks-devops-pipeline.tfstate"
  }
}
```

## Manual State Import Commands

If you need to manually import resources into your local state, use the following syntax:

```bash
# Resource Group
terraform import azurerm_resource_group.rg /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP_NAME>

# Virtual Network
terraform import azurerm_virtual_network.vnet /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP_NAME>/providers/Microsoft.Network/virtualNetworks/fastapi-vnet

# AKS Cluster
terraform import azurerm_kubernetes_cluster.aks /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP_NAME>/providers/Microsoft.ContainerService/managedClusters/<AKS_CLUSTER_NAME>
```

## Partial Apply Recovery Steps

If a GitHub Actions deployment fails mid-way, you might have orphaned resources.

1. **Storage Accounts:** If a storage account was created but the pipeline failed, the next pipeline run will automatically find it via `az storage account list` and adopt it. The storage account name is now deterministically hashed so it won't endlessly orphan new accounts.
2. **ACR / AKS:** If creation fails, log into the Azure Portal and delete the failed resource if it is in a corrupted `Failed` provisioning state.
3. **Role Assignments:** Azure role assignments may be left behind. Terraform will usually gracefully overwrite or ignore them if the principal ID remains the same.

## State Security Notes

- Never commit `terraform.tfstate` or `terraform.tfstate.backup` to the repository.
- The `.gitignore` in this repository explicitly excludes `*.tfstate` files.
- The Azure Storage backend should have public access blocked.
- Use Azure RBAC to control who can read and write state.
