# Runbook — Azure AKS DevOps Pipeline

## Routine Operations

### Trigger a Full Deployment

```bash
git push origin main
# Or use: GitHub → Actions → Deploy to AKS → Run workflow
```

### Check Deployment Status

```bash
az aks get-credentials --resource-group azure-aks-devops-rg --name azure-aks-devops-cluster
kubectl get pods -n fastapi
kubectl get pods -n monitoring
```

### Restart a Deployment

```bash
kubectl rollout restart deployment/fastapi-api -n fastapi
kubectl rollout status deployment/fastapi-api -n fastapi
```

### View Application Logs

```bash
kubectl logs -f deployment/fastapi-api -n fastapi
kubectl logs -f deployment/fastapi-worker -n fastapi
```

### Access Grafana Dashboard

```bash
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
# Open: http://localhost:3000
# Login: admin / <GRAFANA_ADMIN_PASSWORD from GitHub Secrets>
```

### Scale the API Deployment

```bash
kubectl scale deployment fastapi-api -n fastapi --replicas=3
```

## Disaster Recovery

### Recreate AKS Cluster from Scratch

1. Ensure remote Terraform state is intact in `terraform-state-rg`.
2. Trigger `workflow_dispatch` on `aks-cicd.yml`.
3. Terraform will re-provision all resources idempotently.

### Terraform State Corruption

1. Do **not** delete the state blob — download it first:

   ```bash
   az storage blob download --container-name tfstate --name azure-aks-devops-pipeline.tfstate --account-name <TF_STATE_STORAGE_ACCOUNT> --file backup.tfstate
   ```

2. Fix the state using `terraform state rm` for the offending resource.
3. Re-import if needed using scripts in `scripts/`.

## Cleanup / Destroy

> [!CAUTION]
> This permanently deletes all Azure resources.

```bash
az group delete --name azure-aks-devops-rg --yes --no-wait
az group delete --name terraform-state-rg --yes --no-wait  # Optional: removes Terraform state too
```
