import React from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  LinearProgress,
} from '@mui/material'
import {
  Search as SearchIcon,
  Storage as DataIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'
import { useGetStatusQuery } from '../store/api'
import { useSelector } from 'react-redux'
import { RootState } from '../store'

const Dashboard: React.FC = () => {
  const { data: status, isLoading, error } = useGetStatusQuery()
  const { notifications } = useSelector((state: RootState) => state.ui)

  const systemMetrics = [
    {
      title: 'System Status',
      value: status?.status || 'Unknown',
      icon: <CheckCircleIcon color="success" />,
      color: 'success',
    },
    {
      title: 'API Version',
      value: status?.version || 'Unknown',
      icon: <AnalyticsIcon color="primary" />,
      color: 'primary',
    },
    {
      title: 'Active Notifications',
      value: notifications.length.toString(),
      icon: <WarningIcon color="warning" />,
      color: 'warning',
    },
    {
      title: 'System Health',
      value: '95%',
      icon: <TrendingUpIcon color="success" />,
      color: 'success',
    },
  ]

  const quickActions = [
    {
      title: 'Search Knowledge',
      description: 'Search through conversations and knowledge base',
      icon: <SearchIcon />,
      color: 'primary',
      path: '/search',
    },
    {
      title: 'Data Management',
      description: 'Manage data ingestion and processing',
      icon: <DataIcon />,
      color: 'secondary',
      path: '/data',
    },
    {
      title: 'Analytics',
      description: 'View insights and correlations',
      icon: <AnalyticsIcon />,
      color: 'info',
      path: '/analytics',
    },
  ]

  if (isLoading) {
    return (
      <Box sx={{ width: '100%' }}>
        <LinearProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <ErrorIcon color="error" sx={{ fontSize: 48, mb: 2 }} />
        <Typography variant="h6" color="error" gutterBottom>
          Failed to load system status
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Please check your connection and try again.
        </Typography>
      </Paper>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Welcome to NexusKnowledge - Your advanced knowledge management system
      </Typography>

      {/* System Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {systemMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card data-testid={`metric-card-${index}`}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {metric.icon}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {metric.title}
                  </Typography>
                </Box>
                <Typography variant="h4" color={`${metric.color}.main`}>
                  {metric.value}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Actions */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3} data-testid="quick-actions">
        {quickActions.map((action, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Card sx={{ height: '100%' }} data-testid={`${action.title.toLowerCase().replace(/\s+/g, '-')}-action`}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 1,
                      backgroundColor: `${action.color}.light`,
                      color: `${action.color}.contrastText`,
                      mr: 2,
                    }}
                  >
                    {action.icon}
                  </Box>
                  <Typography variant="h6">
                    {action.title}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {action.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  variant="contained"
                  color={action.color as any}
                  fullWidth
                  href={action.path}
                >
                  Go to {action.title}
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Recent Activity */}
      <Paper sx={{ p: 3, mt: 4 }} data-testid="recent-activity">
        <Typography variant="h5" gutterBottom>
          Recent Activity
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }} data-testid="activity-chips">
          <Chip label="System initialized" color="success" size="small" />
          <Chip label="API endpoints active" color="primary" size="small" />
          <Chip label="Database connected" color="success" size="small" />
          <Chip label="Search engine ready" color="info" size="small" />
        </Box>
      </Paper>
    </Box>
  )
}

export default Dashboard
