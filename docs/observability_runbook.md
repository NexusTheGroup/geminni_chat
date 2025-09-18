# Observability Runbook

Phase P8 introduces structured logging, health probes, and Prometheus metrics for NexusKnowledge. Use this guide to validate and troubleshoot the observability stack in development or single-user deployments.

## 1. Logging

- **Format**: JSON with mandatory fields `timestamp`, `level`, `logger`, `message`, `request_id`, `correlation_id`, `celery_task_id`, and optional context (`http_method`, `http_path`, `status_code`, `duration_ms`, `task_name`).
- **Configuration**: Defined in `src/nexus_knowledge/observability/logging.py` and initialised via `configure_logging()` in both API and Celery worker entry points.
- **Correlation**:
  - API middleware injects `X-Request-ID`/`X-Correlation-ID` headers into context (auto-generating UUIDs when absent).
  - Celery tasks accept a `correlation_id` kwarg; task IDs are captured from `task_id` or generated locally.
- **Verification**:
  ```bash
  uvicorn src.nexus_knowledge.api.main:app --reload
  curl -H "X-Request-ID: req-123" http://localhost:8000/api/v1/status
  tail -f logs/app.log | jq '.request_id, .correlation_id, .celery_task_id'
  ```

## 2. Health & Readiness

Endpoints implemented in `src/nexus_knowledge/api/main.py` with checks in `src/nexus_knowledge/observability/health.py`:

- `GET /api/v1/health/live`: process heartbeat (`{"status": "live"}`).
- `GET /api/v1/health/ready`: aggregates database, Redis, and Celery worker health (statuses `healthy`, `degraded`, `unhealthy`). Returns HTTP 503 whenever any dependency is degraded/unhealthy.

**Manual check**:

```bash
# Healthy response
curl http://localhost:8000/api/v1/health/ready | jq

# Simulate Redis outage
docker stop redis
curl -i http://localhost:8000/api/v1/health/ready
```

## 3. Metrics

Prometheus metrics exposed at `GET /api/v1/metrics` via `prometheus-client` observers in `src/nexus_knowledge/observability/metrics.py`:

| Metric                                                  | Description             |
| ------------------------------------------------------- | ----------------------- |
| `nexus_api_requests_total{method,route,status}`         | API request counter     |
| `nexus_api_request_duration_seconds{method,route}`      | API latency histogram   |
| `nexus_api_errors_total{method,route,error_type}`       | API error counter       |
| `nexus_celery_task_total{task_name,status}`             | Task lifecycle counter  |
| `nexus_celery_task_duration_seconds{task_name}`         | Task duration histogram |
| `nexus_celery_task_failures_total{task_name,exception}` | Task failure counter    |

**Prometheus scrape example**:

```yaml
scrape_configs:
  - job_name: "nexusknowledge-api"
    static_configs:
      - targets: ["localhost:8000"]
    metrics_path: /api/v1/metrics
```

**Quick validation**:

```bash
curl http://localhost:8000/api/v1/status
curl http://localhost:8000/api/v1/metrics | grep nexus_api_requests_total
```

## 4. Tracing Plan (Deferred)

- Trace propagation reuses `request_id` as a log-based trace identifier.
- Future OpenTelemetry integration should lift context from `observability.context` and enrich outbound requests with `traceparent`.
- See `docs/P8_OBSERVABILITY_DESIGN.md` for proposed span structure and rollout notes.

## 5. Troubleshooting

| Symptom                               | Likely Cause                           | Resolution                                                                                     |
| ------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `readiness` reports `redis` unhealthy | Redis broker down or URL misconfigured | Verify `REDIS_URL`, restart broker                                                             |
| Missing `celery_task_id` in logs      | Celery worker not passing `task_id`    | Ensure worker upgrades to latest tasks module or pass `task_id` when invoking `apply` in tests |
| Metrics endpoint empty                | No requests/tasks executed yet         | Hit `/api/v1/status` or trigger task to populate counters                                      |
| JSON logs printed twice               | Another handler configured             | Check for duplicate logging configuration in deployment entry points                           |

---

**Cross-References**: `docs/P8_OBSERVABILITY_DESIGN.md`, `docs/BUILD_PLAN.md` (Phase P8), `docs/TODO.md`.
