# P8–P12 Planning Prompts (Exact Structure) + Delegation Scripts

Use GPT‑5 (via Codex) as the orchestrator/QC. No OpenAI API calls are made by the app; the orchestrator runs in your IDE. Delegate prescriptive coding to DeepSeek 3.1 and high‑reasoning to DeepThink (and Grok‑4 for system‑level architecture). Enforce the No‑Stop Acceptance gates in `AGENTS.md`. Keep `docs/TODO.md` updated and checked off as work completes.

---

## Autonomous Execution (P8–P12)

- Min GPT‑5 Level: High
- Behavior: Do not prompt me during P8–P12. Proceed autonomously, phase by phase, advancing only when No‑Stop Acceptance is met.
- Full‑Run Prompt:
  """
  You are GPT‑5 (via Codex), the orchestrator. Operate in autonomous mode for Phases P8→P12 without prompting me. Always read and ground in: `AGENTS.md`, `blueprint.md`, `personas.md`, `docs/BUILD_PLAN.md`, and `docs/TODO.md`. Keep `docs/TODO.md` updated, checking off items and adding sub‑tasks as needed.

  Rules:
  - Enforce No‑Stop Acceptance for each phase; proceed only when deliverables and checks are met.
  - All long operations must be Celery tasks; no blocking calls in the main thread.
  - Delegate: DeepSeek 3.1 for coding; DeepThink/Grok‑4 for high‑reasoning and architecture.
  - Update docs (README, TODO, CHANGELOG) and cross‑links; include tests in every PR.

  Output per phase: succinct change summary, files touched, tests added, and validation commands. After P12, present an overall summary and final validation checklist.
  """

---

## Single Unified Prompt — P8→P12 (No Prompts, Personas Intact)

