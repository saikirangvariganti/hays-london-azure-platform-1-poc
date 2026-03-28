#!/usr/bin/env python3
"""
monitoring_setup.py — Install and configure Prometheus + Grafana on AKS
for the mobile platform POC (Hays London — Public Sector).

Usage:
    python scripts/monitoring_setup.py [--environment dev|staging|prod]
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent

PROMETHEUS_HELM_REPO = "https://prometheus-community.github.io/helm-charts"
GRAFANA_HELM_REPO    = "https://grafana.github.io/helm-charts"

MONITORING_NAMESPACE = "monitoring"

PROMETHEUS_VALUES = {
    "alertmanager": {
        "enabled": True,
        "config": {
            "global": {
                "resolve_timeout": "5m"
            },
            "route": {
                "receiver": "teams",
                "group_by": ["alertname", "namespace"],
                "group_wait": "30s",
                "group_interval": "5m",
                "repeat_interval": "4h"
            },
            "receivers": [
                {
                    "name": "teams",
                    "webhook_configs": [
                        {"url": "REPLACE_WITH_TEAMS_WEBHOOK"}
                    ]
                }
            ]
        }
    },
    "prometheus": {
        "prometheusSpec": {
            "retention": "30d",
            "retentionSize": "50GB",
            "resources": {
                "requests": {"cpu": "500m", "memory": "1Gi"},
                "limits":   {"cpu": "2000m", "memory": "4Gi"}
            },
            "storageSpec": {
                "volumeClaimTemplate": {
                    "spec": {
                        "storageClassName": "managed-premium",
                        "accessModes": ["ReadWriteOnce"],
                        "resources": {
                            "requests": {"storage": "100Gi"}
                        }
                    }
                }
            },
            "additionalScrapeConfigs": [
                {
                    "job_name": "mobile-backend",
                    "kubernetes_sd_configs": [
                        {"role": "pod", "namespaces": {"names": ["mobile-platform"]}}
                    ],
                    "relabel_configs": [
                        {
                            "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_scrape"],
                            "action": "keep",
                            "regex": "true"
                        },
                        {
                            "source_labels": ["__meta_kubernetes_pod_annotation_prometheus_io_path"],
                            "action": "replace",
                            "target_label": "__metrics_path__",
                            "regex": "(.+)"
                        },
                        {
                            "source_labels": [
                                "__address__",
                                "__meta_kubernetes_pod_annotation_prometheus_io_port"
                            ],
                            "action": "replace",
                            "regex": "([^:]+)(?::\\d+)?;(\\d+)",
                            "replacement": "$1:$2",
                            "target_label": "__address__"
                        }
                    ]
                }
            ]
        }
    },
    "grafana": {
        "enabled": True,
        "adminPassword": "REPLACE_WITH_SECURE_PASSWORD",
        "persistence": {
            "enabled": True,
            "storageClassName": "managed-premium",
            "size": "10Gi"
        },
        "dashboardProviders": {
            "dashboardproviders.yaml": {
                "apiVersion": 1,
                "providers": [
                    {
                        "name": "mobile-platform",
                        "orgId": 1,
                        "folder": "Mobile Platform",
                        "type": "file",
                        "disableDeletion": False,
                        "options": {
                            "path": "/var/lib/grafana/dashboards/mobile-platform"
                        }
                    }
                ]
            }
        },
        "sidecar": {
            "dashboards": {
                "enabled": True,
                "searchNamespace": "monitoring"
            }
        }
    },
    "kubeStateMetrics": {"enabled": True},
    "nodeExporter":     {"enabled": True}
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command with logging."""
    log.info("Running: %s", " ".join(cmd))
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True
    )


def helm_repo_add(name: str, url: str) -> None:
    run(["helm", "repo", "add", name, url], check=False)
    run(["helm", "repo", "update"])


def create_namespace(namespace: str) -> None:
    run(
        ["kubectl", "create", "namespace", namespace, "--dry-run=client", "-o", "yaml"],
        capture=True
    )
    result = run(
        ["kubectl", "create", "namespace", namespace],
        check=False,
        capture=True
    )
    if result.returncode != 0 and "already exists" not in result.stderr:
        log.error("Failed to create namespace: %s", result.stderr)
        sys.exit(1)
    log.info("Namespace %s ready", namespace)


