"""
test_poc.py — Comprehensive test suite for hays-london-azure-platform-1-poc.

Covers: Terraform files, Kubernetes manifests, Helm chart, scripts,
        monitoring config, Grafana dashboard, and project structure.

No live API calls — all tests are static file/content validation.
"""

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_text(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def load_yaml_all(rel: str) -> list:
    text = read_text(rel)
    return list(yaml.safe_load_all(text))


def load_yaml(rel: str) -> dict:
    text = read_text(rel)
    return yaml.safe_load(text)


def load_json(rel: str) -> dict:
    text = read_text(rel)
    return json.loads(text)


# ===========================================================================
# PROJECT STRUCTURE
# ===========================================================================

class TestProjectStructure:
    def test_readme_exists(self):
        assert (REPO_ROOT / "README.md").exists()

    def test_requirements_txt_exists(self):
        assert (REPO_ROOT / "requirements.txt").exists()

    def test_terraform_main_tf_exists(self):
        assert (REPO_ROOT / "terraform" / "main.tf").exists()

    def test_terraform_variables_tf_exists(self):
        assert (REPO_ROOT / "terraform" / "variables.tf").exists()

    def test_terraform_outputs_tf_exists(self):
        assert (REPO_ROOT / "terraform" / "outputs.tf").exists()

    def test_terraform_aks_module_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "aks" / "main.tf").exists()

    def test_terraform_networking_module_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "networking" / "main.tf").exists()

    def test_terraform_security_module_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "security" / "main.tf").exists()

    def test_k8s_deployment_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "deployment.yaml").exists()

    def test_k8s_namespace_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "namespace.yaml").exists()

    def test_k8s_service_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "service.yaml").exists()

    def test_k8s_hpa_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "hpa.yaml").exists()

    def test_k8s_ingress_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "ingress.yaml").exists()

    def test_helm_chart_yaml_exists(self):
        assert (REPO_ROOT / "helm" / "mobile-backend" / "Chart.yaml").exists()

    def test_helm_values_yaml_exists(self):
        assert (REPO_ROOT / "helm" / "mobile-backend" / "values.yaml").exists()

    def test_helm_deployment_template_exists(self):
        assert (REPO_ROOT / "helm" / "mobile-backend" / "templates" / "deployment.yaml").exists()

    def test_script_aks_bootstrap_exists(self):
        assert (REPO_ROOT / "scripts" / "aks_bootstrap.sh").exists()

    def test_script_monitoring_setup_exists(self):
        assert (REPO_ROOT / "scripts" / "monitoring_setup.py").exists()

    def test_monitoring_prometheus_rules_exists(self):
        assert (REPO_ROOT / "monitoring" / "prometheus_rules.yaml").exists()

    def test_monitoring_grafana_dashboard_exists(self):
        assert (REPO_ROOT / "monitoring" / "grafana_dashboard.json").exists()

    def test_tests_directory_exists(self):
        assert (REPO_ROOT / "tests").is_dir()


# ===========================================================================
# README
# ===========================================================================

class TestReadme:
    def test_readme_mentions_aks(self):
        content = read_text("README.md")
        assert "AKS" in content

    def test_readme_mentions_terraform(self):
        content = read_text("README.md")
        assert "Terraform" in content

    def test_readme_mentions_hays(self):
        content = read_text("README.md")
        assert "Hays" in content

    def test_readme_mentions_author(self):
        content = read_text("README.md")
        assert "Sai Kiran" in content

    def test_readme_mentions_key_vault(self):
        content = read_text("README.md")
        assert "Key Vault" in content

    def test_readme_mentions_prometheus(self):
        content = read_text("README.md")
        assert "Prometheus" in content

    def test_readme_mentions_github_actions(self):
        content = read_text("README.md")
        assert "GitHub Actions" in content

    def test_readme_mentions_public_sector(self):
        content = read_text("README.md")
        assert "public sector" in content.lower() or "Public Sector" in content

    def test_readme_has_architecture_section(self):
        content = read_text("README.md")
        assert "Architecture" in content

    def test_readme_has_quick_start(self):
        content = read_text("README.md")
        assert "Quick Start" in content


# ===========================================================================
# REQUIREMENTS
# ===========================================================================

class TestRequirements:
    def test_pytest_in_requirements(self):
        content = read_text("requirements.txt")
        assert "pytest" in content

    def test_pyyaml_in_requirements(self):
        content = read_text("requirements.txt")
        assert "pyyaml" in content.lower() or "PyYAML" in content

    def test_python_hcl2_in_requirements(self):
        content = read_text("requirements.txt")
        assert "hcl2" in content.lower()

    def test_jsonschema_in_requirements(self):
        content = read_text("requirements.txt")
        assert "jsonschema" in content


# ===========================================================================
# TERRAFORM — MAIN
# ===========================================================================

class TestTerraformMain:
    def test_required_version_present(self):
        content = read_text("terraform/main.tf")
        assert 'required_version = ">= 1.5.0"' in content

    def test_azurerm_provider_present(self):
        content = read_text("terraform/main.tf")
        assert "hashicorp/azurerm" in content

    def test_azuread_provider_present(self):
        content = read_text("terraform/main.tf")
        assert "hashicorp/azuread" in content

    def test_random_provider_present(self):
        content = read_text("terraform/main.tf")
        assert "hashicorp/random" in content

    def test_backend_azurerm_configured(self):
        content = read_text("terraform/main.tf")
        assert 'backend "azurerm"' in content

    def test_resource_group_defined(self):
        content = read_text("terraform/main.tf")
        assert "azurerm_resource_group" in content

    def test_log_analytics_workspace_defined(self):
        content = read_text("terraform/main.tf")
        assert "azurerm_log_analytics_workspace" in content

    def test_container_registry_defined(self):
        content = read_text("terraform/main.tf")
        assert "azurerm_container_registry" in content

    def test_acr_admin_disabled(self):
        content = read_text("terraform/main.tf")
        assert "admin_enabled       = false" in content

    def test_acr_public_network_access_disabled(self):
        content = read_text("terraform/main.tf")
        assert "public_network_access_enabled = false" in content

    def test_networking_module_referenced(self):
        content = read_text("terraform/main.tf")
        assert 'source = "./modules/networking"' in content

    def test_security_module_referenced(self):
        content = read_text("terraform/main.tf")
        assert 'source = "./modules/security"' in content

    def test_aks_module_referenced(self):
        content = read_text("terraform/main.tf")
        assert 'source = "./modules/aks"' in content

    def test_acr_pull_rbac_defined(self):
        content = read_text("terraform/main.tf")
        assert "AcrPull" in content

    def test_key_vault_secrets_user_rbac_defined(self):
        content = read_text("terraform/main.tf")
        assert "Key Vault Secrets User" in content

    def test_private_endpoint_acr_defined(self):
        content = read_text("terraform/main.tf")
        assert "azurerm_private_endpoint" in content and "acr" in content

    def test_key_vault_purge_protection_disabled_on_destroy(self):
        content = read_text("terraform/main.tf")
        assert "purge_soft_delete_on_destroy" in content

    def test_log_retention_variable_used(self):
        content = read_text("terraform/main.tf")
        assert "log_retention_days" in content


