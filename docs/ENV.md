# Environment Variables

This document lists all the system-level environment variables required to run this project. These must be set in your shell's configuration file (e.g., `~/.bashrc`).

---

### `GITHUB_USERNAME`

- **Description:** Your GitHub username.
- **Example:** `your_github_username`

### `GITHUB_PAT_KEY`

- **Description:** A GitHub Personal Access Token (PAT) with `read:packages` scope.
- **Example:** `github_pat_...`

### `XAI_API_KEY`

- **Description:** Your API key for the Grok-4 model.
- **Example:** `grok_api_key_...`

### `DEEPSEEK_API_KEY`

- **Description:** Your API key for the DeepSeek 3.1 model.
- **Example:** `deepseek_api_key_...`

### `ORCHESTRATOR_MODE`

- **Description:** Orchestrator execution mode. Set to `codex` to indicate the orchestrator (GPT‑5) runs via the IDE (no OpenAI API calls from the app).
- **Example:** `codex`

### `DATABASE_URL`

- **Description:** SQLAlchemy-compatible URL for the primary PostgreSQL instance.
- **Example:** `postgresql+psycopg2://user:password@localhost:5432/nexus_knowledge`

### `REDIS_URL`

- **Description:** Broker/backend URL for Celery tasks.
- **Example:** `redis://localhost:6379/0`

### `MLFLOW_TRACKING_URI`

- **Description:** Tracking server URI for MLflow logging.
- **Example:** `http://localhost:5000` or `file:///home/user/mlruns`
