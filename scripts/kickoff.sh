#!/bin/bash
set -e

echo "🚀 Kicking off project structure setup..."

# Create core directories (idempotent)
mkdir -p .github/workflows docs scripts src tests

# Create empty planning documents
touch docs/BUILD_PLAN.md docs/TEST_MATRIX.md docs/API_SURFACE.md docs/DB_SCHEMA.sql

echo "✅ Project structure created."
