from __future__ import annotations

import importlib

from fastapi.testclient import TestClient


def test_ui_root_served(sqlite_db) -> None:
    module = importlib.import_module("nexus_knowledge.api.main")
    module = importlib.reload(module)
    client = TestClient(module.app)

    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "<!DOCTYPE html>" in body
    assert "Search Conversations" in body
