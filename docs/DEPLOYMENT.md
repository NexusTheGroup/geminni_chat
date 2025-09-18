# Deployment Guide: NexusKnowledge Project

This document provides comprehensive deployment instructions for the NexusKnowledge system.

## Prerequisites

- Docker and Docker Compose installed
- Environment variables configured (see `docs/ENV.md`)
- Git repository cloned

## Quick Start Deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd geminni_chat
```

### 2. Set Environment Variables

Add the following to your `~/.bashrc` or `~/.zshrc`:

```bash
export GITHUB_USERNAME="your_github_username"
export GITHUB_PAT_KEY="github_pat_..."
export XAI_API_KEY="your_grok_api_key"
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export ORCHESTRATOR_MODE="codex"
```

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:

- PostgreSQL database on port 5432
- Redis on port 6379
- MLflow tracking server on port 5000
- FastAPI backend on port 8000
- React frontend on port 3000
- Celery worker for async tasks

### 4. Verify Deployment

Check that all services are running:

```bash
docker-compose ps
```

Test the API:

```bash
curl http://localhost:8000/api/v1/status
```

Access the web interface:

- Frontend: http://localhost:3000
- MLflow UI: http://localhost:5000

## Production Deployment

### Environment Configuration

For production, ensure the following environment variables are set:

```bash
# Database
DATABASE_URL=postgresql+psycopg2://user:password@db:5432/nexus_knowledge

# Redis
REDIS_URL=redis://redis:6379/0

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=NexusKnowledge
VITE_APP_VERSION=1.0.0
```

### Security Considerations

1. **Database Security**:

   - Change default PostgreSQL credentials
   - Enable SSL connections
   - Set up proper firewall rules

2. **API Security**:

   - Implement rate limiting
   - Add authentication/authorization
   - Enable CORS for frontend communication

3. **Network Security**:
   - Use reverse proxy (nginx) for SSL termination
   - Set up proper network segmentation
   - Monitor for suspicious activity

### Monitoring and Observability

The system includes built-in monitoring capabilities:

1. **MLflow Tracking**: Experiment tracking and model monitoring
2. **Database Monitoring**: PostgreSQL metrics and query performance
3. **API Monitoring**: FastAPI built-in metrics and health checks

### Backup and Recovery

#### Database Backups

```bash
# Backup PostgreSQL database
docker exec nexus-db pg_dump -U user nexus_knowledge > backup.sql

# Restore from backup
cat backup.sql | docker exec -i nexus-db psql -U user nexus_knowledge
```

#### Data Volume Backups

```bash
# Backup database volume
tar -czf db_backup.tar.gz db_data/

# Backup MLflow data
tar -czf mlflow_backup.tar.gz mlflow_data/
```

#### DVC Data Versioning

For data assets managed by DVC:

```bash
# Push data to remote storage
dvc push

# Pull data from remote storage
dvc pull
```

### Scaling Considerations

#### Horizontal Scaling

- Add more Celery workers: `docker-compose scale worker=3`
- Use Redis cluster for distributed task queue
- Implement database read replicas

#### Vertical Scaling

- Increase database memory and CPU resources
- Optimize PostgreSQL configuration
- Add caching layers

### Troubleshooting

#### Common Issues

1. **Database Connection Issues**:

   ```bash
   docker logs nexus-db
   docker exec -it nexus-db psql -U user nexus_knowledge
   ```

2. **API Service Issues**:

   ```bash
   docker logs nexus-app
   curl http://localhost:8000/api/v1/status
   ```

3. **Frontend Issues**:

   ```bash
   docker logs nexus-frontend
   ```

4. **Worker Issues**:
   ```bash
   docker logs nexus-worker
   ```

#### Logs and Monitoring

View logs for all services:

```bash
docker-compose logs -f
```

View logs for specific service:

```bash
docker-compose logs app
docker-compose logs worker
docker-compose logs db
```

## Maintenance

### Regular Tasks

1. **Database Maintenance**:
   ```bash
   # Vacuum database
   docker exec nexus-db vacuumdb -U user nexus_knowledge
   ```

# Check database size

docker exec nexus-db psql -U user -c "SELECT pg_size_pretty(pg_database_size('nexus_knowledge'));"

```

2. **Log Rotation**:
- Configure Docker log rotation
- Monitor disk usage

3. **Security Updates**:
- Regularly update Docker images
- Apply security patches
- Rotate API keys and credentials

### Performance Optimization

1. **Database Optimization**:
- Create appropriate indexes
- Optimize queries
- Monitor slow queries

2. **API Optimization**:
- Implement caching
- Optimize response times
- Monitor API performance

3. **Frontend Optimization**:
- Bundle optimization
- CDN for static assets
- Browser caching

## Support

For deployment issues, refer to:
- `docs/TROUBLESHOOTING.md` for comprehensive debugging guide
- MCP servers for real-time debugging assistance
- GitHub issues for known problems and solutions
```
