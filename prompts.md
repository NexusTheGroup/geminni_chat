PROMPTS.md — AI Agent Runbook
This file contains the high-level prompts for orchestrating the project.

## Final Kickoff Prompt

You are GPT-5 (via Codex), assuming the persona of The Weaver. The project environment is fully bootstrapped and all foundational documents are in place.

Your immediate objective is to execute Phase P0: AI-Led Planning.

Your primary inputs are the full contents of blueprint.md, AGENTS.md, and personas.md. You must adhere strictly to the processes defined within them.

### Deliverables:

Generate the following five planning artifacts. Ensure your plan fully incorporates the architectural layers for the User Feedback Loop, Knowledge Base Export (Obsidian), MLflow Experiment Tracking, and Data Version Control (DVC) as detailed in the blueprint.md.

1.  **`docs/BUILD_PLAN.md`**: Create a detailed, phase-by-phase implementation plan (P1-P5). Each task must have a clear description, dependencies, and specific, testable acceptance criteria.

2.  **`docs/TEST_MATRIX.md`**: Create a comprehensive testing plan that maps each feature from the blueprint to specific unit, integration, and end-to-end tests.

3.  **`docs/API_SURFACE.md`**: Generate a complete OpenAPI 3.0 specification sketch for all backend endpoints, including the new `/v1/feedback` endpoint.

4.  **`docs/DB_SCHEMA.sql`**: Generate the complete PostgreSQL 15 schema, including the necessary tables for storing user feedback data and any other entities required by the full blueprint.

5.  **Update `docs/TODO.md`**: Mark Phase P0 as complete and populate the subsequent phases with the high-level tasks generated in the `BUILD_PLAN.md`.

### Constraints:

- Operate strictly within the established framework (`AGENTS.md`, `CODE_QUALITY_FRAMEWORK.md`).
- Utilize the AI delegation strategy (`docs/AI_UTILIZATION_STRATEGY.md`) when creating the build plan, assigning personas and models to tasks. Orchestrate Grok-4, DeepSeek 3.1 (chat), and DeepThink (reasoning) as specified.
- Do not modify any files outside of the `docs/` directory during this planning phase.

### Acceptance and Handoff:

This phase is complete only when all five deliverables have been created, are internally consistent, and have been committed to the repository.

Upon completion, propose the detailed execution plan for Phase P1 and then await the command to proceed.

## P6 Implementation Prompt

You are an AI agent assigned to implement Phase P6: Advanced Web GUI & User Experience Enhancement. Your objective is to transform the basic HTML interface into a comprehensive, modern web application.

### Context:

- **Current State**: Basic HTML shell in `src/nexus_knowledge/api/main.py` with minimal functionality
- **Available APIs**: 14 fully functional API endpoints for comprehensive system management
- **Target**: Modern React/TypeScript web application with advanced UX features

### Primary Inputs:

- `docs/P6_IMPLEMENTATION_GUIDE.md` - Comprehensive technical specifications
- `docs/BUILD_PLAN.md` - P6 phase tasks (P6.1 through P6.6)
- `docs/API_SURFACE.md` - Complete API endpoint documentation
- `src/nexus_knowledge/api/main.py` - Current basic HTML implementation

### Implementation Strategy:

**P6.1: Modern Frontend Architecture Setup**

- Establish React/TypeScript project with Vite build system
- Implement component-based architecture with Material-UI or Chakra UI
- Set up state management (Redux Toolkit or Zustand)
- Configure development environment and build pipeline

**P6.2: System Dashboard & Navigation**

- Create comprehensive system overview dashboard
- Implement sidebar navigation with main sections
- Build real-time system status integration
- Add global search functionality and user preferences

**P6.3: Enhanced Search & Discovery Interface**

- Implement advanced search with multi-faceted filtering
- Build conversation explorer with timeline view
- Add search suggestions and saved searches
- Create search result clustering and visualization

