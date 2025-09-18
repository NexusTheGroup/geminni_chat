PROMPTS.md — AI Agent Runbook
This file contains the high-level prompts for orchestrating the project.

## Final Kickoff Prompt

You are GPT-5 (via Codex), assuming the persona of The Weaver. The project environment is fully bootstrapped and all foundational documents are in place.

Your immediate objective is to execute Phase P0: AI-Led Planning.

Your primary inputs are the full contents of blueprint.md, AGENTS.md, and personas.md. You must adhere strictly to the processes defined within them.

### Deliverables:

Generate the following five planning artifacts. Ensure your plan fully incorporates the architectural layers for the User Feedback Loop, Knowledge Base Export (Obsidian), MLflow Experiment Tracking, and Data Version Control (DVC) as detailed in the blueprint.md.

1.  **`docs/BUILD_PLAN.md`**: Create a detailed, phase-by-phase implementation plan (P1-P5). Each task must have a clear description, dependencies, and specific, testable acceptance criteria.

2.  **`docs/TEST_MATRIX.md`**: Create a comprehensive testing plan that maps each feature from the blueprint to specific unit, integration, and end-to-end tests.

3.  **`docs/API_SURFACE.md`**: Generate a complete OpenAPI 3.0 specification sketch for all backend endpoints, including the new `/v1/feedback` endpoint.

4.  **`docs/DB_SCHEMA.sql`**: Generate the complete PostgreSQL 15 schema, including the necessary tables for storing user feedback data and any other entities required by the full blueprint.

5.  **Update `docs/TODO.md`**: Mark Phase P0 as complete and populate the subsequent phases with the high-level tasks generated in the `BUILD_PLAN.md`.

### Constraints:

- Operate strictly within the established framework (`AGENTS.md`, `CODE_QUALITY_FRAMEWORK.md`).
- Utilize the AI delegation strategy (`docs/AI_UTILIZATION_STRATEGY.md`) when creating the build plan, assigning personas and models to tasks. Orchestrate Grok-4, DeepSeek 3.1 (chat), and DeepThink (reasoning) as specified.
- Do not modify any files outside of the `docs/` directory during this planning phase.

### Acceptance and Handoff:

This phase is complete only when all five deliverables have been created, are internally consistent, and have been committed to the repository.

Upon completion, propose the detailed execution plan for Phase P1 and then await the command to proceed.
