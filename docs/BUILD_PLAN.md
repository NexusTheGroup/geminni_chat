# Build Plan: NexusKnowledge

This document outlines the phase-by-phase implementation plan for the NexusKnowledge system, incorporating architectural layers, AI persona delegation, and acceptance criteria.

---

## Phase P0: AI-Led Planning (Complete)

*   **Objective:** Generate foundational planning artifacts.
*   **Deliverables:** `BUILD_PLAN.md`, `TEST_MATRIX.md`, `API_SURFACE.md`, `DB_SCHEMA.sql`, updated `TODO.md`.
*   **Persona/Model:** The Weaver (Gemini 2.5 Pro).

---

## Phase P1: Foundation & Data Ingestion

*   **Objective:** Establish core project structure, data ingestion pipeline, and initial data model.
*   **Architectural Layers:** Layer 1 (Data Ingestion & Normalization), Layer 2 (Canonical Data Model), Layer 10 (Configuration & Operations), Layer 12 (Experiment Tracking & Data Versioning - DVC setup).

### Tasks:

1.  **P1.1 Project Setup & CI/CD**
    *   **Description:** Initialize project, set up basic CI/CD pipeline (e.g., GitHub Actions), configure pre-commit hooks (e.g., Black, Ruff, Prettier).
    *   **Dependencies:** None.
    *   **Acceptance Criteria:**
        *   Project repository initialized with standard structure.
        *   CI pipeline runs successfully on push/PR.
        *   Pre-commit hooks enforce code quality standards.
    *   **Persona/Model:** Aurora (Gemini 2.5 Pro) for planning, Builder (DeepSeek V3.1 chat) for implementation.

2.  **P1.2 Initial Data Model & Database Setup**
    *   **Description:** Define initial PostgreSQL schema for core entities (users, conversations, messages). Set up a local PostgreSQL instance (e.g., via Docker Compose).
    *   **Dependencies:** P1.1.
    *   **Acceptance Criteria:**
        *   PostgreSQL database is running locally.
        *   Tables defined in `DB_SCHEMA.sql` are created and accessible.
        *   Basic CRUD operations can be performed on core tables.
    *   **Persona/Model:** The Weaver (Gemini 2.5 Pro) for schema design, Builder (DeepSeek V3.1 chat) for implementation.

3.  **P1.3 Data Ingestion Service (Basic)**
    *   **Description:** Implement a basic service to ingest raw conversation data (e.g., from JSON files or a simple text format) into the canonical data model.
    *   **Dependencies:** P1.2.
    *   **Acceptance Criteria:**
        *   Service can parse and store sample raw data into the database.
        *   Error handling for malformed input is present.
    *   **Persona/Model:** Builder (DeepSeek V3.1 chat).

4.  **P1.4 DVC Setup**
    *   **Description:** Initialize Data Version Control (DVC) for versioning large data assets such as raw ingested data, processed datasets, and generated embeddings.
    *   **Dependencies:** P1.1.
    *   **Acceptance Criteria:**
        *   DVC repository initialized and configured.
        *   A sample raw data file is successfully versioned and tracked by DVC.
    *   **Persona/Model:** Helix (Gemini 2.5 Pro) for planning, Builder (DeepSeek V3.1 chat) for implementation.

---

## Phase P2: Core API & User Feedback

*   **Objective:** Develop the core local-only API, including the user feedback loop, and basic data retrieval.
*   **Architectural Layers:** Layer 7 (API), Layer 6 (Web Application - feedback interface), Layer 2 (Canonical Data Model - feedback table).

### Tasks:

1.  **P2.1 API Framework Setup**
    *   **Description:** Set up a FastAPI (Python) or Node.js Express framework for the local-only API.
    *   **Dependencies:** P1.1.
    *   **Acceptance Criteria:**
        *   API server starts successfully.
        *   A basic `/health` endpoint returns a 200 OK response.
    *   **Persona/Model:** Builder (DeepSeek V3.1 chat).

2.  **P2.2 User Feedback Endpoint (`/v1/feedback`)**
    *   **Description:** Implement the `/v1/feedback` endpoint to receive and store user feedback related to conversations or system performance.
    *   **Dependencies:** P1.2 (feedback table in DB_SCHEMA.sql), P2.1.
    *   **Acceptance Criteria:**
        *   API endpoint accepts POST requests with feedback data.
        *   Feedback data is validated and stored correctly in the database.
        *   Appropriate HTTP status codes are returned (e.g., 201 on success).
    *   **Persona/Model:** Builder (DeepSeek V3.1 chat).

3.  **P2.3 Basic Data Retrieval Endpoints**
    *   **Description:** Implement API endpoints to retrieve ingested conversation data, filtered by user or conversation ID.
    *   **Dependencies:** P1.3, P2.1.
    *   **Acceptance Criteria:**
        *   API endpoints can fetch conversation lists and individual conversation details.
        *   Data returned matches the canonical data model.
    *   **Persona/Model:** Builder (DeepSeek V3.1 chat).

---

## Phase P3: Analysis, Correlation & MLflow

*   **Objective:** Implement initial data analysis, correlation mechanisms, and integrate MLflow for experiment tracking.
*   **Architectural Layers:** Layer 3 (Analysis & Modeling), Layer 4 (Correlation & Pairing), Layer 12 (Experiment Tracking & Data Versioning - MLflow setup).

### Tasks:

