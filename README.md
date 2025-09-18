NexusKnowledge Project
This repository contains the source code and documentation for the NexusKnowledge system, a local-first, single-user AI conversation management and knowledge synthesis tool.

Overview
This project follows a strict, AI-driven development process. Please refer to the documents in the docs/ directory and AGENTS.md for a complete overview of the architecture and operating procedures.

Getting Started (Ubuntu 24.04 Desktop)
Step 1: One-Time Environment Setup
Install Prerequisites: Open a terminal and install Docker, VS Code, and other essential tools:

# Add Docker's official GPG key & set up the repository (run these commands one by one)

sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL [https://download.docker.com/linux/ubuntu/gpg](https://download.docker.com/linux/ubuntu/gpg) -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] [https://download.docker.com/linux/ubuntu](https://download.docker.com/linux/ubuntu) $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker Engine, CLI, and Containerd

sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to the docker group to run docker without sudo

sudo usermod -aG docker $USER

# Install VS Code

sudo apt-get install -y wget gpg
wget -qO- [https://packages.microsoft.com/keys/microsoft.asc](https://packages.microsoft.com/keys/microsoft.asc) | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] [https://packages.microsoft.com/repos/code](https://packages.microsoft.com/repos/code) stable main" | sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -f packages.microsoft.gpg
sudo apt-get install -y apt-transport-https
sudo apt-get update
sudo apt-get install -y code

IMPORTANT: After running these commands, you must log out and log back in for the docker group changes to take effect.

Set Environment Variables: Add your API keys (GITHUB_USERNAME, GITHUB_PAT_KEY, etc.) to your ~/.bashrc file. Refer to docs/ENV.md for the full list.

echo 'export GITHUB*USERNAME="your_github_username"' >> ~/.bashrc
echo 'export GITHUB_PAT_KEY="github_pat*...\_with_read_packages_scope"' >> ~/.bashrc
echo 'export XAI_API_KEY="your_grok_api_key"' >> ~/.bashrc
echo 'export DEEPSEEK_API_KEY="your_deepseek_api_key"' >> ~/.bashrc
echo 'export CELERY_WORKER_CONCURRENCY=2' >> ~/.bashrc # defaults are tuned for single-user workloads
echo 'export CELERY_PREFETCH_MULTIPLIER=1' >> ~/.bashrc
source ~/.bashrc

Configuration Loader (optional but recommended):

```bash
cp .env.example .env          # customise values as needed
scripts/config/validate.py    # ensure settings pass validation
scripts/config/migrate.py     # compare against documented schema
```

Authenticate Docker: In the terminal, run the one-time Docker login command:

echo $GITHUB_PAT_KEY | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

You should see a "Login Succeeded" message.

Step 2: Performance Tuning (Important for Stability)
To prevent VS Code from freezing, you must ensure Docker has enough system resources.

Open Docker Desktop.

Go to Settings > Resources.

Increase Memory: Allocate a significant portion of your system's RAM to Docker. For a system with 64GB, allocating 24GB to 32GB is a good starting point.

Increase CPUs: Allocate at least half of your available CPU cores. For a 24-core system, allocating 12 to 16 cores is recommended.

Click "Apply & Restart".

Step 3: Launch the Project Environment
Launch Docker Compose: From your terminal, navigate to the project root and run:

docker-compose up --build -d

This will build and start all necessary services, including the Celery worker. The `app` container runs database migrations automatically using `python scripts/run_migrations.py` before serving the API.

If you are running the stack outside Docker, apply the migrations manually:

```bash
python scripts/run_migrations.py
```

Execute a Sample Task: To execute a sample asynchronous task, shell into the app container:

docker exec -it nexus-app bash

Then, from within the container's bash, run the following Python commands:

python
from nexus_knowledge.tasks import long_running_api_call
long_running_api_call.delay("Hello from Celery!")
exit()

You can observe the worker processing the task in the docker-compose logs:

docker-compose logs -f worker

To validate the MLflow integration, log a dummy experiment (the CLI will reuse the `MLFLOW_TRACKING_URI` environment variable or default to `http://localhost:5000`):

```bash
python scripts/log_dummy_experiment.py
```

Queue a sample ingestion payload (replace the JSON body with your data). The API returns a `rawDataId` you can poll for status:

````bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "sourceType": "deepseek_chat",
        "sourceId": "demo-conversation",
        "content": {
          "messages": [
            {"role": "user", "content": "Hello", "timestamp": "2025-01-01T00:00:00Z"},
            {"role": "assistant", "content": "Hi there!", "timestamp": "2025-01-01T00:00:05Z"}
          ]
        }
      }'

curl http://localhost:8000/api/v1/ingest/<rawDataId>

Once a payload is normalized you can queue the sentiment analysis job and check its status:

```bash
curl -X POST http://localhost:8000/api/v1/analysis \
  -H "Content-Type: application/json" \
  -d '{"rawDataId": "<rawDataId>"}'

curl http://localhost:8000/api/v1/analysis/<rawDataId>

After analysis completes you can generate and inspect correlation candidates:

```bash
curl -X POST http://localhost:8000/api/v1/correlation \
  -H "Content-Type: application/json" \
  -d '{"rawDataId": "<rawDataId>"}'

curl http://localhost:8000/api/v1/correlation/<rawDataId>
````

## Observability Quick Checks

Run these commands after the stack is up to validate the Phase P8 observability features (see `docs/observability_runbook.md` for full guidance):

```bash
# Liveness and readiness endpoints
curl http://localhost:8000/api/v1/health/live | jq
curl http://localhost:8000/api/v1/health/ready | jq

# Metrics endpoint (Prometheus exposition format)
curl http://localhost:8000/api/v1/metrics | grep nexus_api_requests_total

# Structured log sample with a custom request identifier
curl -H "X-Request-ID: demo-req" http://localhost:8000/api/v1/status
```

## Operations Scripts

```bash
scripts/db/migrate.py             # run Alembic migrations
scripts/db/seed.py --normalize    # load sample data and normalise
scripts/worker/control.py ping    # ping Celery workers
scripts/logs/tail.py app.log -f   # tail logs (example file path)
scripts/health/check.py           # hit liveness/readiness endpoints
```

# Single-User Benchmark

Run the lightweight baseline benchmark after seeding sample data to track ingestion/normalization/search timings. Thresholds are defined in `src/nexus_knowledge/performance/__init__.py`.

```bash
scripts/benchmarks/run_single_user_benchmark.py --iterations 5
```

Use `--include-analysis --mlflow-dir ./tmp/mlruns` to measure the optional analysis stage once MLflow is configured.

Run a hybrid search across stored conversation turns:

```bash
curl "http://localhost:8000/api/v1/search?q=hybrid+search&limit=5"
```

## Running Tests Locally

The project is configured to run tests without external services (Redis, Celery workers) using mocking and file-based MLflow.

### Quick Start

```bash
# Using the test harness (recommended)
scripts/test/local.sh

# Or directly with pytest
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest

# Run specific test modules
scripts/test/local.sh tests/ingestion/test_service.py tests/export/test_obsidian.py
```

### Test Configuration

- **Environment**: Tests automatically set up SQLite database, file-based MLflow, and mock Celery tasks
- **No Dependencies**: No Redis, Celery workers, or MLflow server required
- **Isolated**: Each test uses temporary databases and clean environments
- **Fast**: Full test suite runs in under 30 seconds

Launch the modern React frontend at <http://localhost:3000/> for the full user experience, or the lightweight UI at <http://localhost:8000/> for basic functionality.

## Frontend Application

The project includes a comprehensive React/TypeScript frontend application located in the `frontend/` directory:

### Features

- **Modern Architecture**: React 18, TypeScript 5, Vite build system
- **Material-UI Components**: Beautiful, accessible UI with custom theming
- **State Management**: Redux Toolkit with RTK Query for API integration
- **Advanced Search**: Multi-faceted search with filtering and autocomplete
- **Analytics Dashboard**: Interactive charts and correlation analysis
- **Data Management**: Ingestion monitoring and export tools
- **Responsive Design**: Mobile-first approach with full accessibility compliance

### Development

```bash
cd frontend
npm install
npm run dev
```

### Production Build

```bash
cd frontend
npm run build
```

The frontend integrates with all 14 backend API endpoints and provides a comprehensive user interface for the NexusKnowledge system.

Step 4: YOLO Mode Initialization (Required for Each Session)
Before giving the agent a major task, grant it permission to run its tools non-stop.

Grant WriteFile Permission: In the chat, ask the agent to: "Create a file named test.txt with 'hello'." When prompted, click the dropdown next to "Accept" and choose "Always Accept".

Grant Shell Permission: Ask the agent to: "List files using ls." When prompted, choose "Always Accept".

Clean Up: Delete test.txt.

Step 5: Kickoff
The GPT Orchestrator (via Codex) is now fully prepared. Provide it with the "Final Kickoff Prompt" from `prompts.md`.

## P8 Production Readiness Testing Framework

The NexusKnowledge system includes a comprehensive P8 testing framework for production readiness and deployment validation, designed using DeepThink AI reasoning for enterprise-grade quality assurance.

### P8 Testing Overview

**P8: Production Readiness & Deployment Testing** provides comprehensive testing automation for all production readiness components:

- **P8.1: Container Orchestration Testing** - Kubernetes manifests, Helm charts, service mesh
- **P8.2: Security Hardening Testing** - OAuth2/JWT, encryption, network policies
- **P8.3: Monitoring Stack Testing** - Prometheus, Grafana, ELK stack
- **P8.4: Backup & Disaster Recovery Testing** - Automated backups, point-in-time recovery
- **P8.5: SSL/TLS Management Testing** - Certificate validation, TLS 1.3, security headers
- **P8.6: Production Deployment Testing** - CI/CD pipeline, ArgoCD GitOps, rollback automation

### P8 Testing Scripts

**Location**: `scripts/README_P8_TESTING.md`

#### Core Testing Scripts

```bash
# Generate P8 testing plans
python3 scripts/delegate-p8-testing.py
python3 scripts/master-testing-generator.py

# Execute P8 sub-phase delegations
python3 scripts/delegate-p8-1-architecture.py
python3 scripts/delegate-p8-2-security.py
python3 scripts/delegate-p8-3-monitoring.py
python3 scripts/delegate-p8-4-backup.py
python3 scripts/delegate-p8-5-ssl.py
python3 scripts/delegate-p8-6-deployment.py

# Integrate P8 results
python3 scripts/integrate-p8-1-results.py
python3 scripts/integrate-p8-2-security.py
python3 scripts/integrate-p8-3-monitoring.py
python3 scripts/integrate-p8-4-backup.py
python3 scripts/integrate-p8-5-ssl.py
python3 scripts/integrate-p8-6-deployment.py
```

#### P8 Testing Execution

```bash
# Execute P8 testing
bash scripts/execute-p8-1-delegation.sh
bash scripts/k8s-deploy.sh
bash scripts/security-scan.sh
bash scripts/load-testing.sh
```

### P8 Testing Documentation

**Testing Plans**:

- `docs/P8_TESTING_PLAN_*.md` - Comprehensive testing plans
- `docs/P8_PRODUCTION_READINESS_&_DEPLOYMENT_TESTING_PLAN_*.md` - Enterprise testing framework
- `docs/P8_PRODUCTION_TESTING_PLAN_*.md` - Production testing plans

**Testing Scripts**:

- `docs/P8_TESTING_SCRIPTS_*.md` - Testing automation scripts
- `scripts/README_P8_TESTING.md` - P8 testing scripts documentation

**Completion Summaries**:

- `docs/P8_FINAL_COMPLETION_SUMMARY.md` - P8 phase completion
- `docs/P8_*_COMPLETION_SUMMARY.md` - Individual sub-phase completions

## P9 Performance Optimization Testing Framework

The NexusKnowledge system includes a comprehensive P9 testing framework for performance optimization and scaling validation, designed using DeepThink AI reasoning for enterprise-grade performance testing.

### P9 Testing Overview

**P9: Performance Optimization & Scaling Testing** provides comprehensive testing automation for all performance optimization components:

- **P9.1: Database Optimization Testing** - Query performance, indexing, partitioning
- **P9.2: Redis Caching Testing** - Cache hit ratios, invalidation, cluster testing
- **P9.3: Connection Pooling Testing** - Pool efficiency, resource management
- **P9.4: Load Testing & Performance Benchmarking** - API response times, throughput
- **P9.5: Auto-scaling Testing** - HPA/VPA scaling, cluster autoscaler
- **P9.6: CDN Integration Testing** - Asset optimization, global latency

### P9 Testing Scripts

**Location**: `scripts/README_P9_TESTING.md`

#### Core Testing Scripts

```bash
# Generate P9 testing plans
python3 scripts/delegate-p9-testing.py
python3 scripts/comprehensive-performance-testing.py

# Execute P9 sub-phase delegations
python3 scripts/delegate-p9-1-database-optimization.py
python3 scripts/delegate-p9-2-redis-caching.py
python3 scripts/delegate-p9-3-connection-pooling.py
python3 scripts/delegate-p9-4-load-testing.py
python3 scripts/delegate-p9-5-autoscaling.py
python3 scripts/delegate-p9-6-cdn-integration.py
```

#### P9 Performance Testing Execution

```bash
# Execute P9 performance testing
bash scripts/load-testing.sh
python3 scripts/comprehensive-performance-testing.py
```

### P9 Testing Documentation

**Testing Plans**:

- `docs/P9_PERFORMANCE_OPTIMIZATION_TESTING_PLAN_*.md` - Comprehensive testing plans
- `docs/COMPREHENSIVE_PERFORMANCE_TESTING_PLAN_*.md` - Enterprise performance testing
- `docs/P9_TESTING_SCRIPTS_*.md` - Testing automation scripts

**Testing Scripts**:

- `scripts/README_P9_TESTING.md` - P9 testing scripts documentation
- `scripts/comprehensive-performance-testing.py` - Performance testing suite

**Completion Summaries**:

- `P9_AI_HANDOFF.md` - P9 phase completion
- `docs/P9_*_COMPLETION_SUMMARY.md` - Individual sub-phase completions

## Comprehensive Testing Framework (Phases P8-P14)

The NexusKnowledge system includes comprehensive testing frameworks for all production phases (P8-P14), designed using DeepThink AI reasoning for enterprise-grade quality assurance.

### Testing Overview

Our testing framework covers seven critical phases:

- **P8: Production Readiness & Deployment** - Container orchestration, security hardening, monitoring, backup systems
- **P9: Performance Optimization & Scaling** - Database optimization, caching, load testing, auto-scaling
- **P10: Advanced AI & ML Features** - LLM integration, vector search, topic modeling, NER, predictive analytics
- **P11: Integration & Interoperability** - API integrations, webhooks, real-time sync, format support
- **P12: User Experience & Accessibility** - Interactive visualizations, collaboration, mobile app, accessibility
- **P13: Enterprise Features** - Multi-user management, RBAC, SSO, audit logging, compliance
- **P14: Maintenance & Support** - Automated maintenance, documentation, support systems, health monitoring

### Master Testing Script

Use the master testing script to generate comprehensive testing plans for all phases:

```bash
# Generate all testing plans in parallel
python3 scripts/master-testing-generator.py

# Generate individual phase testing plans
python3 scripts/delegate-p8-testing.py   # Production Readiness
python3 scripts/delegate-p9-testing.py   # Performance Optimization
python3 scripts/delegate-p10-testing.py  # AI/ML Features
python3 scripts/delegate-p11-testing.py  # Integration & Interoperability
python3 scripts/delegate-p12-testing.py  # User Experience & Accessibility
python3 scripts/delegate-p13-testing.py  # Enterprise Features
python3 scripts/delegate-p14-testing.py  # Maintenance & Support
```

### Testing Configuration

The testing framework uses JSON configuration for flexibility:

```json
{
  "phases": {
    "P8": {
      "name": "Production Readiness & Deployment",
      "focus_areas": [
        "Kubernetes manifests testing",
        "Security hardening validation",
        "Monitoring stack testing",
        "Backup & disaster recovery testing",
        "SSL/TLS configuration testing",
        "CI/CD pipeline testing"
      ]
    }
  },
  "global_settings": {
    "max_tokens": 6000,
    "temperature": 0.1,
    "parallel_execution": true,
    "max_workers": 7
  }
}
```

### Generated Testing Documentation

The testing framework generates comprehensive documentation in `docs/`:

#### Testing Plans

- `P8_PRODUCTION_READINESS_&_DEPLOYMENT_TESTING_PLAN_*.md`
- `P9_PERFORMANCE_OPTIMIZATION_TESTING_PLAN_*.md`
- `P10_ADVANCED_AI_&_ML_FEATURES_TESTING_PLAN_*.md`
- `P11_INTEGRATION_&_INTEROPERABILITY_TESTING_PLAN_*.md`
- `P12_USER_EXPERIENCE_&_ACCESSIBILITY_TESTING_PLAN_*.md`
- `P13_ENTERPRISE_FEATURES_TESTING_PLAN_*.md`
- `P14_MAINTENANCE_&_SUPPORT_TESTING_PLAN_*.md`

#### Testing Scripts

- `P8_TESTING_SCRIPTS_*.md` - Production readiness testing automation
- `P9_TESTING_SCRIPTS_*.md` - Performance testing automation
- `P10_TESTING_SCRIPTS_*.md` - AI/ML testing automation
- `P11_TESTING_SCRIPTS_*.md` - Integration testing automation
- `P12_TESTING_SCRIPTS_*.md` - UX/Accessibility testing automation
- `P13_TESTING_SCRIPTS_*.md` - Enterprise features testing automation
- `P14_TESTING_SCRIPTS_*.md` - Maintenance & support testing automation

### Testing Categories

Each phase includes comprehensive testing across multiple categories:

1. **Unit Testing** - Individual component testing
2. **Integration Testing** - Component interaction testing
3. **Performance Testing** - Performance and scalability validation
4. **Security Testing** - Security requirements validation
5. **User Interface Testing** - UI/UX testing (where applicable)
6. **API Testing** - API endpoint testing
7. **Database Testing** - Database operations testing
8. **End-to-End Testing** - Complete workflow testing

### Quality Assurance Framework

The testing framework ensures:

- **Enterprise-Grade Quality** - Production-ready testing standards
- **Comprehensive Coverage** - All system components tested
- **Performance Validation** - Performance criteria verification
- **Security Compliance** - Security requirements validation
- **Accessibility Standards** - WCAG 2.1 AAA compliance
- **Documentation Quality** - Complete testing documentation
- **Automation** - Automated testing scripts and tools
- **Monitoring** - Testing monitoring and reporting

### Testing Execution

1. **Review Testing Plans** - Review generated testing documentation
2. **Implement Testing Scripts** - Implement automated testing scripts
3. **Execute Testing Procedures** - Run comprehensive testing
4. **Monitor Quality Metrics** - Track quality and performance metrics
5. **Continuous Improvement** - Iterate and improve testing processes

### Testing Tools Integration

The framework integrates with industry-standard testing tools:

- **Python Testing** - pytest, unittest, pytest-cov
- **JavaScript Testing** - Jest, Cypress, Playwright
- **Performance Testing** - Locust, JMeter, k6
- **Security Testing** - Bandit, Safety, OWASP ZAP
- **API Testing** - Postman, Newman, HTTPie
- **Database Testing** - SQLAlchemy testing, pytest-postgresql
- **Container Testing** - Docker testing, Kubernetes testing
- **Monitoring Testing** - Prometheus testing, Grafana validation

### Quality Gates

Each phase must meet specific quality criteria:

- **Code Quality Score** ≥ 85/100 (per CODE_QUALITY_FRAMEWORK.md)
- **Test Coverage** ≥ 80%
- **Performance Targets** - Phase-specific performance criteria
- **Security Compliance** - No critical vulnerabilities
- **Accessibility Compliance** - WCAG 2.1 AAA where applicable
- **Documentation Completeness** - 100% documentation coverage

### Continuous Testing

The testing framework supports continuous testing through:

- **CI/CD Integration** - Automated testing in deployment pipelines
- **Parallel Execution** - Multi-threaded testing execution
- **Real-time Monitoring** - Continuous quality monitoring
- **Automated Reporting** - Automated test result reporting
- **Quality Dashboards** - Real-time quality dashboards

For detailed testing procedures and implementation guidance, refer to the generated testing documentation in the `docs/` directory.
