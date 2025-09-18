import React from 'react'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@mui/material/styles'
import { store } from '../../store'
import { theme } from '../../theme'
import Layout from '../Layout/Layout'

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Provider store={store}>
    <QueryClientProvider client={new QueryClient()}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  </Provider>
)

describe('Layout', () => {
  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <Layout>
          <div>Test content</div>
        </Layout>
      </TestWrapper>
    )

    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('renders header with title', () => {
    render(
      <TestWrapper>
        <Layout>
          <div>Test content</div>
        </Layout>
      </TestWrapper>
    )

    expect(screen.getByText('NexusKnowledge')).toBeInTheDocument()
  })

  it('renders sidebar navigation', () => {
    render(
      <TestWrapper>
        <Layout>
          <div>Test content</div>
        </Layout>
      </TestWrapper>
    )

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Search')).toBeInTheDocument()
    expect(screen.getByText('Data Management')).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })
})