# ===========================================================================
# TERRAFORM — VARIABLES
# ===========================================================================

class TestTerraformVariables:
    def test_environment_variable_defined(self):
        content = read_text("terraform/variables.tf")
        assert 'variable "environment"' in content

    def test_environment_default_is_dev(self):
        content = read_text("terraform/variables.tf")
        assert 'default     = "dev"' in content

    def test_environment_validation_present(self):
        content = read_text("terraform/variables.tf")
        assert "dev" in content and "staging" in content and "prod" in content

    def test_location_variable_defined(self):
        content = read_text("terraform/variables.tf")
        assert 'variable "location"' in content

    def test_location_default_uksouth(self):
        content = read_text("terraform/variables.tf")
        assert "uksouth" in content

    def test_kubernetes_version_defined(self):
        content = read_text("terraform/variables.tf")
        assert 'variable "kubernetes_version"' in content

    def test_kubernetes_version_default(self):
        content = read_text("terraform/variables.tf")
        assert "1.28" in content

    def test_system_node_count_default_3(self):
        content = read_text("terraform/variables.tf")
        assert "default     = 3" in content

    def test_user_node_min_count_default(self):
        content = read_text("terraform/variables.tf")
        assert 'variable "user_node_min_count"' in content

    def test_user_node_max_count_default_10(self):
        content = read_text("terraform/variables.tf")
        assert "default     = 10" in content

    def test_vnet_address_space_defined(self):
        content = read_text("terraform/variables.tf")
        assert '["10.0.0.0/8"]' in content

    def test_aks_subnet_cidr_defined(self):
        content = read_text("terraform/variables.tf")
        assert "10.1.0.0/16" in content

    def test_appgw_subnet_cidr_defined(self):
        content = read_text("terraform/variables.tf")
        assert "10.2.0.0/24" in content

    def test_key_vault_sku_validation(self):
        content = read_text("terraform/variables.tf")
        assert "standard" in content and "premium" in content

    def test_acr_sku_validation(self):
        content = read_text("terraform/variables.tf")
        assert "Premium" in content

    def test_tags_variable_has_sc_clearance(self):
        content = read_text("terraform/variables.tf")
        assert "clearance" in content and "sc" in content

    def test_log_retention_days_default_90(self):
        content = read_text("terraform/variables.tf")
        assert "default     = 90" in content

    def test_enable_defender_variable_defined(self):
        content = read_text("terraform/variables.tf")
        assert 'variable "enable_defender"' in content


# ===========================================================================
# TERRAFORM — OUTPUTS
# ===========================================================================

class TestTerraformOutputs:
    def test_resource_group_name_output(self):
        content = read_text("terraform/outputs.tf")
        assert 'output "resource_group_name"' in content

    def test_aks_cluster_name_output(self):
        content = read_text("terraform/outputs.tf")
        assert 'output "aks_cluster_name"' in content

    def test_aks_api_server_url_output_sensitive(self):
        content = read_text("terraform/outputs.tf")
        assert "aks_api_server_url" in content
        assert "sensitive   = true" in content

    def test_kube_config_output_sensitive(self):
        content = read_text("terraform/outputs.tf")
        assert "kube_config" in content

    def test_acr_login_server_output(self):
        content = read_text("terraform/outputs.tf")
        assert 'output "acr_login_server"' in content

    def test_key_vault_uri_output(self):
        content = read_text("terraform/outputs.tf")
        assert 'output "key_vault_uri"' in content

    def test_vnet_id_output(self):
        content = read_text("terraform/outputs.tf")
        assert 'output "vnet_id"' in content

    def test_log_analytics_workspace_id_output(self):
        content = read_text("terraform/outputs.tf")
        assert 'output "log_analytics_workspace_id"' in content


# ===========================================================================
# TERRAFORM — AKS MODULE
# ===========================================================================

