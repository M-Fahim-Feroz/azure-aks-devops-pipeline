variable "resource_group_name" {
  default = "azure-aks-devops-rg"
}

variable "location" {
  default = "southeastasia"
}

variable "aks_name" {
  default = "azure-aks-devops-cluster"
}

variable "acr_name" {
  default = "fahimaksdevopsacr"
}

variable "node_vm_size" {
  default = "Standard_B2s_v2"
}

variable "node_count" {
  default = 1
}