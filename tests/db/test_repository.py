from __future__ import annotations

import uuid

from nexus_knowledge.db import repository


def test_create_and_fetch_raw_data(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db
    with session_factory.begin() as session:
        record = repository.create_raw_data(
            session,
            source_type="deepseek_chat",
            content='{"messages": []}',
            metadata={"notes": "test"},
        )
        fetched = repository.get_raw_data(session, record.id)
        assert fetched is not None
        assert fetched.content == record.content


def test_create_and_fetch_user_feedback(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db
    feedback_id = uuid.uuid4()
    with session_factory.begin() as session:
        repository.create_user_feedback(
            session,
            feedback_id=feedback_id,
            feedback_type="general",
            message="Great job!",
        )

    with session_factory() as session:
        fetched = repository.get_user_feedback(session, feedback_id)
        assert fetched is not None
        assert fetched.message == "Great job!"


def test_list_and_update_feedback(sqlite_db) -> None:
    _, session_factory, _ = sqlite_db
    first_id = uuid.uuid4()
    second_id = uuid.uuid4()
    with session_factory.begin() as session:
        repository.create_user_feedback(
            session,
            feedback_id=first_id,
            feedback_type="bug",
            message="Issue 1",
        )
        repository.create_user_feedback(
            session,
            feedback_id=second_id,
            feedback_type="general",
            message="Thoughts",
            status="REVIEWED",
        )

    with session_factory() as session:
        all_feedback = repository.list_feedback(session)
        assert len(all_feedback) >= 2
        reviewed = repository.list_feedback(session, status="REVIEWED")
        assert len(reviewed) == 1
        updated = repository.update_feedback_status(
            session, first_id, status="IN_PROGRESS",
        )
        assert updated is not None
        assert updated.status == "IN_PROGRESS"
