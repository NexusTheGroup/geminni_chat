# AGENTS.md

This document defines the non-negotiable process and guardrails for this repository. It locks the common directory structure, the PR workflow, and the AI persona handoffs.

## 1) Mission & Scope

- Implement the project from `blueprint.md` through deployable build artifacts.
- Scope is build/deploy only; no runtime/prod operations in this repo.

## 2) Canonical Routes (read before any change)

- `AGENTS.md` (this file), `prompts.md`, `personas.md`, `blueprint.md`.
- Planning docs: `docs/TODO.md`, `docs/BUILD_PLAN.md`, `docs/TEST_MATRIX.md`, `docs/API_SURFACE.md`, `docs/DB_SCHEMA.sql`.
- Strategy docs: `docs/AI_UTILIZATION_STRATEGY.md`, `docs/CODE_QUALITY_FRAMEWORK.md`, `docs/ENV.md`.
- Troubleshooting: `docs/TROUBLESHOOTING.md` - Comprehensive debugging guide.

## 3) Common Directory Layout (locked)

```text
.devcontainer/
.github/
docs/
scripts/
src/
tests/
.gitignore
.pre-commit-config.yaml
AGENTS.md
README.md
blueprint.md
docker-compose.yml
package.json
personas.md
prompts.md
pyproject.toml
```

## 4) Branch & PR Protocol

Branches are short-lived: feat/<task>, fix/<scope>.

Each PR MUST include tests and updated docs.

PRs are reviewed by the GPT-5 (via Codex) QC/Debugger persona against the CODE_QUALITY_FRAMEWORK.md.

Prefer Squash and merge.

## 5) No-Stop Acceptance (global)

Do not conclude a phase until:

All phase deliverables exist and are cross-linked in docs/BUILD_PLAN.md.

Smoke and CI checks are green.

docs/TODO.md is up to date.

Required documentation (docs/ENV.md, CHANGELOG.md) is updated.

All code meets the minimum score defined in docs/CODE_QUALITY_FRAMEWORK.md.

## Asynchronous Task Execution

All long-running operations, especially external API calls, MUST be implemented as asynchronous tasks and delegated to a Celery worker. Direct, blocking calls in the main application thread are forbidden.

## Security Considerations

- MCP servers have access to project data and files
- Use appropriate file and directory permissions
- Ensure proper authentication for sensitive operations (GitHub tokens, API keys)
- Monitor network access requirements
- Validate input data and sanitize outputs