1.  **P3.1 MLflow Setup**
    *   **Description:** Set up a local MLflow instance (e.g., via Docker) for tracking machine learning experiments, parameters, metrics, and models.
    *   **Dependencies:** P1.1.
    *   **Acceptance Criteria:**
        *   MLflow UI is accessible locally.
        *   A sample "hello world" MLflow run is successfully logged and visible in the UI.
    *   **Persona/Model:** Helix (Gemini 2.5 Pro) for planning, Builder (DeepSeek V3.1 chat) for implementation.

2.  **P3.2 Basic Text Preprocessing & Embedding Generation**
    *   **Description:** Implement services for text cleaning, tokenization, and generating embeddings from conversation messages using a pre-trained local model.
    *   **Dependencies:** P1.3, P3.1.
    *   **Acceptance Criteria:**
        *   Service can process raw text into clean tokens.
        *   Embeddings are generated for sample messages and stored (DVC versioned).
        *   Embedding generation process is logged as an MLflow run.
    *   **Persona/Model:** Builder (DeepSeek V3.1 reasoner) for algorithm design, Builder (DeepSeek V3.1 chat) for implementation.

3.  **P3.3 Initial Correlation Logic**
    *   **Description:** Develop a basic mechanism to identify related conversations or messages based on embedding similarity.
    *   **Dependencies:** P3.2.
    *   **Acceptance Criteria:**
        *   Given a conversation/message, the system can identify and return a list of correlated items.
        *   Correlation results are logged as part of an MLflow experiment.
    *   **Persona/Model:** Builder (Grok-4) for architectural design, Builder (DeepSeek V3.1 reasoner) for implementation.

---

## Phase P4: Hybrid Search & Web UI

*   **Objective:** Implement hybrid search capabilities and develop the initial web application user interface.
*   **Architectural Layers:** Layer 5 (Hybrid Search & Retrieval), Layer 6 (Web Application).

### Tasks:

1.  **P4.1 Hybrid Search Backend**
    *   **Description:** Integrate a search engine (e.g., SQLite FTS5 for keyword, and a vector store for semantic search) with the API to provide hybrid search capabilities.
    *   **Dependencies:** P2.3, P3.2.
    *   **Acceptance Criteria:**
        *   API endpoints support both keyword and semantic search queries.
        *   Search results are relevant and returned efficiently.
    *   **Persona/Model:** Builder (Grok-4) for architectural design, Builder (DeepSeek V3.1 reasoner) for implementation.

2.  **P4.2 Basic Web UI Framework**
    *   **Description:** Set up a modern frontend framework (e.g., React with Next.js or Vite, or Vue.js) for the web application.
    *   **Dependencies:** P2.1.
    *   **Acceptance Criteria:**
        *   Frontend development server runs successfully.
        *   A basic "Hello World" web page loads in the browser.
    *   **Persona/Model:** Builder (DeepSeek V3.1 chat).

3.  **P4.3 Conversation Display & Search Interface**
    *   **Description:** Develop UI components to display ingested conversations and a search bar to interact with the hybrid search API.
    *   **Dependencies:** P4.1, P4.2.
    *   **Acceptance Criteria:**
        *   Users can browse conversations through the UI.
        *   Users can input search queries and view search results.
        *   Feedback mechanism (from P2.2) is integrated into the UI.
    *   **Persona/Model:** Builder (DeepSeek V3.1 chat).

---

## Phase P5: Export, Observability & Refinement

*   **Objective:** Implement knowledge base export, enhance observability, and refine existing features.
*   **Architectural Layers:** Layer 11 (Import/Export & Interoperability - Obsidian export), Layer 8 (Observability & Reliability), Layer 9 (Performance & Scale).

### Tasks:

1.  **P5.1 Knowledge Base Export (Obsidian)**
    *   **Description:** Implement functionality to export selected conversations, correlated insights, or summarized knowledge into an Obsidian-compatible Markdown format (e.g., with internal links, tags).
    *   **Dependencies:** P2.3, P3.3.
    *   **Acceptance Criteria:**
        *   Exported files are correctly formatted Markdown.
        *   Obsidian can import and display the exported knowledge base with proper linking.
    *   **Persona/Model:** The Clarifier (Gemini 2.5 Pro) for format specification, Builder (DeepSeek V3.1 chat) for implementation.

2.  **P5.2 Basic Observability (Logging & Metrics)**
    *   **Description:** Integrate basic logging (e.g., structured logging with ELK stack or similar) and metrics collection (e.g., Prometheus/Grafana) for API and services.
    *   **Dependencies:** P2.1.
    *   **Acceptance Criteria:**
        *   Application logs are collected and viewable in a centralized system.
        *   Key API metrics (e.g., request rate, error rate, latency) are collected and visualized.
    *   **Persona/Model:** Aurora (Gemini 2.5 Pro) for planning, Builder (DeepSeek V3.1 chat) for implementation.

3.  **P5.3 Performance Optimization (Initial)**
    *   **Description:** Identify and address initial performance bottlenecks in critical paths like data ingestion, embedding generation, or search queries.
    *   **Dependencies:** P1.3, P3.2, P4.1.
    *   **Acceptance Criteria:**
        *   Key operations meet defined performance targets (e.g., ingestion rate, search latency).
        *   Profiling tools are used to identify bottlenecks.
    *   **Persona/Model:** Builder (Grok-4) for analysis, Builder (DeepSeek V3.1 reasoner) for optimization.
