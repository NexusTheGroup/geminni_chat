# NexusKnowledge Troubleshooting Guide

This comprehensive troubleshooting guide covers all MCP (Model Context Protocol) servers and debugging tools available for the NexusKnowledge project.

## Table of Contents

1. [MCP Server Overview](#mcp-server-overview)
2. [Database Debugging](#database-debugging)
3. [API Debugging](#api-debugging)
4. [Build and Dependency Debugging](#build-and-dependency-debugging)
5. [GitHub Integration Debugging](#github-integration-debugging)
6. [Web Debugging](#web-debugging)
7. [Common Issues and Solutions](#common-issues-and-solutions)
8. [MCP Server Management](#mcp-server-management)

---

## MCP Server Overview

The NexusKnowledge project includes several MCP servers for comprehensive debugging and troubleshooting:

### Available MCP Servers

| Server                 | File                                            | Purpose                        | Status       |
| ---------------------- | ----------------------------------------------- | ------------------------------ | ------------ |
| **Python Interpreter** | `mcp-python-interpreter`                        | Interactive Python execution   | ✅ Installed |
| **Web Debug**          | `src/nexus_knowledge/mcp/web_debug_server.py`   | HTTP/API debugging             | ✅ Installed |
| **Build Debug**        | `src/nexus_knowledge/mcp/build_debug_server.py` | Build and dependency debugging | ✅ Installed |
| **GitHub**             | `src/nexus_knowledge/mcp/github_server.py`      | GitHub integration             | ✅ Installed |

---

## Database Debugging

### Tools Available

- **Python Interpreter MCP**: Direct database query execution
- **Build Debug MCP**: Database connection testing
- **Web Debug MCP**: API endpoint testing

### Common Database Issues

#### Issue: Database Connection Failed

**Symptoms:**

- `psycopg2.OperationalError: could not connect to server`
- `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)`

**Debugging Steps:**

```python
# Using Python Interpreter MCP
from nexus_knowledge.db.session import get_session_dependency
session = get_session_dependency()
print("Database connection successful")

# Using Build Debug MCP
check_environment_config()
test_build_process()
```

**Solutions:**

1. Check if PostgreSQL is running: `docker-compose ps`
2. Verify database credentials in environment variables
3. Check network connectivity: `telnet localhost 5432`
4. Restart database service: `docker-compose restart db`

#### Issue: Migration Errors

**Symptoms:**

- `alembic.util.exc.CommandError: Can't locate revision`
- `sqlalchemy.exc.ProgrammingError: relation does not exist`

**Debugging Steps:**

```python
# Using Build Debug MCP
analyze_package_structure()
check_docker_build()
```

**Solutions:**

1. Check migration history: `alembic history`
2. Reset migrations: `alembic stamp head`
3. Run migrations: `python scripts/run_migrations.py`
4. Check database schema: `psql -h localhost -U user -d nexus_knowledge -c "\dt"`

---

## API Debugging

### Tools Available

- **Web Debug MCP**: HTTP request/response testing
- **Python Interpreter MCP**: API endpoint testing
- **Build Debug MCP**: Environment validation

### Common API Issues

#### Issue: API Endpoint Not Responding

**Symptoms:**

- `Connection refused` errors
- `404 Not Found` responses
- `500 Internal Server Error`

**Debugging Steps:**

```python
# Using Web Debug MCP
test_api_endpoint("http://localhost:8000/api/v1/status")
debug_nexus_api("/api/v1/status")
monitor_api_health()
```

**Solutions:**

1. Check if API server is running: `docker-compose ps`
2. Verify port configuration: `netstat -tlnp | grep 8000`
3. Check API logs: `docker-compose logs app`
4. Restart API service: `docker-compose restart app`

#### Issue: Authentication Errors

**Symptoms:**

- `401 Unauthorized` responses
- `403 Forbidden` responses
- `JWT token invalid` errors

**Debugging Steps:**

```python
# Using Web Debug MCP
analyze_http_error(401, "Unauthorized", "http://localhost:8000/api/v1/search")
```

**Solutions:**

1. Check API key configuration
2. Verify JWT token validity
3. Check CORS settings
4. Validate authentication headers

---

## Build and Dependency Debugging

### Tools Available

- **Build Debug MCP**: Comprehensive build analysis
- **Python Interpreter MCP**: Package testing
- **GitHub MCP**: Repository status monitoring

### Common Build Issues

#### Issue: Dependency Conflicts

**Symptoms:**

- `pip install` failures
- `ImportError: cannot import name`
- Version conflicts in requirements

**Debugging Steps:**

```python
# Using Build Debug MCP
check_dependencies()
analyze_dependency_conflicts()
test_build_process()
```

**Solutions:**

1. Check dependency versions: `pip list`
2. Resolve conflicts: `pip install --upgrade package-name`
3. Use virtual environment: `source .venv/bin/activate`
4. Reinstall dependencies: `pip install -r requirements.txt`

#### Issue: Docker Build Failures

**Symptoms:**

- `docker build` failures
- Container startup errors
- Port binding issues

**Debugging Steps:**

```python
# Using Build Debug MCP
check_docker_build()
test_build_process()
```

**Solutions:**

1. Check Dockerfile syntax
2. Verify base image availability
3. Check port conflicts: `netstat -tlnp | grep 8000`
4. Rebuild containers: `docker-compose build --no-cache`

---

## GitHub Integration Debugging

### Tools Available

- **GitHub MCP**: Repository management and monitoring
- **Build Debug MCP**: Local git status checking
- **Web Debug MCP**: GitHub API testing

### Common GitHub Issues

#### Issue: GitHub API Authentication Failed

**Symptoms:**

- `401 Unauthorized` from GitHub API
- `403 Forbidden` responses
- `GITHUB_PAT_KEY` not found errors

**Debugging Steps:**

```python
# Using GitHub MCP
get_repository_info()
get_local_git_status()
```

**Solutions:**

1. Set GitHub credentials:
   ```bash
   export GITHUB_PAT_KEY=your-pat-key
   export GITHUB_USERNAME=your-username
   ```
2. Check PAT permissions
3. Verify repository access
4. Regenerate PAT if expired

#### Issue: Git Operations Failed

**Symptoms:**

- `git push` failures
- `git pull` conflicts
- Branch synchronization issues

**Debugging Steps:**

```python
# Using GitHub MCP
get_local_git_status()
list_recent_commits()
```

**Solutions:**

1. Check git configuration: `git config --list`
2. Verify remote URL: `git remote -v`
3. Resolve merge conflicts
4. Check branch status: `git status`

---

## Docker Debugging

### Tools Available

- **Docker MCP**: Real-time container monitoring and debugging
- **Build Debug MCP**: Docker build validation and dependency checking
- **Web Debug MCP**: Container health endpoint testing

### Common Docker Issues

#### Issue: Container Won't Start

**Symptoms:**

- `docker-compose up` fails
- Container exits immediately
- Port binding errors
- Resource allocation failures

**Debugging Steps:**

```python
# Using Docker MCP
get_docker_status()
check_docker_health()
get_container_logs("container-name", lines=100)
debug_docker_issues()
```

**Solutions:**

1. Check Docker daemon: `docker info`
2. Verify port availability: `netstat -tlnp`
3. Check resource limits: `docker stats`
4. Review container logs: `docker logs container-name`
5. Validate Dockerfile syntax
6. Check environment variables

#### Issue: Build Process Fails

**Symptoms:**

- Docker build hangs or fails
- Dependency installation errors
- Multi-stage build issues
- Cache invalidation problems

**Debugging Steps:**

```python
# Using Docker MCP
monitor_docker_build()
analyze_docker_performance()
debug_docker_issues()
```

**Solutions:**

1. Clear Docker cache: `docker system prune -a`
2. Check Dockerfile layers
3. Verify base image availability
4. Use `--no-cache` flag for fresh builds
5. Check disk space: `df -h`
6. Validate build context

#### Issue: Container Performance Issues

**Symptoms:**

- High CPU usage
- Memory leaks
- Slow response times
- Resource exhaustion

**Debugging Steps:**

```python
# Using Docker MCP
analyze_docker_performance()
get_docker_status()
check_docker_health()
```

**Solutions:**

1. Monitor resource usage: `docker stats`
2. Check container limits
3. Optimize Dockerfile
4. Use multi-stage builds
5. Implement health checks
6. Scale containers appropriately

#### Issue: Service Communication Failures

**Symptoms:**

- Inter-container communication fails
- Network connectivity issues
- DNS resolution problems
- Service discovery failures

**Debugging Steps:**

```python
# Using Docker MCP
get_docker_status()
check_docker_health()
```

**Solutions:**

1. Check Docker network: `docker network ls`
2. Verify service names and ports
3. Test connectivity: `docker exec -it container ping other-container`
4. Check firewall rules
5. Validate docker-compose network configuration

---

## Web Debugging

### Tools Available

- **Web Debug MCP**: HTTP request/response testing
- **Python Interpreter MCP**: Web service testing
- **Build Debug MCP**: Network configuration

### Common Web Issues

#### Issue: CORS Errors

**Symptoms:**

- `CORS policy` errors in browser
- `Access-Control-Allow-Origin` issues
- Cross-origin request blocked

**Debugging Steps:**

```python
# Using Web Debug MCP
test_api_endpoint("http://localhost:8000/api/v1/search", headers={"Origin": "http://localhost:3000"})
```

**Solutions:**

1. Configure CORS settings in FastAPI
2. Add allowed origins to CORS_ORIGINS
3. Check preflight requests
4. Verify HTTPS/HTTP protocol matching

#### Issue: Request Timeouts

**Symptoms:**

- `TimeoutError` exceptions
- Slow API responses
- Connection timeouts

**Debugging Steps:**

```python
# Using Web Debug MCP
test_nexus_search_api("test query", limit=10)
monitor_api_health()
```

**Solutions:**

1. Increase timeout settings
2. Check database query performance
3. Optimize API endpoints
4. Monitor resource usage

---

## Common Issues and Solutions

### Environment Issues

#### Issue: Virtual Environment Not Activated

**Symptoms:**

- `ModuleNotFoundError` exceptions
- Package import failures
- Permission denied errors

**Solutions:**

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify activation
which python
pip list
```

#### Issue: Environment Variables Missing

**Symptoms:**

- `KeyError` for environment variables
- Configuration errors
- Service startup failures

**Solutions:**

```bash
# Check environment variables
env | grep -E "(DATABASE|REDIS|MLFLOW)"

# Set missing variables
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/nexus_knowledge"
export REDIS_URL="redis://localhost:6379/0"
```

### Docker Issues

#### Issue: Container Startup Failures

**Symptoms:**

- `docker-compose up` failures
- Container exit codes
- Port binding errors

**Solutions:**

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs app

# Restart services
docker-compose restart
```

#### Issue: Volume Mount Issues

**Symptoms:**

- File not found errors
- Permission denied errors
- Data persistence issues

**Solutions:**

```bash
# Check volume mounts
docker-compose config

# Fix permissions
sudo chown -R nexus:nexus ./db_data ./mlflow_data

# Recreate volumes
docker-compose down -v
docker-compose up
```

---

## MCP Server Management

### Starting MCP Servers

```bash
# Start all MCP servers
./scripts/start_web_debug_mcp.sh &
./scripts/start_build_debug_mcp.sh &
./scripts/start_github_mcp.sh &

# Check server status
ps aux | grep mcp
```

### Testing MCP Servers

```bash
# Test Python Interpreter MCP
python -c "import mcp; print('MCP SDK available')"

# Test Web Debug MCP
python -c "from nexus_knowledge.mcp.web_debug_server import test_api_endpoint; print('Web debug available')"

# Test Build Debug MCP
python -c "from nexus_knowledge.mcp.build_debug_server import check_dependencies; print('Build debug available')"

# Test GitHub MCP
python -c "from nexus_knowledge.mcp.github_server import get_repository_info; print('GitHub MCP available')"
```

### MCP Server Configuration

```json
{
  "mcpServers": {
    "python-interpreter": {
      "command": "python",
      "args": ["-m", "mcp_python_interpreter"]
    },
    "web-debug": {
      "command": "python",
      "args": ["src/nexus_knowledge/mcp/web_debug_server.py"]
    },
    "build-debug": {
      "command": "python",
      "args": ["src/nexus_knowledge/mcp/build_debug_server.py"]
    },
    "github": {
      "command": "python",
      "args": ["src/nexus_knowledge/mcp/github_server.py"],
      "env": {
        "GITHUB_PAT_KEY": "your-github-pat-key",
        "GITHUB_USERNAME": "your-github-username"
      }
    }
  }
}
```

---

## Emergency Procedures

### Complete System Reset

```bash
# Stop all services
docker-compose down

# Remove all data
sudo rm -rf db_data mlflow_data

# Recreate environment
docker-compose up --build

# Run migrations
python scripts/run_migrations.py
```

### Data Recovery

```bash
# Backup current data
tar -czf backup-$(date +%Y%m%d).tar.gz db_data mlflow_data

# Restore from backup
tar -xzf backup-YYYYMMDD.tar.gz
```

### Log Analysis

```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs db

# View Redis logs
docker-compose logs redis

# View MLflow logs
docker-compose logs mlflow
```

---

## Support and Resources

### Documentation

- [MCP.md](../MCP.md) - MCP server documentation
- [BUILD_PLAN.md](BUILD_PLAN.md) - Project build plan
- [API_SURFACE.md](API_SURFACE.md) - API documentation

### Community

- [GitHub Issues](https://github.com/NexusTheGroup/geminni_chat/issues)
- [MCP Documentation](https://modelcontextprotocol.io/)

### Contact

For additional support, create an issue in the project repository or contact the development team.

---

_Last updated: $(date)_
_Version: 1.0_