- Min GPT‑5 Level: High
- Paste this entire block into Codex and run once.
  """
  You are GPT‑5 (via Codex), acting as the Orchestrator/QC for NexusKnowledge.
  Operate autonomously from P8 through P12 without asking me anything. Keep personas intact and delegate accordingly.

  Grounding documents you must read and continually reference:
  - AGENTS.md (guardrails, No‑Stop Acceptance, async/Celery rule)
  - blueprint.md (layers 8–12 focus)
  - personas.md (orchestrator, Grok‑4, DeepSeek 3.1, DeepThink, QC/Debugger)
  - docs/BUILD_PLAN.md (phase tasks)
  - docs/TODO.md (keep up to date; check items off as completed; add sub‑tasks as needed)

  Global rules:
  - Enforce No‑Stop Acceptance before advancing phases.
  - All long operations run as Celery tasks; never block the main thread.
  - No OpenAI API calls from the app; orchestrator runs via IDE Codex only.
  - Include tests in every PR; update README/TODO/CHANGELOG and cross‑link docs.

  Personas and delegation:
  - GPT‑5 (via Codex): Orchestrator + QC/Debugger. Runs this plan and reviews PRs.
  - DeepSeek 3.1: Specialist Coder for prescriptive implementation and tests.
  - DeepThink: High‑reasoning for non‑trivial design decisions.
  - Grok‑4: System‑level architecture validation where it adds value.

  Execute the following phases sequentially. For each phase, produce: succinct change summary, files touched, tests added, validation commands. Then proceed to the next phase without prompting me.

  PHASE P8 — Observability & Reliability
  Goals:
  - Structured JSON logging with correlation/request IDs; include Celery task IDs.
  - Health/readiness endpoints and service checks (DB, Redis, Celery ping).
  - Metrics: basic counters/timers for API latency, task duration, error rates.
  - Optional tracing plan; document approach even if deferred.
  - Add observability runbook.
    Delegation:
  - DeepThink: observability design (fields, checks, metrics, tracing plan).
  - DeepSeek 3.1: implement logging/middleware, health endpoints, metrics hooks + tests.
  - QC/Debugger: verify tests/docs/Celery compliance.
    Acceptance:
  - Health/ready tests; log field assertions; docs updated; CI/lint green.

  PHASE P9 — Performance & Scale (Single User)
  Goals:
  - DB indexes (e.g., raw_data.source_type, conversation_turns keys); analyze plans.
  - Tune Celery concurrency/prefetch; add timeouts/backoff; memory‑safe iteration.
  - Pagination defaults; lightweight benchmark scripts with thresholds.
    Delegation:
  - DeepThink: performance strategy and thresholds.
  - DeepSeek 3.1: indices/migrations, refactors, benchmarks + tests.
  - QC/Debugger: reproducible benchmarks, no new blocking calls.
    Acceptance:
  - Baselines + thresholds documented; indices used; docs updated.

  PHASE P10 — Configuration & Operations
  Goals:
  - Central config loader with validation and safe errors; secret handling guidance.
  - Developer scripts: db migrate/seed, worker control, log tail, health check.
  - Migration approach consistent with docs/DB_SCHEMA.sql.
    Delegation:
  - DeepThink: config schema/validation policy.
  - DeepSeek 3.1: config loader, scripts, tests; docs.
  - QC/Debugger: validation coverage, script reliability.
    Acceptance:
  - Config tests pass; scripts conform; ENV + runbook updated; CI green.

  PHASE P11 — Import/Export & Interoperability
  Goals:
  - Finalize ingestion connectors with normalization; ensure idempotency/metadata.
  - Obsidian export with deterministic paths/links; clean content + metadata.
  - Minimal stable file formats; versioning + breaking changes policy.
    Delegation:
  - DeepThink: canonical mapping + interop policy.
  - DeepSeek 3.1: connectors + exporter + golden‑file tests; docs.
  - QC/Debugger: idempotency/export correctness; Celery compliance.
    Acceptance:
  - Ingest/Export tests (incl. golden files); docs updated; CI green.

  PHASE P12 — Experiment Tracking & Data Versioning
  Goals:
  - MLflow logging wrappers in Celery tasks; experiment structure/tags.
  - DVC for datasets/artifacts; remotes, pipeline steps; reproducibility docs.
    Delegation:
  - DeepThink: experiment design + metrics; DVC grouping strategy.
  - DeepSeek 3.1: MLflow/DVC integration, smoke tests, docs.
  - QC/Debugger: verify logging paths, reproducibility, and docs completeness.
    Acceptance:
  - MLflow/DVC smoke tests; reproducibility steps clear; CHANGELOG updated.

  Final output after P12:
  - Overall summary; consolidated validation checklist; pointers to key docs and tests.
    Execute now from P8 through P12 without stopping or prompting me.
    """

---

