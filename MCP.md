# MCP (Model Context Protocol) Integration

This document outlines the MCP servers integrated with the NexusKnowledge project for enhanced debugging, troubleshooting, and development capabilities.

## Overview

The Model Context Protocol (MCP) is an open standard that enables seamless integration between AI models and external tools, systems, and data sources. For the NexusKnowledge project, MCP servers provide powerful debugging and development capabilities.

## Installed MCP Servers

### 1. MCP Python SDK

- **Package**: `mcp`
- **Version**: 1.14.0
- **Purpose**: Core MCP framework for building custom servers and clients
- **Features**:
  - Decorator-based server development
  - Resource, tool, and prompt definitions
  - Integration with various LLMs
  - Standard transports (stdio, SSE, HTTP)

### 2. MCP Python Interpreter Server

- **Package**: `mcp-python-interpreter`
- **Version**: 1.1
- **Purpose**: Interactive Python code execution and debugging
- **Features**:
  - Execute Python code directly
  - Debug database queries in real-time
  - Test API endpoints interactively
  - Inspect variables and data structures
  - Run analysis pipelines step by step
  - Environment management (system and conda)
  - Package management
  - File reading and writing

### 3. Custom Web Debug MCP Server

- **File**: `src/nexus_knowledge/mcp/web_debug_server.py`
- **Purpose**: Web debugging and HTTP request testing for NexusKnowledge
- **Features**:
  - Test API endpoints with custom HTTP methods
  - Debug NexusKnowledge API endpoints
  - Analyze HTTP errors with suggestions
  - Test search API functionality
  - Monitor API health across multiple endpoints
  - Real-time HTTP request/response debugging

### 4. Custom Build Debug MCP Server

- **File**: `src/nexus_knowledge/mcp/build_debug_server.py`
- **Purpose**: Build and dependency debugging for NexusKnowledge
- **Features**:
  - Check project dependencies and versions
  - Analyze dependency conflicts
  - Test build process and environment
  - Check Docker build configuration
  - Analyze package structure
  - Check environment configuration
  - Run linting checks (ruff, black)
  - Identify build issues and provide recommendations

### 5. Custom GitHub MCP Server

- **File**: `src/nexus_knowledge/mcp/github_server.py`
- **Purpose**: GitHub integration and repository management for NexusKnowledge
- **Features**:
  - Get repository information and statistics
  - List recent commits and pull requests
  - Monitor open issues and their status
  - Check GitHub Actions workflow status
  - Get local git status and branch information
  - Create new GitHub issues
  - Track repository activity and changes

### 6. Custom Docker MCP Server

- **File**: `src/nexus_knowledge/mcp/docker_server.py`
- **Purpose**: Real-time Docker monitoring and troubleshooting for NexusKnowledge
- **Features**:
  - Monitor Docker container status and health
  - Real-time Docker build monitoring
  - Container logs retrieval and analysis
  - Docker service health checking
  - Container restart and management
  - Docker performance analysis
  - Common Docker issues debugging
  - Resource usage monitoring

## Debugging Capabilities

### Database Debugging

- **Direct SQL query execution** for testing database operations
- **Connection testing** to verify PostgreSQL connectivity
- **Schema inspection** to debug migration issues
- **Performance monitoring** for database operations

### API Debugging

- **Interactive endpoint testing** for FastAPI routes
- **Request/response inspection** for API calls
- **Authentication testing** for protected endpoints
- **Error handling verification** for edge cases
- **HTTP method testing** (GET, POST, PUT, DELETE)
- **Custom header and parameter testing**
- **Response time monitoring**
- **Error analysis with debugging suggestions**

### Data Processing Debugging

- **Step-by-step pipeline execution** for analysis workflows
- **Variable inspection** during data processing
- **Memory usage monitoring** for large datasets
- **Performance profiling** for optimization

### Build and Dependency Debugging

- **Dependency conflict analysis** for version issues
- **Build process testing** for environment validation
- **Package structure analysis** for import issues
- **Environment configuration checking** for missing variables
- **Docker build testing** for containerization issues
- **Linting checks** for code quality issues
- **Build issue identification** with recommendations

### GitHub Integration Debugging

- **Repository status monitoring** for project health
- **Commit history analysis** for change tracking
- **Issue and PR management** for project coordination
- **GitHub Actions monitoring** for CI/CD debugging
- **Local git status checking** for development workflow
- **Repository statistics** for project insights

### Docker Debugging

- **Real-time container monitoring** for build processes
- **Docker build troubleshooting** for compilation issues
- **Container health checking** for service validation
- **Performance analysis** for resource optimization
- **Log analysis** for error identification
- **Service management** for container orchestration

### File System Debugging

- **Real-time log monitoring**
- **Export file verification** for Obsidian integration\*\*
- **Data directory monitoring** for storage issues
- **Permission debugging** for file access problems

## Usage Examples

### Testing Search Functionality

```python
from nexus_knowledge.search import hybrid_search
from nexus_knowledge.db.session import get_session_dependency

# Test search function
session = get_session_dependency()
results = hybrid_search(session, "test query", limit=5)
print(f"Found {len(results)} results")
```

### Testing API Endpoints

