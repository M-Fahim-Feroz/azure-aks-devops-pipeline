# Architecture — Azure AKS DevOps Pipeline

This document describes the end-to-end architecture of the CI/CD pipeline and deployed infrastructure.

## CI/CD Flow

```mermaid
flowchart TD
    A([Developer Push to main]) --> B[GitHub Actions]
    B --> B1[Secret Validation]
    B1 --> B2[Build & Test\nFlake8 · Bandit · Pytest]
    B2 --> B3{infra/** changed?}
    B3 -->|Yes| C[Terraform Apply\nAzure Remote Backend]
    B3 -->|No| D[Docker Build & Push → ACR]
    C --> D
    D --> E[Ansible Playbook\nKubernetes Manifests + Helm]
    E --> F[Force Restart Deployments]
    F --> G[Smoke Test\ncurl LoadBalancer IP]
    G --> H([Deployment Complete])
```

## Azure Infrastructure

```mermaid
flowchart LR
    subgraph Azure["Azure — azure-aks-devops-rg"]
        VNet[Virtual Network\nfastapi-vnet] --> Subnet[Node Subnet]
        Subnet --> AKS[AKS Cluster\nazure-aks-devops-cluster]
        ACR[Container Registry\nfahimaksdevopsacr] --> AKS
        Storage[Storage Account\nPostgreSQL PVC] --> AKS
    end
    subgraph TFState["Terraform State — terraform-state-rg"]
        Blob[Azure Blob Storage\ntfstate container]
    end
    GitHub[GitHub Actions] --> ACR
    GitHub --> TFState
```

## Kubernetes Workloads

```mermaid
flowchart TD
    LB[Azure LoadBalancer\nfastapi-service :80] --> API
    subgraph fastapi["fastapi namespace"]
        API[fastapi-api\nDeployment x2] --> PG[postgres\nStatefulSet]
        API --> Redis[redis\nDeployment]
        Worker[fastapi-worker\nDeployment] --> Redis
        Worker --> PG
        PG --> PVC[Azure Files PVC\npostgres-data]
    end
    subgraph monitoring["monitoring namespace"]
        Prom[Prometheus] --> Grafana[Grafana]
        Prom -.scrapes.-> fastapi
    end
```

## Back to Main

[← README](../README.md)