## P8 — Observability & Reliability

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P8 grounded in `blueprint.md` Layer 8 and `AGENTS.md`. Also read `personas.md`, `docs/BUILD_PLAN.md`, and sync `docs/TODO.md` (check off items as completed). Do not prompt me; proceed autonomously.

  Goals:
  - Logging: standardize structured logging (JSON), log levels, correlation/request IDs; include Celery task IDs. Ensure worker logs surface task lifecycle events.
  - Health: implement health/readiness endpoints and service checks (DB, Redis, Celery ping). Add minimal diagnostics to `/v1/status` if applicable.
  - Metrics: instrument key counters/timers for API latency, task duration, and error rates; expose a metrics endpoint if feasible.
  - Tracing (optional): define trace IDs and propagation across API → Celery → DB; document approach even if tracing infra is deferred.
  - Runbooks: add troubleshooting, log formats, and metrics dashboards documentation.

  Acceptance:
  - Tests for health endpoints and Celery liveness checks; assertions for structured log fields (request ID, task ID).
  - Documentation updated (observability runbook) and cross‑linked; CHANGELOG updated.
  - CI/lint green; no blocking calls; long ops are Celery tasks.

  Produce: PR plan, files to be created/modified, test list, and validation commands (including how to tail logs and verify metrics).
  """

### Delegation Scripts (P8)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Observability design
  Read: `AGENTS.md`, `blueprint.md` (Layer 8), `docs/BUILD_PLAN.md` (P8), `docs/TODO.md`
  Task: Propose observability architecture: logging schema (JSON fields), correlation IDs, metrics to instrument, health/readiness checks, and optional tracing plan.
  Output: A concrete design with:
  - Logging fields and examples
  - Health/ready checks list and failure modes
  - Metrics list (name, type, labels)
  - Tracing propagation plan (optional)
  - Test scenarios and acceptance mapping
    Keep it minimal yet complete, optimized for a single-user system.
    """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement observability
  Read: P8 design from DeepThink, `AGENTS.md` async rule
  Tasks:
  - Implement structured logging and correlation IDs across API/Celery codepaths
  - Add `/v1/status` or similar; include service checks (DB, Redis, Celery ping)
  - Instrument metrics stubs/hooks; add tests
    Deliverables: code diffs, tests, and README/runbook updates. All long ops as Celery tasks.
    """
- Grok‑4 (Architecture, optional):
  """
  Role: Grok‑4 — Validate observability approach
  Review the P8 design for resilience and clarity; suggest improvements for single-user performance and debuggability.
  Output: targeted deltas (bullets or patch suggestions).
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P8 PR
  Checklist: tests, structured logs, health checks, metrics coverage, docs updated, Celery compliance. Output Pass/Fail with actionable diffs.
  """

---

## P9 — Performance & Scale (Single User)

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P9 grounded in `blueprint.md` Layer 9 and `AGENTS.md`. Read `docs/BUILD_PLAN.md` and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously.

  Goals:
  - DB: add indexes (e.g., `raw_data.source_type`, `conversation_turns.conversation_id, turn_index`) and analyze query plans; add pagination defaults.
  - App: profiling plan for hot paths; tune Celery concurrency/prefetch; enforce timeouts/backoff for external calls; add simple caching where appropriate.
  - I/O: validate streaming/chunking for large payloads; ensure memory‑safe iteration.
  - Benchmarks: add lightweight performance smoke tests and baseline metrics with pass/fail thresholds.

  Acceptance:
  - Bench tests with documented baseline/thresholds; indices present and used.
  - CI/lint green; docs updated with tuning guidance; Celery compliance.

  Output: PR plan, changes list (schema/index scripts, code tweaks), benchmark scripts, and reproduction steps.
  """

### Delegation Scripts (P9)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Performance strategy
  Read: `blueprint.md` Layer 9, `docs/BUILD_PLAN.md` (P9)
  Task: Identify probable bottlenecks and propose indexing, pagination, caching, and worker tuning plan. Provide thresholds and measurement plan.
  Output: prioritized actions with rationale and success criteria.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement performance improvements
  Tasks: add DB indexes/migrations, pagination defaults, critical path refactors (memory‑safe iteration, timeouts), benchmark scripts, and tests. Ensure Celery settings tuned.
  Deliverables: diffs, tests, and doc updates (performance notes).
  """
- Grok‑4 (Architecture, optional):
  """
  Role: Grok‑4 — Validate performance plan
  Review the plan for simplicity and ROI; recommend minimal viable set for single-user context.
  Output: deltas and risk notes.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P9 PR
  Checklist: indices used, benchmarks reproducible, observable improvements, no new blocking calls, docs updated.
  """

---

## P10 — Configuration & Operations

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P10 grounded in `blueprint.md` Layer 10 and `AGENTS.md`. Read `docs/ENV.md`, `docs/BUILD_PLAN.md`, and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously.

  Goals:
  - Config loader: centralize configuration with validation (required vars, defaults), and safe error messages.
  - Secrets: document handling; ensure no secrets in repo; validate `.env`/environment usage where applicable.
  - CLI & scripts: provide developer scripts for common ops (db migrate/seed, worker control, log tail, health check).
  - Migrations: codify DB migration approach aligned with `docs/DB_SCHEMA.sql`.

  Acceptance:
  - Tests for config validation and error cases; scripts meet repo standards.
  - Docs updated (`docs/ENV.md`, operational runbook) and cross‑linked; CHANGELOG updated.

  Output: PR plan, new scripts listed, test plan, and usage examples.
  """

