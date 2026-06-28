# Troubleshooting Guide

## Pipeline Failures

### Secret validation fails

- Go to **Settings → Secrets and variables → Actions** and verify all 13 secrets are set.
- Common typos: `AZURE_RESOURCE_GROUP` vs `AZURE_RESOURCE_GROUPS`, trailing spaces.

### Terraform Apply — resource already exists

This means your Terraform remote state is empty but Azure resources already exist.
Run the import script: `scripts/import-terraform-state.ps1` — see [README.md](../README.md#step-4-import-existing-azure-resources-into-remote-state).

### Terraform Apply — state empty after storage backend change

You changed `TF_STATE_STORAGE_ACCOUNT`. Run `terraform init -reconfigure` locally with the new backend values.

### Docker push to ACR fails

```bash
az acr login --name fahimaksdevopsacr
# Then verify the service principal has AcrPush role:
az role assignment list --assignee <clientId> --scope /subscriptions/<subId>/resourceGroups/azure-aks-devops-rg/providers/Microsoft.ContainerRegistry/registries/fahimaksdevopsacr
```

### Pods stuck in `ImagePullBackOff`

```bash
kubectl describe pod <pod-name> -n fastapi
# Check if AKS has AcrPull role on ACR:
az role assignment list --assignee <AKS kubelet managed identity> --scope <ACR resource ID>
```

### Smoke test times out (LoadBalancer IP never appears)

Azure LoadBalancer provisioning can take 3–10 minutes on first deploy.

```bash
kubectl get svc fastapi-service -n fastapi -w
```

### Grafana cannot be accessed

```bash
kubectl get pods -n monitoring
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
```

Login: `admin` / value of `GRAFANA_ADMIN_PASSWORD` GitHub Secret.

## Local Development

### Docker Compose won't start

```bash
docker compose down -v  # remove old volumes
docker compose up --build
```

### Tests fail with database connection error

Ensure Postgres service is healthy before pytest runs:

```bash
docker compose ps  # check postgres is healthy
```

### Celery worker not processing tasks

Verify Redis is running and `CELERY_BROKER_URL=redis://localhost:6379/0` is set.
