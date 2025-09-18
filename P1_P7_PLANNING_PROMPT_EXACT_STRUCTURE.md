# P1–P7 Planning Prompts (Exact Structure) + Delegation Scripts

Use GPT‑5 (via Codex) as the orchestrator/QC. No OpenAI API calls are made by the app; the orchestrator runs in your IDE. Delegate prescriptive coding to DeepSeek 3.1 and high‑reasoning to DeepThink (and Grok‑4 for system‑level architecture). Enforce the No‑Stop Acceptance gates in `AGENTS.md`. Keep `docs/TODO.md` updated and checked off as work completes.

---

## Autonomous Execution (P1–P7)

- Min GPT‑5 Level: High
- Behavior: Do not prompt me during P1–P7. Proceed autonomously, phase by phase, advancing only when No‑Stop Acceptance is met.
- Full‑Run Prompt:
  """
  You are GPT‑5 (via Codex), the orchestrator. Operate in autonomous mode for Phases P1→P7 without prompting me. Always read and ground in: `AGENTS.md`, `blueprint.md`, `personas.md`, `docs/BUILD_PLAN.md`, and `docs/TODO.md`. Keep `docs/TODO.md` updated, checking off items and adding sub‑tasks as needed.

  Rules:
  - Enforce No‑Stop Acceptance for each phase; proceed only when deliverables and checks are met.
  - All long operations must be Celery tasks; no blocking calls in the main thread.
  - Delegate: DeepSeek 3.1 for coding; DeepThink/Grok‑4 for high‑reasoning and architecture.
  - Update docs (README, TODO, CHANGELOG) and cross‑links; include tests in every PR.

  Output per phase: succinct change summary, files touched, tests added, and validation commands. After P7, present an overall summary and readiness to enter P8.
  """

---

## P1 — Foundational Services & Data Model

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P1 per `docs/BUILD_PLAN.md` (P1.1–P1.4) with strict adherence to `AGENTS.md`, `blueprint.md`, `personas.md`, `docs/BUILD_PLAN.md`, `docs/TODO.md`, and `docs/AI_UTILIZATION_STRATEGY.md`. Keep `docs/TODO.md` updated and check off tasks as they complete. Do not prompt me; proceed autonomously within P1 and move to P2 when P1 meets No‑Stop Acceptance.

  Goals:
  - Apply `docs/DB_SCHEMA.sql` to Postgres (via docker-compose init). Add migrations only if required by acceptance criteria.
  - Implement initial API endpoint(s) (e.g., `/v1/status`) as sketched in `docs/API_SURFACE.md`.
  - Integrate MLflow via docker-compose service. No runtime OpenAI calls.
  - Confirm Celery worker wiring for long tasks (`src/tasks.py`) — all long operations must be asynchronous.

  Acceptance:
  - Tests added under `tests/` to satisfy PR policy.
  - Docs updated (`README.md`, `docs/TODO.md`, `docs/CHANGELOG.md`) and cross‑linked.
  - CI/lint green per `docs/CODE_QUALITY_FRAMEWORK.md`.

  Output: PR plan with file diffs overview, test list, and validation steps.
  """

### Delegation Scripts (P1)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Data model review
  Read: `docs/DB_SCHEMA.sql`, `blueprint.md` (Layer 2), `docs/BUILD_PLAN.md` (P1)
  Task: Validate schema adequacy, key constraints, UUID usage, and indexing strategy; propose minimal changes for robustness.
  Output: schema deltas + rationale + acceptance mapping.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Bootstrap services
  Tasks: apply schema, wire `/v1/status`, ensure Celery tasks run, add smoke tests, update README run instructions.
  Deliverables: code diffs, tests, docs.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P1 PR
  Checklist: schema created, status endpoint works, Celery async verified, tests/docs satisfactory.
  """

---

