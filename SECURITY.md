# Security Policy

## Supported Versions

This is a portfolio demonstration project. No production version is currently maintained.

| Version | Supported |
|---------|----------|
| main    |  Yes (latest) |

## Reporting a Vulnerability

If you discover a security issue in this portfolio project:

1. **Do not open a public GitHub issue.**
2. Contact the repository owner directly via GitHub profile: [M-Fahim-Feroz](https://github.com/M-Fahim-Feroz)
3. Describe the issue including steps to reproduce, impact, and affected components.

I will respond as soon as possible, typically within 48 hours.

## Security Design Notes

- No secrets or credentials are committed to this repository.
- All secrets are managed via GitHub Actions Secrets.
- Terraform state is managed locally within GitHub Actions runs (not committed).
- Docker images are built and pushed to a private Azure Container Registry.
- Kubernetes secrets are injected at deploy time via GitHub Actions.
- The Storage Account key is masked with `::add-mask::` before use.
- Azure authentication uses a Service Principal via `AZURE_CREDENTIALS`.

## Recommended Future Improvements

- Migrate Azure authentication from Service Principal JSON to GitHub OIDC federated credentials.
- Use Azure Key Vault for secrets instead of GitHub Secrets directly.
- Enable image signing (Cosign / Notation).
- Add Software Bill of Materials (SBOM) generation.
- Run Trivy container scanning on pushed images.
