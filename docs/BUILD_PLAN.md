# Build Plan: NexusKnowledge Project

This document outlines the phase-by-phase implementation plan for the NexusKnowledge system, incorporating the architectural layers for User Feedback Loop, Knowledge Base Export (Obsidian), MLflow Experiment Tracking, and Data Version Control (DVC). This plan adheres to the AI delegation strategy outlined in AGENTS.md and personas.md.

## Phase P1: Foundational Services & Data Model

**Objective:** Establish the core infrastructure, database schema, and foundational services.

### Tasks:

1.  **P1.1: Database Schema Implementation**

    - **Description:** Translate `docs/DB_SCHEMA.sql` into an executable migration script and apply it to the PostgreSQL database.
    - **Dependencies:** P0 (Planning Complete)
    - **Acceptance Criteria:**
      - Database tables are created as per `docs/DB_SCHEMA.sql`.
      - A migration script exists and can be run successfully.
      - Basic CRUD operations can be performed on core tables.
    - **Assigned Persona:** Builder (High-Reasoning) - Grok-4 / DeepThink
    - **Deliverables:** `alembic/versions/20240306_01_initial_schema.py`, `scripts/run_migrations.py`, `src/nexus_knowledge/db/models.py`, `tests/db/test_repository.py`

2.  **P1.2: Core API Endpoint Setup**

    - **Description:** Implement basic API endpoints for health checks and initial data interaction (e.g., `/v1/status`).
    - **Dependencies:** P1.1
    - **Acceptance Criteria:**
      - `/v1/status` endpoint returns a 200 OK response.
      - API documentation in `docs/API_SURFACE.md` is updated to reflect new endpoints.
    - **Assigned Persona:** Builder (Specialist Coder) - DeepSeek 3.1 (chat)
    - **Deliverables:** `src/nexus_knowledge/api/main.py`, `src/nexus_knowledge/tasks.py`, `docker-compose.yml`, `tests/api/test_api.py`

3.  **P1.3: MLflow Integration for Experiment Tracking**

    - **Description:** Configure MLflow to track experiments, parameters, metrics, and artifacts for analysis and modeling tasks.
    - **Dependencies:** P0 (Planning Complete), Docker Compose setup for MLflow.
    - **Acceptance Criteria:**
      - A sample Python script can log a dummy experiment to MLflow.
      - MLflow UI is accessible and displays logged experiments.
    - **Assigned Persona:** Helix (Data & IR Engineer)
    - **Deliverables:** `src/nexus_knowledge/mlflow_utils.py`, `scripts/log_dummy_experiment.py`, `tests/mlflow/test_mlflow_utils.py`

4.  **P1.4: DVC Integration for Data Versioning**
    - **Description:** Set up DVC to version large data assets (e.g., embeddings, datasets) used in the project.
    - **Dependencies:** P0 (Planning Complete)
    - **Acceptance Criteria:**
      - A sample data file is successfully versioned using DVC.
      - DVC commands can reproduce a specific data version.
    - **Assigned Persona:** Helix (Data & IR Engineer)
    - **Deliverables:** `.dvc/config`, `sample_data.json.dvc`, `tests/dvc/test_dvc_setup.py`

## Phase P2: Data Ingestion & Normalization

**Objective:** Develop robust pipelines for ingesting and normalizing data from various sources.

### Tasks:

1.  **P2.1: Initial Data Ingestion Pipeline**

    - **Description:** Implement a pipeline to ingest data from a primary source (e.g., a specific AI conversation format).
    - **Dependencies:** P1.1, P1.2
    - **Acceptance Criteria:**
      - Data from the primary source can be successfully ingested into the database.
      - Ingested data conforms to the defined schema.
    - **Assigned Persona:** Builder (High-Reasoning) - Grok-4 / DeepThink
    - **Deliverables:** `src/nexus_knowledge/ingestion/service.py`, `src/nexus_knowledge/api/main.py` (ingest routes), `tests/ingestion/test_service.py`, `tests/api/test_api.py` (ingest cases)

2.  **P2.2: Data Normalization Routines**
    - **Description:** Develop and apply routines to normalize ingested data into the canonical data model.
    - **Dependencies:** P2.1
    - **Acceptance Criteria:**
      - Raw ingested data is transformed into the canonical format.
      - Normalization process handles edge cases and errors gracefully.
    - **Assigned Persona:** Builder (Specialist Coder) - DeepSeek 3.1 (chat)
    - **Deliverables:** `src/nexus_knowledge/tasks.py` (normalization task), `docs/API_SURFACE.md` updates, `tests/ingestion/test_service.py`

## Phase P3: Analysis & Modeling (Local-First)

**Objective:** Integrate local AI models and develop analysis pipelines for deep insights.

### Tasks:

1.  **P3.1: Local AI Model Integration**

    - **Description:** Integrate a pre-trained local AI model for initial text analysis (e.g., sentiment analysis, entity extraction).
    - **Dependencies:** P2.2, P1.3
    - **Acceptance Criteria:**
      - The local AI model can be invoked successfully.
      - Model outputs are stored and associated with the relevant data.
      - Model performance metrics are logged to MLflow.
    - **Assigned Persona:** Helix (Data & IR Engineer)
    - **Deliverables:** `src/nexus_knowledge/analysis/model.py`, `src/nexus_knowledge/analysis/pipeline.py`, `tests/analysis/test_pipeline.py`

