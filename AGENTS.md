# AGENTS.md

This document defines the non-negotiable process and guardrails for this repository. It locks the common directory structure, the PR workflow, and the AI persona handoffs.

## 1) Mission & Scope

- Implement the project from `blueprint.md` through deployable build artifacts.
- Scope is build/deploy only; no runtime/prod operations in this repo.

## 2) Canonical Routes (read before any change)

- `AGENTS.md` (this file), `prompts.md`, `personas.md`, `blueprint.md`, `MCP.md`.
- Planning docs: `docs/TODO.md`, `docs/BUILD_PLAN.md`, `docs/TEST_MATRIX.md`, `docs/API_SURFACE.md`, `docs/DB_SCHEMA.sql`.
- Strategy docs: `docs/AI_UTILIZATION_STRATEGY.md`, `docs/CODE_QUALITY_FRAMEWORK.md`, `docs/ENV.md`.
- Troubleshooting: `docs/TROUBLESHOOTING.md` - Comprehensive MCP debugging guide.

## 3) Common Directory Layout (locked)

```text
.devcontainer/
.github/
docs/
scripts/
src/
tests/
.gitignore
.pre-commit-config.yaml
AGENTS.md
MCP.md
README.md
blueprint.md
docker-compose.yml
package.json
personas.md
prompts.md
pyproject.toml
```

## 4) Branch & PR Protocol

Branches are short-lived: feat/<task>, fix/<scope>.

Each PR MUST include tests and updated docs.

PRs are reviewed by the GPT-5 (via Codex) QC/Debugger persona against the CODE_QUALITY_FRAMEWORK.md.

Prefer Squash and merge.

## 5) No-Stop Acceptance (global)

Do not conclude a phase until:

All phase deliverables exist and are cross-linked in docs/BUILD_PLAN.md.

Smoke and CI checks are green.

docs/TODO.md is up to date.

Required documentation (docs/ENV.md, CHANGELOG.md) is updated.

All code meets the minimum score defined in docs/CODE_QUALITY_FRAMEWORK.md.

## Asynchronous Task Execution

All long-running operations, especially external API calls, MUST be implemented as asynchronous tasks and delegated to a Celery worker. Direct, blocking calls in the main application thread are forbidden.

## MCP (Model Context Protocol) Integration

The project includes comprehensive MCP servers for enhanced debugging, troubleshooting, and development capabilities:

### Installed MCP Servers

- **MCP Python SDK** (v1.14.0): Core framework for building custom MCP servers
- **MCP Python Interpreter** (v1.1): Interactive Python code execution and debugging
- **Custom Web Debug MCP**: HTTP/API debugging and testing (`src/nexus_knowledge/mcp/web_debug_server.py`)
- **Custom Build Debug MCP**: Build and dependency debugging (`src/nexus_knowledge/mcp/build_debug_server.py`)
- **Custom GitHub MCP**: Repository management and monitoring (`src/nexus_knowledge/mcp/github_server.py`)

### MCP Server Capabilities

- **Database Debugging**: Direct SQL query execution, connection testing, migration debugging
- **API Debugging**: HTTP request/response testing, error analysis, endpoint monitoring
- **Build Debugging**: Dependency analysis, Docker testing, environment validation
- **GitHub Integration**: Repository monitoring, issue tracking, CI/CD status
- **Web Debugging**: CORS testing, timeout analysis, performance monitoring
- **Docker Monitoring**: Real-time container monitoring, build process tracking, performance analysis

### MCP Server Management

- **Startup Scripts**: `scripts/start_*_mcp.sh` for each server type
- **Configuration**: Environment variables and authentication setup
- **Documentation**: See `MCP.md` for detailed configuration and usage
- **Troubleshooting**: See `docs/TROUBLESHOOTING.md` for comprehensive debugging guide

### Persona Integration with MCP Servers

The MCP servers are designed to work seamlessly with the project's AI personas:

- **Builder Persona**: Uses Build Debug MCP for dependency analysis and build validation
- **Helix Persona**: Leverages GitHub MCP for repository management and CI/CD monitoring
- **QC/Debugger Persona**: Employs Web Debug MCP for API testing and error analysis
- **Weaver Persona**: Utilizes Python Interpreter MCP for code generation and testing
- **Docker Specialist Persona**: Uses Docker MCP for container management and real-time monitoring

### MCP Server Workflow Integration

1. **Development Phase**: Build Debug MCP validates environment and dependencies
2. **Testing Phase**: Web Debug MCP tests API endpoints and HTTP operations
3. **Integration Phase**: GitHub MCP monitors repository status and CI/CD pipelines
4. **Debugging Phase**: Python Interpreter MCP provides interactive debugging capabilities
5. **Docker Operations Phase**: Docker MCP provides real-time container monitoring and build tracking

### Security Considerations

- MCP servers have access to project data and files
- Use appropriate file and directory permissions
- Ensure proper authentication for sensitive operations (GitHub tokens, API keys)
- Monitor network access requirements
- Validate input data and sanitize outputs
