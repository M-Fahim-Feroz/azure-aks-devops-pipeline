# Deployment Screenshot Reference

> **Status:** All screenshots have been captured and are stored in `docs/screenshots/`.
> See the [screenshot index](docs/screenshots/README.md) for a full categorized listing.

---

## Screenshots Captured

All deployment proof is now in `docs/screenshots/` using professional naming conventions.

### CI/CD Pipeline
- `01-github-actions-overall-success.png` — All 5 jobs passing
- `02-github-actions-build-test-success.png` — Build and test job detail
- `03-github-actions-terraform-provision-success.png` — Terraform provision job
- `04-github-actions-docker-build-push-success.png` — Docker build and push job
- `05-github-actions-deploy-app-success.png` — Deploy app job
- `06-github-actions-ansible-playbook-success.png` — Ansible PLAY RECAP
- `07-github-actions-smoke-test-success.png` — Smoke test with endpoint response

### Azure Infrastructure
- `08-azure-resource-group-overview.png` — Resource group with all resources
- `09-azure-aks-cluster-overview.png` — AKS cluster overview
- `10-azure-aks-node-ready.png` — Node status Ready
- `11-azure-aks-monitor-dashboard.png` — Azure Monitor dashboard

### ACR
- `12-azure-acr-repositories.png` — ACR api and worker repositories
- `13-azure-acr-api-tags.png` — api repository tags
- `14-azure-acr-worker-tags.png` — worker repository tags

### Kubernetes Workloads
- `15-kubectl-all-fastapi.png` — kubectl get all output
- `16-kubectl-services-loadbalancer.png` — Services with LoadBalancer IP
- `17-fastapi-public-endpoint.png` — FastAPI endpoint response in browser

### Monitoring
- `19-monitoring-stack-helm-running.png` — Helm list showing monitoring deployed
- `20-grafana-cluster-dashboard.png` — Grafana cluster compute resources
- `21-grafana-fastapi-namespace-pods.png` — Grafana fastapi namespace pods
- `22-grafana-node-pods-dashboard.png` — Grafana node pods
- `23-grafana-node-exporter-dashboard.png` — Node exporter dashboard
- `24-grafana-kubelet-dashboard.png` — Kubelet dashboard
- `25-prometheus-targets-up.png` — Prometheus targets all UP
- `26-prometheus-query-up.png` — Prometheus `up` query graph

---

## Excluded Screenshots

Screenshots that showed database error logs, duplicate table constraint errors, or other non-clean terminal output were moved to `docs/screenshots/_excluded/` and are not referenced in documentation.
