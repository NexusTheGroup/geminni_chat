from __future__ import annotations

import uuid

from nexus_knowledge.db.repository import get_user_feedback
from nexus_knowledge.tasks import persist_feedback


def test_persist_feedback_task(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db

    feedback_id = uuid.uuid4()
    payload = {"feedback_type": "bug", "message": "Button broken", "user_id": None}

    result = persist_feedback.apply(args=(str(feedback_id), payload)).get()
    assert result == str(feedback_id)

    with session_factory() as session:
        stored = get_user_feedback(session, feedback_id)
        assert stored is not None
        assert stored.message == "Button broken"
        assert stored.feedback_type == "bug"
