"""NexusKnowledge API Main Application.

This module provides the main FastAPI application for the NexusKnowledge system,
including all API endpoints for chat, knowledge management, and data ingestion.
"""

from __future__ import annotations

import importlib.metadata
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from fastapi.responses import HTMLResponse, JSONResponse, Response
from nexus_knowledge.config import get_settings
from nexus_knowledge.db.repository import (
    get_raw_data,
    get_user_feedback,
    list_correlation_candidates,
    list_feedback,
    update_feedback_status,
)
from nexus_knowledge.db.session import get_session_dependency, get_session_factory
from nexus_knowledge.ingestion import ingest_raw_payload
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

try:
    from nexus_knowledge.integrations.api import router as integrations_router
except ModuleNotFoundError:  # pragma: no cover - optional component
    integrations_router = APIRouter()
from nexus_knowledge.observability import (
    CONTENT_TYPE_LATEST,
    collect_metrics,
    configure_logging,
)
from nexus_knowledge.observability.context import get_correlation_id
from nexus_knowledge.observability.health import liveness_summary, readiness_summary
from nexus_knowledge.observability.middleware import RequestContextMiddleware
from nexus_knowledge.search import hybrid_search
from nexus_knowledge.search.service import SearchError
from nexus_knowledge.tasks import (
    analyze_raw_data_task,
    celery_app,
    export_obsidian_task,
    fuse_correlation_candidates_task,
    generate_correlation_candidates_task,
    normalize_raw_data_task,
    persist_feedback,
)


def _resolve_version() -> str:
    try:
        return importlib.metadata.version("nexus_knowledge")
    except (
        importlib.metadata.PackageNotFoundError
    ):  # pragma: no cover - falls back for editable installs
        return "0.1.0"


configure_logging()


settings = get_settings()
API_VERSION = _resolve_version()
API_PREFIX = settings.api_root

app = FastAPI(
    title="NexusKnowledge API",
    version=API_VERSION,
    openapi_url=f"{API_PREFIX}/openapi.json",
)
app.add_middleware(RequestContextMiddleware)
api_router = APIRouter(prefix=API_PREFIX)


SessionDependency = Annotated[Session, Depends(get_session_dependency)]


