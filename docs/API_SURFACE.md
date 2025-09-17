openapi: 3.0.0
info:
  title: NexusKnowledge API
  version: 1.0.0
  description: Local-first API for NexusKnowledge AI conversation management system.
servers:
  - url: http://localhost:8000/api/v1
    description: Local Development Server
paths:
  /health:
    get:
      summary: Health Check
      responses:
        '200':
          description: API is healthy
  /feedback:
    post:
      summary: Submit User Feedback
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FeedbackInput'
      responses:
        '201':
          description: Feedback submitted successfully
        '400':
          description: Invalid input
  /conversations:
    get:
      summary: Get All Conversations
      parameters:
        - in: query
          name: limit
          schema: { type: integer, default: 10 }
          description: Maximum number of conversations to return.
        - in: query
          name: offset
          schema: { type: integer, default: 0 }
          description: Number of conversations to skip.
      responses:
        '200':
          description: List of conversations
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Conversation'
  /conversations/{conversation_id}:
    get:
      summary: Get Conversation by ID
      parameters:
        - in: path
          name: conversation_id
          required: true
          schema: { type: string }
          description: Unique identifier of the conversation.
      responses:
        '200':
          description: Conversation details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Conversation'
        '404':
          description: Conversation not found
  /search:
    get:
      summary: Hybrid Search
      parameters:
        - in: query
          name: query
          required: true
          schema: { type: string }
          description: Search query string.
        - in: query
          name: type
          schema: { type: string, enum: [keyword, semantic, hybrid], default: hybrid }
          description: Type of search to perform.
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/SearchResult'
  /correlate:
    post:
      summary: Correlate Conversations/Messages
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                conversation_id:
                  type: string
                  description: ID of the conversation to correlate.
                message_id:
                  type: string
                  description: ID of the message to correlate.
              oneOf:
                - required: [conversation_id]
                - required: [message_id]
      responses:
        '200':
          description: List of correlated items
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/CorrelationResult'
  /export/obsidian:
    post:
      summary: Export to Obsidian Format
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                conversation_ids:
                  type: array
                  items:
                    type: string
                  description: List of conversation IDs to export.
                include_embeddings:
                  type: boolean
                  default: false
                  description: Whether to include embedding data in the export.
      responses:
        '200':
          description: Export successful, returns file path or content
          content:
            application/json:
              schema:
                type: object
                properties:
                  file_path:
                    type: string
                    description: Path to the exported file.
        '400':
          description: Invalid request
components:
  schemas:
    FeedbackInput:
      type: object
      required: [type, message]
      properties:
        type:
          type: string
          enum: [bug, feature_request, general]
          description: Type of feedback.
        message:
          type: string
          description: The feedback message.
        context:
          type: string
          nullable: true
          description: Optional context or additional details for the feedback.
    Conversation:
      type: object
      properties:
        id:
          type: string
          description: Unique identifier for the conversation.
        title:
          type: string
          description: Title or summary of the conversation.
        created_at:
          type: string
          format: date-time
          description: Timestamp when the conversation was created.
        updated_at:
          type: string
          format: date-time
          description: Timestamp when the conversation was last updated.
        messages:
          type: array
          items:
            $ref: '#/components/schemas/Message'
          description: List of messages in the conversation.
    Message:
      type: object
      properties:
        id:
          type: string
          description: Unique identifier for the message.
        conversation_id:
          type: string
          description: ID of the conversation this message belongs to.
        role:
          type: string
          enum: [user, assistant]
          description: Role of the speaker (user or assistant).
        content:
          type: string
          description: The content of the message.
        timestamp:
          type: string
          format: date-time
          description: Timestamp when the message was sent.
        embedding:
          type: array
          items:
            type: number
          nullable: true
          description: Optional vector embedding of the message content.
    SearchResult:
      type: object
      properties:
        id:
          type: string
          description: ID of the found item (conversation or message).
        type:
          type: string
          enum: [conversation, message]
          description: Type of the found item.
        title:
          type: string
          nullable: true
          description: Title or excerpt of the found item.
        excerpt:
          type: string
          description: A snippet of the content matching the search query.
        score:
          type: number
          format: float
          description: Relevance score of the search result.
    CorrelationResult:
      type: object
      properties:
        id:
          type: string
          description: ID of the correlated item (conversation or message).
        type:
          type: string
          enum: [conversation, message]
          description: Type of the correlated item.
        title:
          type: string
          nullable: true
          description: Title or excerpt of the correlated item.
        similarity_score:
          type: number
          format: float
          description: Similarity score with the queried item.
