# Roadmap

Planned improvements for the Azure AKS DevOps Pipeline project.

These are tracked as GitHub Issues in `docs/github-issues.md`.

## Near-Term (v1.1)

- [ ] **[Security]** Migrate Azure authentication from Service Principal JSON to GitHub OIDC federated credentials — eliminates long-lived secrets
- [ ] **[Security]** Add dedicated `GRAFANA_ADMIN_PASSWORD` secret separate from PostgreSQL password  (completed)
- [ ] **[CI]** Add pytest-cov coverage reporting to build-and-test job
- [ ] **[CI]** Upload test coverage report as GitHub Actions artifact
- [ ] **[Terraform]** Move Terraform state from local GitHub Actions runner to Azure Storage remote backend with state locking
- [ ] **[Monitoring]** Add Grafana alerting rules for pod restarts and high error rates

## Medium-Term (v1.2)

- [ ] **[Security]** Implement image signing using Notation or Cosign
- [ ] **[Security]** Generate SBOM (Software Bill of Materials) for Docker images
- [ ] **[Security]** Add Trivy scanning of built images before push to ACR
- [ ] **[Monitoring]** Add CloudWatch-style cost alerting via Azure Cost Management alerts
- [ ] **[CI]** Add branch protection enforcement: require status checks, no force push
- [ ] **[Docs]** Add cost estimate for a full pipeline run

## Long-Term (v2.0)

- [ ] **[Architecture]** Split into multi-environment: dev and prod namespaces
- [ ] **[Architecture]** Add GitOps with ArgoCD or Flux for continuous delivery
- [ ] **[Architecture]** Add production-grade persistent volume setup with Azure Disk CSI
- [ ] **[Security]** Use Azure Key Vault for secrets instead of GitHub Secrets
- [ ] **[Observability]** Add distributed tracing with OpenTelemetry
- [ ] **[Release]** Create v1.0.0 portfolio release with deployment proof

## Known Limitations (Out of Scope)

- This project does not claim to be production-ready.
- Single AKS node is used for cost efficiency in a demo context.
- Terraform state is not persisted between pipeline runs (no remote backend).
- Azure authentication uses a Service Principal JSON; OIDC is the recommended approach.
- No multi-region or disaster recovery setup.