2.  **P3.2: Analysis Pipeline Development**
    - **Description:** Create pipelines to process normalized data using the integrated AI models and store the results.
    - **Dependencies:** P3.1
    - **Acceptance Criteria:**
      - Analysis pipelines run automatically on new data.
      - Analyzed data is accessible for correlation.
    - **Assigned Persona:** Builder (High-Reasoning) - Grok-4 / DeepThink
    - **Deliverables:** `src/nexus_knowledge/tasks.py` (analysis task), `/api/v1/analysis` endpoints, `tests/tasks/test_analysis_tasks.py`, `tests/api/test_api.py`

## Phase P4: Correlation & Pairing

**Objective:** Implement mechanisms to correlate and pair related pieces of information.

### Tasks:

1.  **P4.1: Candidate Generation for Correlation**

    - **Description:** Develop algorithms to identify potential correlations between different data points (e.g., similar topics, entities).
    - **Dependencies:** P3.2
    - **Acceptance Criteria:**
      - The system can generate a list of candidate correlations.
      - Candidate generation is efficient and scalable.
    - **Assigned Persona:** Helix (Data & IR Engineer)
    - **Deliverables:** `alembic/versions/20240306_02_add_correlation_candidates.py`, `src/nexus_knowledge/correlation/pipeline.py`, `tests/correlation/test_correlation_pipeline.py`, `/api/v1/correlation` endpoints

2.  **P4.2: Evidence Fusion & Re-weaving**
    - **Description:** Implement logic to fuse evidence from multiple sources to confirm correlations and re-weave knowledge graphs.
    - **Dependencies:** P4.1
    - **Acceptance Criteria:**
      - Confirmed correlations are stored and linked in the database.
      - Knowledge graph is updated based on new correlations.
    - **Assigned Persona:** Builder (High-Reasoning) - Grok-4 / DeepThink
    - **Deliverables:** `src/nexus_knowledge/tasks.py` (fusion task), `/api/v1/correlation/{rawDataId}/fuse`, `tests/tasks/test_correlation_tasks.py`, `tests/api/test_api.py`

## Phase P5: Hybrid Search, Retrieval & User Experience

**Objective:** Deliver a functional search interface, user feedback mechanism, and knowledge export.

### Tasks:

1.  **P5.1: Hybrid Search & Retrieval Implementation**

    - **Description:** Implement a search engine that combines keyword and semantic search capabilities.
    - **Dependencies:** P4.2
    - **Acceptance Criteria:**
      - Users can perform searches and retrieve relevant results.
      - Search results are ranked effectively.
    - **Assigned Persona:** Builder (Specialist Coder) - DeepSeek 3.1 (chat)
    - **Deliverables:** `src/nexus_knowledge/search/service.py`, `/api/v1/search`, `tests/search/test_search_service.py`, `tests/api/test_api.py` (search cases)

2.  **P5.2: User Feedback Loop Implementation**

    - **Description:** Implement the `/v1/feedback` API endpoint and associated database storage for user feedback.
    - **Dependencies:** P1.1, P1.2
    - **Acceptance Criteria:**
      - Users can submit feedback via the API.
      - Feedback is stored correctly in the database.
      - API documentation in `docs/API_SURFACE.md` is updated.
    - **Assigned Persona:** Builder (Specialist Coder) - DeepSeek 3.1 (chat)
    - **Deliverables:** Feedback listing/status endpoints (`src/nexus_knowledge/api/main.py`), repository utilities, tests (`tests/api/test_api.py`, `tests/db/test_repository.py`)

3.  **P5.3: Knowledge Base Export to Obsidian**

    - **Description:** Develop a mechanism to export synthesized knowledge into an Obsidian-compatible format (e.g., Markdown files with front matter).
    - **Dependencies:** P4.2
    - **Acceptance Criteria:**
      - Knowledge can be exported to a specified directory in Obsidian format.
      - Exported files are correctly formatted and linked.
    - **Assigned Persona:** The Clarifier (Technical Writer)
    - **Deliverables:** `src/nexus_knowledge/export/obsidian.py`, `/api/v1/export/obsidian`, `tests/export/test_obsidian.py`, `tests/tasks/test_export_tasks.py`, docs updates

4.  **P5.4: Basic Web Application UI**
    - **Description:** Develop initial UI components for displaying search results and interacting with the system.
    - **Dependencies:** P5.1, P5.2
    - **Acceptance Criteria:**
      - A basic web interface is accessible.
      - Search results are displayed in the UI.
      - User can submit feedback through the UI.
    - **Assigned Persona:** Builder (Specialist Coder) - DeepSeek 3.1 (chat)
    - **Deliverables:** FastAPI-root HTML shell (`src/nexus_knowledge/api/main.py`), UI tests (`tests/api/test_ui.py`), README instructions
