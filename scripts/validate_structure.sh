#!/bin/bash
set -e

echo "🛡️ Validating repository structure..."

EXPECTED=(
  ".devcontainer"
  ".github"
  "docs"
  "scripts"
  "src"
  "tests"
  ".gitignore"
  ".pre-commit-config.yaml"
  "AGENTS.md"
  "README.md"
  "blueprint.md"
  "docker-compose.yml"
  "package.json"
  "personas.md"
  "prompts.md"
  "pyproject.toml"
)

ACTUAL=($(ls -A1))
MISSING=()

for item in "${EXPECTED[@]}"; do
  if [[ ! " ${ACTUAL[@]} " =~ " ${item} " ]]; then
    MISSING+=("$item")
  fi
done

if [ ${#MISSING[@]} -ne 0 ]; then
  echo "❌ Structure-Guard Failed! Missing:"
  printf -- '- %s
' "${MISSING[@]}"
  exit 1
fi

echo "✅ Repository structure is valid."
