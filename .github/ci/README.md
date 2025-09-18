# Continuous Integration Guide

## Common failures and quick fixes
- **`pytest` fails on DVC steps** – ensure `.dvc/config`, `dvc.yaml`, and `dvc.lock` are committed and run `dvc repro prepare_sample` locally before pushing. The CI runner expects a clean `dvc status` output.
- **`docker/build-push-action` unauthorized errors** – the workflow now logs in to GHCR. If this fails, confirm the default `GITHUB_TOKEN` still has `packages: write` permission and that the branch is pushed to the main repository.
- **`github/codeql-action/upload-sarif` denied on forks** – uploads are skipped automatically for forked pull requests. If you need the SARIF for debugging, run `npm run test:security` locally and inspect the generated `trivy-results.sarif` file instead.

## Reproducing CI locally
1. Install [`actionlint`](https://github.com/rhysd/actionlint) and [`act`](https://github.com/nektos/act).
2. Copy the secret template and populate values you need for the workflows: `cp .secrets.example .secrets.local`.
3. Run `make ci` to execute `actionlint` and a representative `act pull_request` run (uses `.secrets.local` automatically).
4. To target a specific workflow with `act`, run `act pull_request -W .github/workflows/<workflow>.yml --secret-file .secrets.local`.

## Adding a new workflow job
- Add a `permissions:` block scoped to the minimum APIs required (`contents: read` unless pushing artifacts).
- Re-use the existing `concurrency` pattern: `group: ${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true`.
- Cache heavy dependency managers (pip, npm, pnpm, etc.) and prefer maintained action versions (e.g., `checkout@v4`).
- Guard secret-consuming steps with `if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false`.
- Update this guide with any new required checks or reproduction steps.

## Permissions policy
- Default to `contents: read` across workflows.
- Elevate to `packages: write` only when publishing Docker images.
- Request `security-events: write` exclusively for SARIF uploads and skip those steps on forks.
- Use `pull-requests: write` / `checks: write` only for workflows that report annotations (e.g., reviewdog).

## Working with forked pull requests
- Secrets are not exposed to forks; guarded steps will be skipped automatically. Ensure alternative validation paths (unit tests, linting) still run without secrets.
- Contributors from forks should rely on `make ci` locally and attach logs if a guarded step is required for debugging.

## Required status checks
The protected `main` branch should require the following workflows before merging:
- **CI/CD Pipeline** (`.github/workflows/ci.yml`)
- **Unit Tests** (`.github/workflows/test.yml`)
- **Lint** (`.github/workflows/lint.yml` – includes actionlint + Python linters)
- **Production Deployment** (`.github/workflows/production-deploy.yml` – runs fully on push to `main`)

Ensure branch protection settings reflect this list so GitHub blocks merges when any required workflow fails.
