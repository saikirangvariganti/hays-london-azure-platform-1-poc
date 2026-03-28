# Hays London — Azure Platform Engineer POC
## AKS Platform for Mobile App Workloads (Public Sector, SC Clearance)

[![CI/CD Pipeline](https://github.com/saikirangvariganti/hays-london-azure-platform-1-poc/actions/workflows/aks_deploy.yml/badge.svg)](https://github.com/saikirangvariganti/hays-london-azure-platform-1-poc/actions/workflows/aks_deploy.yml)

> **Author:** Sai Kiran Goud Variganti
> **Role Target:** Azure Platform Engineer — Hays Specialist Recruitment (London)
> **Focus:** AKS for mobile application workloads, Terraform IaC, Azure security, public sector compliance

---

## Overview

This POC demonstrates end-to-end Azure platform engineering for a public sector mobile application backend. It covers:

- **AKS cluster provisioning** with system and user node pools, autoscaling, and RBAC
- **Terraform IaC** for full infrastructure lifecycle management
- **Mobile app backend deployment** on Kubernetes (iOS/Android API services)
- **Azure security controls**: Key Vault, RBAC, Azure Policy, Defender for Cloud
- **CI/CD pipelines** via GitHub Actions with staging/production gates
- **Observability**: Prometheus metrics, Grafana dashboards, Azure Monitor integration
- **Network hardening**: VNet, NSGs, private endpoints, App Gateway ingress

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Public Sector Tenant                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Resource Group                        │  │
│  │                                                          │  │
│  │  ┌─────────────┐    ┌──────────────┐   ┌─────────────┐  │  │
│  │  │    VNet     │    │  AKS Cluster │   │  Key Vault  │  │  │
│  │  │  10.0.0.0/8 │───▶│  (3 nodes)  │──▶│ (secrets)   │  │  │
│  │  │             │    │  +autoscale  │   │             │  │  │
│  │  └─────────────┘    └──────┬───────┘   └─────────────┘  │  │
│  │                           │                              │  │
│  │  ┌────────────────────────▼──────────────────────────┐  │  │
│  │  │              Kubernetes Workloads                 │  │  │
│  │  │  ┌──────────────┐   ┌──────────────┐             │  │  │
│  │  │  │  iOS Backend │   │Android Backend│            │  │  │
│  │  │  │  (3 replicas)│   │ (3 replicas) │            │  │  │
│  │  │  └──────────────┘   └──────────────┘             │  │  │
│  │  │       HPA (2–10 replicas per service)             │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ┌─────────────┐    ┌──────────────┐   ┌─────────────┐  │  │
│  │  │     ACR     │    │Azure Monitor │   │  Defender   │  │  │
│  │  │  (registry) │    │+Prometheus   │   │  for Cloud  │  │  │
│  │  └─────────────┘    └──────────────┘   └─────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
hays-london-azure-platform-1-poc/
├── README.md
├── requirements.txt
├── terraform/
│   ├── main.tf                    # Root: AKS + VNet + Key Vault + ACR
│   ├── variables.tf               # Input variables with defaults
│   ├── outputs.tf                 # Exported values (cluster name, endpoint, etc.)
│   └── modules/
│       ├── aks/main.tf            # AKS cluster, node pools, autoscaling, RBAC
│       ├── networking/main.tf     # VNet, subnets, NSGs, private endpoints
│       └── security/main.tf      # Key Vault, Azure Policy, Defender for Cloud
├── k8s/
│   ├── namespace.yaml             # Isolated namespace for mobile workloads
│   ├── deployment.yaml            # Mobile app backend (iOS/Android) deployment
│   ├── service.yaml               # ClusterIP + LoadBalancer services
│   ├── hpa.yaml                   # Horizontal Pod Autoscaler (CPU/memory)
│   └── ingress.yaml               # NGINX ingress with TLS + routing rules
├── helm/
│   └── mobile-backend/
│       ├── Chart.yaml             # Helm chart metadata
│       ├── values.yaml            # Configurable values (image, replicas, resources)
│       └── templates/deployment.yaml  # Helm deployment template
├── scripts/
│   ├── aks_bootstrap.sh           # AKS cluster bootstrap (kubeconfig, namespaces, secrets)
│   └── monitoring_setup.py        # Prometheus + Grafana installation via Helm
├── monitoring/
│   ├── prometheus_rules.yaml      # Alert rules: latency, error rate, pod restarts
│   └── grafana_dashboard.json     # Pre-built mobile backend Grafana dashboard
├── .github/
│   └── workflows/
│       └── aks_deploy.yml         # GitHub Actions: build → push → deploy pipeline
└── tests/
    └── test_poc.py                # 90+ validation tests
```

---

## Quick Start

### Prerequisites

```bash
# Azure CLI
az login
az account set --subscription "<SUBSCRIPTION_ID>"

# Terraform
terraform version  # >= 1.5.0

# kubectl + helm
kubectl version --client
helm version
```

### 1. Provision Infrastructure

```bash
cd terraform/
terraform init
terraform plan -var="environment=dev" -var="location=uksouth"
terraform apply -auto-approve
```

### 2. Connect to AKS

```bash
bash scripts/aks_bootstrap.sh
kubectl get nodes
```

### 3. Deploy Mobile Backend

```bash
# Direct kubectl
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# OR via Helm
helm upgrade --install mobile-backend helm/mobile-backend/ \
  --namespace mobile-platform \
  --set image.tag=latest
```

### 4. Set Up Monitoring

```bash
python scripts/monitoring_setup.py
kubectl apply -f monitoring/prometheus_rules.yaml
# Import monitoring/grafana_dashboard.json into Grafana UI
```

---

## Security Controls

| Control | Implementation |
|---------|---------------|
| Secrets management | Azure Key Vault + CSI driver |
| Network isolation | Private VNet, NSGs, private endpoints |
| Container registry | ACR with private endpoint, admin disabled |
| RBAC | Azure RBAC + Kubernetes RBAC |
| Policy enforcement | Azure Policy (no privileged containers, required tags) |
| Threat detection | Defender for Cloud (CSPM + CWP) |
| TLS termination | NGINX ingress with cert-manager |

---

## CI/CD Pipeline

The GitHub Actions workflow (`aks_deploy.yml`) implements:

1. **Build**: Docker image build + vulnerability scan
2. **Push**: ACR image push with semantic versioning
3. **Staging deploy**: Deploy to `staging` namespace + smoke tests
4. **Production gate**: Manual approval required
5. **Production deploy**: Rolling update to `mobile-platform` namespace
6. **Notify**: Teams/Slack notification on completion

---

## Monitoring & Observability

- **Prometheus** scrapes metrics from all pods (port 8080/metrics)
- **Alert rules**: P95 latency > 500ms, error rate > 5%, pod restart loops
- **Grafana dashboard**: Mobile backend golden signals (latency, throughput, errors, saturation)
- **Azure Monitor**: Container Insights integration for node-level metrics

---

## Public Sector Compliance

- SC Clearance environment alignment (UK Government classifications)
- Azure Policy enforces: required tags, no public IPs on AKS nodes, encryption at rest
- All secrets in Key Vault — no plaintext credentials in code or environment variables
- Private endpoints for ACR and Key Vault (no public internet access)
- Audit logging enabled on Key Vault + AKS API server

---

## Technologies Demonstrated

`AKS` `Terraform` `GitHub Actions` `Azure DevOps` `Key Vault` `Azure Policy` `RBAC` `Defender for Cloud` `Prometheus` `Grafana` `Azure Monitor` `Docker` `Helm` `NGINX Ingress` `VNet` `NSG` `Private Endpoints` `ACR` `HPA` `cert-manager`
