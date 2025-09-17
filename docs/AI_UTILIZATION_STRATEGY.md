# AI Utilization Strategy & Best Practices

This document outlines the operational strategy and best practices for using Gemini 2.5 Pro, Grok-4, and the latest DeepSeek models. It defines the roles and responsibilities of each AI to maximize efficiency and code quality, integrating directly with the project's existing persona framework [cite: `personas.md`].

## 1. Core Principle: The Trifecta Model

*   **The Orchestrator & Quality Gate (Gemini 2.5 Pro):** The general contractor and site inspector. It manages the entire project, reads all blueprints and documentation, assigns tasks, reviews all work, and makes the final decision on quality and integration.
*   **The System Architect (Grok-4):** The lead architect for high-level, complex reasoning tasks. It's used for designing complex systems, debugging intricate multi-component bugs, and tasks requiring real-time external knowledge.
*   **The Specialist Coder (DeepSeek V3.1):** The master craftsperson. It is an expert in writing high-quality, idiomatic code. We will primarily use its fast, "non-thinking" `deepseek-chat` mode for well-defined tasks, and its "thinking" `deepseek-reasoner` mode for complex, code-centric reasoning.

## 2. Persona Mapping

*   **Gemini 2.5 Pro (Orchestrator & QC):**
    *   **The Weaver / Aurora (Architect/Planner):** Generates the initial `BUILD_PLAN.md`, `TEST_MATRIX.md`, etc.
    *   **Aletheia / QC/Debugger (Reviewer):** The exclusive agent for reviewing all PRs and enforcing the `CODE_QUALITY_FRAMEWORK.md`.
    *   **Sentinel (Security Auditor):** Performs security reviews.
*   **Grok-4 (System Architect):**
    *   **Builder Persona (High-Reasoning):** Invoked by Gemini for complex, non-code-centric architectural design and novel problem-solving.
*   **DeepSeek V3.1 (Specialist Coder):**
    *   **Builder Persona (Specialized / Non-Reasoning):** The default choice for all well-defined coding tasks, using the `deepseek-chat` (non-thinking) mode.
    *   **Builder Persona (Code-Centric Reasoning):** Can be invoked by Gemini using the `deepseek-reasoner` (thinking) mode for complex coding problems.

## 3. Task Delegation Rules

*   **For Code Generation (Specialized / Non-Reasoning):** Use **DeepSeek V3.1's `deepseek-chat` mode** for over 80% of coding tasks.
*   **For Complex Reasoning & Architecture:**
    *   Use **Grok-4** for novel architectural problems.
    *   Use **DeepSeek V3.1's `deepseek-reasoner` mode** for complex coding problems.

## 4. Prompting Philosophy & Delegation

*   **Gemini 2.5 Pro (Directive Prompts)**
    *   Prompts for Gemini are high-level directives that reference the project's canonical documents.
    *   *Example:* `"Execute Phase P1 from docs/BUILD_PLAN.md..."`
*   **Grok-4 (Exploratory Prompts)**
    *   Prompts for Grok are open-ended and provide broad context, encouraging it to explore architectural solutions.
    *   *Example:* `"Design a resilient, queue-based ingestion pipeline..."`
*   **DeepSeek V3.1 (Prescriptive Prompts)**
    *   Prompts for DeepSeek are highly specific and structured, resembling a technical ticket.
    *   *Example (`deepseek-chat` mode):* `"Implement the Python FastAPI endpoint..."`
    *   *Example (`deepseek-reasoner` mode):* `"Refactor our existing data access layer..."`
