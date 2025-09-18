# Kickoff Prompt Guide (GPT‑5 via Codex)

This guide provides ready-to-use kickoff prompts for each project phase. Use GPT‑5 (via Codex) as the orchestrator/QC. No OpenAI API calls are made by the app; the orchestrator runs in your IDE. Delegate high‑reasoning to Grok‑4 and DeepThink, and prescriptive coding to DeepSeek 3.1.

---

## How To Use

- Open your IDE’s Codex chat with repo context loaded.
- Always read and ground in: `AGENTS.md`, `blueprint.md`, `personas.md`, `docs/BUILD_PLAN.md`, and `docs/TODO.md`.
- Copy a phase prompt below, adjust scope if needed, and run it.
- Ensure “Min GPT‑5 Level: High” (or higher) for all kickoffs.
- Require compliance with `AGENTS.md` No‑Stop Acceptance and async/Celery rule.
- Keep `docs/TODO.md` in sync: check off items as they are completed; add sub‑tasks as needed.

---

## Autonomous Execution (P1–P5)

- Min GPT‑5 Level: High
- Behavior: Do not stop to ask for confirmations during P1–P5. Proceed autonomously through tasks and phases while enforcing No‑Stop Acceptance gates per `AGENTS.md`.
- Full‑Run Prompt:
  """
  You are GPT‑5 (via Codex), the orchestrator. Operate in autonomous mode for Phases P1→P5 without prompting me. Strictly adhere to `AGENTS.md`, `blueprint.md`, `personas.md`, `docs/BUILD_PLAN.md`, and keep `docs/TODO.md` updated, checking off items as completed.

  Rules:

  - Enforce No‑Stop Acceptance for each phase; only move on when deliverables and checks are met.
  - All long operations are Celery tasks; no blocking calls.
  - Delegate: DeepSeek 3.1 for coding; DeepThink/Grok‑4 for high‑reasoning.
  - Keep docs updated (README, TODO, CHANGELOG) and cross‑linked; include tests in every PR.

  Output per phase: succinct change summary, files touched, tests added, and validation commands. When P5 is complete, deliver an overall summary and final validation checklist.
  """

---

## P0 — AI‑Led Planning (Already Completed)

- Min GPT‑5 Level: High
- Prompt:
  """
  You are GPT‑5 (via Codex), acting as The Weaver. Execute Phase P0: AI‑Led Planning strictly within docs/ only. Primary inputs: `blueprint.md`, `AGENTS.md`, `personas.md`.
  Deliverables: update `docs/BUILD_PLAN.md`, `docs/TEST_MATRIX.md`, `docs/API_SURFACE.md`, `docs/DB_SCHEMA.sql`, and `docs/TODO.md` per constraints in `prompts.md`.
  Enforce No‑Stop Acceptance from `AGENTS.md` and reference personas & delegation in `docs/AI_UTILIZATION_STRATEGY.md` (Grok‑4, DeepSeek 3.1, DeepThink).
  Output a concise summary of changes and next steps for P1.
  """

---

## P1 — Foundational Services & Data Model

- Min GPT‑5 Level: High
- Prompt:
  """
  Orchestrate Phase P1 per `docs/BUILD_PLAN.md` (P1.1–P1.4) with strict adherence to `AGENTS.md`, `blueprint.md`, `personas.md`, `docs/BUILD_PLAN.md`, `docs/TODO.md`, and `docs/AI_UTILIZATION_STRATEGY.md`.
  Keep `docs/TODO.md` updated and check off tasks as they complete. Do not prompt me; proceed autonomously within P1 and move to P2 when P1 meets No‑Stop Acceptance.
  Goals:
  - Apply `docs/DB_SCHEMA.sql` to Postgres (via docker-compose init). Add migrations only if required by acceptance criteria.
  - Implement initial API endpoint(s) (e.g., `/v1/status`) as sketched in `docs/API_SURFACE.md`.
  - Integrate MLflow via docker-compose service. No runtime OpenAI calls.
  - Confirm Celery worker wiring for long tasks (`src/tasks.py`) — all long operations must be asynchronous.
    Delegation:
  - DeepSeek 3.1 for prescriptive coding tasks.
  - DeepThink/Grok‑4 for high‑reasoning decisions or schema adaptations.
    Acceptance:
  - Tests added under `tests/` to satisfy PR policy.
  - Docs updated (`README.md`, `docs/TODO.md`, `docs/CHANGELOG.md`) and cross‑linked.
  - CI/lint green per `docs/CODE_QUALITY_FRAMEWORK.md`.
    Produce: a PR plan with file diffs overview, test list, and validation steps.
    """

---

## P2 — Data Ingestion & Normalization