### Delegation Scripts (P10)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Config design
  Task: Define a minimal, safe configuration schema: required envs, validation rules, error messaging, and migration policy. Provide examples.
  Output: config spec + validation matrix.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement config + ops scripts
  Tasks: implement config loader/validator, add CLI/scripts for db and worker ops, and write tests. Update docs.
  Deliverables: diffs, tests, usage examples.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P10 PR
  Checklist: config validation coverage, error ergonomics, script reliability, docs completeness.
  """

---

## P11 — Import/Export & Interoperability

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P11 grounded in `blueprint.md` Layer 11 and `AGENTS.md`. Read `docs/API_SURFACE.md`, `docs/BUILD_PLAN.md`, and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously.

  Goals:
  - Import: finalize ingestion connectors (permitted sources) with normalization to canonical model; ensure idempotency and metadata capture.
  - Export: implement Obsidian export flow with deterministic file paths/links; ensure content hygiene and metadata retention.
  - Interop: define minimal stable file formats/schemas for import/export; version them and document breaking changes policy.

  Acceptance:
  - Tests for ingest idempotency and export correctness (golden‑file tests where feasible).
  - Docs updated (import/export runbook) and cross‑linked.
  - CI/lint green; Celery used for long‑running import/export jobs.

  Output: PR plan, connectors/exporters list, tests, and demonstration steps.
  """

### Delegation Scripts (P11)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Canonical data mapping
  Task: Define canonical mapping rules for sources to internal model, idempotency strategy, and export format for Obsidian. Provide examples and edge cases.
  Output: mapping spec + test cases (including golden files).
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement connectors and exporter
  Tasks: implement ingestion adapters with normalization, add export to Obsidian with deterministic paths/links, write tests (including golden files), and update docs.
  Deliverables: diffs, tests, and runbook.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P11 PR
  Checklist: idempotency verified, export correctness, tests comprehensive, Celery compliance, docs clarity.
  """

---

## P12 — Experiment Tracking & Data Versioning

- Min GPT‑5 Level: High
- Orchestrator Prompt:
  """
  Orchestrate Phase P12 grounded in `blueprint.md` Layer 12 and `AGENTS.md`. Read `docs/BUILD_PLAN.md`, `docs/TEST_MATRIX.md`, and keep `docs/TODO.md` updated. Do not prompt me; proceed autonomously.

  Goals:
  - MLflow: add thin wrappers to log experiments/metrics/artifacts from Celery tasks; document experiment structure and tags.
  - DVC: track large datasets/artifacts; configure remotes; define workflow for adding/updating data and reproducing experiments.
  - Reproducibility: document end‑to‑end steps to reproduce an analysis pipeline with specific data and parameters.

  Acceptance:
  - Tests/smoke checks for MLflow logging paths and DVC pipelines; clear reproduction steps.
  - Docs updated (experiments guide, DVC usage) and cross‑linked; CHANGELOG updated.

  Output: PR plan, code changes, scripts, and an experiments reproducibility checklist.
  """

### Delegation Scripts (P12)

- DeepThink (Reasoning):
  """
  Role: DeepThink — Experiment design
  Task: Define key experiments, metrics, tagging, and evaluation criteria; propose a minimal MLflow structure. Outline DVC asset grouping and remote strategy.
  Output: experiment plan + DVC structure and governance.
  """
- DeepSeek 3.1 (Coding):
  """
  Role: DeepSeek 3.1 — Implement MLflow/DVC integration
  Tasks: implement logging wrappers in Celery tasks, add DVC pipelines/config, write tests/smoke checks, and docs for reproducibility.
  Deliverables: diffs, tests, docs.
  """
- QC/Debugger (GPT‑5):
  """
  Role: QC/Debugger — Review P12 PR
  Checklist: MLflow logging correctness, DVC reproducibility, tests/docs completeness, Celery compliance.
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