```python
# Test API endpoint with custom parameters
test_api_endpoint(
    url="http://localhost:8000/api/v1/search",
    method="GET",
    params={"q": "test query", "limit": 10}
)

# Debug specific API endpoint
debug_nexus_api("/api/v1/status")

# Test search API
test_nexus_search_api("hybrid search", limit=5)

# Monitor API health
monitor_api_health()
```

### Build and Dependency Testing

```python
# Check project dependencies
check_dependencies()

# Analyze dependency conflicts
analyze_dependency_conflicts()

# Test build process
test_build_process()

# Check Docker build
check_docker_build()

# Analyze package structure
analyze_package_structure()

# Check environment configuration
check_environment_config()

# Run linting checks
run_linting_checks()
```

### GitHub Integration Testing

```python
# Get repository information
get_repository_info()

# List recent commits
list_recent_commits(limit=10)

# List open issues
list_open_issues(limit=10)

# List pull requests
list_pull_requests(limit=10)

# Check GitHub Actions status
check_github_actions_status()

# Get local git status
get_local_git_status()

# Create a new issue
create_issue("Bug Report", "Description of the bug", ["bug", "high-priority"])
```

### Docker Monitoring and Troubleshooting

```python
# Get Docker status
get_docker_status()

# Monitor Docker build in real-time
monitor_docker_build()

# Get container logs
get_container_logs("nexus-app", lines=100)

# Check Docker health
check_docker_health()

# Restart Docker services
restart_docker_services(["app", "db", "redis"])

# Analyze Docker performance
analyze_docker_performance()

# Debug Docker issues
debug_docker_issues()
```

### Database Query Testing

```python
from nexus_knowledge.db.repository import get_raw_data
from nexus_knowledge.db.session import get_session_dependency

# Test database operations
session = get_session_dependency()
raw_data = get_raw_data(session, "some-uuid")
print(f"Raw data status: {raw_data.status}")
```

### API Endpoint Testing

```python
import requests

# Test API endpoints
response = requests.get("http://localhost:8000/api/v1/status")
print(f"API Status: {response.json()}")
```

## Configuration

### Environment Setup

MCP servers are installed in the project's virtual environment:

```bash
source .venv/bin/activate
pip install mcp mcp-python-interpreter
```

### Server Configuration

MCP servers can be configured through:

- Environment variables
- Configuration files
- Command-line arguments
- Programmatic configuration

## Integration with Development Workflow

### Pre-commit Hooks

MCP servers can be integrated with pre-commit hooks for:

- Code quality checks
- Automated testing
- Performance monitoring
- Security scanning

### CI/CD Pipeline

MCP servers support continuous integration through:

- Automated testing
- Performance benchmarking
- Security scanning
- Deployment verification

## Troubleshooting

### Common Issues

1. **Permission errors**: Ensure proper file permissions for data directories
2. **Connection failures**: Verify database and Redis connections
3. **Memory issues**: Monitor memory usage for large datasets
4. **Performance problems**: Use profiling tools to identify bottlenecks

### Debug Commands

```bash
# Check MCP server status
mcp --version

# Test Python interpreter
python -c "import mcp; print('MCP installed successfully')"

# Verify database connection
python -c "from nexus_knowledge.db.session import get_session_dependency; print('Database connection OK')"

# Start Web Debug MCP Server
./scripts/start_web_debug_mcp.sh

# Start Build Debug MCP Server
./scripts/start_build_debug_mcp.sh

# Start GitHub MCP Server
./scripts/start_github_mcp.sh

# Start Docker MCP Server
./scripts/start_docker_mcp.sh

# Test web debugging tools
python -c "from nexus_knowledge.mcp.web_debug_server import test_api_endpoint; print('Web debug tools available')"

# Test build debugging tools
python -c "from nexus_knowledge.mcp.build_debug_server import check_dependencies; print('Build debug tools available')"

# Test GitHub integration tools
python -c "from nexus_knowledge.mcp.github_server import get_repository_info; print('GitHub MCP tools available')"

# Test Docker monitoring tools
python -c "from nexus_knowledge.mcp.docker_server import get_docker_status; print('Docker MCP tools available')"
```

## Security Considerations

- **Data access**: MCP servers have access to project data and files
- **Network access**: Some servers may require network access
- **Authentication**: Ensure proper authentication for sensitive operations (GitHub PAT keys, API keys)
- **Permissions**: Use appropriate file and directory permissions

## Future Enhancements

### Planned MCP Servers

1. **Filesystem MCP**: Enhanced file system operations
2. **Database MCP**: Advanced database debugging tools
3. **Memory MCP**: Persistent debugging state management
4. **Web Search MCP**: External knowledge integration

### Custom MCP Servers

The project can be extended with custom MCP servers for:

- NexusKnowledge-specific debugging tools
- Integration with external services
- Custom data processing workflows
- Advanced analytics capabilities

## Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Python Interpreter](https://pypi.org/project/mcp-python-interpreter/)
- [NexusKnowledge Project](https://github.com/NexusTheGroup/geminni_chat)

## Support

For MCP-related issues:

1. Check the troubleshooting section above
2. Review MCP server logs
3. Verify environment configuration
4. Consult the official MCP documentation
5. Create an issue in the project repository
