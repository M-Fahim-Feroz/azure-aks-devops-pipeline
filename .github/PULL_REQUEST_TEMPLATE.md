## Description

Briefly describe what this PR changes and why.

## Type of Change

- [ ] Bug fix
- [ ] New feature / improvement
- [ ] Documentation update
- [ ] CI/CD pipeline change
- [ ] Infrastructure change (Terraform / Ansible / K8s)
- [ ] Security improvement

## Testing

- [ ] I ran `flake8 api/` and it passes
- [ ] I ran `bandit -r api/ -lll` and it passes
- [ ] I ran `pytest api/tests/` and it passes
- [ ] I verified no secrets are committed
- [ ] I verified `.gitignore` covers new sensitive files if added

## Infrastructure Changes (if applicable)

- [ ] `terraform plan` output reviewed
- [ ] No `*.tfstate` or `*.tfvars` files are committed
- [ ] K8s manifests validated with `kubectl apply --dry-run=client`

## Checklist

- [ ] PR title is clear and descriptive
- [ ] Changes are documented in README or docs/ if needed
- [ ] No hardcoded credentials or secrets
