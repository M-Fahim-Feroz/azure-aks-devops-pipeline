

# -------------------------------
# Resource Group
# -------------------------------
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# -------------------------------
# Virtual Network
# -------------------------------
resource "azurerm_virtual_network" "vnet" {
  name                = "fastapi-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# -------------------------------
# Subnet
# -------------------------------
resource "azurerm_subnet" "subnet" {
  name                 = "fastapi-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# -------------------------------
# Azure Container Registry (ACR)
# -------------------------------
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false
}

# -------------------------------
# Azure Kubernetes Service (AKS)
# -------------------------------
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "fastapi"

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.node_vm_size
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin = "azure"
  }

  oidc_issuer_enabled       = true
  workload_identity_enabled = true
}

# -------------------------------
# AKS → ACR PULL PERMISSION
# -------------------------------
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name = "AcrPull"
  scope                = azurerm_container_registry.acr.id
}
# -------------------------------
# Storage Account
# -------------------------------
resource "azurerm_storage_account" "storage" {
  name                     = "fastapi${substr(md5(azurerm_resource_group.rg.id), 0, 8)}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# -------------------------------
# File Share for Postgres
# -------------------------------
resource "azurerm_storage_share" "postgres_share" {
  name                 = "postgres-data"
  storage_account_name = azurerm_storage_account.storage.name
  quota                = 1 # 1 GB
}