- Min GPT‑5 Level: High
- Prompt:
  """
  Orchestrate Phase P2 (P2.1–P2.2) per `docs/BUILD_PLAN.md`, `docs/API_SURFACE.md`, and `docs/TODO.md`. Keep `docs/TODO.md` checked off as items complete. Do not prompt me; proceed autonomously and move to P3 upon meeting No‑Stop Acceptance.
  Goals:
  - Implement ingestion pipeline and normalization routines; persist to `raw_data` and `conversation_turns` (see `docs/DB_SCHEMA.sql`).
  - Ensure `source_type` values align with examples: `deepseek_chat`, `deepthink`, `grok_chat`.
  - All long operations are Celery tasks. No blocking calls in the main thread.
    Delegation:
  - DeepSeek 3.1 for pipeline code and adapters.
  - DeepThink for complex normalization logic and edge cases.
    Acceptance:
  - Unit/integration tests for ingestion + normalization.
  - Update `docs/TODO.md` and any API sketches if endpoints change.
    Produce: PR plan, code changes, tests, and validation commands.
    """

---

## P3 — Analysis & Modeling (Local‑First)

- Min GPT‑5 Level: High
- Prompt:
  """
  Orchestrate Phase P3 as defined in `docs/BUILD_PLAN.md` with a local‑first mindset and MLflow logging. Read `AGENTS.md`, `blueprint.md`, `personas.md`, and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously and move to P4 when No‑Stop Acceptance is met.
  Goals:
  - Implement analysis tasks as Celery jobs; log experiments to MLflow.
  - No OpenAI API usage; if external calls are needed, they must be async and configurable.
  - Define clear interfaces for model inputs/outputs, and persist results per schema.
    Delegation:
  - DeepThink for algorithmic design and evaluation criteria.
  - DeepSeek 3.1 for implementation and refactoring.
    Acceptance:
  - Tests for pipelines and result schemas; performance smoke checks.
  - Documentation updates for runbooks and parameters.
    Output: PR plan with experiments checklist and reproducibility steps.
    """

---

## P4 — Correlation & Pairing

- Min GPT‑5 Level: High
- Prompt:
  """
  Orchestrate Phase P4 per `docs/BUILD_PLAN.md` and `blueprint.md` Layer 4. Read personas and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously and move to P5 when No‑Stop Acceptance is met.
  Goals:
  - Implement candidate generation and evidence fusion; persist correlation artifacts.
  - Provide Celery tasks for correlation jobs; ensure idempotency and observability.
    Delegation:
  - DeepThink for correlation strategy and weighting.
  - DeepSeek 3.1 for implementation and optimizations.
    Acceptance:
  - Unit/integration tests for correlation correctness and data integrity.
  - Update `docs/API_SURFACE.md` if new endpoints are exposed.
    Deliver: PR plan with test scenarios and verification data.
    """

---

## P5 — Hybrid Search, Retrieval & UX

- Min GPT‑5 Level: High
- Prompt:
  """
  Orchestrate Phase P5 per `docs/BUILD_PLAN.md` and API sketches. Read `AGENTS.md`, `blueprint.md`, `personas.md` and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously.
  Goals:
  - Implement hybrid search endpoint(s) and `/v1/feedback`.
  - Add Export to Obsidian flow; ensure file outputs match blueprint expectations.
  - Provide a basic UI where specified, keeping backend contracts stable.
    Delegation:
  - DeepSeek 3.1 for endpoint and UI coding.
  - DeepThink for ranking logic and retrieval strategies.
    Acceptance:
  - End‑to‑end tests for search and export; accessibility checks for UI.
  - Docs updated and cross‑linked; smoke/CI green.
    Provide: PR plan, test matrix mapping, and demo steps.
    """

---

## Continuous — PR Review/QC & Security

- Min GPT‑5 Level: High
- QC/Debugger Prompt:
  """
  Act as QC/Debugger per `AGENTS.md` and `docs/CODE_QUALITY_FRAMEWORK.md`. Review the PR for:
  - Test coverage and clarity; adherence to `docs/TEST_MATRIX.md`.
  - Celery compliance for long ops; no blocking calls.
  - Doc updates (README, TODO, CHANGELOG) and cross‑links.
  - Security, secrets, dependency hygiene; provide fix-it diffs if needed.
    Outcome: Pass/Fail with actionable diffs and checklists.
    """
- Security Prompt:
  """
  Act as Sentinel. Perform a focused security review: threat modeling, dependency/licensing checks, and secrets scanning. Output prioritized issues and remediation steps aligned with `AGENTS.md`.
  """

---

## Notes & Defaults

- Always set: Min GPT‑5 Level = High.
- Delegate by default: DeepSeek 3.1 for coding; DeepThink for reasoning; Grok‑4 for system‑level architecture.
- Enforce No‑Stop Acceptance and async/Celery execution across all phases.
- Use branch naming: `feat/<task>` or `fix/<scope>` and prefer squash-merge.
