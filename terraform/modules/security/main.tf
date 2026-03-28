terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "environment" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "key_vault_sku" {
  type    = string
  default = "standard"
}

variable "enable_defender" {
  type    = bool
  default = true
}

variable "log_analytics_workspace_id" {
  type = string
}

variable "aks_subnet_id" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}

# ------------------------------------------------------------------
# Azure Key Vault
# ------------------------------------------------------------------
resource "azurerm_key_vault" "main" {
  name                        = "kv-mobile-plat-${var.environment}"
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = var.tenant_id
  sku_name                    = var.key_vault_sku

  # SC clearance: no public access
  public_network_access_enabled = false
  enable_rbac_authorization     = true

  # Soft delete + purge protection for compliance
  soft_delete_retention_days = 90
  purge_protection_enabled   = true

  network_acls {
    bypass                     = "AzureServices"
    default_action             = "Deny"
    ip_rules                   = []
    virtual_network_subnet_ids = [var.aks_subnet_id]
  }

  tags = var.tags
}

# ------------------------------------------------------------------
# Key Vault Diagnostic Settings → Log Analytics
# ------------------------------------------------------------------
resource "azurerm_monitor_diagnostic_setting" "key_vault" {
  name                       = "diag-kv-${var.environment}"
  target_resource_id         = azurerm_key_vault.main.id
  log_analytics_workspace_id = var.log_analytics_workspace_id

  enabled_log {
    category = "AuditEvent"
  }

  metric {
    category = "AllMetrics"
    enabled  = true
  }
}

# ------------------------------------------------------------------
# Azure Policy — No Privileged Containers
# ------------------------------------------------------------------
resource "azurerm_resource_group_policy_assignment" "no_privileged_containers" {
  name                 = "no-privileged-containers"
  resource_group_id    = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/${var.resource_group_name}-${var.environment}"
  policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/95edb821-ddaf-4404-9732-666045e056b4"

  description  = "Prevents privileged containers in AKS clusters"
  display_name = "No Privileged Containers Policy"

  parameters = jsonencode({
    excludedNamespaces = {
      value = ["kube-system", "gatekeeper-system", "azure-arc"]
    }
  })
}

# ------------------------------------------------------------------
# Azure Policy — Require Resource Tags
# ------------------------------------------------------------------
resource "azurerm_resource_group_policy_assignment" "require_tags" {
  name                 = "require-platform-tags"
  resource_group_id    = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/${var.resource_group_name}-${var.environment}"
  policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/96670d01-0a4d-4649-9c89-2d3abc0a5025"

  description  = "Requires environment and team tags on all resources"
  display_name = "Require Platform Tags"

  parameters = jsonencode({
    tagName = {
      value = "environment"
    }
  })
}

# ------------------------------------------------------------------
# Microsoft Defender for Cloud — AKS
# ------------------------------------------------------------------
resource "azurerm_security_center_subscription_pricing" "aks" {
  count         = var.enable_defender ? 1 : 0
  tier          = "Standard"
  resource_type = "KubernetesService"
}

resource "azurerm_security_center_subscription_pricing" "key_vault" {
  count         = var.enable_defender ? 1 : 0
  tier          = "Standard"
  resource_type = "KeyVaults"
}

resource "azurerm_security_center_subscription_pricing" "containers" {
  count         = var.enable_defender ? 1 : 0
  tier          = "Standard"
  resource_type = "Containers"
}

# ------------------------------------------------------------------
# Outputs
# ------------------------------------------------------------------
output "key_vault_id" {
  value = azurerm_key_vault.main.id
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}

output "key_vault_name" {
  value = azurerm_key_vault.main.name
}
