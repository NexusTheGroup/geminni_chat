import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  LinearProgress,
} from '@mui/material'
import {
  TrendingUp as TrendingUpIcon,
  Insights as InsightsIcon,
  Timeline as TimelineIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  PlayArrow as PlayIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const Analytics: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [timeRange, setTimeRange] = useState('7d')

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  // Mock data for charts
  const conversationData = [
    { name: 'Mon', conversations: 12, messages: 45 },
    { name: 'Tue', conversations: 19, messages: 67 },
    { name: 'Wed', conversations: 15, messages: 52 },
    { name: 'Thu', conversations: 22, messages: 78 },
    { name: 'Fri', conversations: 18, messages: 63 },
    { name: 'Sat', conversations: 8, messages: 29 },
    { name: 'Sun', conversations: 6, messages: 21 },
  ]

  const sentimentData = [
    { name: 'Positive', value: 45, color: '#4caf50' },
    { name: 'Neutral', value: 35, color: '#2196f3' },
    { name: 'Negative', value: 20, color: '#f44336' },
  ]

  const correlationData = [
    { name: 'Topic A', correlations: 12, strength: 0.85 },
    { name: 'Topic B', correlations: 8, strength: 0.72 },
    { name: 'Topic C', correlations: 15, strength: 0.91 },
    { name: 'Topic D', correlations: 6, strength: 0.68 },
    { name: 'Topic E', correlations: 10, strength: 0.79 },
  ]

  const mockCorrelations = [
    {
      id: '1',
      source: 'Conversation 1',
      target: 'Document A',
      score: 0.92,
      status: 'CONFIRMED',
      rationale: 'High semantic similarity in technical concepts',
    },
    {
      id: '2',
      source: 'Conversation 2',
      target: 'Document B',
      score: 0.78,
      status: 'PENDING',
      rationale: 'Moderate correlation based on shared entities',
    },
    {
      id: '3',
      source: 'Conversation 3',
      target: 'Document C',
      score: 0.85,
      status: 'CONFIRMED',
      rationale: 'Strong thematic alignment in discussion topics',
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'CONFIRMED':
        return 'success'
      case 'PENDING':
        return 'warning'
      case 'REJECTED':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics & Insights
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Comprehensive analytics and correlation insights for your knowledge base
      </Typography>

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon color="primary" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Total Correlations
                </Typography>
              </Box>
              <Typography variant="h4" color="primary">
                247
              </Typography>
              <Typography variant="body2" color="text.secondary">
                +12% from last week
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <InsightsIcon color="secondary" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Active Analysis
                </Typography>
              </Box>
              <Typography variant="h4" color="secondary">
                89
              </Typography>
              <Typography variant="body2" color="text.secondary">
                15 pending review
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TimelineIcon color="success" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Success Rate
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                94%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Correlation accuracy
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircleIcon color="info" />
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Processed
                </Typography>
              </Box>
              <Typography variant="h4" color="info.main">
                1,247
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Data points analyzed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="analytics tabs"
        >
          <Tab label="Overview" />
          <Tab label="Correlations" />
          <Tab label="Trends" />
          <Tab label="Insights" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Conversation Activity
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={conversationData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="conversations" stroke="#1976d2" strokeWidth={2} />
                      <Line type="monotone" dataKey="messages" stroke="#dc004e" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Sentiment Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={sentimentData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {sentimentData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Correlation Analysis
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <FormControl size="small">
                  <InputLabel>Time Range</InputLabel>
                  <Select
                    value={timeRange}
                    label="Time Range"
                    onChange={(e) => setTimeRange(e.target.value)}
                  >
                    <MenuItem value="24h">Last 24 hours</MenuItem>
                    <MenuItem value="7d">Last 7 days</MenuItem>
                    <MenuItem value="30d">Last 30 days</MenuItem>
                  </Select>
                </FormControl>
                <Button startIcon={<RefreshIcon />} size="small">
                  Refresh
                </Button>
              </Box>
            </Box>

            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Source</TableCell>
                    <TableCell>Target</TableCell>
                    <TableCell>Score</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Rationale</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockCorrelations.map((correlation) => (
                    <TableRow key={correlation.id}>
                      <TableCell>{correlation.source}</TableCell>
                      <TableCell>{correlation.target}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={correlation.score * 100}
                            sx={{ width: 60, height: 8, borderRadius: 4 }}
                          />
                          <Typography variant="body2">
                            {correlation.score.toFixed(2)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={correlation.status}
                          size="small"
                          color={getStatusColor(correlation.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 200 }}>
                          {correlation.rationale}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <ViewIcon />
                        </IconButton>
                        <IconButton size="small" color="primary">
                          <PlayIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Correlation Strength by Topic
                  </Typography>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={correlationData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="strength" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Key Insights
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box sx={{ p: 2, backgroundColor: 'primary.light', borderRadius: 1 }}>
                      <Typography variant="body2" color="primary.contrastText">
                        <strong>High Correlation:</strong> Technical discussions show 85% correlation with documentation
                      </Typography>
                    </Box>
                    <Box sx={{ p: 2, backgroundColor: 'warning.light', borderRadius: 1 }}>
                      <Typography variant="body2" color="warning.contrastText">
                        <strong>Trend:</strong> Sentiment analysis indicates increasing positive engagement
                      </Typography>
                    </Box>
                    <Box sx={{ p: 2, backgroundColor: 'success.light', borderRadius: 1 }}>
                      <Typography variant="body2" color="success.contrastText">
                        <strong>Pattern:</strong> User questions follow predictable knowledge gaps
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recommendations
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                      <Typography variant="body2">
                        <strong>Content Gap:</strong> Create documentation for frequently asked questions
                      </Typography>
                    </Box>
                    <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                      <Typography variant="body2">
                        <strong>Optimization:</strong> Improve search relevance for technical terms
                      </Typography>
                    </Box>
                    <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                      <Typography variant="body2">
                        <strong>Enhancement:</strong> Consider implementing topic clustering
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>
    </Box>
  )
}

export default Analytics
