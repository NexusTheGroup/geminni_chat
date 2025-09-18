import { mount } from 'cypress/react18'
import { Provider } from 'react-redux'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { store } from '../../src/store'
import { theme } from '../../src/theme'

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Custom mount command for React components with providers
Cypress.Commands.add('mount', (component, options = {}) => {
  const { reduxStore = store, ...mountOptions } = options

  const wrapped = (
    <Provider store={reduxStore}>
      <QueryClientProvider client={new QueryClient()}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          {component}
        </ThemeProvider>
      </QueryClientProvider>
    </Provider>
  )

  return mount(wrapped, mountOptions)
})

declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount
    }
  }
}
