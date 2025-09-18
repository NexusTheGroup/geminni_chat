# API Surface: NexusKnowledge Project (OpenAPI 3.0 Sketch)

This document outlines the OpenAPI 3.0 specification sketch for the NexusKnowledge backend API, including core endpoints and the new `/v1/feedback` endpoint.

```yaml
openapi: 3.0.0
info:
  title: NexusKnowledge API
  version: 1.0.0
  description: API for managing and synthesizing AI conversations and knowledge.
servers:
  - url: http://localhost:8000/api/v1
    description: Local Development Server

tags:
  - name: System
    description: Core system operations
  - name: Feedback
    description: User feedback operations
  - name: Ingestion
    description: Data ingestion operations
  - name: Analysis
    description: Data analysis and modeling operations
  - name: Correlation
    description: Knowledge correlation and pairing operations
  - name: Search
    description: Hybrid search and retrieval operations
  - name: Export
    description: Data export operations

paths:
  /status:
    get:
      tags:
        - System
      summary: Get API status
      description: Returns the current status of the API.
      responses:
        '200':
          description: API is operational.
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "operational"
                  version:
                    type: string
                    example: "1.0.0"

  /feedback:
    get:
      tags:
        - Feedback
      summary: List feedback submissions
      description: Returns stored feedback entries optionally filtered by status.
      parameters:
        - in: query
          name: status
          schema:
            type: string
          required: false
          description: Optional status filter (e.g., NEW, IN_PROGRESS, REVIEWED).
        - in: query
          name: limit
          schema:
            type: integer
            default: 50
          required: false
          description: Maximum number of items to return.
      responses:
        '200':
          description: Feedback list.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/FeedbackListItem'
    post:
      tags:
        - Feedback
      summary: Submit user feedback
      description: Allows users to submit feedback about the system.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FeedbackInput'
      responses:
        '202':
          description: Feedback accepted for processing.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FeedbackResponse'
        '400':
          description: Invalid feedback data provided.
  /feedback/{feedbackId}:
    get:
      tags:
        - Feedback
      summary: Retrieve feedback details
      description: Returns a single feedback entry.
      parameters:
        - in: path
          name: feedbackId
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Feedback entry.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FeedbackResponse'
        '404':
          description: Feedback not found.
    patch:
      tags:
        - Feedback
      summary: Update feedback status
      description: Updates the status of an existing feedback entry.
      parameters:
        - in: path
          name: feedbackId
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FeedbackStatusInput'
      responses:
        '200':
          description: Updated feedback entry.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FeedbackListItem'
        '404':
          description: Feedback not found.
  /feedback/{feedbackId}:
    get:
      tags:
        - Feedback
      summary: Retrieve persisted feedback details
      description: Returns the stored feedback payload once the asynchronous task has completed.
      parameters:
        - in: path
          name: feedbackId
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Matching feedback record.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FeedbackResponse'
        '404':
          description: Feedback not found.

  /ingest:
    post:
      tags:
        - Ingestion
      summary: Ingest new data
      description: Endpoint for ingesting raw conversation data or other knowledge sources.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IngestionInput'
      responses:
        '202':
          description: Data ingestion initiated and normalization scheduled.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IngestionResponse'
  /ingest/{rawDataId}:
    get:
      tags:
        - Ingestion
      summary: Get ingestion status
      description: Returns the processing status for a previously ingested payload.
      parameters:
        - in: path
          name: rawDataId
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Status payload.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IngestionStatus'
        '404':
          description: Ingestion not found.

  /analysis:
    post:
      tags:
        - Analysis
      summary: Trigger data analysis
      description: Initiates the analysis pipeline for newly ingested or updated data.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AnalysisInput'
      responses:
        '202':
          description: Analysis task queued.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnalysisQueued'

  /analysis/{rawDataId}:
    get:
      tags:
        - Analysis
      summary: Get analysis status
      description: Returns the latest status for the requested analysis job.
      parameters:
        - in: path
          name: rawDataId
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Analysis status payload.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnalysisStatus'
        '404':
          description: Analysis target not found.

  /correlation:
    post:
      tags:
        - Correlation
      summary: Generate correlation candidates
      description: Queues candidate generation for previously analyzed datasets.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CorrelationInput'
      responses:
        '202':
          description: Correlation task queued.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CorrelationQueued'
  /correlation/{rawDataId}:
    get:
      tags:
        - Correlation
      summary: List correlation candidates
      description: Returns generated correlation candidates for an analyzed dataset.
      parameters:
        - in: path
          name: rawDataId
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Correlation candidate list.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CorrelationCandidate'
        '404':
          description: Correlation target not found.

  /search:
    get:
      tags:
        - Search
      summary: Search knowledge base
      description: Performs a hybrid search across the knowledge base.
      parameters:
        - in: query
          name: q
          schema:
            type: string
          required: true
          description: Search query string.
        - in: query
          name: limit
          schema:
            type: integer
            default: 10
          description: Maximum number of results to return.
      responses:
        '200':
          description: Search results.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/SearchResult'

  /export/obsidian:
    post:
      tags:
        - Export
      summary: Export knowledge to Obsidian format
      description: Exports synthesized knowledge into a format compatible with Obsidian.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                exportPath:
                  type: string
                  description: The local path where Obsidian files should be exported.
      responses:
        '202':
          description: Export task queued.

components:
  schemas:
    FeedbackInput:
      type: object
      required:
        - type
        - message
      properties:
        type:
          type: string
          enum: [bug, feature_request, general]
          description: Type of feedback.
        message:
          type: string
          description: The feedback message.
        userId:
          type: string
          format: uuid
          nullable: true
          description: Optional user ID if authenticated.
    FeedbackListItem:
      type: object
      properties:
        feedbackId:
          type: string
          format: uuid
        feedbackType:
          type: string
        message:
          type: string
        status:
          type: string
        submittedAt:
          type: string
          format: date-time
        userId:
          type: string
          format: uuid
          nullable: true
    FeedbackStatusInput:
      type: object
      required:
        - status
      properties:
        status:
          type: string
          description: New feedback status value.
    FeedbackResponse:
      type: object
      properties:
        message:
          type: string
          example: Feedback received and being processed.
        feedbackId:
          type: string
          format: uuid
          example: a1b2c3d4-e5f6-7890-1234-567890abcdef

    IngestionInput:
      type: object
      required:
        - sourceType
        - content
      properties:
        sourceType:
          type: string
          description: Type of the data source (e.g., "deepseek_chat", "deepthink", "grok_chat").
        content:
          type: string
          description: The raw content to be ingested.
        metadata:
          type: object
          additionalProperties: true
          description: Optional metadata associated with the content.
    IngestionResponse:
      type: object
      properties:
        message:
          type: string
          example: Ingestion accepted and normalization scheduled.
        rawDataId:
          type: string
          format: uuid
    IngestionStatus:
      type: object
      properties:
        rawDataId:
          type: string
          format: uuid
        status:
          type: string
          example: NORMALIZED
    AnalysisInput:
      type: object
      required:
        - rawDataId
      properties:
        rawDataId:
          type: string
          format: uuid
    AnalysisQueued:
      type: object
      properties:
        message:
          type: string
          example: Analysis queued for execution.
        rawDataId:
          type: string
          format: uuid
    AnalysisStatus:
      type: object
      properties:
        rawDataId:
          type: string
          format: uuid
        status:
          type: string
          example: ANALYZED
    CorrelationInput:
      type: object
      required:
        - rawDataId
      properties:
        rawDataId:
          type: string
          format: uuid
    CorrelationQueued:
      type: object
      properties:
        message:
          type: string
          example: Correlation candidate generation queued.
        rawDataId:
          type: string
          format: uuid
    CorrelationCandidate:
      type: object
      properties:
        id:
          type: string
          format: uuid
        rawDataId:
          type: string
          format: uuid
        sourceEntityId:
          type: string
          format: uuid
        targetEntityId:
          type: string
          format: uuid
        score:
          type: number
          format: float
        status:
          type: string
          example: PENDING
        rationale:
          type: string

    SearchResult:
      type: object
      properties:
        turnId:
          type: string
          format: uuid
        conversationId:
          type: string
          format: uuid
        turnIndex:
          type: integer
        timestamp:
          type: string
          format: date-time
        snippet:
          type: string
        score:
          type: number
          format: float
        sentiment:
          type: string
          nullable: true
```
