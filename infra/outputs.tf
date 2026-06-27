output "resource_group" {
  value = azurerm_resource_group.rg.name
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "node_vm_size" {
  value = var.node_vm_size
}

output "region" {
  value = var.location
}
output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "file_share_name" {
  value = azurerm_storage_share.postgres_share.name
}

