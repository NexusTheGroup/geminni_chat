# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

- Alembic-based bootstrap migrations and SQLAlchemy models for the canonical schema (`alembic/`, `src/nexus_knowledge/db/models.py`).
- FastAPI `/api/v1/status` and asynchronous `/api/v1/feedback` workflow with Celery persistence (`src/nexus_knowledge/api/main.py`, `src/nexus_knowledge/tasks.py`).
- MLflow helper module and CLI smoke test (`src/nexus_knowledge/mlflow_utils.py`, `scripts/log_dummy_experiment.py`).
- Automated regression coverage for database CRUD, Celery tasks, API endpoints, MLflow logging, and DVC status (`tests/`).
- Asynchronous ingestion and normalization pipeline with REST endpoints and Celery orchestration (`src/nexus_knowledge/ingestion/service.py`, `/api/v1/ingest`).
- Local heuristic analysis model with MLflow logging, Celery worker integration, and `/api/v1/analysis` status endpoints (`src/nexus_knowledge/analysis/`, `src/nexus_knowledge/tasks.py`).
- Correlation candidate generation, fusion workflow, and persistence (`src/nexus_knowledge/correlation/`, `/api/v1/correlation` endpoints, new Celery tasks).
- Hybrid search service and REST endpoint combining keyword + semantic heuristics (`src/nexus_knowledge/search/service.py`, `/api/v1/search`).
- Feedback triage endpoints for listing and status updates (`/api/v1/feedback`, PATCH support) with repository helpers and coverage.
- Obsidian export pipeline with Celery task and REST endpoint (`src/nexus_knowledge/export/obsidian.py`, `/api/v1/export/obsidian`).
- Basic web UI shell served at `/` for search + feedback interactions.

### Changed

- Orchestrator/QC roles migrated from Gemini 2.5 Pro to GPT-5 (via Codex). The orchestrator runs in the IDE and does not make OpenAI API calls from the application.
- Terminology aligned for DeepSeek models:
  - DeepSeek 3.1 — API/chat model for prescriptive coding tasks.
  - DeepThink — high‑reasoning model for complex, code‑centric reasoning.
- Updated `AGENTS.md`, `personas.md`, `prompts.md`, `docs/AI_UTILIZATION_STRATEGY.md`, `README.md`, `docs/ENV.md`.
- Clarified example source types in `docs/API_SURFACE.md` and `docs/DB_SCHEMA.sql` to include `deepseek_chat`, `deepthink`, and `grok_chat`.
