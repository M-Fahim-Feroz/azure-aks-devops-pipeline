# GitHub Issues Backlog

Prepared issues for the azure-aks-devops-pipeline repository.
Create these on GitHub when ready: https://github.com/M-Fahim-Feroz/azure-aks-devops-pipeline/issues/new

---

## Issue 1

**Title:** [CI] Make smoke test fail correctly on unhealthy endpoint
**Labels:** `ci`, `bug`
**Priority:** High

**Description:**
The smoke test currently uses `curl -f ... || echo "Health check failed"` which allows the pipeline to pass even when the endpoint is unhealthy. The smoke test must exit with a non-zero code when the endpoint is unreachable.

**Acceptance Criteria:**
- [ ] `curl` fails the pipeline step on non-2xx response
- [ ] Empty `EXTERNAL_IP` causes immediate exit with error message
- [ ] `set -euo pipefail` is used in smoke test step
- [ ] Debug logs only appear on failure (`if: failure()`)

---

## Issue 2

**Title:** [CI] Add pytest and Bandit to build-and-test job
**Labels:** `ci`, `testing`
**Priority:** High

**Description:**
The build-and-test job installs pytest but does not run it. Bandit is also not executed. Both should run as quality gates before deployment.

**Acceptance Criteria:**
- [ ] `bandit -r api/ -lll` runs and fails on HIGH issues
- [ ] `pytest api/tests/` runs and test results are visible in logs
- [ ] Job fails if any test fails

---

## Issue 3

**Title:** [Security] Use dedicated Grafana admin password secret
**Labels:** `security`
**Priority:** High

**Description:**
The Ansible playbook currently receives `grafana_password` from `POSTGRES_PASSWORD`. This is poor credential separation. A dedicated `GRAFANA_ADMIN_PASSWORD` secret should be used.

**Acceptance Criteria:**
- [ ] New secret `GRAFANA_ADMIN_PASSWORD` is documented in README
- [ ] Workflow passes `GRAFANA_ADMIN_PASSWORD` to Ansible
- [ ] `POSTGRES_PASSWORD` is no longer used for Grafana
- [ ] Secret preflight includes `GRAFANA_ADMIN_PASSWORD`

---

## Issue 4

**Title:** [Terraform] Move state to Azure remote backend
**Labels:** `infrastructure`, `terraform`
**Priority:** Medium

**Description:**
Terraform state currently exists only on the GitHub Actions runner and is lost after each run. A remote Azure Storage backend with state locking should be used for production-style usage.

**Acceptance Criteria:**
- [ ] Azure Storage backend configured in `infra/main.tf`
- [ ] Backend bootstrap documented in `docs/terraform-state.md`
- [ ] State locking via Azure Blob lease works
- [ ] `.gitignore` confirmed to exclude `*.tfstate`

---

## Issue 5

**Title:** [Security] Migrate Azure auth to GitHub OIDC
**Labels:** `security`, `infrastructure`
**Priority:** Medium

**Description:**
Currently using `AZURE_CREDENTIALS` JSON (long-lived Service Principal secret). GitHub OIDC federated credentials eliminate the need for stored secrets and rotate automatically.

**Acceptance Criteria:**
- [ ] Azure federated credential created for the GitHub repo
- [ ] Workflow uses `azure/login@v2` with OIDC (no `creds` parameter)
- [ ] `AZURE_CREDENTIALS` secret is no longer needed
- [ ] `permissions: id-token: write` added to workflow

---

## Issue 6

**Title:** [Docs] Add cost estimate and limitations
**Labels:** `documentation`
**Priority:** Low

**Description:**
The README and deployment guide should include an estimated cost for a full pipeline run and clear demo limitations.

**Acceptance Criteria:**
- [ ] Estimated Azure cost per run documented
- [ ] Demo limitations clearly noted (single node, no HA)
- [ ] Cleanup command prominently placed

---

## Issue 7

**Title:** [Release] Create v1.0.0 portfolio release
**Labels:** `release`
**Priority:** Low

**Description:**
Tag the repository at its current stable state as v1.0.0 to mark the portfolio milestone.

**Acceptance Criteria:**
- [ ] Git tag `v1.0.0` created
- [ ] GitHub Release created with deployment proof screenshots
- [ ] Release notes summarize the full pipeline capabilities