class TestTerraformAksModule:
    def test_azurerm_kubernetes_cluster_defined(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "azurerm_kubernetes_cluster" in content

    def test_rbac_enabled(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "role_based_access_control_enabled = true" in content

    def test_azure_ad_rbac_enabled(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "azure_rbac_enabled     = true" in content

    def test_network_plugin_azure(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert 'network_plugin     = "azure"' in content

    def test_network_policy_calico(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert 'network_policy     = "calico"' in content

    def test_oms_agent_configured(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "oms_agent" in content

    def test_key_vault_secrets_provider_configured(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "key_vault_secrets_provider" in content

    def test_secret_rotation_enabled(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "secret_rotation_enabled  = true" in content

    def test_workload_identity_enabled(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "workload_identity_enabled = true" in content

    def test_oidc_issuer_enabled(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "oidc_issuer_enabled       = true" in content

    def test_azure_policy_enabled(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "azure_policy_enabled = true" in content

    def test_http_routing_disabled(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "http_application_routing_enabled = false" in content

    def test_system_node_pool_taint(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "CriticalAddonsOnly=true:NoSchedule" in content

    def test_user_node_pool_autoscaling(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "enable_auto_scaling = true" in content

    def test_user_node_pool_mobile_label(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "mobile-backend" in content

    def test_maintenance_window_sunday(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert 'day   = "Sunday"' in content

    def test_cluster_identity_output(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "cluster_identity_principal_id" in content

    def test_kubelet_identity_output(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "kubelet_identity_principal_id" in content

    def test_os_disk_size_system_pool(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert "os_disk_size_gb     = 128" in content

    def test_upgrade_settings_max_surge(self):
        content = read_text("terraform/modules/aks/main.tf")
        assert 'max_surge = "33%"' in content


# ===========================================================================
# TERRAFORM — NETWORKING MODULE
# ===========================================================================

class TestTerraformNetworkingModule:
    def test_vnet_defined(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "azurerm_virtual_network" in content

    def test_aks_subnet_defined(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "azurerm_subnet" in content

    def test_nsg_defined(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "azurerm_network_security_group" in content

    def test_nsg_deny_all_inbound(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "DenyAllInBound" in content

    def test_nsg_allow_https_from_appgw(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "AllowHttpsFromAppGw" in content

    def test_application_gateway_defined(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "azurerm_application_gateway" in content

    def test_waf_enabled(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "waf_configuration" in content
        assert "enabled          = true" in content

    def test_waf_in_prevention_mode(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert 'firewall_mode    = "Prevention"' in content

    def test_waf_owasp_ruleset(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert 'rule_set_type    = "OWASP"' in content

    def test_private_dns_zone_acr(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "privatelink.azurecr.io" in content

    def test_private_endpoint_policies_disabled(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert "private_endpoint_network_policies_enabled     = false" in content

    def test_public_ip_static(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert 'allocation_method   = "Static"' in content

    def test_appgw_sku_waf_v2(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert 'name     = "WAF_v2"' in content

    def test_vnet_id_output(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert 'output "vnet_id"' in content

    def test_aks_subnet_id_output(self):
        content = read_text("terraform/modules/networking/main.tf")
        assert 'output "aks_subnet_id"' in content


# ===========================================================================
# TERRAFORM — SECURITY MODULE
# ===========================================================================

class TestTerraformSecurityModule:
    def test_key_vault_defined(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "azurerm_key_vault" in content

    def test_key_vault_public_access_disabled(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "public_network_access_enabled = false" in content

    def test_key_vault_rbac_authorization_enabled(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "enable_rbac_authorization     = true" in content

    def test_key_vault_soft_delete_90_days(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "soft_delete_retention_days = 90" in content

    def test_key_vault_purge_protection_enabled(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "purge_protection_enabled   = true" in content

    def test_key_vault_network_acls_deny_default(self):
        content = read_text("terraform/modules/security/main.tf")
        assert 'default_action             = "Deny"' in content

    def test_diagnostic_settings_audit_event(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "AuditEvent" in content

    def test_policy_no_privileged_containers(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "no-privileged-containers" in content or "no_privileged_containers" in content

    def test_policy_require_tags(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "require_tags" in content or "require-platform-tags" in content

    def test_defender_for_aks_defined(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "KubernetesService" in content

    def test_defender_for_key_vault_defined(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "KeyVaults" in content

    def test_defender_for_containers_defined(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "Containers" in content

    def test_defender_conditional_on_variable(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "var.enable_defender" in content

    def test_key_vault_id_output(self):
        content = read_text("terraform/modules/security/main.tf")
        assert 'output "key_vault_id"' in content

    def test_key_vault_uri_output(self):
        content = read_text("terraform/modules/security/main.tf")
        assert 'output "key_vault_uri"' in content


# ===========================================================================
# KUBERNETES — NAMESPACE
# ===========================================================================

class TestK8sNamespace:
    def setup_method(self):
        self.docs = load_yaml_all("k8s/namespace.yaml")

    def test_namespace_doc_present(self):
        kinds = [d.get("kind") for d in self.docs if d]
        assert "Namespace" in kinds

    def test_namespace_name_mobile_platform(self):
        ns = next(d for d in self.docs if d and d.get("kind") == "Namespace")
        assert ns["metadata"]["name"] == "mobile-platform"

    def test_namespace_label_environment_production(self):
        ns = next(d for d in self.docs if d and d.get("kind") == "Namespace")
        assert ns["metadata"]["labels"]["environment"] == "production"

    def test_namespace_label_team(self):
        ns = next(d for d in self.docs if d and d.get("kind") == "Namespace")
        assert ns["metadata"]["labels"]["team"] == "platform-engineering"

    def test_resource_quota_defined(self):
        kinds = [d.get("kind") for d in self.docs if d]
        assert "ResourceQuota" in kinds

    def test_resource_quota_pods_limit_50(self):
        rq = next(d for d in self.docs if d and d.get("kind") == "ResourceQuota")
        assert rq["spec"]["hard"]["pods"] == "50"

    def test_resource_quota_cpu_requests(self):
        rq = next(d for d in self.docs if d and d.get("kind") == "ResourceQuota")
        assert "requests.cpu" in rq["spec"]["hard"]

    def test_limit_range_defined(self):
        kinds = [d.get("kind") for d in self.docs if d]
        assert "LimitRange" in kinds

    def test_limit_range_has_container_type(self):
        lr = next(d for d in self.docs if d and d.get("kind") == "LimitRange")
        types = [lim["type"] for lim in lr["spec"]["limits"]]
        assert "Container" in types

    def test_namespace_annotation_owner(self):
        ns = next(d for d in self.docs if d and d.get("kind") == "Namespace")
        assert "owner" in ns["metadata"]["annotations"]


# ===========================================================================
# KUBERNETES — DEPLOYMENT
# ===========================================================================

class TestK8sDeployment:
    def setup_method(self):
        self.docs = [d for d in load_yaml_all("k8s/deployment.yaml") if d]

    def _get_deployment(self, name: str) -> dict:
        return next(
            d for d in self.docs
            if d.get("kind") == "Deployment" and d["metadata"]["name"] == name
        )

    def test_ios_deployment_exists(self):
        names = [d["metadata"]["name"] for d in self.docs if d.get("kind") == "Deployment"]
        assert "mobile-backend-ios" in names

    def test_android_deployment_exists(self):
        names = [d["metadata"]["name"] for d in self.docs if d.get("kind") == "Deployment"]
        assert "mobile-backend-android" in names

    def test_ios_deployment_namespace(self):
        d = self._get_deployment("mobile-backend-ios")
        assert d["metadata"]["namespace"] == "mobile-platform"

    def test_ios_deployment_replicas_3(self):
        d = self._get_deployment("mobile-backend-ios")
        assert d["spec"]["replicas"] == 3

    def test_android_deployment_replicas_3(self):
        d = self._get_deployment("mobile-backend-android")
        assert d["spec"]["replicas"] == 3

    def test_ios_rolling_update_strategy(self):
        d = self._get_deployment("mobile-backend-ios")
        assert d["spec"]["strategy"]["type"] == "RollingUpdate"

    def test_ios_rolling_update_max_unavailable_zero(self):
        d = self._get_deployment("mobile-backend-ios")
        assert d["spec"]["strategy"]["rollingUpdate"]["maxUnavailable"] == 0

    def test_ios_run_as_non_root(self):
        d = self._get_deployment("mobile-backend-ios")
        sc = d["spec"]["template"]["spec"]["securityContext"]
        assert sc["runAsNonRoot"] is True

    def test_ios_run_as_user_1000(self):
        d = self._get_deployment("mobile-backend-ios")
        sc = d["spec"]["template"]["spec"]["securityContext"]
        assert sc["runAsUser"] == 1000

    def test_ios_seccomp_runtime_default(self):
        d = self._get_deployment("mobile-backend-ios")
        sc = d["spec"]["template"]["spec"]["securityContext"]
        assert sc["seccompProfile"]["type"] == "RuntimeDefault"

    def test_ios_container_no_privilege_escalation(self):
        d = self._get_deployment("mobile-backend-ios")
        csc = d["spec"]["template"]["spec"]["containers"][0]["securityContext"]
        assert csc["allowPrivilegeEscalation"] is False

    def test_ios_container_readonly_root_fs(self):
        d = self._get_deployment("mobile-backend-ios")
        csc = d["spec"]["template"]["spec"]["containers"][0]["securityContext"]
        assert csc["readOnlyRootFilesystem"] is True

    def test_ios_container_drop_all_capabilities(self):
        d = self._get_deployment("mobile-backend-ios")
        csc = d["spec"]["template"]["spec"]["containers"][0]["securityContext"]
        assert "ALL" in csc["capabilities"]["drop"]

    def test_ios_prometheus_scrape_annotation(self):
        d = self._get_deployment("mobile-backend-ios")
        annotations = d["spec"]["template"]["metadata"]["annotations"]
        assert annotations.get("prometheus.io/scrape") == "true"

    def test_ios_resource_requests_cpu(self):
        d = self._get_deployment("mobile-backend-ios")
        req = d["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]
        assert req["cpu"] == "250m"

    def test_ios_resource_requests_memory(self):
        d = self._get_deployment("mobile-backend-ios")
        req = d["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]
        assert req["memory"] == "256Mi"

    def test_ios_resource_limits_cpu(self):
        d = self._get_deployment("mobile-backend-ios")
        lim = d["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]
        assert lim["cpu"] == "1000m"

    def test_ios_resource_limits_memory(self):
        d = self._get_deployment("mobile-backend-ios")
        lim = d["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]
        assert lim["memory"] == "1Gi"

    def test_ios_liveness_probe_defined(self):
        d = self._get_deployment("mobile-backend-ios")
        c = d["spec"]["template"]["spec"]["containers"][0]
        assert "livenessProbe" in c

    def test_ios_readiness_probe_defined(self):
        d = self._get_deployment("mobile-backend-ios")
        c = d["spec"]["template"]["spec"]["containers"][0]
        assert "readinessProbe" in c

    def test_ios_startup_probe_defined(self):
        d = self._get_deployment("mobile-backend-ios")
        c = d["spec"]["template"]["spec"]["containers"][0]
        assert "startupProbe" in c

    def test_ios_secrets_store_volume_mounted(self):
        d = self._get_deployment("mobile-backend-ios")
        vol_names = [v["name"] for v in d["spec"]["template"]["spec"]["volumes"]]
        assert "secrets-store" in vol_names

    def test_ios_csi_driver_secrets_store(self):
        d = self._get_deployment("mobile-backend-ios")
        vols = d["spec"]["template"]["spec"]["volumes"]
        csi_vols = [v for v in vols if "csi" in v]
        assert len(csi_vols) > 0
        assert csi_vols[0]["csi"]["driver"] == "secrets-store.csi.k8s.io"

    def test_ios_termination_grace_period_60(self):
        d = self._get_deployment("mobile-backend-ios")
        assert d["spec"]["template"]["spec"]["terminationGracePeriodSeconds"] == 60

    def test_ios_node_selector_mobile_backend(self):
        d = self._get_deployment("mobile-backend-ios")
        ns = d["spec"]["template"]["spec"]["nodeSelector"]
        assert ns.get("workload-type") == "mobile-backend"

    def test_service_account_defined(self):
        kinds = [d.get("kind") for d in self.docs]
        assert "ServiceAccount" in kinds

    def test_android_container_no_privilege_escalation(self):
        d = self._get_deployment("mobile-backend-android")
        csc = d["spec"]["template"]["spec"]["containers"][0]["securityContext"]
        assert csc["allowPrivilegeEscalation"] is False

    def test_pod_anti_affinity_spread_across_nodes(self):
        d = self._get_deployment("mobile-backend-ios")
        affinity = d["spec"]["template"]["spec"]["affinity"]
        assert "podAntiAffinity" in affinity


# ===========================================================================
# KUBERNETES — SERVICE
# ===========================================================================

class TestK8sService:
    def setup_method(self):
        self.docs = [d for d in load_yaml_all("k8s/service.yaml") if d]

    def test_ios_service_exists(self):
        names = [d["metadata"]["name"] for d in self.docs]
        assert "mobile-backend-ios-svc" in names

    def test_android_service_exists(self):
        names = [d["metadata"]["name"] for d in self.docs]
        assert "mobile-backend-android-svc" in names

    def test_ios_service_type_clusterip(self):
        svc = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-svc")
        assert svc["spec"]["type"] == "ClusterIP"

    def test_ios_service_port_80(self):
        svc = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-svc")
        ports = {p["name"]: p["port"] for p in svc["spec"]["ports"]}
        assert ports["http"] == 80

    def test_ios_service_target_port_8080(self):
        svc = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-svc")
        ports = {p["name"]: p["targetPort"] for p in svc["spec"]["ports"]}
        assert ports["http"] == 8080

    def test_ios_service_metrics_port(self):
        svc = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-svc")
        ports = {p["name"]: p["port"] for p in svc["spec"]["ports"]}
        assert "metrics" in ports

    def test_ios_service_selector_app(self):
        svc = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-svc")
        assert svc["spec"]["selector"]["app"] == "mobile-backend"

    def test_ios_service_namespace(self):
        svc = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-svc")
        assert svc["metadata"]["namespace"] == "mobile-platform"

    def test_services_have_prometheus_annotation(self):
        for svc in self.docs:
            annotations = svc["metadata"].get("annotations", {})
            assert annotations.get("prometheus.io/scrape") == "true"


# ===========================================================================
# KUBERNETES — HPA
# ===========================================================================

class TestK8sHpa:
    def setup_method(self):
        self.docs = [d for d in load_yaml_all("k8s/hpa.yaml") if d]

    def test_ios_hpa_exists(self):
        names = [d["metadata"]["name"] for d in self.docs]
        assert "mobile-backend-ios-hpa" in names

    def test_android_hpa_exists(self):
        names = [d["metadata"]["name"] for d in self.docs]
        assert "mobile-backend-android-hpa" in names

    def test_ios_hpa_api_version_v2(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-hpa")
        assert hpa["apiVersion"] == "autoscaling/v2"

    def test_ios_hpa_min_replicas_2(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-hpa")
        assert hpa["spec"]["minReplicas"] == 2

    def test_ios_hpa_max_replicas_10(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-hpa")
        assert hpa["spec"]["maxReplicas"] == 10

    def test_ios_hpa_cpu_target_70(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-hpa")
        cpu_metric = next(
            m for m in hpa["spec"]["metrics"]
            if m["resource"]["name"] == "cpu"
        )
        assert cpu_metric["resource"]["target"]["averageUtilization"] == 70

    def test_ios_hpa_memory_target_80(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-hpa")
        mem_metric = next(
            m for m in hpa["spec"]["metrics"]
            if m["resource"]["name"] == "memory"
        )
        assert mem_metric["resource"]["target"]["averageUtilization"] == 80

    def test_ios_hpa_scale_down_stabilization_300s(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-hpa")
        assert hpa["spec"]["behavior"]["scaleDown"]["stabilizationWindowSeconds"] == 300

    def test_ios_hpa_scale_up_stabilization_60s(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-hpa")
        assert hpa["spec"]["behavior"]["scaleUp"]["stabilizationWindowSeconds"] == 60

    def test_ios_hpa_targets_ios_deployment(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-ios-hpa")
        ref = hpa["spec"]["scaleTargetRef"]
        assert ref["name"] == "mobile-backend-ios"

    def test_android_hpa_targets_android_deployment(self):
        hpa = next(d for d in self.docs if d["metadata"]["name"] == "mobile-backend-android-hpa")
        ref = hpa["spec"]["scaleTargetRef"]
        assert ref["name"] == "mobile-backend-android"

    def test_hpa_namespace_mobile_platform(self):
        for hpa in self.docs:
            assert hpa["metadata"]["namespace"] == "mobile-platform"


# ===========================================================================
# KUBERNETES — INGRESS
# ===========================================================================

class TestK8sIngress:
    def setup_method(self):
        self.docs = [d for d in load_yaml_all("k8s/ingress.yaml") if d]
        self.ingress = self.docs[0]

    def test_ingress_kind(self):
        assert self.ingress["kind"] == "Ingress"

    def test_ingress_name(self):
        assert self.ingress["metadata"]["name"] == "mobile-backend-ingress"

    def test_ingress_namespace(self):
        assert self.ingress["metadata"]["namespace"] == "mobile-platform"

    def test_ingress_class_nginx(self):
        annotations = self.ingress["metadata"]["annotations"]
        assert annotations.get("kubernetes.io/ingress.class") == "nginx"

    def test_ingress_ssl_redirect(self):
        annotations = self.ingress["metadata"]["annotations"]
        assert annotations.get("nginx.ingress.kubernetes.io/ssl-redirect") == "true"

    def test_ingress_cert_manager_issuer(self):
        annotations = self.ingress["metadata"]["annotations"]
        assert annotations.get("cert-manager.io/cluster-issuer") == "letsencrypt-prod"

    def test_ingress_tls_configured(self):
        assert "tls" in self.ingress["spec"]
        assert len(self.ingress["spec"]["tls"]) > 0

    def test_ingress_tls_secret_name(self):
        tls = self.ingress["spec"]["tls"][0]
        assert tls["secretName"] == "mobile-platform-tls"

    def test_ingress_ios_route_defined(self):
        rules = self.ingress["spec"]["rules"]
        paths = [p["path"] for rule in rules for p in rule["http"]["paths"]]
        assert any("ios" in p for p in paths)

    def test_ingress_android_route_defined(self):
        rules = self.ingress["spec"]["rules"]
        paths = [p["path"] for rule in rules for p in rule["http"]["paths"]]
        assert any("android" in p for p in paths)

    def test_ingress_health_route_defined(self):
        rules = self.ingress["spec"]["rules"]
        paths = [p["path"] for rule in rules for p in rule["http"]["paths"]]
        assert any("health" in p for p in paths)

    def test_ingress_rate_limiting_enabled(self):
        annotations = self.ingress["metadata"]["annotations"]
        assert annotations.get("nginx.ingress.kubernetes.io/rate-limit") == "on"

    def test_ingress_host_gov_uk(self):
        rules = self.ingress["spec"]["rules"]
        hosts = [r["host"] for r in rules]
        assert any("gov.uk" in h for h in hosts)


# ===========================================================================
# HELM — CHART.YAML
# ===========================================================================

class TestHelmChart:
    def setup_method(self):
        self.chart = load_yaml("helm/mobile-backend/Chart.yaml")

    def test_chart_api_version_v2(self):
        assert self.chart["apiVersion"] == "v2"

    def test_chart_name(self):
        assert self.chart["name"] == "mobile-backend"

    def test_chart_version(self):
        assert "version" in self.chart
        assert self.chart["version"] == "1.0.0"

    def test_chart_app_version(self):
        assert "appVersion" in self.chart

    def test_chart_type_application(self):
        assert self.chart["type"] == "application"

    def test_chart_maintainer_saikiran(self):
        maintainers = self.chart.get("maintainers", [])
        names = [m["name"] for m in maintainers]
        assert any("Sai Kiran" in n for n in names)

    def test_chart_keywords_include_aks(self):
        keywords = self.chart.get("keywords", [])
        assert "aks" in keywords

    def test_chart_has_source_url(self):
        sources = self.chart.get("sources", [])
        assert any("github.com" in s for s in sources)


# ===========================================================================
# HELM — VALUES.YAML
# ===========================================================================

class TestHelmValues:
    def setup_method(self):
        self.values = load_yaml("helm/mobile-backend/values.yaml")

    def test_replica_count_3(self):
        assert self.values["replicaCount"] == 3

    def test_image_pull_policy_always(self):
        assert self.values["image"]["pullPolicy"] == "Always"

    def test_image_repository_acr(self):
        assert "azurecr.io" in self.values["image"]["repository"]

    def test_service_type_clusterip(self):
        assert self.values["service"]["type"] == "ClusterIP"

    def test_service_port_80(self):
        assert self.values["service"]["port"] == 80

    def test_autoscaling_enabled(self):
        assert self.values["autoscaling"]["enabled"] is True

    def test_autoscaling_min_replicas_2(self):
        assert self.values["autoscaling"]["minReplicas"] == 2

    def test_autoscaling_max_replicas_10(self):
        assert self.values["autoscaling"]["maxReplicas"] == 10

    def test_autoscaling_cpu_target_70(self):
        assert self.values["autoscaling"]["targetCPUUtilizationPercentage"] == 70

    def test_pod_security_run_as_non_root(self):
        assert self.values["podSecurityContext"]["runAsNonRoot"] is True

    def test_pod_security_run_as_user_1000(self):
        assert self.values["podSecurityContext"]["runAsUser"] == 1000

    def test_container_security_no_privilege_escalation(self):
        assert self.values["securityContext"]["allowPrivilegeEscalation"] is False

    def test_container_security_readonly_root_fs(self):
        assert self.values["securityContext"]["readOnlyRootFilesystem"] is True

    def test_container_security_drop_all(self):
        assert "ALL" in self.values["securityContext"]["capabilities"]["drop"]

    def test_ingress_enabled(self):
        assert self.values["ingress"]["enabled"] is True

    def test_ingress_class_nginx(self):
        assert self.values["ingress"]["className"] == "nginx"

    def test_node_selector_mobile_backend(self):
        assert self.values["nodeSelector"]["workload-type"] == "mobile-backend"

    def test_key_vault_enabled(self):
        assert self.values["keyVault"]["enabled"] is True

    def test_key_vault_name_present(self):
        assert "vaultName" in self.values["keyVault"]

    def test_resources_requests_cpu(self):
        assert self.values["resources"]["requests"]["cpu"] == "250m"

    def test_resources_limits_memory(self):
        assert self.values["resources"]["limits"]["memory"] == "1Gi"

    def test_prometheus_scrape_annotation(self):
        annotations = self.values.get("podAnnotations", {})
        assert annotations.get("prometheus.io/scrape") == "true"

    def test_liveness_probe_defined(self):
        assert "livenessProbe" in self.values

    def test_readiness_probe_defined(self):
        assert "readinessProbe" in self.values


# ===========================================================================
# HELM — DEPLOYMENT TEMPLATE
# ===========================================================================

class TestHelmDeploymentTemplate:
    def test_template_uses_fullname_helper(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert "mobile-backend.fullname" in content

    def test_template_rolling_update_strategy(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert "RollingUpdate" in content

    def test_template_max_unavailable_zero(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert "maxUnavailable: 0" in content

    def test_template_security_context_from_values(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert ".Values.podSecurityContext" in content

    def test_template_container_security_context(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert ".Values.securityContext" in content

    def test_template_image_tag_from_values(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert ".Values.image.tag" in content

    def test_template_termination_grace_period_60(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert "terminationGracePeriodSeconds: 60" in content

    def test_template_key_vault_volume_conditional(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert ".Values.keyVault.enabled" in content

    def test_template_secrets_store_csi_driver(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert "secrets-store.csi.k8s.io" in content

    def test_template_env_vars_from_values(self):
        content = read_text("helm/mobile-backend/templates/deployment.yaml")
        assert ".Values.env" in content


# ===========================================================================
# SCRIPT — AKS BOOTSTRAP
# ===========================================================================

class TestAksBootstrapScript:
    def test_script_has_shebang(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert content.startswith("#!/usr/bin/env bash")

    def test_script_set_euo_pipefail(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "set -euo pipefail" in content

    def test_script_checks_az_cli(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "command -v az" in content

    def test_script_checks_kubectl(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "command -v kubectl" in content

    def test_script_checks_helm(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "command -v helm" in content

    def test_script_gets_aks_credentials(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "az aks get-credentials" in content

    def test_script_installs_nginx_ingress(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "ingress-nginx" in content

    def test_script_installs_cert_manager(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "cert-manager" in content

    def test_script_installs_csi_secrets_store(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "csi-secrets-store" in content

    def test_script_applies_k8s_manifests(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "kubectl apply -f k8s/deployment.yaml" in content

    def test_script_waits_for_rollout(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "kubectl rollout status" in content

    def test_script_default_environment_dev(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert 'ENVIRONMENT="${1:-dev}"' in content

    def test_script_configures_secret_provider_class(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "SecretProviderClass" in content

    def test_script_acr_login(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "az acr login" in content

    def test_script_applies_namespace(self):
        content = read_text("scripts/aks_bootstrap.sh")
        assert "kubectl apply -f k8s/namespace.yaml" in content


# ===========================================================================
# SCRIPT — MONITORING SETUP
# ===========================================================================

class TestMonitoringSetupScript:
    def test_script_imports_argparse(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "import argparse" in content

    def test_script_imports_subprocess(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "import subprocess" in content

    def test_script_defines_repo_root(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "REPO_ROOT = Path(__file__).parent.parent" in content

    def test_script_prometheus_community_repo(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "prometheus-community.github.io/helm-charts" in content

    def test_script_grafana_repo(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "grafana.github.io/helm-charts" in content

    def test_script_monitoring_namespace(self):
        content = read_text("scripts/monitoring_setup.py")
        assert 'MONITORING_NAMESPACE = "monitoring"' in content

    def test_script_prometheus_retention_30d(self):
        content = read_text("scripts/monitoring_setup.py")
        assert '"retention": "30d"' in content

    def test_script_node_exporter_enabled(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "nodeExporter" in content

    def test_script_kube_state_metrics_enabled(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "kubeStateMetrics" in content

    def test_script_defines_main_function(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "def main()" in content

    def test_script_has_environment_argument(self):
        content = read_text("scripts/monitoring_setup.py")
        assert '"--environment"' in content

    def test_script_has_skip_install_flag(self):
        content = read_text("scripts/monitoring_setup.py")
        assert '"--skip-install"' in content

    def test_script_applies_prometheus_rules(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "apply_prometheus_rules" in content

    def test_script_imports_grafana_dashboard(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "import_grafana_dashboard" in content

    def test_prometheus_values_alertmanager_enabled(self):
        content = read_text("scripts/monitoring_setup.py")
        assert '"alertmanager"' in content

    def test_script_azure_monitor_info(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "Azure Monitor" in content or "azure_monitor" in content.lower()


# ===========================================================================
# MONITORING — PROMETHEUS RULES
# ===========================================================================

class TestPrometheusRules:
    def setup_method(self):
        self.doc = load_yaml("monitoring/prometheus_rules.yaml")

    def test_api_version_coreos(self):
        assert self.doc["apiVersion"] == "monitoring.coreos.com/v1"

    def test_kind_prometheus_rule(self):
        assert self.doc["kind"] == "PrometheusRule"

    def test_namespace_monitoring(self):
        assert self.doc["metadata"]["namespace"] == "monitoring"

    def test_alert_groups_defined(self):
        assert "groups" in self.doc["spec"]
        assert len(self.doc["spec"]["groups"]) > 0

    def test_availability_group_exists(self):
        group_names = [g["name"] for g in self.doc["spec"]["groups"]]
        assert any("availability" in n for n in group_names)

    def test_latency_group_exists(self):
        group_names = [g["name"] for g in self.doc["spec"]["groups"]]
        assert any("latency" in n for n in group_names)

    def test_resource_group_exists(self):
        group_names = [g["name"] for g in self.doc["spec"]["groups"]]
        assert any("resource" in n for n in group_names)

    def test_scaling_group_exists(self):
        group_names = [g["name"] for g in self.doc["spec"]["groups"]]
        assert any("scaling" in n for n in group_names)

    def test_mobile_backend_down_alert(self):
        all_alerts = [
            rule["alert"]
            for group in self.doc["spec"]["groups"]
            for rule in group["rules"]
            if "alert" in rule
        ]
        assert "MobileBackendDown" in all_alerts

    def test_high_error_rate_alert(self):
        all_alerts = [
            rule["alert"]
            for group in self.doc["spec"]["groups"]
            for rule in group["rules"]
            if "alert" in rule
        ]
        assert "MobileBackendHighErrorRate" in all_alerts

    def test_p95_latency_alert(self):
        all_alerts = [
            rule["alert"]
            for group in self.doc["spec"]["groups"]
            for rule in group["rules"]
            if "alert" in rule
        ]
        assert "MobileBackendHighLatencyP95" in all_alerts

    def test_hpa_max_replicas_alert(self):
        all_alerts = [
            rule["alert"]
            for group in self.doc["spec"]["groups"]
            for rule in group["rules"]
            if "alert" in rule
        ]
        assert "HPAMaxReplicasReached" in all_alerts

    def test_node_not_ready_alert(self):
        all_alerts = [
            rule["alert"]
            for group in self.doc["spec"]["groups"]
            for rule in group["rules"]
            if "alert" in rule
        ]
        assert "AKSNodeNotReady" in all_alerts

    def test_all_alerts_have_severity_label(self):
        for group in self.doc["spec"]["groups"]:
            for rule in group["rules"]:
                if "alert" in rule:
                    assert "severity" in rule.get("labels", {}), \
                        f"Alert {rule['alert']} missing severity label"

    def test_critical_alerts_exist(self):
        severities = [
            rule["labels"]["severity"]
            for group in self.doc["spec"]["groups"]
            for rule in group["rules"]
            if "alert" in rule and "labels" in rule
        ]
        assert "critical" in severities

    def test_all_alerts_have_summary_annotation(self):
        for group in self.doc["spec"]["groups"]:
            for rule in group["rules"]:
                if "alert" in rule:
                    assert "summary" in rule.get("annotations", {}), \
                        f"Alert {rule['alert']} missing summary annotation"


# ===========================================================================
# MONITORING — GRAFANA DASHBOARD
# ===========================================================================

class TestGrafanaDashboard:
    def setup_method(self):
        self.dashboard = load_json("monitoring/grafana_dashboard.json")

    def test_dashboard_has_inputs(self):
        assert "__inputs" in self.dashboard

    def test_dashboard_has_prometheus_datasource(self):
        inputs = self.dashboard["__inputs"]
        plugin_ids = [i.get("pluginId") for i in inputs]
        assert "prometheus" in plugin_ids

    def test_dashboard_has_panels(self):
        assert "panels" in self.dashboard
        assert len(self.dashboard["panels"]) > 0

    def test_dashboard_has_description(self):
        assert "description" in self.dashboard
        assert len(self.dashboard["description"]) > 0

    def test_dashboard_mentions_mobile_backend(self):
        desc = self.dashboard.get("description", "")
        assert "Mobile" in desc or "mobile" in desc

    def test_dashboard_has_requires_section(self):
        assert "__requires" in self.dashboard

    def test_dashboard_requires_grafana(self):
        requires = self.dashboard["__requires"]
        grafana_req = [r for r in requires if r.get("id") == "grafana"]
        assert len(grafana_req) > 0

    def test_dashboard_annotations_defined(self):
        assert "annotations" in self.dashboard


# ===========================================================================
# CROSS-CUTTING SECURITY CHECKS
# ===========================================================================

class TestSecurityControls:
    def test_no_plaintext_passwords_in_deployment(self):
        content = read_text("k8s/deployment.yaml")
        assert "password" not in content.lower() or "secretKeyRef" in content

    def test_no_plaintext_passwords_in_terraform_main(self):
        content = read_text("terraform/main.tf")
        # Ensure no obvious hardcoded credentials
        assert "password" not in content.lower() or "var." in content

    def test_acr_private_endpoint_in_terraform(self):
        content = read_text("terraform/main.tf")
        assert "azurerm_private_endpoint" in content

    def test_key_vault_private_network_only(self):
        content = read_text("terraform/modules/security/main.tf")
        assert "public_network_access_enabled = false" in content

    def test_k8s_deployment_no_root_user(self):
        docs = [d for d in load_yaml_all("k8s/deployment.yaml") if d]
        for doc in docs:
            if doc.get("kind") == "Deployment":
                sc = doc["spec"]["template"]["spec"].get("securityContext", {})
                assert sc.get("runAsNonRoot") is True, \
                    f"{doc['metadata']['name']} missing runAsNonRoot"

    def test_helm_values_no_root_user(self):
        values = load_yaml("helm/mobile-backend/values.yaml")
        assert values["podSecurityContext"]["runAsNonRoot"] is True

    def test_ingress_tls_configured(self):
        docs = [d for d in load_yaml_all("k8s/ingress.yaml") if d]
        ingress = docs[0]
        assert "tls" in ingress["spec"]

    def test_terraform_tags_include_managed_by(self):
        content = read_text("terraform/variables.tf")
        assert "managed_by" in content and "terraform" in content


# ===========================================================================
# CONSISTENCY CHECKS
# ===========================================================================

class TestConsistency:
    def test_namespace_consistent_across_k8s_files(self):
        """All k8s resources use mobile-platform namespace."""
        files = ["k8s/deployment.yaml", "k8s/service.yaml",
                 "k8s/hpa.yaml", "k8s/ingress.yaml"]
        for f in files:
            docs = [d for d in load_yaml_all(f) if d]
            for doc in docs:
                ns = doc.get("metadata", {}).get("namespace")
                assert ns == "mobile-platform", \
                    f"File {f} resource {doc['metadata']['name']} has namespace {ns!r}"

    def test_hpa_references_existing_deployments(self):
        deploy_docs = [d for d in load_yaml_all("k8s/deployment.yaml") if d]
        deploy_names = {d["metadata"]["name"] for d in deploy_docs if d.get("kind") == "Deployment"}
        hpa_docs = [d for d in load_yaml_all("k8s/hpa.yaml") if d]
        for hpa in hpa_docs:
            target = hpa["spec"]["scaleTargetRef"]["name"]
            assert target in deploy_names, \
                f"HPA {hpa['metadata']['name']} references unknown deployment {target}"

    def test_service_selectors_match_deployment_labels(self):
        deploy_docs = [d for d in load_yaml_all("k8s/deployment.yaml") if d]
        svc_docs = [d for d in load_yaml_all("k8s/service.yaml") if d]
        for svc in svc_docs:
            selector = svc["spec"]["selector"]
            matched = False
            for dep in deploy_docs:
                if dep.get("kind") != "Deployment":
                    continue
                labels = dep["spec"]["selector"]["matchLabels"]
                if all(labels.get(k) == v for k, v in selector.items()):
                    matched = True
                    break
            assert matched, \
                f"Service {svc['metadata']['name']} selector {selector} matches no deployment"

    def test_helm_replica_matches_k8s_deployment(self):
        values = load_yaml("helm/mobile-backend/values.yaml")
        docs = [d for d in load_yaml_all("k8s/deployment.yaml") if d]
        ios_dep = next(d for d in docs if d.get("kind") == "Deployment"
                       and "ios" in d["metadata"]["name"])
        assert values["replicaCount"] == ios_dep["spec"]["replicas"]

    def test_helm_cpu_requests_match_k8s(self):
        values = load_yaml("helm/mobile-backend/values.yaml")
        docs = [d for d in load_yaml_all("k8s/deployment.yaml") if d]
        ios_dep = next(d for d in docs if d.get("kind") == "Deployment"
                       and "ios" in d["metadata"]["name"])
        k8s_req = ios_dep["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["cpu"]
        helm_req = values["resources"]["requests"]["cpu"]
        assert helm_req == k8s_req

    def test_hpa_max_replicas_consistent(self):
        values = load_yaml("helm/mobile-backend/values.yaml")
        hpa_docs = [d for d in load_yaml_all("k8s/hpa.yaml") if d]
        ios_hpa = next(d for d in hpa_docs if "ios" in d["metadata"]["name"])
        assert values["autoscaling"]["maxReplicas"] == ios_hpa["spec"]["maxReplicas"]

    def test_monitoring_script_references_prometheus_rules_file(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "prometheus_rules.yaml" in content

    def test_monitoring_script_references_grafana_dashboard_file(self):
        content = read_text("scripts/monitoring_setup.py")
        assert "grafana_dashboard.json" in content
