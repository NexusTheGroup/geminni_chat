FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
COPY src /app/src

RUN pip install --upgrade pip setuptools wheel \
    && pip install -e .[dev]

COPY . /app

CMD ["uvicorn", "nexus_knowledge.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
