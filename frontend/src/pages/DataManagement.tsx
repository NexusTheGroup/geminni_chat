import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Upload as UploadIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material'
import { useIngestMutation, useGetIngestionStatusQuery } from '../store/api'

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
      id={`data-tabpanel-${index}`}
      aria-labelledby={`data-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const DataManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [ingestionDialog, setIngestionDialog] = useState(false)
  const [ingestionForm, setIngestionForm] = useState({
    sourceType: '',
    content: '',
    metadata: '',
    sourceId: '',
  })

  const [ingest, { isLoading: isIngesting }] = useIngestMutation()

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handleIngestionSubmit = async () => {
    try {
      const payload = {
        sourceType: ingestionForm.sourceType,
        content: JSON.parse(ingestionForm.content),
        metadata: ingestionForm.metadata ? JSON.parse(ingestionForm.metadata) : undefined,
        sourceId: ingestionForm.sourceId || undefined,
      }

      await ingest(payload).unwrap()
      setIngestionDialog(false)
      setIngestionForm({ sourceType: '', content: '', metadata: '', sourceId: '' })
    } catch (error) {
      console.error('Ingestion failed:', error)
    }
  }

  const mockDataItems = [
    {
      id: '1',
      sourceType: 'conversation',
      status: 'NORMALIZED',
      timestamp: '2024-01-15T10:30:00Z',
      size: '2.3 MB',
    },
    {
      id: '2',
      sourceType: 'document',
      status: 'ANALYZED',
      timestamp: '2024-01-15T09:15:00Z',
      size: '1.8 MB',
    },
    {
      id: '3',
      sourceType: 'conversation',
      status: 'PROCESSING',
      timestamp: '2024-01-15T08:45:00Z',
      size: '3.1 MB',
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'NORMALIZED':
      case 'ANALYZED':
        return 'success'
      case 'PROCESSING':
        return 'warning'
      case 'ERROR':
        return 'error'
      default:
        return 'default'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'NORMALIZED':
      case 'ANALYZED':
        return <CheckCircleIcon />
      case 'PROCESSING':
        return <ScheduleIcon />
      case 'ERROR':
        return <ErrorIcon />
      default:
        return null
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Data Management
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage data ingestion, processing, and export operations
      </Typography>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="data management tabs"
        >
          <Tab label="Ingestion" />
          <Tab label="Processing Status" />
          <Tab label="Export" />
          <Tab label="Analytics" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Ingest
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Upload and process new data sources
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<UploadIcon />}
                    onClick={() => setIngestionDialog(true)}
                    fullWidth
                  >
                    Start Data Ingestion
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    System Status
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Processing Queue
                    </Typography>
                    <LinearProgress variant="determinate" value={65} sx={{ mb: 1 }} />
                    <Typography variant="body2">3 items processing</Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Storage Usage
                    </Typography>
                    <LinearProgress variant="determinate" value={42} sx={{ mb: 1 }} />
                    <Typography variant="body2">42% of 100GB used</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Processing Status
              </Typography>
              <Button startIcon={<RefreshIcon />} size="small">
                Refresh
              </Button>
            </Box>

            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Source Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockDataItems.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.id}</TableCell>
                      <TableCell>
                        <Chip label={item.sourceType} size="small" />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusIcon(item.status)}
                          <Chip
                            label={item.status}
                            size="small"
                            color={getStatusColor(item.status) as any}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        {new Date(item.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell>{item.size}</TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <ViewIcon />
                        </IconButton>
                        <IconButton size="small" color="error">
                          <DeleteIcon />
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
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Export to Obsidian
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Export processed data to Obsidian-compatible format
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<DownloadIcon />}
                    fullWidth
                  >
                    Export to Obsidian
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Export History
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Last export: 2024-01-15 10:30 AM
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Files exported: 15
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            Data Analytics
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="primary">
                    1,247
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Documents
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="secondary">
                    89
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Conversations
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="success.main">
                    2.3 GB
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Data Processed
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      {/* Ingestion Dialog */}
      <Dialog open={ingestionDialog} onClose={() => setIngestionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Data Ingestion</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Source Type</InputLabel>
                <Select
                  value={ingestionForm.sourceType}
                  label="Source Type"
                  onChange={(e) => setIngestionForm({ ...ingestionForm, sourceType: e.target.value })}
                >
                  <MenuItem value="conversation">Conversation</MenuItem>
                  <MenuItem value="document">Document</MenuItem>
                  <MenuItem value="webpage">Web Page</MenuItem>
                  <MenuItem value="api">API Response</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Source ID (Optional)"
                value={ingestionForm.sourceId}
                onChange={(e) => setIngestionForm({ ...ingestionForm, sourceId: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Content (JSON)"
                value={ingestionForm.content}
                onChange={(e) => setIngestionForm({ ...ingestionForm, content: e.target.value })}
                placeholder='{"messages": [{"role": "user", "content": "Hello"}]}'
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Metadata (JSON, Optional)"
                value={ingestionForm.metadata}
                onChange={(e) => setIngestionForm({ ...ingestionForm, metadata: e.target.value })}
                placeholder='{"author": "John Doe", "tags": ["important"]}'
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIngestionDialog(false)}>Cancel</Button>
          <Button
            onClick={handleIngestionSubmit}
            variant="contained"
            disabled={!ingestionForm.sourceType || !ingestionForm.content || isIngesting}
          >
            {isIngesting ? 'Processing...' : 'Ingest Data'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default DataManagement
