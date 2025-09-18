describe('Dashboard', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should display the dashboard with system metrics', () => {
    cy.get('[data-testid="dashboard-title"]').should('contain', 'Dashboard')
    cy.get('[data-testid="system-status"]').should('be.visible')
    cy.get('[data-testid="api-version"]').should('be.visible')
  })

  it('should show quick action cards', () => {
    cy.get('[data-testid="quick-actions"]').should('be.visible')
    cy.get('[data-testid="search-action"]').should('contain', 'Search Knowledge')
    cy.get('[data-testid="data-action"]').should('contain', 'Data Management')
    cy.get('[data-testid="analytics-action"]').should('contain', 'Analytics')
  })

  it('should navigate to search page when clicking search action', () => {
    cy.get('[data-testid="search-action"]').click()
    cy.url().should('include', '/search')
  })

  it('should display recent activity', () => {
    cy.get('[data-testid="recent-activity"]').should('be.visible')
    cy.get('[data-testid="activity-chips"]').should('have.length.greaterThan', 0)
  })
})
