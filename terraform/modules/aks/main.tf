terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }
}

variable "cluster_name" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "kubernetes_version" {
  type    = string
  default = "1.28.5"
}

variable "aks_subnet_id" {
  type = string
}

variable "system_node_count" {
  type    = number
  default = 3
}

variable "system_vm_size" {
  type    = string
  default = "Standard_D4s_v3"
}

variable "user_vm_size" {
  type    = string
  default = "Standard_D8s_v3"
}

variable "user_node_min_count" {
  type    = number
  default = 2
}

variable "user_node_max_count" {
  type    = number
  default = 10
}

variable "log_analytics_workspace_id" {
  type = string
}

variable "key_vault_id" {
  type = string
}

variable "acr_id" {
  type = string
}

variable "environment" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}

# ------------------------------------------------------------------
# AKS Cluster
# ------------------------------------------------------------------
resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.cluster_name
  kubernetes_version  = var.kubernetes_version

  # System node pool — only system pods scheduled here
  default_node_pool {
    name                = "system"
    node_count          = var.system_node_count
    vm_size             = var.system_vm_size
    vnet_subnet_id      = var.aks_subnet_id
    type                = "VirtualMachineScaleSets"
    os_disk_size_gb     = 128
    os_disk_type        = "Managed"

    node_labels = {
      "kubernetes.azure.com/mode" = "system"
      "workload-type"             = "system"
    }

    node_taints = ["CriticalAddonsOnly=true:NoSchedule"]

    upgrade_settings {
      max_surge = "33%"
    }
  }

  # Cluster identity
  identity {
    type = "SystemAssigned"
  }

  # Kubelet identity for ACR pulls
  kubelet_identity {
    # Managed by AKS
  }

  # RBAC
  role_based_access_control_enabled = true

  azure_active_directory_role_based_access_control {
    managed                = true
    azure_rbac_enabled     = true
    admin_group_object_ids = []
  }

  # Networking
  network_profile {
    network_plugin     = "azure"
    network_policy     = "calico"
    dns_service_ip     = "10.100.0.10"
    service_cidr       = "10.100.0.0/16"
    load_balancer_sku  = "standard"
    outbound_type      = "loadBalancer"
  }

  # OMS / Container Insights
  oms_agent {
    log_analytics_workspace_id = var.log_analytics_workspace_id
  }

  # Key Vault CSI driver
  key_vault_secrets_provider {
    secret_rotation_enabled  = true
    secret_rotation_interval = "2m"
  }

  # Azure Policy add-on
  azure_policy_enabled = true

  # HTTP application routing disabled (use custom ingress)
  http_application_routing_enabled = false

  # Workload identity
  workload_identity_enabled = true
  oidc_issuer_enabled       = true

  # Maintenance window
  maintenance_window {
    allowed {
      day   = "Sunday"
      hours = [2, 3, 4]
    }
  }

  tags = var.tags
}

# ------------------------------------------------------------------
# User Node Pool — Mobile App Workloads
# ------------------------------------------------------------------
resource "azurerm_kubernetes_cluster_node_pool" "mobile" {
  name                  = "mobile"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.user_vm_size
  vnet_subnet_id        = var.aks_subnet_id
  os_type               = "Linux"
  os_sku                = "Ubuntu"
  os_disk_size_gb       = 256
  os_disk_type          = "Managed"

  # Autoscaling
  enable_auto_scaling = true
  min_count           = var.user_node_min_count
  max_count           = var.user_node_max_count
  node_count          = var.user_node_min_count

  mode = "User"

  node_labels = {
    "workload-type"    = "mobile-backend"
    "environment"      = var.environment
    "node-pool"        = "mobile"
  }

  upgrade_settings {
    max_surge = "33%"
  }

  tags = var.tags
}

# ------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------
output "cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "cluster_id" {
  value = azurerm_kubernetes_cluster.main.id
}

output "api_server_url" {
  value     = azurerm_kubernetes_cluster.main.kube_config[0].host
  sensitive = true
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}

output "cluster_identity_principal_id" {
  value = azurerm_kubernetes_cluster.main.identity[0].principal_id
}

output "kubelet_identity_principal_id" {
  value = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}
