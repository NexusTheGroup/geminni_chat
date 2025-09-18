# Phase P8 — Observability & Reliability Design (DeepThink)

## Logging Schema

- **Formatter:** JSON via python-json-logger with UTC timestamps.
- **Mandatory fields:** `timestamp`, `level`, `logger`, `message`, `request_id`, `correlation_id`, `celery_task_id`, `span_id`, `duration_ms`, `source`.
- **Optional fields:** `user_id`, `task_status`, `http_method`, `http_path`, `status_code`, `exception`.
- **Example:**
  ```json
  {
    "timestamp": "2024-03-01T12:01:03.412Z",
    "level": "INFO",
    "logger": "nexus_knowledge.api.middleware",
    "message": "request.completed",
    "request_id": "req-4129c3b2",
    "correlation_id": "corr-4129c3b2",
    "celery_task_id": null,
    "span_id": "span-7a56",
    "duration_ms": 182.3,
    "http_method": "GET",
    "http_path": "/api/v1/status",
    "status_code": 200,
    "source": "api"
  }
  ```

## Correlation Context

- **Request ID:** Accept `X-Request-ID`; generate UUID4 if missing; echo on response.
- **Correlation ID:** Accept `X-Correlation-ID`; default to request ID; propagate to Celery tasks via kwargs.
- **Span ID:** Generate per log event requiring duration measurement (middleware + task instrumentation).

## Health & Readiness Checks

| Component      | Probe                                  | Failure Mode                | Response                                      |
| -------------- | -------------------------------------- | --------------------------- | --------------------------------------------- | --------------- |
| API process    | Always `alive`                         | Process crash               | HTTP 500; surfaced by infrastructure          | `status="live"` |
| Database       | `SELECT 1` via SQLAlchemy              | Connection refused, timeout | Mark `db` unhealthy; readiness returns 503    |
| Redis broker   | `redis.Redis.ping()` using broker URL  | Broker unreachable          | Mark `redis` unhealthy; readiness returns 503 |
| Celery workers | `celery_app.control.ping(timeout=1.0)` | No workers or broker issue  | Mark `celery` degraded; readiness 503         |

- `/api/v1/health/live`: lightweight; no external calls.
- `/api/v1/health/ready`: runs full checks; JSON payload with component statuses.

## Metrics Inventory

| Metric                               | Type      | Labels                          | Description                  |
| ------------------------------------ | --------- | ------------------------------- | ---------------------------- |
| `nexus_api_requests_total`           | Counter   | `method`, `route`, `status`     | Total API requests processed |
| `nexus_api_request_duration_seconds` | Histogram | `method`, `route`               | API latency distribution     |
| `nexus_api_errors_total`             | Counter   | `method`, `route`, `error_type` | API error tally              |
| `nexus_celery_task_total`            | Counter   | `task_name`, `status`           | Celery task lifecycle counts |
| `nexus_celery_task_duration_seconds` | Histogram | `task_name`                     | Task duration distribution   |
| `nexus_celery_task_failures_total`   | Counter   | `task_name`, `exception`        | Task failure counts          |

- Metrics exported via `/api/v1/metrics`; relies on Prometheus client; default buckets tuned for sub-second API responses and multi-second tasks.

## Tracing Plan (Deferred Implementation)

- Use log-based trace propagation leveraging `request_id` as root trace.
- Future integration target: OpenTelemetry SDK with OTLP exporter; reuse context vars to seed `traceparent` header.
- Documented in runbook with instructions to plug in OTLP collector when available.

## Test Matrix & Acceptance Mapping

| Scenario                               | Requirement                                  | Test Strategy                                                  |
| -------------------------------------- | -------------------------------------------- | -------------------------------------------------------------- |
| `GET /api/v1/health/live` success      | Health endpoint returns `live`               | API test asserting 200 and payload                             |
| `GET /api/v1/health/ready` full pass   | All dependencies healthy                     | API test with Redis/DB mocked                                  |
| `GET /api/v1/health/ready` degradation | Celery ping timeout surfaces degraded status | API test monkeypatching `check_celery` to raise                |
| Structured logs                        | Logs include request/correlation/task IDs    | Capture logs in test, assert record fields                     |
| Metrics endpoint                       | Prometheus format available                  | API test `GET /api/v1/metrics`                                 |
| Task instrumentation                   | Duration recorded and correlation propagated | Unit test invoking task function directly with patched metrics |

## Risks & Mitigations

- **Redis absence during tests:** Provide graceful fallback with `optional` health status; use monkeypatch to avoid real network.
- **JSON logging performance:** Configure single handler, ensure no heavy serialization; keep log field set minimal.
- **Celery ping latency:** Bound timeout to 1s and mark as degraded rather than blocking readiness.
- **Metric cardinality:** Route label normalized to templated path (e.g., `/api/v1/feedback/{feedback_id}`) via Starlette router mapping.
