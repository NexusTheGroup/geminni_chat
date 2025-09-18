describe('Search', () => {
  beforeEach(() => {
    cy.visit('/search')
  })

  it('should display the search interface', () => {
    cy.get('[data-testid="search-title"]').should('contain', 'Advanced Search')
    cy.get('[data-testid="search-input"]').should('be.visible')
    cy.get('[data-testid="search-button"]').should('be.visible')
  })

  it('should perform a search when clicking search button', () => {
    cy.get('[data-testid="search-input"]').type('test query')
    cy.get('[data-testid="search-button"]').click()

    // Mock API response
    cy.intercept('GET', '/api/v1/search*', {
      fixture: 'search-results.json'
    }).as('searchRequest')

    cy.wait('@searchRequest')
  })

  it('should show search history', () => {
    // Add some search history first
    cy.get('[data-testid="search-input"]').type('first search')
    cy.get('[data-testid="search-button"]').click()

    cy.get('[data-testid="search-input"]').type('second search')
    cy.get('[data-testid="search-button"]').click()

    cy.get('[data-testid="search-history"]').should('be.visible')
    cy.get('[data-testid="history-chip"]').should('have.length.greaterThan', 0)
  })

  it('should toggle filters panel', () => {
    cy.get('[data-testid="filters-toggle"]').click()
    cy.get('[data-testid="filters-panel"]').should('be.visible')

    cy.get('[data-testid="filters-toggle"]').click()
    cy.get('[data-testid="filters-panel"]').should('not.be.visible')
  })

  it('should display search results', () => {
    cy.get('[data-testid="search-input"]').type('test query')
    cy.get('[data-testid="search-button"]').click()

    // Mock successful search results
    cy.intercept('GET', '/api/v1/search*', {
      statusCode: 200,
      body: [
        {
          turnId: '123',
          conversationId: '456',
          turnIndex: 1,
          timestamp: '2024-01-15T10:30:00Z',
          snippet: 'Test search result',
          score: 0.95,
          sentiment: 'positive'
        }
      ]
    }).as('searchResults')

    cy.wait('@searchResults')
    cy.get('[data-testid="search-results"]').should('be.visible')
    cy.get('[data-testid="result-card"]').should('have.length', 1)
  })
})