UI_HTML = """<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <title>NexusKnowledge</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; background: #f7f8fa; color: #1f2933; }
      h1 { margin-bottom: 0.5rem; }
      section { margin-bottom: 2rem; padding: 1.5rem; background: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.12); }
      label { display: block; font-weight: 600; margin-bottom: 0.5rem; }
      input[type=\"text\"], textarea { width: 100%; padding: 0.5rem; border-radius: 6px; border: 1px solid #cbd5e0; margin-bottom: 0.75rem; }
      button { background: #2563eb; color: #fff; border: none; padding: 0.6rem 1.2rem; border-radius: 6px; cursor: pointer; }
      button:hover { background: #1d4ed8; }
      ul { list-style: none; padding: 0; }
      li { border-bottom: 1px solid #e2e8f0; padding: 0.75rem 0; }
      .meta { font-size: 0.85rem; color: #64748b; }
      .sentiment { font-style: italic; color: #475569; }
      .status { margin-top: 1rem; font-weight: 600; }
      @media (min-width: 768px) { section { max-width: 720px; } }
    </style>
  </head>
  <body>
    <h1>NexusKnowledge</h1>
    <p class=\"meta\">Hybrid search and feedback console.</p>

    <section>
      <h2>Search Conversations</h2>
      <form id=\"search-form\">
        <label for=\"search-query\">Search query</label>
        <input id=\"search-query\" name=\"q\" type=\"text\" placeholder=\"e.g. hybrid search\" required />
        <button type=\"submit\">Search</button>
      </form>
      <div id=\"search-status\" class=\"status\"></div>
      <ul id=\"search-results\"></ul>
    </section>

    <section>
      <h2>Submit Feedback</h2>
      <form id=\"feedback-form\">
        <label for=\"feedback-type\">Feedback type</label>
        <input id=\"feedback-type\" name=\"type\" type=\"text\" value=\"general\" required />
        <label for=\"feedback-message\">Message</label>
        <textarea id=\"feedback-message\" name=\"message\" rows=\"4\" required placeholder=\"Tell us what to improve...\"></textarea>
        <button type=\"submit\">Send feedback</button>
      </form>
      <div id=\"feedback-status\" class=\"status\"></div>
    </section>

    <script>
      const searchForm = document.getElementById('search-form');
      const searchStatus = document.getElementById('search-status');
      const searchResults = document.getElementById('search-results');
      const feedbackForm = document.getElementById('feedback-form');
      const feedbackStatus = document.getElementById('feedback-status');

      searchForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(searchForm);
        const query = formData.get('q');
        searchStatus.textContent = 'Searching...';
        searchResults.innerHTML = '';
        try {
          const response = await fetch(`/api/v1/search?q=${encodeURIComponent(query)}&limit=10`);
          if (!response.ok) throw new Error('Search failed');
          const data = await response.json();
          if (data.length === 0) {
            searchStatus.textContent = 'No results.';
            return;
          }
          searchStatus.textContent = `${data.length} result(s).`;
          data.forEach((item) => {
            const li = document.createElement('li');
            li.innerHTML = `<div><strong>Turn ${item.turnIndex}</strong> — ${item.snippet}</div>` +
              `<div class=\"meta\">Conversation: ${item.conversationId} | Score: ${item.score.toFixed(2)} ${item.sentiment ? `| Sentiment: <span class=\"sentiment\">${item.sentiment}</span>` : ''}</div>`;
            searchResults.appendChild(li);
          });
        } catch (error) {
          console.error(error);
          searchStatus.textContent = 'Something went wrong while searching.';
        }
      });

      feedbackForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(feedbackForm);
        const payload = {
          type: formData.get('type'),
          message: formData.get('message'),
        };
        feedbackStatus.textContent = 'Sending...';
        try {
          const response = await fetch('/api/v1/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          });
          if (!response.ok) throw new Error('Feedback failed');
          feedbackStatus.textContent = 'Thanks! Feedback queued.';
          feedbackForm.reset();
        } catch (error) {
          console.error(error);
          feedbackStatus.textContent = 'Unable to send feedback right now.';
        }
      });
    </script>
  </body>
</html>
"""


class StatusResponse(BaseModel):
    status: str = "operational"
    version: str = API_VERSION


class FeedbackRequest(BaseModel):
    feedback_type: str = Field(..., alias="type", description="Type of feedback.")
    message: str = Field(..., min_length=1, description="Feedback message body.")
    user_id: uuid.UUID | None = Field(
        None,
        alias="userId",
        description="Optional user identifier.",
    )

    model_config = ConfigDict(populate_by_name=True)


class FeedbackResponse(BaseModel):
    message: str = Field(default="Feedback received and being processed.")
    feedback_id: uuid.UUID = Field(..., alias="feedbackId")

    model_config = ConfigDict(populate_by_name=True)


class FeedbackListItem(BaseModel):
    feedback_id: uuid.UUID = Field(..., alias="feedbackId")
    feedback_type: str = Field(..., alias="feedbackType")
    message: str
    status: str
    submitted_at: str = Field(..., alias="submittedAt")
    user_id: uuid.UUID | None = Field(None, alias="userId")

    model_config = ConfigDict(populate_by_name=True)


class FeedbackStatusUpdate(BaseModel):
    status: str = Field(..., description="Updated feedback status.")


class IngestionRequest(BaseModel):
    source_type: str = Field(
        ...,
        alias="sourceType",
        description="Identifier for the data source.",
    )
    content: Any = Field(..., description="Raw payload to ingest.")
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata for the payload.",
    )
    source_id: str | None = Field(
        default=None,
        alias="sourceId",
        description="Provider-specific conversation identifier.",
    )

    model_config = ConfigDict(populate_by_name=True)


