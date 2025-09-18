from __future__ import annotations

import importlib
import uuid

from fastapi.testclient import TestClient
from nexus_knowledge.analysis import run_analysis_for_raw_data
from nexus_knowledge.db import repository
from nexus_knowledge.db.session import reset_session_factory
from nexus_knowledge.ingestion import ingest_raw_payload
from nexus_knowledge.ingestion.service import normalize_raw_data


def test_status_endpoint(sqlite_db) -> None:
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)
    client = TestClient(module.app)
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data


def test_feedback_submission_enqueues_task(sqlite_db, monkeypatch) -> None:
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    calls = {}

    class DummyResult:
        def __init__(self):
            self.id = "task-123"

    def fake_delay(feedback_id: str, payload: dict) -> DummyResult:
        calls["feedback_id"] = feedback_id
        calls["payload"] = payload
        return DummyResult()

    monkeypatch.setattr(module.persist_feedback, "delay", fake_delay)

    client = TestClient(module.app)
    response = client.post(
        "/api/v1/feedback",
        json={"type": "general", "message": "Great work!"},
    )
    assert response.status_code == 202
    body = response.json()
    assert body["feedbackId"] == calls["feedback_id"]
    assert body["message"] == "Feedback received and being processed."
    assert calls["payload"]["feedback_type"] == "general"