**P6.4: Data Management & Analytics Dashboard**

- Build data ingestion and pipeline monitoring interface
- Implement analytics visualization with charts and graphs
- Create export tools and import management
- Add data quality indicators and validation display

**P6.5: Advanced Features & Tools Integration**

- Implement correlation analysis visualization interface
- Build export tools with multiple format support
- Add system configuration and notification system
- Integrate all 14 API endpoints with proper error handling

**P6.6: Performance Optimization & Polish**

- Optimize bundle size and implement lazy loading
- Ensure WCAG 2.1 accessibility compliance
- Implement mobile responsiveness across all devices
- Add comprehensive testing (unit, integration, e2e)

### Technical Requirements:

- **Framework**: React 18+ with TypeScript 5+
- **Build Tool**: Vite for fast development and building
- **UI Library**: Material-UI or Chakra UI for consistent components
- **State Management**: Redux Toolkit or Zustand for complex state
- **HTTP Client**: React Query for efficient API state management
- **Styling**: Styled-components or Tailwind CSS
- **Testing**: Jest, React Testing Library, Cypress for e2e

### Success Criteria:

- **Performance**: Page load time < 2 seconds, Lighthouse score > 90
- **Accessibility**: WCAG 2.1 compliance, keyboard navigation
- **Responsiveness**: Mobile-first design across all device sizes
- **Functionality**: Full integration with all 14 API endpoints
- **Testing**: > 90% code coverage, comprehensive test suite

### Constraints:

- Follow existing project structure and coding standards
- Maintain compatibility with existing backend APIs
- Ensure proper error handling and user feedback
- Implement proper TypeScript types for all API interactions
- Follow the CODE_QUALITY_FRAMEWORK.md guidelines

### Deliverables:

- Complete frontend application in `frontend/` directory
- Updated build pipeline and deployment configuration
- Comprehensive test suite with > 90% coverage
- Updated documentation for frontend development
- Performance optimization and accessibility compliance

### Handoff:

This phase is complete when the modern web application is fully functional, tested, and deployed, providing an exceptional user experience that leverages all backend capabilities.

## P7 Quality Assurance & Validation Prompt

You are GPT-5 (via Codex), assuming the persona of **QC/Debugger Persona**. The frontend application (P6) has been implemented and your objective is to execute **Phase P7: Quality Assurance & Validation**.

### Mission Context

Perform comprehensive quality assurance, security validation, and performance optimization of the complete web application system to ensure production readiness.

### Primary Inputs & References

1. **`docs/BUILD_PLAN.md`** - P7 phase tasks (P7.1 through P7.6) with acceptance criteria
2. **`docs/CODE_QUALITY_FRAMEWORK.md`** - Quality scoring framework (minimum 85/100)
3. **`frontend/`** - Complete frontend application from P6
4. **`src/nexus_knowledge/api/main.py`** - Backend API endpoints
5. **`docs/API_SURFACE.md`** - Complete API endpoint documentation
6. **`docs/TROUBLESHOOTING.md`** - MCP debugging guide for comprehensive testing

### Implementation Strategy

**P7.1: Code Quality & Security Audit**

- Perform comprehensive code quality analysis using static analysis tools
- Conduct security audit and vulnerability assessment
- Validate dependency security and update vulnerable packages
- Ensure code meets minimum quality score of 85/100
- Generate security audit report and vulnerability assessment

**P7.2: Performance & Accessibility Validation**

- Run comprehensive performance testing with Lighthouse
- Validate accessibility compliance (WCAG 2.1 AA)
- Test page load times and ensure < 2 seconds consistently
- Validate mobile responsiveness across all device sizes
- Confirm cross-browser compatibility
- Generate performance audit and accessibility compliance reports

**P7.3: Integration & API Testing**

- Test all 14 API endpoints integration with frontend
- Validate error handling for all failure scenarios
- Test real-time updates and WebSocket connections
- Confirm data flow integrity across all components
- Generate integration test suite and API testing results

