import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@mui/material/styles'
import { store } from '../../store'
import { theme } from '../../theme'
import Dashboard from '../Dashboard'

// Mock the API hook
jest.mock('../../store/api', () => ({
  useGetStatusQuery: () => ({
    data: {
      status: 'operational',
      version: '1.0.0'
    },
    isLoading: false,
    error: null
  })
}))

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

describe('Dashboard', () => {
  it('renders dashboard title', () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    )

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('displays system metrics', async () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText('System Status')).toBeInTheDocument()
      expect(screen.getByText('API Version')).toBeInTheDocument()
      expect(screen.getByText('operational')).toBeInTheDocument()
      expect(screen.getByText('1.0.0')).toBeInTheDocument()
    })
  })

  it('shows quick action cards', () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    )

    expect(screen.getByText('Quick Actions')).toBeInTheDocument()
    expect(screen.getByText('Search Knowledge')).toBeInTheDocument()
    expect(screen.getByText('Data Management')).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
  })

  it('displays recent activity section', () => {
    render(
      <TestWrapper>
        <Dashboard />
      </TestWrapper>
    )

    expect(screen.getByText('Recent Activity')).toBeInTheDocument()
  })
})