## P2 — Data Ingestion & Normalization

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P2 (P2.1–P2.2) per `docs/BUILD_PLAN.md`, `docs/API_SURFACE.md`, and `docs/TODO.md`. Keep `docs/TODO.md` checked off as items complete. Do not prompt me; proceed autonomously and move to P3 upon meeting No‑Stop Acceptance.

  Goals:
  - Implement ingestion pipeline and normalization routines; persist to `raw_data` and `conversation_turns` (see `docs/DB_SCHEMA.sql`).
  - Ensure `source_type` values align with examples: `deepseek_chat`, `deepthink`, `grok_chat`.
  - All long operations are Celery tasks. No blocking calls in the main thread.

  Acceptance:
  - Unit/integration tests for ingestion + normalization.
  - Update `docs/TODO.md` and any API sketches if endpoints change.

  Output: PR plan, code changes, tests, and validation commands.
  """

### Delegation Scripts (P2)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Normalization design
  Task: Define canonical mapping rules and edge cases for conversations, turns, metadata. Provide testable examples.
  Output: mapping spec + test scenarios.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement ingestion + normalization
  Tasks: adapters, parser/normalizer, Celery tasks, tests, and docs updates.
  Deliverables: diffs, tests, runbook snippets.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P2 PR
  Checklist: idempotent ingestion, correct normalization, tests coverage, Celery compliance.
  """

---

## P3 — Analysis & Modeling (Local‑First)

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P3 as defined in `docs/BUILD_PLAN.md` with a local‑first mindset and MLflow logging. Read `AGENTS.md`, `blueprint.md`, `personas.md`, and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously and move to P4 when No‑Stop Acceptance is met.

  Goals:
  - Implement analysis tasks as Celery jobs; log experiments to MLflow.
  - No OpenAI API usage; if external calls are needed, they must be async and configurable.
  - Define clear interfaces for model inputs/outputs, and persist results per schema.

  Acceptance:
  - Tests for pipelines and result schemas; performance smoke checks.
  - Documentation updates for runbooks and parameters.

  Output: PR plan with experiments checklist and reproducibility steps.
  """

### Delegation Scripts (P3)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Analysis design
  Task: Choose minimal algorithms/pipelines suitable for single-user knowledge synthesis; define metrics and MLflow structure.
  Output: analysis plan + metrics.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement analysis tasks
  Tasks: Celery jobs, data contracts, MLflow logging wrappers, and tests.
  Deliverables: diffs, tests, docs.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P3 PR
  Checklist: async compliance, MLflow logging present, tests adequate, docs updated.
  """

---

## P4 — Correlation & Pairing

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P4 per `docs/BUILD_PLAN.md` and `blueprint.md` Layer 4. Read personas and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously and move to P5 when No‑Stop Acceptance is met.

  Goals:
  - Implement candidate generation and evidence fusion; persist correlation artifacts.
  - Provide Celery tasks for correlation jobs; ensure idempotency and observability.

  Acceptance:
  - Unit/integration tests for correlation correctness and data integrity.
  - Update `docs/API_SURFACE.md` if new endpoints are exposed.

  Output: PR plan with test scenarios and verification data.
  """

### Delegation Scripts (P4)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Correlation strategy
  Task: Define candidate generation heuristics and evidence fusion approach; specify evaluation criteria and edge cases.
  Output: strategy + evaluation plan.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement correlation pipeline
  Tasks: candidate generation task, fusion module, persistence model, tests.
  Deliverables: diffs, tests, docs.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P4 PR
  Checklist: correctness, idempotency, tests coverage, observability hooks present.
  """

---

## P5 — Hybrid Search, Retrieval & UX

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P5 per `docs/BUILD_PLAN.md` and API sketches. Read `AGENTS.md`, `blueprint.md`, `personas.md` and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously.

  Goals:
  - Implement hybrid search endpoint(s) and `/v1/feedback`.
  - Add Export to Obsidian flow; ensure file outputs match blueprint expectations.
  - Provide a basic UI where specified, keeping backend contracts stable.

  Acceptance:
  - End‑to‑end tests for search and export; accessibility checks for UI.
  - Docs updated and cross‑linked; smoke/CI green.

  Output: PR plan, test matrix mapping, and demo steps.
  """

### Delegation Scripts (P5)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Search design
  Task: Define hybrid search composition (keyword + vector/hybrid strategy), scoring, and ranking; outline UX implications.
  Output: search spec + ranking evaluation plan.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement search + feedback + export
  Tasks: endpoints, Obsidian exporter, basic UI scaffolding as needed, tests, and docs.
  Deliverables: diffs, tests, docs.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P5 PR
  Checklist: endpoint contracts, ranking sanity, e2e tests present, accessibility checks completed.
  """