def test_feedback_retrieval(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    feedback_id = uuid.uuid4()
    with session_factory.begin() as session:
        repository.create_user_feedback(
            session,
            feedback_id=feedback_id,
            feedback_type="general",
            message="Great feature",
        )

    client = TestClient(module.app)
    response = client.get(f"/api/v1/feedback/{feedback_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["feedbackId"] == str(feedback_id)
    assert data["message"] == "Great feature"


def test_feedback_listing_and_status_update(sqlite_db, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    class DummyResult:
        id = "task"

    def fake_delay(feedback_id: str, payload: dict[str, str]) -> DummyResult:
        with session_factory.begin() as session:
            repository.create_user_feedback(
                session,
                feedback_id=uuid.UUID(feedback_id),
                feedback_type=payload["feedback_type"],
                message=payload["message"],
                user_id=(
                    uuid.UUID(payload["user_id"]) if payload.get("user_id") else None
                ),
            )
        return DummyResult()

    monkeypatch.setattr(module.persist_feedback, "delay", fake_delay)

    client = TestClient(module.app)
    response = client.post(
        "/api/v1/feedback",
        json={"type": "bug", "message": "Broken"},
    )
    feedback_id = response.json()["feedbackId"]

    with session_factory() as session:
        item_id = feedback_id
        # ensure record exists
        record = repository.get_user_feedback(session, uuid.UUID(item_id))
        assert record is not None

    list_response = client.get("/api/v1/feedback")
    assert list_response.status_code == 200
    assert any(item["feedbackId"] == feedback_id for item in list_response.json())

    patch_response = client.patch(
        f"/api/v1/feedback/{feedback_id}",
        json={"status": "REVIEWED"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "REVIEWED"


def test_ingestion_endpoint_triggers_normalization(sqlite_db, monkeypatch) -> None:
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    captured = {}

    class DummyResult:
        def __init__(self):
            self.id = "normalize-task-1"

    def fake_delay(raw_data_id: str) -> DummyResult:
        captured["raw_data_id"] = raw_data_id
        return DummyResult()

    monkeypatch.setattr(module.normalize_raw_data_task, "delay", fake_delay)

    client = TestClient(module.app)
    response = client.post(
        "/api/v1/ingest",
        json={
            "sourceType": "deepseek_chat",
            "sourceId": "ingest-1",
            "content": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello",
                        "timestamp": "2025-01-01T00:00:00Z",
                    },
                ],
            },
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert data["rawDataId"] == captured["raw_data_id"]


def test_ingestion_status_endpoint(sqlite_db, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    monkeypatch.setattr(module.normalize_raw_data_task, "delay", lambda raw_id: None)

    client = TestClient(module.app)
    payload = {
        "sourceType": "deepseek_chat",
        "content": {
            "source_id": "ingest-2",
            "messages": [
                {"role": "user", "content": "Hi", "timestamp": "2025-01-01T00:00:00Z"},
            ],
        },
    }

    response = client.post("/api/v1/ingest", json=payload)
    raw_data_id = response.json()["rawDataId"]

    # Manually set status to NORMALIZED for deterministic response
    with session_factory.begin() as session:
        repository.update_raw_data_status(
            session,
            uuid.UUID(raw_data_id),
            status="NORMALIZED",
        )

    status_response = client.get(f"/api/v1/ingest/{raw_data_id}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "NORMALIZED"


def test_analysis_endpoint_monkeypatched(sqlite_db, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    monkeypatch.setattr(module.normalize_raw_data_task, "delay", lambda raw_id: None)
    monkeypatch.setattr(module.analyze_raw_data_task, "delay", lambda raw_id: None)
    monkeypatch.setattr(
        module.generate_correlation_candidates_task,
        "delay",
        lambda raw_id: None,
    )

    client = TestClient(module.app)
    ingest_resp = client.post(
        "/api/v1/ingest",
        json={
            "sourceType": "deepseek_chat",
            "content": {
                "source_id": "analysis-api",
                "messages": [
                    {
                        "role": "user",
                        "content": "I love this",
                        "timestamp": "2025-01-01T00:00:00Z",
                    },
                ],
            },
        },
    )
    raw_data_id = ingest_resp.json()["rawDataId"]

    # Mark as normalized to satisfy precondition
    with session_factory.begin() as session:
        repository.update_raw_data_status(
            session,
            uuid.UUID(raw_data_id),
            status="NORMALIZED",
        )

    analysis_resp = client.post(
        "/api/v1/analysis",
        json={"rawDataId": raw_data_id},
    )
    assert analysis_resp.status_code == 202
    assert analysis_resp.json()["rawDataId"] == raw_data_id


def test_analysis_status_endpoint(sqlite_db, monkeypatch, tmp_path) -> None:
    _, session_factory, _ = sqlite_db
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    monkeypatch.setattr(module.normalize_raw_data_task, "delay", lambda raw_id: None)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())
    monkeypatch.setattr(
        module.generate_correlation_candidates_task,
        "delay",
        lambda raw_id: None,
    )
    client = TestClient(module.app)

    ingest_resp = client.post(
        "/api/v1/ingest",
        json={
            "sourceType": "deepseek_chat",
            "content": {
                "source_id": "analysis-status",
                "messages": [
                    {
                        "role": "user",
                        "content": "bad experience",
                        "timestamp": "2025-01-01T00:00:00Z",
                    },
                ],
            },
        },
    )
    raw_data_id = ingest_resp.json()["rawDataId"]

    with session_factory.begin() as session:
        normalize_raw_data(session, uuid.UUID(raw_data_id))
        run_analysis_for_raw_data(session, uuid.UUID(raw_data_id))

    status_resp = client.get(f"/api/v1/analysis/{raw_data_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "ANALYZED"


def test_correlation_endpoints(sqlite_db, monkeypatch, tmp_path) -> None:
    _, session_factory, _ = sqlite_db
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    monkeypatch.setattr(module.normalize_raw_data_task, "delay", lambda raw_id: None)
    monkeypatch.setattr(module.analyze_raw_data_task, "delay", lambda raw_id: None)
    monkeypatch.setattr(
        module.generate_correlation_candidates_task,
        "delay",
        lambda raw_id: None,
    )
    monkeypatch.setattr(
        module.fuse_correlation_candidates_task,
        "delay",
        lambda raw_id: None,
    )
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    client = TestClient(module.app)

    ingest_resp = client.post(
        "/api/v1/ingest",
        json={
            "sourceType": "deepseek_chat",
            "content": {
                "source_id": "correlation-api",
                "messages": [
                    {
                        "role": "user",
                        "content": "I love this",
                        "timestamp": "2025-01-01T00:00:00Z",
                    },
                    {
                        "role": "assistant",
                        "content": "That is great",
                        "timestamp": "2025-01-01T00:00:05Z",
                    },
                ],
            },
        },
    )
    raw_data_id = ingest_resp.json()["rawDataId"]

    with session_factory.begin() as session:
        normalize_raw_data(session, uuid.UUID(raw_data_id))
        run_analysis_for_raw_data(session, uuid.UUID(raw_data_id))

    # Queue correlation (task monkeypatched)
    response = client.post("/api/v1/correlation", json={"rawDataId": raw_data_id})
    assert response.status_code == 202

    # Materialize candidates for GET endpoint
    module.generate_correlation_candidates_task(str(raw_data_id))

    # Monkeypatch to no-op for GET (should already exist)
    candidates_resp = client.get(f"/api/v1/correlation/{raw_data_id}")
    assert candidates_resp.status_code == 200
    assert candidates_resp.json()

    # Queue fusion and ensure request accepted
    fuse_resp = client.post(f"/api/v1/correlation/{raw_data_id}/fuse")
    assert fuse_resp.status_code == 202


def test_search_endpoint(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    monkeypatch.setattr(module.normalize_raw_data_task, "delay", lambda raw_id: None)
    client = TestClient(module.app)

    payload = {
        "sourceType": "deepseek_chat",
        "content": {
            "source_id": "search-api",
            "messages": [
                {
                    "role": "user",
                    "content": "Hybrid search is great",
                    "timestamp": "2025-01-01T00:00:00Z",
                },
                {
                    "role": "assistant",
                    "content": "Indeed, search combines signals",
                    "timestamp": "2025-01-01T00:00:05Z",
                },
            ],
        },
    }

    ingest_resp = client.post("/api/v1/ingest", json=payload)
    raw_data_id = ingest_resp.json()["rawDataId"]

    with session_factory.begin() as session:
        normalize_raw_data(session, uuid.UUID(raw_data_id))

    response = client.get("/api/v1/search", params={"q": "hybrid search", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert data
    assert "snippet" in data[0]


def test_obsidian_export_endpoint(sqlite_db, tmp_path, monkeypatch) -> None:
    _, session_factory, _ = sqlite_db
    reset_session_factory()
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)

    calls = []
    monkeypatch.setenv("MLFLOW_TRACKING_URI", (tmp_path / "mlruns").as_uri())

    def fake_delay(raw_id: str, path: str):
        calls.append((raw_id, path))

    monkeypatch.setattr(module.export_obsidian_task, "delay", fake_delay, raising=False)
    client = TestClient(module.app)

    with session_factory.begin() as session:
        raw_id = ingest_raw_payload(
            session,
            source_type="deepseek_chat",
            content={
                "messages": [
                    {
                        "role": "user",
                        "content": "Export me",
                        "timestamp": "2025-01-01T00:00:00Z",
                    },
                    {
                        "role": "assistant",
                        "content": "Here is data",
                        "timestamp": "2025-01-01T00:00:05Z",
                    },
                ],
            },
        )
        normalize_raw_data(session, raw_id)
        run_analysis_for_raw_data(session, raw_id)

    raw_data_id = str(raw_id)

    response = client.post(
        "/api/v1/export/obsidian",
        json={"rawDataId": raw_data_id, "exportPath": str(tmp_path / "vault")},
    )
    assert response.status_code == 202
    assert calls
