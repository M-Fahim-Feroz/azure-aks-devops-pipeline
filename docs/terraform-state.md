# Terraform State Management

## Current Behavior (Demo)

In this portfolio project, Terraform runs directly inside GitHub Actions without a remote backend.

This means:
- The state file exists only on the GitHub Actions runner for the duration of the pipeline run.
- The state is **not persisted** between pipeline runs.
- Each pipeline run provisions infrastructure from scratch.
- If a run fails mid-way, manual cleanup may be required.

This is acceptable for a **demo portfolio project** where the goal is to demonstrate end-to-end pipeline execution.

## Recommended Production Approach (Azure Storage Backend)

For a production workload, use an Azure Storage remote backend:

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

Add to `infra/main.tf`:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "tf-state-rg"
    storage_account_name = "<STORAGE_ACCOUNT_NAME>"
    container_name       = "tfstate"
    key                  = "azure-aks-devops-pipeline.tfstate"
  }
}
```

### 3. Benefits of Remote Backend

- **State locking:** Prevents concurrent modifications using Azure Blob lease locking.
- **State persistence:** Survives pipeline runs; can be referenced by multiple team members.
- **Versioning:** Azure Blob versioning provides state history and rollback.
- **Encryption:** Azure Storage encrypts at rest by default.
- **Access control:** State access is controlled by Azure RBAC.

### 4. GitHub Actions Configuration

With a remote backend, the workflow does not need to manage state between runs:

```yaml
- name: Terraform Init (Remote Backend)
  working-directory: ./infra
  env:
    ARM_CLIENT_ID: ${{ secrets.ARM_CLIENT_ID }}
    ARM_CLIENT_SECRET: ${{ secrets.ARM_CLIENT_SECRET }}
    ARM_SUBSCRIPTION_ID: ${{ secrets.ARM_SUBSCRIPTION_ID }}
    ARM_TENANT_ID: ${{ secrets.ARM_TENANT_ID }}
  run: terraform init
```

## State Security Notes

- Never commit `terraform.tfstate` or `terraform.tfstate.backup` to the repository.
- The `.gitignore` in this repository explicitly excludes `*.tfstate` files.
- The Azure Storage backend should have public access blocked.
- Use Azure RBAC to control who can read and write state.
