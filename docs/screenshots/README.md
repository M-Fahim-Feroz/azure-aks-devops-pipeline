# Deployment Screenshots

This folder contains deployment proof for the Azure AKS DevOps pipeline, including CI/CD execution, Terraform provisioning, ACR image publishing, AKS workloads, application endpoint validation, and Prometheus/Grafana observability.

> Screenshots containing secrets, passwords, failed connection output, or sensitive credentials are intentionally excluded from this folder and moved to `_excluded/`.

> **Note:** Some screenshots may show temporary public IPs or AKS hostnames from a short-lived demo deployment. Azure resources were intended to be deleted after proof capture to avoid ongoing cost.

---

## CI/CD Pipeline

| Screenshot | Description |
|---|---|
| [01-github-actions-overall-success.png](01-github-actions-overall-success.png) | GitHub Actions workflow run with all 5 jobs passing: build-and-test, provision-infra, docker-build, deploy-app, smoke-test. |
| [02-github-actions-build-test-success.png](02-github-actions-build-test-success.png) | build-and-test job detail showing secret validation, Python setup, dependency install, and linting steps all succeeded. |
| [03-github-actions-terraform-provision-success.png](03-github-actions-terraform-provision-success.png) | provision-infra job showing Terraform Init, Terraform Apply (5m 19s), and output retrieval steps succeeded. |
| [04-github-actions-docker-build-push-success.png](04-github-actions-docker-build-push-success.png) | docker-build job showing ACR login, Build & Push API, and Build & Push Worker steps all succeeded. |
| [05-github-actions-deploy-app-success.png](05-github-actions-deploy-app-success.png) | deploy-app job showing AKS context setup, Ansible playbook run, and force restart steps succeeded. |
| [06-github-actions-ansible-playbook-success.png](06-github-actions-ansible-playbook-success.png) | Ansible playbook output showing manifest deployment, Helm repo setup, Prometheus/Grafana install, and PLAY RECAP with ok=8, changed=4, failed=0. |
| [07-github-actions-smoke-test-success.png](07-github-actions-smoke-test-success.png) | Smoke test job with Verify Endpoints step expanded, showing LoadBalancer service status and `"Alperen":"Cubuk"` endpoint response confirming successful deployment. |

---

## Azure Infrastructure

| Screenshot | Description |
|---|---|
| [08-azure-resource-group-overview.png](08-azure-resource-group-overview.png) | Azure Portal resource group `azure-aks-devops-rg` showing all provisioned resources: AKS cluster, ACR, virtual network, and storage account. |
| [09-azure-aks-cluster-overview.png](09-azure-aks-cluster-overview.png) | Azure AKS cluster `azure-aks-devops-cluster` overview with Kubernetes v1.34.8, Southeast Asia region, and cluster operation status Succeeded. |
| [10-azure-aks-node-ready.png](10-azure-aks-node-ready.png) | AKS node overview showing status Ready with conditions: Ready, Disk pressure False, Memory pressure False. |
| [11-azure-aks-monitor-dashboard.png](11-azure-aks-monitor-dashboard.png) | Azure Monitor dashboard for the AKS cluster showing 1 node Ready, 26 pods Running, and CPU/memory utilization graphs. |

---

## Azure Container Registry

| Screenshot | Description |
|---|---|
| [12-azure-acr-repositories.png](12-azure-acr-repositories.png) | ACR `fahimaksdevopsacr` Repositories blade showing `api` and `worker` image repositories published by the pipeline. |
| [13-azure-acr-api-tags.png](13-azure-acr-api-tags.png) | ACR `api` repository showing `latest` and commit-SHA tags with digest, confirming successful image push. |
| [14-azure-acr-worker-tags.png](14-azure-acr-worker-tags.png) | ACR `worker` repository showing `latest` and commit-SHA tags with digest, confirming successful worker image push. |

---

## Kubernetes Workloads

| Screenshot | Description |
|---|---|
| [15-kubectl-all-fastapi.png](15-kubectl-all-fastapi.png) | `kubectl get all -n fastapi` output showing all pods Running: fastapi-api (2 replicas), fastapi-worker, postgres StatefulSet, and redis — plus services and replicasets. |
| [16-kubectl-services-loadbalancer.png](16-kubectl-services-loadbalancer.png) | `kubectl get svc -n fastapi` showing fastapi-service as LoadBalancer with public external IP 40.119.215.246 on port 80. |
| [17-fastapi-public-endpoint.png](17-fastapi-public-endpoint.png) | Browser showing the FastAPI public endpoint at the LoadBalancer IP returning `{"Alperen":"Cubuk"}`, confirming successful end-to-end deployment. |

---

## Monitoring and Observability

| Screenshot | Description |
|---|---|
| [19-monitoring-stack-helm-running.png](19-monitoring-stack-helm-running.png) | Terminal output of `helm list -A` showing the `monitoring` release (kube-prometheus-stack-87.2.1) deployed in the monitoring namespace. |
| [20-grafana-cluster-dashboard.png](20-grafana-cluster-dashboard.png) | Grafana Kubernetes / Compute Resources / Cluster dashboard showing CPU (10.5%), memory (32.2%), and per-namespace breakdown including fastapi, kube-system, and monitoring. |
| [21-grafana-fastapi-namespace-pods.png](21-grafana-fastapi-namespace-pods.png) | Grafana Kubernetes / Compute Resources / Namespace (Pods) dashboard filtered to the `fastapi` namespace showing CPU and memory usage for all running pods. |
| [22-grafana-node-pods-dashboard.png](22-grafana-node-pods-dashboard.png) | Grafana Kubernetes / Compute Resources / Node (Pods) dashboard showing per-pod CPU usage and quota table for the AKS node. |
| [23-grafana-node-exporter-dashboard.png](23-grafana-node-exporter-dashboard.png) | Grafana Node Exporter / Nodes dashboard showing node-level CPU, load average, memory usage (33.6%), and disk space metrics. |
| [24-grafana-kubelet-dashboard.png](24-grafana-kubelet-dashboard.png) | Grafana Kubernetes / Kubelet dashboard showing 1 running kubelet, 25 running pods, 36 containers, and kubelet operation rates. |
| [25-prometheus-targets-up.png](25-prometheus-targets-up.png) | Prometheus Status / Target health page showing all scrape targets (Grafana, Alertmanager, Prometheus, API server) reporting state UP. |
| [26-prometheus-query-up.png](26-prometheus-query-up.png) | Prometheus query interface with `up` metric showing value 1 (UP) for all monitored services over the last 1 hour. |
