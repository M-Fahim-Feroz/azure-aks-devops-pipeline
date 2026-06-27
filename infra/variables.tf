variable "resource_group_name" {
  default = "fastapi-rg"
}

variable "location" {
  default = "southeastasia"
}

variable "aks_name" {
  default = "fastapi-aks"
}

variable "acr_name" {
  default = "fastapiacr123456789"
}

variable "node_vm_size" {
  default = "Standard_B2s_v2"
}

variable "node_count" {
  default = 1
}