**P7.4: User Experience & Usability Testing**

- Conduct comprehensive user experience testing
- Validate user task completion rates (> 95%)
- Test search success rates (> 90%)
- Measure user satisfaction scores (> 4.5/5)
- Optimize all user journeys and resolve usability issues
- Generate UX testing report and usability analysis

**P7.5: Documentation & Deployment Validation**

- Review and validate all documentation completeness
- Test deployment process and document procedures
- Complete production readiness checklist
- Configure monitoring and observability
- Document backup and recovery procedures
- Generate documentation audit and deployment validation report

**P7.6: Final System Validation & Sign-off**

- Perform final comprehensive system validation
- Ensure all quality gates passed successfully
- Validate system meets all performance and accessibility targets
- Confirm security audit passed with no critical issues
- Achieve user experience targets
- Validate production deployment
- Generate final validation report and project sign-off

### Quality Framework Compliance

**Minimum Score to Merge: 85/100**

**Static Analysis & Maintainability (40 points):**

- Linter & Formatter Compliance (20 pts): 100% compliant with Ruff and Prettier rules
- Complexity Score (10 pts): Cyclomatic complexity within acceptable limits
- Docstrings & Comments (10 pts): All public modules, classes, and functions have clear docstrings

**Test Coverage & Reliability (30 points):**

- Unit Test Coverage (20 pts): Code coverage meets or exceeds 80%
- Integration & E2E Tests (10 pts): All new features covered by integration or e2e tests

**Security & Vulnerability Analysis (20 points):**

- SAST Scan (10 pts): No critical or high-severity vulnerabilities
- Dependency Scan (10 pts): No known critical vulnerabilities in dependencies

**AI-Powered Qualitative Review (10 points):**

- Readability & Idiomatic Code (5 pts): Clear, understandable, language-specific best practices
- Architectural Adherence (5 pts): Implementation aligns with blueprint.md and architectural documents

### MCP Integration for QC Testing

**Available MCP Servers for P7 Validation:**

- **Web Debug MCP**: HTTP/API testing and error analysis
- **Build Debug MCP**: Build and dependency validation
- **Python Interpreter MCP**: Interactive debugging and testing
- **GitHub MCP**: Repository monitoring and CI/CD validation

### Success Criteria

**Performance Targets:**

- Lighthouse performance score > 90
- Accessibility score > 95 (WCAG 2.1 AA compliance)
- Page load times < 2 seconds consistently
- Mobile responsiveness 100% across all devices

**Quality Targets:**

- Code quality score > 85/100
- Security audit passed with no critical issues
- User task completion rate > 95%
- Search success rate > 90%
- User satisfaction score > 4.5/5

**Technical Targets:**

- All 14 API endpoints properly integrated and tested
- Cross-browser compatibility confirmed
- Real-time updates and WebSocket connections validated
- Data flow integrity confirmed across all components

### Deliverables

1. **Security Audit Report** with vulnerability assessment
2. **Performance Audit Report** with Lighthouse scores and optimization recommendations
3. **Accessibility Compliance Validation** with WCAG 2.1 AA compliance report
4. **Integration Test Suite** with API testing results
5. **UX Testing Report** with usability analysis and user journey optimization
6. **Documentation Audit** with completeness validation
7. **Deployment Validation Report** with production readiness assessment
8. **Final Validation Report** with quality gate approval and project sign-off

### Acceptance and Handoff

This phase is complete when:

- All quality gates passed successfully (85/100 minimum)
- System meets all performance and accessibility targets
- Security audit passed with no critical issues
- User experience targets achieved
- Production deployment validated
- All documentation is complete and up-to-date
- Final validation report and project sign-off documentation generated

**Begin implementation with P7.1: Code Quality & Security Audit to establish the foundation for comprehensive quality assurance.**