class IngestionResponse(BaseModel):
    message: str = Field(default="Ingestion accepted and normalization scheduled.")
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")

    model_config = ConfigDict(populate_by_name=True)


class IngestionStatusResponse(BaseModel):
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")
    status: str

    model_config = ConfigDict(populate_by_name=True)


class AnalysisRequest(BaseModel):
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")

    model_config = ConfigDict(populate_by_name=True)


class AnalysisResponse(BaseModel):
    message: str = Field(default="Analysis queued for execution.")
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")

    model_config = ConfigDict(populate_by_name=True)


class AnalysisStatusResponse(BaseModel):
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")
    status: str

    model_config = ConfigDict(populate_by_name=True)


class CorrelationRequest(BaseModel):
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")

    model_config = ConfigDict(populate_by_name=True)


class CorrelationQueuedResponse(BaseModel):
    message: str = Field(default="Correlation candidate generation queued.")
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")

    model_config = ConfigDict(populate_by_name=True)


class CorrelationCandidateResponse(BaseModel):
    id: uuid.UUID
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")
    source_entity_id: uuid.UUID = Field(..., alias="sourceEntityId")
    target_entity_id: uuid.UUID = Field(..., alias="targetEntityId")
    score: float
    status: str
    rationale: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class CorrelationFusionResponse(BaseModel):
    message: str = Field(default="Correlation fusion queued.")
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")

    model_config = ConfigDict(populate_by_name=True)


class SearchResult(BaseModel):
    turn_id: uuid.UUID = Field(..., alias="turnId")
    conversation_id: uuid.UUID = Field(..., alias="conversationId")
    turn_index: int = Field(..., alias="turnIndex")
    timestamp: str
    snippet: str
    score: float
    sentiment: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ObsidianExportRequest(BaseModel):
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")
    export_path: str = Field(..., alias="exportPath")

    model_config = ConfigDict(populate_by_name=True)


class ObsidianExportResponse(BaseModel):
    message: str = Field(default="Export queued.")
    raw_data_id: uuid.UUID = Field(..., alias="rawDataId")

    model_config = ConfigDict(populate_by_name=True)


@api_router.get("/status", response_model=StatusResponse, tags=["System"])
async def get_status() -> StatusResponse:
    """Return the API's operational status."""
    return StatusResponse()


@api_router.get("/health/live", tags=["System"])
async def get_liveness() -> dict[str, str]:
    """Return liveness information for Kubernetes-style probes."""
    return liveness_summary()


@api_router.get("/health/ready", tags=["System"])
async def get_readiness() -> JSONResponse:
    """Return readiness information including dependency health."""
    summary = readiness_summary(
        session_factory=get_session_factory(),
        redis_url=settings.redis_url,
        celery_app=celery_app,
    )
    return JSONResponse(
        content={"status": summary["status"], "checks": summary["checks"]},
        status_code=summary["http_status"],
    )


@api_router.get("/metrics", tags=["System"])
async def get_metrics() -> Response:
    """Expose Prometheus metrics for scraping."""
    payload = collect_metrics()
    return Response(
        content=payload,
        media_type=CONTENT_TYPE_LATEST,
        headers={"Cache-Control": "no-store"},
    )


@api_router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Feedback"],
)
async def submit_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    """Queue feedback persistence and respond immediately."""
    feedback_id = uuid.uuid4()
    task = persist_feedback.delay(
        str(feedback_id),
        {
            "feedback_type": payload.feedback_type,
            "message": payload.message,
            "user_id": str(payload.user_id) if payload.user_id else None,
        },
        correlation_id=get_correlation_id(),
    )

    if not task.id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to queue feedback persistence",
        )

    # Optimistically confirm the feedback will be available when the task completes.
    return FeedbackResponse(feedback_id=feedback_id)


