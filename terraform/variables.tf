variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "uksouth"
}

variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "rg-mobile-platform"
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "aks-mobile-platform"
}

variable "kubernetes_version" {
  description = "Kubernetes version for the AKS cluster"
  type        = string
  default     = "1.28.5"
}

variable "system_node_count" {
  description = "Number of nodes in the system node pool"
  type        = number
  default     = 3
}

variable "user_node_min_count" {
  description = "Minimum number of nodes in the user node pool"
  type        = number
  default     = 2
}

variable "user_node_max_count" {
  description = "Maximum number of nodes in the user node pool"
  type        = number
  default     = 10
}

variable "system_vm_size" {
  description = "VM size for system node pool"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "user_vm_size" {
  description = "VM size for user (workload) node pool"
  type        = string
  default     = "Standard_D8s_v3"
}

variable "vnet_address_space" {
  description = "Address space for the virtual network"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}

variable "aks_subnet_cidr" {
  description = "CIDR block for AKS subnet"
  type        = string
  default     = "10.1.0.0/16"
}

variable "appgw_subnet_cidr" {
  description = "CIDR block for Application Gateway subnet"
  type        = string
  default     = "10.2.0.0/24"
}

variable "key_vault_sku" {
  description = "SKU for Azure Key Vault (standard or premium)"
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "premium"], var.key_vault_sku)
    error_message = "Key Vault SKU must be 'standard' or 'premium'."
  }
}

variable "acr_sku" {
  description = "SKU for Azure Container Registry"
  type        = string
  default     = "Premium"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "ACR SKU must be Basic, Standard, or Premium."
  }
}

variable "enable_defender" {
  description = "Enable Microsoft Defender for Cloud on AKS"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Days to retain logs in Log Analytics workspace"
  type        = number
  default     = 90
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    project     = "mobile-platform"
    team        = "platform-engineering"
    environment = "dev"
    managed_by  = "terraform"
    clearance   = "sc"
  }
}
