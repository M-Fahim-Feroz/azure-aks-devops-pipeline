# DevOps Report

> **Deployment Status:**  End-to-end deployment successfully completed through GitHub Actions.
> All 5 pipeline jobs passed. FastAPI public endpoint responded with `{"status":"ok"}`.
> Prometheus/Grafana monitoring stack confirmed operational. Deployment proof in `docs/screenshots/`.

## Technologies Used
- **FastAPI**: For building the REST API, chosen for its speed and auto-docs.
- **Celery**: Handles background tasks like fetching data, using Redis as broker.
- **Redis**: Acts as message broker for Celery and potential caching.
- **PostgreSQL**: Relational database for persistent storage.
- **Docker**: Containerizes the app for consistent environments across dev, test, prod.
- **Docker Compose**: Manages multi-container setups locally.
- **GitHub Actions**: For CI/CD, automating builds, tests, and deployments.
- **Pytest**: Testing framework with async support for API and Celery tasks.
- **Flake8 and Bandit**: For linting and security scans.

## Pipeline Design
The CI/CD pipeline is defined in `.github/workflows/aks-cicd.yml` and runs on GitHub Actions for Azure AKS deployment.

**6-Stage Pipeline:**
1. **Build & Test**: Installs Python dependencies, runs Flake8 (linting), Bandit (security scan), and Pytest (unit tests).
2. **Docker Build & Push**: Builds multistage Docker image and pushes to Azure Container Registry (ACR).
3. **Terraform Apply**: Provisions Azure infrastructure (AKS, VNet, ACR, Storage).
4. **Ansible Deploy**: Applies Kubernetes manifests and installs Prometheus/Grafana via Helm.
5. **Force Restart**: Ensures latest image is pulled by restarting deployments.
6. **Smoke Test**: Verifies the application is accessible via the LoadBalancer endpoint.

Diagram:
```
Push/PR -> Build & Test -> Docker Build -> Terraform Apply -> Ansible Deploy -> Smoke Test
                |                              |
           (Flake8, Bandit, Pytest)      (AKS, VNet, ACR)
```

This ensures quality gates: no deployment without passing tests.

## Secret Management Strategy
**Policy**: No sensitive data is ever committed to the repository.

1.  **Local Development**:
    - Secrets are stored in a `.env` file (which is in `.gitignore`).
    - `docker-compose.yml` loads these variables dynamically.

2.  **Production (Kubernetes on Azure AKS)**:
    - Secrets are managed via **GitHub Repository Secrets**.
    - During the CI/CD pipeline, these secrets are securely passed to **Ansible**, which templates them into the Kubernetes manifests.
    - The Ansible templates in `ansible/templates/` contain *placeholders only*.

3.  **Required GitHub Secrets**:
    | Secret Name | Purpose |
    |-------------|---------|
    | `AZURE_CREDENTIALS` | Azure Service Principal JSON for authentication (includes ARM variables) |
    | `ACR_LOGIN_SERVER` | Azure Container Registry URL |
    | `ACR_NAME` | Azure Container Registry name |
    | `AKS_CLUSTER_NAME` | Azure Kubernetes Service cluster name |
    | `AZURE_RESOURCE_GROUP` | Azure resource group name |
    | `POSTGRES_DB` | PostgreSQL database name |
    | `POSTGRES_USER` | PostgreSQL username |
    | `POSTGRES_PASSWORD` | PostgreSQL password |
    | `WEATHER_API_KEY` | Weather API integration key |
    | `AZURE_STORAGE_ACCOUNT_NAME` | Azure Storage Account name for persistent storage |
    | `TF_STATE_RG` | Terraform State Azure resource group name |
    | `TF_STATE_STORAGE_ACCOUNT` | Terraform State Azure storage account name |

## Testing Process
- **Unit Tests**: Test individual functions in api/.
- **CI Execution**: Tests run with real Postgres and Redis containers, Celery worker started via nohup.
- **Coverage**: Focus on async flows, error handling.
- **Failure Handling**: Logs Celery output on test failure for debugging.
- Local testing: Run `pytest` after starting services with docker-compose.

## Lessons Learned
- Setting up services in CI was challenging but crucial for realistic tests.
- Secrets management prevents leaks but requires careful setup.
- Containerization simplifies deployment but adds complexity in local dev.
- Automation in CI/CD saves time but needs regular updates to avoid pipeline failures from outdated tools or dependencies.
- Version pinning in Dockerfiles and requirements.txt prevents unexpected breaks from library updates.
- Branch protection rules on GitHub enforce code reviews, reducing bugs in merges to main.
- Balancing security scans with build speed avoids slowing down the pipeline unnecessarily.
- Continuous improvement means iterating on the pipeline, like adding more test coverage or integrating monitoring tools