---

## P6 — Web Application (UX) Polish & Accessibility

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P6 grounded in `blueprint.md` Layer 6. Read `personas.md`, `docs/BUILD_PLAN.md` (for dependencies), and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously.

  Goals:
  - Accessibility: keyboard navigation, focus management, ARIA labels, contrast and color modes; basic WCAG checks.
  - UX Polish: error/empty states, loading skeletons, and consistent layout/components.
  - Observability: minimal client‑side event logging (non‑PII) wired to backend if applicable.

  Acceptance:
  - Accessibility checklist completed; basic automated a11y tests or linters run.
  - UX guidelines documented; screenshots or short demo steps added.

  Output: PR plan, component/state changes, a11y report, and test steps.
  """

### Delegation Scripts (P6)

- DeepThink (Reasoning):
  """
  Role: DeepThink — UX/a11y guidance
  Task: Provide a minimal a11y/UX guideline tailored to the app’s scope with examples and acceptance checks.
  Output: guideline + acceptance list.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Apply UX/a11y
  Tasks: implement a11y fixes, component polish, and add lightweight a11y tests.
  Deliverables: diffs, tests, docs.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P6 PR
  Checklist: a11y items verified, UX consistency, tests/docs sufficient.
  """

---

## P7 — API (Local‑Only) Hardening & Stability

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P7 grounded in `blueprint.md` Layer 7 and `docs/API_SURFACE.md`. Read `AGENTS.md`, `personas.md`, and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously.

  Goals:
  - Contracts: finalize response envelopes, error schema, pagination/sorting/query params; ensure consistent HTTP status usage.
  - Versioning: enforce `/v1` conventions; serve OpenAPI; document any breaking changes policy (local‑only by default).
  - Validation: strict request validation and informative error messages; input sanitation.
  - Stability: rate limiting optional (local use), timeouts, and graceful error handling; Celery for long ops.

  Acceptance:
  - Contract tests for all public endpoints; negative tests for validation.
  - OpenAPI served and matches `docs/API_SURFACE.md`.

  Output: PR plan, endpoint diffs, test suite additions, and verification commands.
  """

### Delegation Scripts (P7)

- DeepThink (Reasoning):
  """
  Role: DeepThink — API contracts
  Task: Define error/response schema, pagination/sorting rules, and breaking‑change policy; map to OpenAPI.
  Output: API contract spec + test cases.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement API hardening
  Tasks: validations, error handler middleware, OpenAPI alignment, contract tests, and docs.
  Deliverables: diffs, tests, docs.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P7 PR
  Checklist: contract coverage, negative tests, OpenAPI parity, Celery compliance.
  """

---

## Generic Delegation Templates (Copy/Paste)

- DeepSeek 3.1 — Coding
  """
  Role: DeepSeek 3.1 (Specialist Coder)
  Inputs: {phase}, {task_id}, {files to edit}, {acceptance}, {constraints}
  Constraints: Follow `AGENTS.md`, async rule, repo style. Produce minimal, focused diffs and tests.
  Deliverables: code patches, tests, and concise doc updates.
  """

- DeepThink — Reasoning
  """
  Role: DeepThink (High‑Reasoning)
  Inputs: {phase}, {topic}, {goals}, {trade‑offs}
  Output: concrete design/plan with acceptance mapping and risks.
  """

- Grok‑4 — Architecture
  """
  Role: Grok‑4 (System Architect)
  Inputs: {phase}, {architecture decision}
  Output: targeted review with deltas and rationale.
  """

- QC/Debugger — Review
  """
  Role: GPT‑5 QC/Debugger
  Inputs: {PR}, {tests}, {docs}
  Output: pass/fail with actionable diffs and checklist results.
  """
