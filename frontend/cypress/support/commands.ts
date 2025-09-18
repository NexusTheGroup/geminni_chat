/// <reference types="cypress" />

// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>
      drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
      dismiss(selector: string): Chainable<Element>
      visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
    }
  }
}

// Custom command for API mocking
Cypress.Commands.add('mockApi', (method: string, url: string, response: any) => {
  cy.intercept(method, url, response).as('mockApi')
})

// Custom command for waiting for API calls
Cypress.Commands.add('waitForApi', (alias: string) => {
  cy.wait(`@${alias}`)
})

// Custom command for testing accessibility
Cypress.Commands.add('checkA11y', () => {
  cy.injectAxe()
  cy.checkA11y()
})
