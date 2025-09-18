"""Base SQLAlchemy configuration for the NexusKnowledge project."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import CHAR, TypeDecorator


class Base(DeclarativeBase):
    """Declarative base shared across all ORM models."""


class GUID(TypeDecorator):
    """Platform-independent UUID type.

    Stores UUIDs as native UUID on PostgreSQL and as string elsewhere.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Any, dialect):  # type: ignore[override]
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value: Any, dialect):  # type: ignore[override]
        if value is None or isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


class JSONBType(TypeDecorator):
    """Use JSONB on PostgreSQL and JSON elsewhere."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB())
        return dialect.type_descriptor(JSON)
