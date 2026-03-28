terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.46"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "stmobileplatformtfstate"
    container_name       = "tfstate"
    key                  = "mobile-platform.terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = true
    }
  }
}

# ------------------------------------------------------------------
# Data Sources
# ------------------------------------------------------------------
data "azurerm_client_config" "current" {}

# ------------------------------------------------------------------
# Resource Group
# ------------------------------------------------------------------
resource "azurerm_resource_group" "main" {
  name     = "${var.resource_group_name}-${var.environment}"
  location = var.location

  tags = merge(var.tags, {
    environment = var.environment
  })
}

# ------------------------------------------------------------------
# Log Analytics Workspace (for AKS Container Insights + Defender)
# ------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "main" {
  name                = "law-mobile-platform-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days

  tags = var.tags
}

# ------------------------------------------------------------------
# Azure Container Registry
# ------------------------------------------------------------------
resource "azurerm_container_registry" "main" {
  name                = "acrmobileplatform${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.acr_sku
  admin_enabled       = false

  # Disable public network access for SC clearance environments
  public_network_access_enabled = false

  network_rule_bypass_option = "AzureServices"

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

# ------------------------------------------------------------------
# Networking Module
# ------------------------------------------------------------------
module "networking" {
  source = "./modules/networking"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  environment         = var.environment
  vnet_address_space  = var.vnet_address_space
  aks_subnet_cidr     = var.aks_subnet_cidr
  appgw_subnet_cidr   = var.appgw_subnet_cidr
  tags                = var.tags
}

# ------------------------------------------------------------------
# Security Module (Key Vault, Azure Policy, Defender)
# ------------------------------------------------------------------
module "security" {
  source = "./modules/security"

  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  environment                = var.environment
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  key_vault_sku              = var.key_vault_sku
  enable_defender            = var.enable_defender
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  aks_subnet_id              = module.networking.aks_subnet_id
  tags                       = var.tags
}

# ------------------------------------------------------------------
# AKS Module
# ------------------------------------------------------------------
module "aks" {
  source = "./modules/aks"

  cluster_name               = "${var.cluster_name}-${var.environment}"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  kubernetes_version         = var.kubernetes_version
  aks_subnet_id              = module.networking.aks_subnet_id
  system_node_count          = var.system_node_count
  system_vm_size             = var.system_vm_size
  user_vm_size               = var.user_vm_size
  user_node_min_count        = var.user_node_min_count
  user_node_max_count        = var.user_node_max_count
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  key_vault_id               = module.security.key_vault_id
  acr_id                     = azurerm_container_registry.main.id
  environment                = var.environment
  tags                       = var.tags
}

# ------------------------------------------------------------------
# RBAC: AKS → ACR pull
# ------------------------------------------------------------------
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = module.aks.kubelet_identity_principal_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.main.id
  skip_service_principal_aad_check = true
}

# ------------------------------------------------------------------
# RBAC: AKS → Key Vault secrets user
# ------------------------------------------------------------------
resource "azurerm_role_assignment" "aks_kv_secrets_user" {
  principal_id         = module.aks.cluster_identity_principal_id
  role_definition_name = "Key Vault Secrets User"
  scope                = module.security.key_vault_id
}

# ------------------------------------------------------------------
# Private endpoint: ACR
# ------------------------------------------------------------------
resource "azurerm_private_endpoint" "acr" {
  name                = "pe-acr-${var.environment}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = module.networking.aks_subnet_id

  private_service_connection {
    name                           = "psc-acr-${var.environment}"
    private_connection_resource_id = azurerm_container_registry.main.id
    subresource_names              = ["registry"]
    is_manual_connection           = false
  }

  tags = var.tags
}
