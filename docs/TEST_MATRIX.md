# Test Matrix: NexusKnowledge

This document outlines the comprehensive testing plan for the NexusKnowledge system, mapping features to specific unit, integration, and end-to-end tests. It aligns with the `CODE_QUALITY_FRAMEWORK.md` to ensure robust test coverage.

---

## General Testing Principles

*   **Unit Tests:** Focus on isolated functions, methods, and classes. Mock external dependencies.
*   **Integration Tests:** Verify interactions between different components (e.g., API and database, service and external library).
*   **End-to-End (E2E) Tests:** Simulate user flows through the entire system, from UI to backend and database.
*   **Code Coverage:** Aim for a minimum of 80% unit test coverage as per `CODE_QUALITY_FRAMEWORK.md`.

---

## Phase P1: Foundation & Data Ingestion

### P1.1 Project Setup & CI/CD
*   **Unit Tests:** N/A (Configuration-focused)
*   **Integration Tests:**
    *   Verify CI pipeline executes successfully on push/PR.
    *   Validate pre-commit hooks run and enforce formatting/linting rules.
*   **E2E Tests:** N/A

### P1.2 Initial Data Model & Database Setup
*   **Unit Tests:**
    *   Database connection utility functions.
    *   ORM model definitions (e.g., field types, relationships).
*   **Integration Tests:**
    *   Schema migration tests (applying and rolling back migrations).
    *   Basic CRUD operations (Create, Read, Update, Delete) against a test database for core entities (users, conversations, messages).
*   **E2E Tests:** N/A

### P1.3 Data Ingestion Service (Basic)
*   **Unit Tests:**
    *   Data parsing logic for various input formats.
    *   Normalization and transformation functions.
    *   Error handling for malformed input data.
*   **Integration Tests:**
    *   Ingestion of valid sample data into the test database, verifying data integrity and completeness.
    *   Testing ingestion with invalid data to ensure proper error handling and logging.
*   **E2E Tests:** N/A

### P1.4 DVC Setup
*   **Unit Tests:** N/A
*   **Integration Tests:**
    *   DVC repository initialization and configuration verification.
    *   Tracking and versioning of a dummy data file.
    *   Retrieval of different versions of a DVC-tracked file.
*   **E2E Tests:** N/A

---

## Phase P2: Core API & User Feedback

### P2.1 API Framework Setup
*   **Unit Tests:** N/A (Framework setup)
*   **Integration Tests:**
    *   Verify the `/health` endpoint returns a 200 OK response.
    *   API server starts and stops cleanly.
*   **E2E Tests:** N/A

### P2.2 User Feedback Endpoint (`/v1/feedback`)
*   **Unit Tests:**
    *   Validation logic for feedback payload (e.g., required fields, data types).
*   **Integration Tests:**
    *   POST requests to `/v1/feedback` with valid feedback data, verifying database persistence.
    *   POST requests with invalid/missing data, asserting appropriate error responses (e.g., 400 Bad Request).
    *   Security tests (e.g., rate limiting, input sanitization).
*   **E2E Tests:** N/A (Will be covered by UI E2E tests in P4.3)

### P2.3 Basic Data Retrieval Endpoints
*   **Unit Tests:**
    *   Data serialization/deserialization logic for API responses.
*   **Integration Tests:**
    *   GET requests for conversation lists, verifying correct data structure and content.
    *   GET requests for individual conversation details by ID.
    *   Testing filtering and pagination parameters.
*   **E2E Tests:** N/A

---

## Phase P3: Analysis, Correlation & MLflow

### P3.1 MLflow Setup
*   **Unit Tests:** N/A
*   **Integration Tests:**
    *   MLflow server accessibility and basic functionality (e.g., logging a dummy run).
    *   Verification that MLflow tracking URI is correctly configured.
*   **E2E Tests:** N/A

### P3.2 Basic Text Preprocessing & Embedding Generation
*   **Unit Tests:**
    *   Text cleaning functions (e.g., punctuation removal, lowercasing).
    *   Tokenization logic.
    *   Embedding model inference for known inputs, verifying output shape and type.
*   **Integration Tests:**
    *   Full pipeline from raw text input to generated and stored embeddings (DVC-tracked).
    *   Verification that embedding generation process is logged as an MLflow run with relevant parameters and metrics.
*   **E2E Tests:** N/A

### P3.3 Initial Correlation Logic
*   **Unit Tests:**
    *   Similarity calculation algorithms (e.g., cosine similarity).
    *   Core correlation algorithm logic (e.g., nearest neighbors).
*   **Integration Tests:**
    *   Correlation of sample conversation data, verifying the accuracy and relevance of correlated items.
    *   Verification that correlation results and metrics are logged as part of an MLflow experiment.
*   **E2E Tests:** N/A

---

## Phase P4: Hybrid Search & Web UI

### P4.1 Hybrid Search Backend
*   **Unit Tests:**
    *   Keyword search query parsing and execution logic.
    *   Vector similarity search query execution logic.
    *   Result merging and ranking algorithms for hybrid search.
*   **Integration Tests:**
    *   API endpoints for hybrid search, testing various keyword and semantic queries.
    *   Relevance and recall of search results for a diverse set of test cases.
    *   Performance benchmarks for search queries.
*   **E2E Tests:** N/A

### P4.2 Basic Web UI Framework
*   **Unit Tests:** N/A (Framework setup)
*   **Integration Tests:**
    *   Frontend build process and asset compilation.
    *   Basic page rendering and navigation.
*   **E2E Tests:** N/A

### P4.3 Conversation Display & Search Interface
*   **Unit Tests:**
    *   UI component rendering (e.g., ConversationCard, SearchBar).
    *   State management logic for UI components.
*   **Integration Tests:**
    *   UI interaction with API: displaying conversation lists, submitting search queries, rendering search results.
    *   Feedback form submission through the UI to the `/v1/feedback` endpoint.
*   **E2E Tests:**
    *   User flow: browsing conversations, performing keyword and semantic searches, viewing search results.
    *   User flow: submitting feedback via the UI and verifying backend persistence.
    *   Accessibility testing for key UI elements.

---

## Phase P5: Export, Observability & Refinement

### P5.1 Knowledge Base Export (Obsidian)
*   **Unit Tests:**
    *   Markdown formatting logic for various content types (e.g., conversations, notes, links).
    *   Internal link generation and tag formatting for Obsidian compatibility.
*   **Integration Tests:**
    *   Exporting sample data (conversations, correlated insights) and verifying the generated Markdown files.
    *   Importing exported files into a test Obsidian vault and verifying correct display and linking.
*   **E2E Tests:**
    *   User flow: initiating a knowledge base export from the UI and verifying the output in Obsidian.

### P5.2 Basic Observability (Logging & Metrics)
*   **Unit Tests:** N/A
*   **Integration Tests:**
    *   Verification of structured log collection for API requests and service operations.
    *   Accessibility of metrics endpoints (e.g., Prometheus `/metrics`).
    *   Alerting mechanism tests (if implemented).
*   **E2E Tests:** N/A

### P5.3 Performance Optimization (Initial)
*   **Unit Tests:** N/A
*   **Integration Tests:**
    *   Performance benchmarks for critical operations (e.g., data ingestion rate, search latency, embedding generation time).
    *   Load testing for API endpoints.
*   **E2E Tests:** N/A
