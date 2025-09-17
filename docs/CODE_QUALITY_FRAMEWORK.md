# Code Quality Scoring Framework

This document defines the automated quality gate that all code must pass before being merged. The **QC/Debugger** persona enforces these rules.

**Minimum Score to Merge: 85 / 100**

---

## Scoring Axes

### 1. Static Analysis & Maintainability (40 points)
*   **Linter & Formatter Compliance (20 pts):** Code is 100% compliant with Ruff and Prettier rules. No violations are present.
*   **Complexity Score (10 pts):** Cyclomatic complexity is within acceptable limits (details TBD).
*   **Docstrings & Comments (10 pts):** All public modules, classes, and functions have clear, concise docstrings.

### 2. Test Coverage & Reliability (30 points)
*   **Unit Test Coverage (20 pts):** Code coverage meets or exceeds the project minimum of 80%.
*   **Integration & E2E Tests (10 pts):** All new features are covered by at least one integration or end-to-end test.

### 3. Security & Vulnerability Analysis (20 points)
*   **SAST Scan (10 pts):** No critical or high-severity vulnerabilities are found by static analysis security testing tools.
*   **Dependency Scan (10 pts):** No known critical vulnerabilities exist in any third-party dependencies.

### 4. AI-Powered Qualitative Review (10 points)
*   **Readability & Idiomatic Code (5 pts):** Code is clear, understandable, and follows language-specific best practices.
*   **Architectural Adherence (5 pts):** The implementation aligns with the designs laid out in `blueprint.md` and other architectural documents.
