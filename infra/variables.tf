variable "resource_group_name" {
  description = "Name of the Azure Resource Group."
  default     = "azure-aks-devops-rg"
}

variable "location" {
  description = "Azure region for all resources."
  default     = "southeastasia"
}

variable "aks_name" {
  description = "Name of the AKS cluster."
  default     = "azure-aks-devops-cluster"
}

variable "acr_name" {
  description = "Name of the Azure Container Registry (without .azurecr.io)."
  default     = "fahimaksdevopsacr"
}

variable "node_vm_size" {
  description = "VM size for AKS node pool."
  default     = "Standard_B2s_v2"
}

variable "node_count" {
  description = "Number of nodes in the AKS default node pool."
  default     = 1
}

variable "storage_account_name" {
  description = "Name of the Azure Storage Account used for PostgreSQL file share persistence. Must be globally unique, 3-24 lowercase alphanumeric characters."
}