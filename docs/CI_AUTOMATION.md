# CI/CD Automation Guide

This document describes the automated tools and processes set up to maintain code quality and keep dependencies up-to-date.

## Automated Dependency Updates

### Dependabot Configuration (`.github/dependabot.yml`)

Dependabot automatically creates pull requests to update:

- **GitHub Actions** (weekly) - Keeps workflow actions up-to-date
- **Python dependencies** (weekly) - Updates packages in `pyproject.toml`
- **Docker dependencies** (weekly) - Updates base images and tools

**Benefits:**
- Prevents using deprecated actions (like `actions/upload-artifact@v3`)
- Keeps security vulnerabilities patched
- Maintains compatibility with latest tools

### Manual Actions Update Script

For immediate updates, use the maintenance script:

```bash
# Install dependencies (if not already installed)
pip install requests

# Run the update script
python scripts/ci/update-actions.py
```

This script:
- Fetches latest versions from GitHub API
- Updates all workflow files automatically
- Validates changes with actionlint (if available)

## Code Quality Automation

### Pre-commit Hooks

Automatically run on every commit:
- **black** - Code formatting
- **ruff** - Linting and auto-fixes
- **prettier** - YAML/JSON formatting
- **actionlint** - GitHub Actions validation
- **bandit** - Security scanning

Install and activate:
```bash
pip install pre-commit
pre-commit install
```

### GitHub Actions Workflows

#### 1. Test Workflow (`.github/workflows/test.yml`)
- Runs on every push and PR
- Executes full test suite with environment setup
- Uses caching for faster builds
- Uploads test artifacts for debugging

#### 2. Lint Workflow (`.github/workflows/lint.yml`)
- Validates GitHub Actions syntax with actionlint
- Checks Python code formatting and style
- Runs security and type checking

#### 3. Auto-fix Workflow (`.github/workflows/auto-fix.yml`)
- Automatically fixes formatting issues on feature branches
- Can be triggered manually via GitHub UI
- Commits fixes back to the branch

## Preventing Common Issues

### GitHub Actions Deprecation

**Problem:** Actions like `upload-artifact@v3` become deprecated
**Solution:**
- Dependabot creates PRs for updates automatically
- Manual script available for immediate fixes
- actionlint catches deprecated usage in pre-commit

### Code Formatting Drift

**Problem:** Inconsistent code style across contributors
**Solution:**
- Pre-commit hooks enforce formatting before commit
- Auto-fix workflow repairs formatting on feature branches
- CI fails if formatting is inconsistent

### Security Vulnerabilities

**Problem:** Dependencies with known security issues
**Solution:**
- Dependabot updates vulnerable packages
- bandit scans for security anti-patterns
- safety checks for known CVEs (in lint workflow)

## Usage Examples

### Updating GitHub Actions Manually

```bash
# Check current versions
grep -r "uses:" .github/workflows/

# Run update script
python scripts/ci/update-actions.py

# Validate changes
pre-commit run actionlint-docker --all-files
```

### Fixing Code Style Issues

```bash
# Auto-fix locally
pre-commit run --all-files

# Or trigger auto-fix workflow in GitHub
# Go to Actions → Auto-fix Code Issues → Run workflow
```

### Reviewing Dependabot PRs

1. Check the changelog/release notes for breaking changes
2. Ensure tests pass in the PR
3. Merge if everything looks good
4. Dependabot will automatically rebase/update related PRs

## Troubleshooting

### Pre-commit Hook Failures

If hooks fail:
```bash
# See what changed
git diff

# Fix manually or auto-fix
pre-commit run --all-files

# Add and commit
git add .
git commit -m "fix: resolve linting issues"
```

### GitHub Actions Failures

Common issues:
- **Deprecated actions**: Update with Dependabot or manual script
- **Missing dependencies**: Check cache configuration
- **Permission issues**: Verify GITHUB_TOKEN permissions

### Tool Installation

If tools are missing:
```bash
# Python tools
pip install black ruff mypy bandit safety pre-commit

# actionlint (Go required)
go install github.com/rhysd/actionlint/cmd/actionlint@latest

# Or use Docker version in pre-commit
```

## Best Practices

1. **Enable Dependabot**: Merge dependency updates promptly
2. **Use pre-commit hooks**: Catch issues before they reach CI
3. **Monitor workflows**: Set up notifications for failed builds
4. **Regular maintenance**: Run update scripts monthly
5. **Test changes**: Always validate automated fixes in feature branches

This automation setup significantly reduces maintenance overhead and prevents common CI/CD issues from occurring.