def install_prometheus_stack(environment: str, values_override: dict) -> None:
    """Install kube-prometheus-stack via Helm."""
    import tempfile
    import yaml

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(values_override, f)
        values_file = f.name

    run([
        "helm", "upgrade", "--install", "kube-prometheus-stack",
        "prometheus-community/kube-prometheus-stack",
        "--namespace", MONITORING_NAMESPACE,
        "--values", values_file,
        "--set", f"global.labels.environment={environment}",
        "--wait", "--timeout", "10m"
    ])

    log.info("kube-prometheus-stack installed in namespace: %s", MONITORING_NAMESPACE)


def apply_prometheus_rules() -> None:
    """Apply custom Prometheus alerting rules."""
    rules_file = REPO_ROOT / "monitoring" / "prometheus_rules.yaml"
    if rules_file.exists():
        run(["kubectl", "apply", "-f", str(rules_file)])
        log.info("Prometheus rules applied from %s", rules_file)
    else:
        log.warning("Prometheus rules file not found: %s", rules_file)


def import_grafana_dashboard() -> None:
    """Apply Grafana dashboard ConfigMap."""
    dashboard_file = REPO_ROOT / "monitoring" / "grafana_dashboard.json"
    if not dashboard_file.exists():
        log.warning("Grafana dashboard file not found: %s", dashboard_file)
        return

    dashboard_json = dashboard_file.read_text(encoding="utf-8")

    configmap_yaml = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: mobile-backend-dashboard
  namespace: {MONITORING_NAMESPACE}
  labels:
    grafana_dashboard: "1"
data:
  mobile-backend-dashboard.json: |
{chr(10).join('    ' + line for line in dashboard_json.splitlines())}
"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(configmap_yaml)
        cm_file = f.name

    run(["kubectl", "apply", "-f", cm_file])
    log.info("Grafana dashboard ConfigMap applied")


def configure_azure_monitor_integration() -> None:
    """Output instructions for Azure Monitor Container Insights."""
    log.info(
        "Azure Monitor Container Insights is enabled via Terraform (oms_agent block in AKS module). "
        "No additional configuration required here."
    )
    log.info(
        "To view metrics: Azure Portal -> AKS -> Monitoring -> Insights"
    )


def print_access_info() -> None:
    """Print how to access Prometheus and Grafana."""
    print("\n" + "="*60)
    print("  Monitoring Stack Ready")
    print("="*60)
    print("\nPrometheus:")
    print("  kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090")
    print("  http://localhost:9090\n")
    print("Grafana:")
    print("  kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80")
    print("  http://localhost:3000")
    print("  Username: admin")
    print("  Password: (set in values or retrieve from secret)")
    print("\nAlertmanager:")
    print("  kubectl port-forward -n monitoring svc/kube-prometheus-stack-alertmanager 9093:9093")
    print("  http://localhost:9093\n")
    print("="*60 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install Prometheus/Grafana monitoring stack on AKS"
    )
    parser.add_argument(
        "--environment",
        default="dev",
        choices=["dev", "staging", "prod"],
        help="Target environment"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Skip Helm install (apply rules/dashboards only)"
    )
    args = parser.parse_args()

    log.info("Setting up monitoring stack for environment: %s", args.environment)

    # Add Helm repos
    helm_repo_add("prometheus-community", PROMETHEUS_HELM_REPO)
    helm_repo_add("grafana", GRAFANA_HELM_REPO)

    # Create monitoring namespace
    create_namespace(MONITORING_NAMESPACE)

    # Install kube-prometheus-stack
    if not args.skip_install:
        install_prometheus_stack(args.environment, PROMETHEUS_VALUES)

    # Apply custom rules
    apply_prometheus_rules()

    # Import Grafana dashboard
    import_grafana_dashboard()

    # Azure Monitor info
    configure_azure_monitor_integration()

    # Print access details
    print_access_info()

    log.info("Monitoring setup complete!")


if __name__ == "__main__":
    main()
