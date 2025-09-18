# Test Matrix: NexusKnowledge Project

This document outlines the comprehensive testing plan for the NexusKnowledge system, mapping features to specific unit, integration, and end-to-end tests. It aligns with the phases and tasks defined in `docs/BUILD_PLAN.md`.

## Phase P1: Foundational Services & Data Model

### P1.1: Database Schema Implementation

- **Unit Tests:**
  - Verify individual table and column definitions.
  - Test constraints (e.g., primary keys, foreign keys, unique constraints).
- **Integration Tests:**
  - Execute migration scripts against a test database.
  - Verify successful schema creation and data integrity after migrations.
- **End-to-End Tests:**
  - (N/A for schema directly, covered by API interaction tests)

### P1.2: Core API Endpoint Setup

- **Unit Tests:**
  - Test individual API handler functions for correct logic and error handling.
- **Integration Tests:**
  - Send requests to `/v1/status` and assert a 200 OK response.
  - Verify basic CRUD operations against the database via API endpoints.
  - Retrieve existing records via `GET /v1/feedback/{feedbackId}` after asynchronous persistence completes.
- **End-to-End Tests:**
  - Deploy the application and hit the `/v1/status` endpoint from an external client.

### P1.3: MLflow Integration for Experiment Tracking

- **Unit Tests:**
  - Test MLflow logging functions with mock data.
- **Integration Tests:**
  - Run a sample experiment that logs parameters, metrics, and artifacts to a local MLflow instance.
  - Verify that logged data appears correctly in the MLflow UI.
- **End-to-End Tests:**
  - (Covered by integration tests for now, as MLflow is an internal tool)

### P1.4: DVC Integration for Data Versioning

- **Unit Tests:**
  - Test DVC command wrappers with mock file paths.
- **Integration Tests:**
  - Version a sample data file using DVC and verify its presence in the DVC cache.
  - Attempt to reproduce a previous version of a data file.
- **End-to-End Tests:**
  - (Covered by integration tests for now, as DVC is an internal tool)

## Phase P2: Data Ingestion & Normalization

### P2.1: Initial Data Ingestion Pipeline

- **Unit Tests:**
  - Test individual parsing and extraction functions for various data formats.
- **Integration Tests:**
  - Ingest a known dataset and verify its presence and correctness in the database.
  - Test error handling for malformed input data.
  - Exercise API ingestion endpoint to confirm Celery normalization is queued.
- **End-to-End Tests:**
  - Run the full ingestion pipeline with a representative dataset and verify the final state of the database.

### P2.2: Data Normalization Routines

- **Unit Tests:**
  - Test individual normalization functions with various input scenarios (e.g., valid, invalid, edge cases).
- **Integration Tests:**
  - Ingest raw data, apply normalization, and verify the transformed data in the database.
  - Confirm ingestion status endpoint reflects the final state post-normalization.
- **End-to-End Tests:**
  - (Covered by P2.1 E2E tests, ensuring normalized data is correct)

## Phase P3: Analysis & Modeling (Local-First)

### P3.1: Local AI Model Integration

- **Unit Tests:**
  - Test model loading and inference with mock inputs and expected outputs.
  - Validate heuristic sentiment predictions across positive/negative samples.
- **Integration Tests:**
  - Run the integrated model on a sample dataset and verify the output and its storage.
  - Verify that model performance metrics are logged to MLflow.
  - Ensure Celery analysis task completes without blocking the API thread.
- **End-to-End Tests:**
  - (Covered by P3.2 E2E tests)

### P3.2: Analysis Pipeline Development

- **Unit Tests:**
  - Test individual steps of the analysis pipeline.
- **Integration Tests:**
  - Run the full analysis pipeline on a normalized dataset and verify the processed results in the database.
  - Exercise `/api/v1/analysis` endpoints to confirm job dispatch and status reporting.
- **End-to-End Tests:**
  - Ingest raw data, run normalization and analysis pipelines, and verify the final analyzed data.

## Phase P4: Correlation & Pairing

### P4.1: Candidate Generation for Correlation

- **Unit Tests:**
  - Test candidate generation algorithms with various synthetic datasets.
  - Verify duplicate prevention and scoring thresholds for sentiment-based candidates.
- **Integration Tests:**
  - Run candidate generation on a processed dataset and verify the generated candidates.
  - Ensure `/api/v1/correlation` queues Celery tasks without blocking.
- **End-to-End Tests:**
  - (Covered by P4.2 E2E tests)

### P4.2: Evidence Fusion & Re-weaving

- **Unit Tests:**
  - Test evidence fusion logic with different combinations of evidence.
  - Confirm relationships persist with correct metadata and status transitions.
- **Integration Tests:**
  - Run evidence fusion on generated candidates and verify the updated knowledge graph/correlations in the database.
  - Exercise `/api/v1/correlation/{rawDataId}/fuse` endpoint to confirm queueing and data changes.
- **End-to-End Tests:**
  - Run the full correlation pipeline from processed data to updated knowledge graph.

## Phase P5: Hybrid Search, Retrieval & User Experience

### P5.1: Hybrid Search & Retrieval Implementation

- **Unit Tests:**
  - Test individual search components (e.g., keyword matching, semantic similarity).
  - Validate hybrid tokenizer edge cases and empty query handling.
- **Integration Tests:**
  - Perform searches against a populated database and verify the relevance and ranking of results.
  - Ensure `/api/v1/search` returns scored results and enforces query validation.
- **End-to-End Tests:**
  - Deploy the application, populate with data, and perform various search queries via the UI/API, verifying results.

### P5.2: User Feedback Loop Implementation

- **Unit Tests:**
  - Test the API endpoint handler for `/v1/feedback` with valid and invalid payloads.
  - Validate repository helpers for listing and status updates.
- **Integration Tests:**
  - Submit feedback via the API and verify its correct storage in the database.
  - Exercise feedback listing + status update endpoints.
- **End-to-End Tests:**
  - Submit feedback via the UI (once available) and verify API call and database storage.

### P5.3: Knowledge Base Export to Obsidian

- **Unit Tests:**
  - Test Markdown generation and front matter formatting with mock data.
  - Validate export errors when prerequisites are missing.
- **Integration Tests:**
  - Export a sample knowledge graph to a local directory and verify the generated Obsidian files.
  - Exercise `/api/v1/export/obsidian` enqueue behaviour.
- **End-to-End Tests:**
  - Run the full export process and verify the integrity and correctness of the exported Obsidian vault.

### P5.4: Basic Web Application UI

- **Unit Tests:**
  - Test individual UI components (e.g., search bar, result display) in isolation.
  - Verify root route returns HTML shell.
- **Integration Tests:**
  - Test UI components' interaction with the backend API (e.g., search queries, feedback submission).
- **End-to-End Tests:**
  - Deploy the full application and perform user flows (e.g., search, view results, submit feedback) through the web interface.
