# Contributing

This is a personal portfolio project. External contributions are welcome as learning collaborations.

## How to Contribute

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-improvement`
3. Make changes following the guidelines below.
4. Test your changes locally.
5. Open a Pull Request against `main`.

## Guidelines

- Do not commit secrets, credentials, `.env` files, or `terraform.tfstate`.
- Keep Terraform changes backwards-compatible or clearly document breaking changes.
- Follow existing code style (Python: PEP8 with max-line-length=120, YAML: 2-space indent).
- Add or update documentation for any infrastructure changes.
- Run `flake8 api/` and `bandit -r api/ -lll` before submitting.

## Branch Protection

The `main` branch is protected. All changes require a Pull Request.
Recommended branch protection rules:
- Require pull request before merge
- Require status checks to pass
- Require branch to be up to date
- Restrict force pushes

## Reporting Issues

Use GitHub Issues to report bugs or suggest improvements.
See `docs/github-issues.md` for a list of planned issues.
