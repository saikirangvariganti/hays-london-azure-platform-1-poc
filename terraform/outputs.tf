output "resource_group_name" {
  description = "Name of the Azure resource group"
  value       = azurerm_resource_group.main.name
}

output "aks_cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.cluster_name
}

output "aks_cluster_id" {
  description = "Resource ID of the AKS cluster"
  value       = module.aks.cluster_id
}

output "aks_api_server_url" {
  description = "AKS API server URL"
  value       = module.aks.api_server_url
  sensitive   = true
}

output "kube_config" {
  description = "Kubeconfig for connecting to AKS"
  value       = module.aks.kube_config
  sensitive   = true
}

output "acr_login_server" {
  description = "ACR login server URL"
  value       = azurerm_container_registry.main.login_server
}

output "key_vault_uri" {
  description = "URI of the Key Vault"
  value       = module.security.key_vault_uri
}

output "vnet_id" {
  description = "Resource ID of the VNet"
  value       = module.networking.vnet_id
}

output "aks_subnet_id" {
  description = "Resource ID of the AKS subnet"
  value       = module.networking.aks_subnet_id
}

output "log_analytics_workspace_id" {
  description = "Resource ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.main.id
}

output "cluster_identity_principal_id" {
  description = "Principal ID of the AKS cluster managed identity"
  value       = module.aks.cluster_identity_principal_id
}
