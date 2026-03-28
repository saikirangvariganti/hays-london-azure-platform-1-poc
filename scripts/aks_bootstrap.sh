#!/usr/bin/env bash
# =============================================================================
# aks_bootstrap.sh — AKS cluster setup for mobile platform (Public Sector)
# =============================================================================
# Usage: bash scripts/aks_bootstrap.sh [environment]
# Environment: dev | staging | prod (default: dev)
# =============================================================================
set -euo pipefail

ENVIRONMENT="${1:-dev}"
RESOURCE_GROUP="rg-mobile-platform-${ENVIRONMENT}"
CLUSTER_NAME="aks-mobile-platform-${ENVIRONMENT}"
NAMESPACE="mobile-platform"
KEY_VAULT_NAME="kv-mobile-plat-${ENVIRONMENT}"
ACR_NAME="acrmobileplatform${ENVIRONMENT}"

# Colours
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ---------------------------------------------------------------------------
# 1. Prerequisites check
# ---------------------------------------------------------------------------
log_info "Checking prerequisites..."

command -v az      >/dev/null 2>&1 || log_error "Azure CLI not installed"
command -v kubectl >/dev/null 2>&1 || log_error "kubectl not installed"
command -v helm    >/dev/null 2>&1 || log_error "helm not installed"

# Verify logged in
az account show >/dev/null 2>&1 || log_error "Not logged in to Azure. Run: az login"
log_info "Prerequisites OK"

# ---------------------------------------------------------------------------
# 2. Get AKS credentials
# ---------------------------------------------------------------------------
log_info "Getting AKS credentials for ${CLUSTER_NAME}..."
az aks get-credentials \
  --resource-group "${RESOURCE_GROUP}" \
  --name "${CLUSTER_NAME}" \
  --overwrite-existing

kubectl config use-context "${CLUSTER_NAME}"
log_info "Connected to AKS cluster: ${CLUSTER_NAME}"

# ---------------------------------------------------------------------------
# 3. Verify cluster health
# ---------------------------------------------------------------------------
log_info "Checking cluster nodes..."
kubectl get nodes -o wide
READY_NODES=$(kubectl get nodes --no-headers | grep -c " Ready " || true)
log_info "Ready nodes: ${READY_NODES}"

# ---------------------------------------------------------------------------
# 4. Create namespace
# ---------------------------------------------------------------------------
log_info "Creating namespace: ${NAMESPACE}"
kubectl apply -f k8s/namespace.yaml
kubectl get namespace "${NAMESPACE}"

# ---------------------------------------------------------------------------
# 5. Install NGINX Ingress Controller
# ---------------------------------------------------------------------------
log_info "Installing NGINX Ingress Controller..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-internal"="true" \
  --set controller.metrics.enabled=true \
  --set controller.metrics.serviceMonitor.enabled=true \
  --wait --timeout 5m

log_info "NGINX Ingress Controller installed"

# ---------------------------------------------------------------------------
# 6. Install cert-manager
# ---------------------------------------------------------------------------
log_info "Installing cert-manager..."
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true \
  --wait --timeout 5m

log_info "cert-manager installed"

# ---------------------------------------------------------------------------
# 7. Install Secrets Store CSI Driver + Azure provider
# ---------------------------------------------------------------------------
log_info "Installing Secrets Store CSI Driver..."
helm repo add csi-secrets-store-provider-azure \
  https://azure.github.io/secrets-store-csi-driver-provider-azure/charts
helm repo update

helm upgrade --install csi-secrets-store \
  csi-secrets-store-provider-azure/csi-secrets-store-provider-azure \
  --namespace kube-system \
  --set secrets-store-csi-driver.syncSecret.enabled=true \
  --set secrets-store-csi-driver.enableSecretRotation=true \
  --wait --timeout 5m

log_info "Secrets Store CSI Driver installed"

# ---------------------------------------------------------------------------
# 8. Configure Key Vault SecretProviderClass
# ---------------------------------------------------------------------------
log_info "Configuring Azure Key Vault SecretProviderClass..."

TENANT_ID=$(az account show --query tenantId -o tsv)

cat <<EOF | kubectl apply -f -
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-keyvault-mobile-backend
  namespace: ${NAMESPACE}
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "false"
    clientID: "REPLACE_WITH_WORKLOAD_IDENTITY_CLIENT_ID"
    keyvaultName: ${KEY_VAULT_NAME}
    objects: |
      array:
        - |
          objectName: db-connection-string
          objectType: secret
          objectVersion: ""
        - |
          objectName: jwt-secret
          objectType: secret
          objectVersion: ""
        - |
          objectName: apns-certificate
          objectType: secret
          objectVersion: ""
        - |
          objectName: fcm-server-key
          objectType: secret
          objectVersion: ""
    tenantId: ${TENANT_ID}
  secretObjects:
  - secretName: mobile-backend-secrets
    type: Opaque
    data:
    - objectName: db-connection-string
      key: db-connection-string
    - objectName: jwt-secret
      key: jwt-secret
EOF

log_info "SecretProviderClass configured"

# ---------------------------------------------------------------------------
# 9. ACR login
# ---------------------------------------------------------------------------
log_info "Logging in to ACR: ${ACR_NAME}..."
az acr login --name "${ACR_NAME}"
log_info "ACR login successful"

# ---------------------------------------------------------------------------
# 10. Deploy mobile backend
# ---------------------------------------------------------------------------
log_info "Deploying mobile backend workloads..."
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# Wait for deployments to be ready
kubectl rollout status deployment/mobile-backend-ios     -n "${NAMESPACE}" --timeout=5m
kubectl rollout status deployment/mobile-backend-android -n "${NAMESPACE}" --timeout=5m

log_info "Mobile backend deployed successfully"

# ---------------------------------------------------------------------------
# 11. Summary
# ---------------------------------------------------------------------------
echo ""
echo "================================================="
echo "  AKS Bootstrap Complete"
echo "================================================="
echo "  Cluster:    ${CLUSTER_NAME}"
echo "  Namespace:  ${NAMESPACE}"
echo "  Environment:${ENVIRONMENT}"
echo "================================================="
kubectl get pods -n "${NAMESPACE}"
echo "================================================="
