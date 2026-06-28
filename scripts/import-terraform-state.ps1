param (
    [Parameter(Mandatory=$true)][string]$SubscriptionId,
    [Parameter(Mandatory=$true)][string]$ResourceGroup,
    [Parameter(Mandatory=$true)][string]$AksName,
    [Parameter(Mandatory=$true)][string]$AcrName,
    [Parameter(Mandatory=$true)][string]$StorageAccountName,
    [Parameter(Mandatory=$true)][string]$TfStateRg,
    [Parameter(Mandatory=$true)][string]$TfStateStorageAccount
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================================="
Write-Host " Importing Existing Azure Resources to Terraform State"
Write-Host "=========================================================="

cd infra

Write-Host "`n[1/4] Initializing Terraform backend..."
terraform init `
  -backend-config="resource_group_name=$TfStateRg" `
  -backend-config="storage_account_name=$TfStateStorageAccount" `
  -backend-config="container_name=tfstate" `
  -backend-config="key=azure-aks-devops-pipeline.tfstate" `
  -input=false

Write-Host "`n[2/4] Retrieving current Terraform state..."
$currentState = terraform state list

function Import-Resource {
    param(
        [string]$ResourceAddress,
        [string]$AzureId
    )
    if ($currentState -contains $ResourceAddress) {
        Write-Host "  [SKIP] $ResourceAddress is already in state."
    } else {
        Write-Host "  [IMPORT] Importing $ResourceAddress ..."
        terraform import $ResourceAddress $AzureId
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to import $ResourceAddress"
            exit 1
        }
    }
}

Write-Host "`n[3/4] Importing resources..."

$RgId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup"
Import-Resource -ResourceAddress "azurerm_resource_group.rg" -AzureId $RgId

$VnetId = "$RgId/providers/Microsoft.Network/virtualNetworks/fastapi-vnet"
Import-Resource -ResourceAddress "azurerm_virtual_network.vnet" -AzureId $VnetId

$SubnetId = "$VnetId/subnets/fastapi-subnet"
Import-Resource -ResourceAddress "azurerm_subnet.subnet" -AzureId $SubnetId

$AcrId = "$RgId/providers/Microsoft.ContainerRegistry/registries/$AcrName"
Import-Resource -ResourceAddress "azurerm_container_registry.acr" -AzureId $AcrId

$AksId = "$RgId/providers/Microsoft.ContainerService/managedClusters/$AksName"
Import-Resource -ResourceAddress "azurerm_kubernetes_cluster.aks" -AzureId $AksId

$StorageId = "$RgId/providers/Microsoft.Storage/storageAccounts/$StorageAccountName"
Import-Resource -ResourceAddress "azurerm_storage_account.storage" -AzureId $StorageId

$ShareId = "$StorageId/fileServices/default/shares/postgres-data"
Import-Resource -ResourceAddress "azurerm_storage_share.postgres_share" -AzureId $ShareId

Write-Host "  Checking for AKS to ACR role assignment..."
if ($currentState -contains "azurerm_role_assignment.aks_acr_pull") {
     Write-Host "  [SKIP] azurerm_role_assignment.aks_acr_pull is already in state."
} else {
    Write-Host "  Retrieving kubelet identity..."
    $KubeletObjectId = az aks show --resource-group $ResourceGroup --name $AksName --query "identityProfile.kubeletidentity.objectId" -o tsv
    if ([string]::IsNullOrWhiteSpace($KubeletObjectId)) {
        Write-Host "  [WARN] Could not retrieve kubelet identity. Skipping role assignment import."
    } else {
        Write-Host "  Finding AcrPull role assignment for $KubeletObjectId on $AcrId ..."
        $RoleAssignmentId = az role assignment list --scope $AcrId --role "AcrPull" --query "[?principalId=='$KubeletObjectId'].id | [0]" -o tsv
        if (-not [string]::IsNullOrWhiteSpace($RoleAssignmentId)) {
            Write-Host "  [IMPORT] Importing azurerm_role_assignment.aks_acr_pull ..."
            terraform import azurerm_role_assignment.aks_acr_pull $RoleAssignmentId
             if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to import azurerm_role_assignment.aks_acr_pull"
                exit 1
            }
        } else {
            Write-Host "  [SKIP] No existing role assignment found."
        }
    }
}


Write-Host "`n[4/4] Running terraform plan..."
terraform plan -input=false `
  -var="resource_group_name=$ResourceGroup" `
  -var="aks_name=$AksName" `
  -var="acr_name=$AcrName" `
  -var="storage_account_name=$StorageAccountName"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Terraform plan failed."
    exit 1
}

Write-Host "`n=========================================================="
Write-Host " Import process completed."
Write-Host " Review the terraform plan output above."
Write-Host " It should indicate 'No changes. Your infrastructure matches the configuration.'"
Write-Host "=========================================================="
cd ..