@api_router.get(
    "/feedback/{feedback_id}",
    response_model=FeedbackResponse,
    tags=["Feedback"],
)
async def get_feedback_status(
    feedback_id: uuid.UUID,
    session: SessionDependency,
) -> FeedbackResponse:
    """Retrieve persisted feedback details after the Celery task completes."""
    record = get_user_feedback(session, feedback_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    return FeedbackResponse(feedback_id=record.id, message=record.message)


@api_router.get(
    "/feedback",
    response_model=list[FeedbackListItem],
    tags=["Feedback"],
)
async def list_feedback_items(
    status: str | None = Query(None, description="Filter by feedback status."),
    limit: int = Query(50, ge=1, le=200),
    *,
    session: SessionDependency,
) -> list[FeedbackListItem]:
    """Return stored feedback items."""
    records = list_feedback(session, status=status, limit=limit)
    return [
        FeedbackListItem(
            feedback_id=record.id,
            feedback_type=record.feedback_type,
            message=record.message,
            status=record.status,
            submitted_at=record.submitted_at.isoformat(),
            user_id=record.user_id,
        )
        for record in records
    ]


@api_router.patch(
    "/feedback/{feedback_id}",
    response_model=FeedbackListItem,
    tags=["Feedback"],
)
async def update_feedback(
    feedback_id: uuid.UUID,
    payload: FeedbackStatusUpdate,
    session: SessionDependency,
) -> FeedbackListItem:
    """Update feedback status for triage workflows."""
    record = update_feedback_status(session, feedback_id, status=payload.status)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    return FeedbackListItem(
        feedback_id=record.id,
        feedback_type=record.feedback_type,
        message=record.message,
        status=record.status,
        submitted_at=record.submitted_at.isoformat(),
        user_id=record.user_id,
    )


@api_router.post(
    "/ingest",
    response_model=IngestionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Ingestion"],
)
async def ingest_payload(
    payload: IngestionRequest,
    session: SessionDependency,
) -> IngestionResponse:
    """Persist a raw payload and schedule normalization via Celery."""
    raw_data_id = ingest_raw_payload(
        session,
        source_type=payload.source_type,
        content=payload.content,
        metadata=payload.metadata,
        source_id=payload.source_id,
    )
    session.commit()
    normalize_raw_data_task.delay(str(raw_data_id), correlation_id=get_correlation_id())
    return IngestionResponse(raw_data_id=raw_data_id)


@api_router.get(
    "/ingest/{raw_data_id}",
    response_model=IngestionStatusResponse,
    tags=["Ingestion"],
)
async def get_ingestion_status(
    raw_data_id: uuid.UUID,
    session: SessionDependency,
) -> IngestionStatusResponse:
    """Return the current status of an ingested payload."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion not found",
        )
    return IngestionStatusResponse(raw_data_id=record.id, status=record.status)


@api_router.post(
    "/analysis",
    response_model=AnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Analysis"],
)
async def queue_analysis(
    payload: AnalysisRequest,
    session: SessionDependency,
) -> AnalysisResponse:
    """Queue an analysis job for a previously normalized payload."""
    record = get_raw_data(session, payload.raw_data_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion not found",
        )
    if record.status not in {"NORMALIZED", "ANALYZED"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Raw data must be normalized before analysis",
        )

    analyze_raw_data_task.delay(
        str(payload.raw_data_id),
        correlation_id=get_correlation_id(),
    )
    return AnalysisResponse(raw_data_id=payload.raw_data_id)


@api_router.get(
    "/analysis/{raw_data_id}",
    response_model=AnalysisStatusResponse,
    tags=["Analysis"],
)
async def get_analysis_status(
    raw_data_id: uuid.UUID,
    session: SessionDependency,
) -> AnalysisStatusResponse:
    """Return the status of the analysis job for the specified payload."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis target not found",
        )
    return AnalysisStatusResponse(raw_data_id=record.id, status=record.status)


