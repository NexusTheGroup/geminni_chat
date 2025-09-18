# AI Utilization Strategy & Best Practices

This document outlines the operational strategy and best practices for using GPT-5 (via Codex), Grok-4, and the latest DeepSeek models. It defines the roles and responsibilities of each AI to maximize efficiency and code quality, integrating directly with the project's existing persona framework [cite: `personas.md`].

## 1. Core Principle: The Trifecta Model

- **The Orchestrator & Quality Gate (GPT-5 via Codex):** The general contractor and site inspector. It manages the entire project, reads all blueprints and documentation, assigns tasks, reviews all work, and makes the final decision on quality and integration. Runs in the IDE via Codex; no OpenAI API calls are made from the application.
- **The System Architect (Grok-4):** The lead architect for high-level, complex reasoning tasks. It's used for designing complex systems, debugging intricate multi-component bugs, and tasks requiring real-time external knowledge.
- **The Specialist Coder (DeepSeek 3.1 + DeepThink):** The master craftsperson. Use DeepSeek 3.1 for fast, non-thinking chat/API tasks, and DeepThink for complex, code‑centric reasoning.

## 2. Persona Mapping

- **GPT-5 (via Codex) — Orchestrator & QC:**
  - **The Weaver / Aurora (Architect/Planner):** Generates the initial `BUILD_PLAN.md`, `TEST_MATRIX.md`, etc.
  - **Aletheia / QC/Debugger (Reviewer):** The exclusive agent for reviewing all PRs and enforcing the `CODE_QUALITY_FRAMEWORK.md`.
  - **Sentinel (Security Auditor):** Performs security reviews.
- **Grok-4 (System Architect):**
  - **Builder Persona (High-Reasoning):** Invoked by the GPT orchestrator for complex, non-code-centric architectural design and novel problem-solving.
- **DeepSeek 3.1 + DeepThink (Specialist Coder):**
  - **Builder Persona (Specialized / Non-Reasoning):** The default choice for all well-defined coding tasks, using DeepSeek 3.1 (chat/API).
  - **Builder Persona (Code-Centric Reasoning):** Can be invoked by the GPT orchestrator using DeepThink (DeepSeek’s high‑reasoning model) for complex coding problems.

## 3. Task Delegation Rules

- **For Code Generation (Specialized / Non-Reasoning):** Use **DeepSeek 3.1 (chat/API)** for over 80% of coding tasks.
- **For Complex Reasoning & Architecture:**
  - Use **Grok-4** for novel architectural problems.
  - Use **DeepThink** for complex coding problems.

## 4. Prompting Philosophy & Delegation

- **GPT-5 (via Codex) — Directive Prompts**
  - Prompts for the GPT orchestrator are high-level directives that reference the project's canonical documents.
  - _Example:_ `"Execute Phase P1 from docs/BUILD_PLAN.md..."`
- **Grok-4 (Exploratory Prompts)**
  - Prompts for Grok are open-ended and provide broad context, encouraging it to explore architectural solutions.
  - _Example:_ `"Design a resilient, queue-based ingestion pipeline..."`
- **DeepSeek 3.1 (Prescriptive Prompts)**
  - Prompts for DeepSeek 3.1 (chat/API) are highly specific and structured, resembling a technical ticket.
  - _Example (DeepSeek 3.1 chat):_ `"Implement the Python FastAPI endpoint..."`
  - _Example (DeepThink reasoning):_ `"Refactor our existing data access layer..."`
