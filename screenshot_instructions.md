# Validation Screenshots

## 📸 Screenshot Checklist

### Step 2: Terraform Infrastructure
- [ ] **Azure Portal** showing created resources (Resource Group, AKS, ACR, Storage)
- [ ] **`terraform output`** command results
- [ ] **`terraform destroy`** proof (cleanup confirmation)

### Step 4: Ansible
- [ ] **Successful playbook run**: `ansible-playbook -i ansible/inventory.ini ansible/playbook.yaml`

### Step 5: Kubernetes
- [ ] **`kubectl get pods -n fastapi`** - Show running pods
- [ ] **`kubectl get svc -n fastapi`** - Show services with External IPs
- [ ] **`kubectl describe pod <pod-name> -n fastapi`** - Pod details
- [ ] **`kubectl get pods -n monitoring`** - Prometheus/Grafana pods

### Step 6: CI/CD Pipeline
- [ ] **GitHub Actions** pipeline showing all stages passed (green checkmarks)
- [ ] Pipeline details showing: Build & Test → Docker → Terraform → Deploy → Smoke Test

### Step 7: Monitoring
- [ ] **Grafana Dashboard** - CPU metrics
- [ ] **Grafana Dashboard** - Memory metrics  
- [ ] **Grafana Dashboard** - Request count/latency (if applicable)
- [ ] **Prometheus Targets** - Showing scrape targets active

---

## 🔧 Commands to Run for Screenshots

```bash
# Kubernetes screenshots
kubectl get pods -n fastapi
kubectl get svc -n fastapi
kubectl describe pod fastapi-api-<hash> -n fastapi
kubectl get pods -n monitoring

# Terraform screenshots  
cd infra
terraform output
terraform destroy -auto-approve  # AFTER all other screenshots!

# Ansible screenshot
ansible-playbook -i ansible/inventory.ini ansible/playbook.yaml
```

## 📁 Save Screenshots To
Save all screenshots in the `img/` folder with descriptive names:
- `img/azure-portal-resources.png`
- `img/terraform-output.png`
- `img/terraform-destroy.png`
- `img/kubectl-get-pods.png`
- `img/kubectl-get-svc.png`
- `img/kubectl-describe-pod.png`
- `img/ansible-playbook-run.png`
- `img/github-actions-pipeline.png`
- `img/grafana-dashboard-cpu.png`
- `img/grafana-dashboard-memory.png`
- `img/prometheus-targets.png`