@api_router.post(
    "/correlation",
    response_model=CorrelationQueuedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Correlation"],
)
async def queue_correlation(
    payload: CorrelationRequest,
    session: SessionDependency,
) -> CorrelationQueuedResponse:
    """Queue correlation candidate generation after analysis."""
    record = get_raw_data(session, payload.raw_data_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion not found",
        )
    if record.status not in {
        "ANALYZED",
        "CORRELATION_GENERATED",
        "CORRELATION_SKIPPED",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis must complete before correlation",
        )

    generate_correlation_candidates_task.delay(
        str(payload.raw_data_id),
        correlation_id=get_correlation_id(),
    )
    return CorrelationQueuedResponse(raw_data_id=payload.raw_data_id)


@api_router.get(
    "/correlation/{raw_data_id}",
    response_model=list[CorrelationCandidateResponse],
    tags=["Correlation"],
)
async def list_correlation(
    raw_data_id: uuid.UUID,
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Optional status filter (e.g. PENDING, CONFIRMED).",
    ),
    limit: int = Query(100, ge=1, le=500),
    *,
    session: SessionDependency,
) -> list[CorrelationCandidateResponse]:
    """Return generated correlation candidates for the given payload."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correlation target not found",
        )

    candidates = list_correlation_candidates(
        session,
        raw_data_id,
        status=status_filter,
        limit=limit,
    )
    return [
        CorrelationCandidateResponse(
            id=candidate.id,
            raw_data_id=candidate.raw_data_id,
            source_entity_id=candidate.source_entity_id,
            target_entity_id=candidate.target_entity_id,
            score=candidate.score,
            status=candidate.status,
            rationale=candidate.rationale,
        )
        for candidate in candidates
    ]


@api_router.post(
    "/correlation/{raw_data_id}/fuse",
    response_model=CorrelationFusionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Correlation"],
)
async def fuse_correlation(
    raw_data_id: uuid.UUID,
    session: SessionDependency,
) -> CorrelationFusionResponse:
    """Queue evidence fusion and relationship creation for a dataset."""
    record = get_raw_data(session, raw_data_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correlation target not found",
        )
    if record.status not in {"CORRELATION_GENERATED", "CORRELATED", "ANALYZED"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Correlation candidates must be generated first",
        )

    fuse_correlation_candidates_task.delay(
        str(raw_data_id),
        correlation_id=get_correlation_id(),
    )
    return CorrelationFusionResponse(raw_data_id=raw_data_id)


@api_router.get(
    "/search",
    response_model=list[SearchResult],
    tags=["Search"],
)
async def search_knowledge(
    q: str = Query(..., min_length=1, description="Search query string."),
    limit: int = Query(10, ge=1, le=50),
    *,
    session: SessionDependency,
) -> list[SearchResult]:
    """Perform hybrid search over conversation turns."""
    try:
        results = hybrid_search(session, q, limit=limit)
    except SearchError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return [
        SearchResult(
            turnId=result["turn_id"],
            conversationId=result["conversation_id"],
            turnIndex=result["turn_index"],
            timestamp=result["timestamp"],
            snippet=result["snippet"],
            score=result["score"],
            sentiment=result.get("sentiment"),
        )
        for result in results
    ]


@api_router.post(
    "/export/obsidian",
    response_model=ObsidianExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Export"],
)
async def queue_obsidian_export(
    payload: ObsidianExportRequest,
    session: SessionDependency,
) -> ObsidianExportResponse:
    """Queue an Obsidian export task for the provided dataset."""
    record = get_raw_data(session, payload.raw_data_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingestion not found",
        )

    export_obsidian_task.delay(
        str(payload.raw_data_id),
        payload.export_path,
        correlation_id=get_correlation_id(),
    )
    return ObsidianExportResponse(raw_data_id=payload.raw_data_id)


app.include_router(api_router)
app.include_router(integrations_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def ui_root() -> HTMLResponse:
    """Serve the lightweight UI shell."""
    return HTMLResponse(content=UI_HTML)
