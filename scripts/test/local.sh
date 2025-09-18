#!/bin/bash
# Local test runner script that sets up environment and runs pytest with correct configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up test environment...${NC}"

# Set default environment variables for tests (these can be overridden)
export DATABASE_URL="${DATABASE_URL:-sqlite:///test_nexus_knowledge.db}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export MLFLOW_TRACKING_URI="${MLFLOW_TRACKING_URI:-file://$(pwd)/mlruns}"
export SECRET_KEY="${SECRET_KEY:-test-secret-key-for-testing-purposes-only}"
export APP_ENV="${APP_ENV:-test}"
# LOG_LEVEL is intentionally not set to allow tests to use application defaults

# Disable plugin autoload to avoid interference
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

echo -e "${YELLOW}Environment variables set:${NC}"
echo "DATABASE_URL=$DATABASE_URL"
echo "REDIS_URL=$REDIS_URL"
echo "MLFLOW_TRACKING_URI=$MLFLOW_TRACKING_URI"
echo "APP_ENV=$APP_ENV"
echo "LOG_LEVEL=${LOG_LEVEL:-INFO} (using default if not set)"
echo "PYTEST_DISABLE_PLUGIN_AUTOLOAD=$PYTEST_DISABLE_PLUGIN_AUTOLOAD"

echo -e "${YELLOW}Running tests...${NC}"

# Run pytest with the proper configuration
if command -v pytest >/dev/null 2>&1; then
    pytest "$@"
elif [ -f "venv/bin/pytest" ]; then
    venv/bin/pytest "$@"
elif [ -f ".venv/bin/pytest" ]; then
    .venv/bin/pytest "$@"
else
    echo -e "${RED}Error: pytest not found. Please install pytest or activate your virtual environment.${NC}"
    echo "Try: pip install pytest"
    exit 1
fi

echo -e "${GREEN}Tests completed!${NC}"
