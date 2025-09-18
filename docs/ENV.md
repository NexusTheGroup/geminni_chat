# Environment Configuration

This project loads configuration via `src/nexus_knowledge/config/settings.py`, powered by Pydantic. Values are sourced from (in order):

1. Defaults defined in the `Settings` model.
2. An optional `.env` file in the repository root.
3. Real environment variables.

Run `scripts/config/validate.py` after updating your environment to confirm everything is wired correctly. A template is provided at `.env.example`.

---

## Quick Start

```bash
cp .env.example .env
scripts/config/validate.py --json          # inspect resolved values
scripts/config/migrate.py                  # compare with documented schema
```

If validation fails, the CLI prints actionable guidance (missing variables, invalid URLs, weak secrets, etc.).

---

## Configuration Schema

| Variable                        | Description                                        | Default   | Local    | Test     | Prod                              |
| ------------------------------- | -------------------------------------------------- | --------- | -------- | -------- | --------------------------------- |
| `APP_ENV`                       | Deployment environment (`local`, `test`, `prod`)   | `local`   | Optional | Optional | Required                          |
| `DATABASE_URL`                  | SQLAlchemy database URL                            | —         | Required | Required | Required                          |
| `REDIS_URL`                     | Celery broker/backend                              | —         | Required | Required | Required                          |
| `MLFLOW_TRACKING_URI`           | MLflow tracking URI                                | —         | Required | Required | Required                          |
| `SECRET_KEY`                    | Application secret for signing/encryption          | —         | Required | Required | Required (≥32 chars, non-default) |
| `LOG_LEVEL`                     | Logging level (`DEBUG`, `INFO`, …)                 | `INFO`    | Optional | Optional | Required (not `DEBUG`)            |
| `API_ROOT`                      | API route prefix                                   | `/api/v1` | Optional | Optional | Optional                          |
| `BENCHMARK_THRESHOLDS_PATH`     | Optional JSON file overriding benchmark thresholds | `None`    | Optional | Optional | Optional                          |
| `CELERY_WORKER_CONCURRENCY`     | Celery worker concurrency                          | `2`       | Optional | Optional | Required                          |
| `CELERY_PREFETCH_MULTIPLIER`    | Celery prefetch multiplier                         | `1`       | Optional | Optional | Required                          |
| `CELERY_TASK_SOFT_TIME_LIMIT`   | Celery soft time limit (seconds)                   | `600`     | Optional | Optional | Required                          |
| `CELERY_TASK_TIME_LIMIT`        | Celery hard time limit (seconds)                   | `900`     | Optional | Optional | Required                          |
| `CELERY_TASK_RETRY_DELAY`       | Default Celery retry delay (seconds)               | `5`       | Optional | Optional | Required                          |
| `CELERY_TASK_RETRY_BACKOFF_MAX` | Max retry backoff (seconds)                        | `600`     | Optional | Optional | Required                          |
| `CELERY_MAX_TASKS_PER_CHILD`    | Tasks processed before worker recycle              | `200`     | Optional | Optional | Optional                          |
| `CELERY_BROKER_POOL_LIMIT`      | Broker connection pool size                        | `10`      | Optional | Optional | Optional                          |
| `CELERY_BROKER_CONN_TIMEOUT`    | Broker connection timeout (seconds)                | `5.0`     | Optional | Optional | Optional                          |

See `config/schema.json` for the machine-readable version used by the migration CLI.

---

## Validation Rules

- URLs (`DATABASE_URL`, `REDIS_URL`, `MLFLOW_TRACKING_URI`) must be parseable by SQLAlchemy. SQLite is blocked in production.
- `SECRET_KEY` must be custom and at least 32 characters in production.
- Production must not run with `LOG_LEVEL=DEBUG`.
- Celery numeric settings must be positive integers (or floats for timeouts).

Validation errors are returned as a structured list via `ConfigurationError`. The CLI surfaces them with user-friendly messages.

---

## Migration Workflow

1. Update `config/schema.json` when adding or modifying configuration fields.
2. Document the change in `docs/CHANGELOG.md` and `docs/TODO.md` (Phase P10 section).
3. Provide backfill guidance in `docs/ENV.md` (this file) and update `.env.example`.
4. Run `scripts/config/migrate.py` to confirm the new schema passes for each environment.

---

## Secrets & Sensitive Data

- Never commit real secrets. Store only placeholders or instructions in `.env.example`.
- Use a dedicated secret manager in production (e.g. Vault, AWS Secrets Manager) and point `SECRET_KEY`/`DATABASE_URL` at those values.
- The validation CLI redacts secrets when `--json` is used.

---

## Related CLI Utilities

| Command                      | Description                                                          |
| ---------------------------- | -------------------------------------------------------------------- |
| `scripts/config/validate.py` | Validate configuration and render values.                            |
| `scripts/config/migrate.py`  | Compare current env against the documented schema.                   |
| `scripts/db/migrate.py`      | Run Alembic migrations (wrapper around `scripts/run_migrations.py`). |
| `scripts/db/seed.py`         | Seed the database with sample data (optionally normalising).         |
| `scripts/worker/control.py`  | Ping/stats/purge commands for the Celery worker.                     |
| `scripts/logs/tail.py`       | Tail log files with optional follow mode.                            |
| `scripts/health/check.py`    | Hit `/health/live` and `/health/ready` endpoints.                    |

Keep this document in sync with `config/schema.json` and the P10 acceptance criteria.
