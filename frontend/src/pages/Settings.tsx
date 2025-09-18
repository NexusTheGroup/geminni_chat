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
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Palette as PaletteIcon,
} from '@mui/icons-material'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../store'
import { updateUserPreferences, setTheme } from '../store/slices/uiSlice'

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
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

const Settings: React.FC = () => {
  const [tabValue, setTabValue] = useState(0)
  const [apiKeyDialog, setApiKeyDialog] = useState(false)
  const [newApiKey, setNewApiKey] = useState('')

  const dispatch = useDispatch()
  const { userPreferences, theme } = useSelector((state: RootState) => state.ui)

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const handlePreferenceChange = (key: string, value: any) => {
    dispatch(updateUserPreferences({ [key]: value }))
  }

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    dispatch(setTheme(newTheme))
  }

  const handleSaveApiKey = () => {
    // In a real app, this would save to backend
    console.log('Saving API key:', newApiKey)
    setApiKeyDialog(false)
    setNewApiKey('')
  }

  const mockApiKeys = [
    { id: '1', name: 'OpenAI API', key: 'sk-***...***abc', lastUsed: '2024-01-15' },
    { id: '2', name: 'Anthropic API', key: 'ant-***...***def', lastUsed: '2024-01-14' },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Configure your NexusKnowledge experience and system preferences
      </Typography>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="settings tabs"
        >
          <Tab label="General" />
          <Tab label="API Keys" />
          <Tab label="Notifications" />
          <Tab label="Appearance" />
          <Tab label="Data" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Search Preferences
                  </Typography>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Default Search Limit</InputLabel>
                    <Select
                      value={userPreferences.searchLimit}
                      label="Default Search Limit"
                      onChange={(e) => handlePreferenceChange('searchLimit', Number(e.target.value))}
                    >
                      <MenuItem value={5}>5 results</MenuItem>
                      <MenuItem value={10}>10 results</MenuItem>
                      <MenuItem value={25}>25 results</MenuItem>
                      <MenuItem value={50}>50 results</MenuItem>
                    </Select>
                  </FormControl>

                  <FormControlLabel
                    control={
                      <Switch
                        checked={userPreferences.autoRefresh}
                        onChange={(e) => handlePreferenceChange('autoRefresh', e.target.checked)}
                      />
                    }
                    label="Auto-refresh search results"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    System Preferences
                  </Typography>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={userPreferences.notifications}
                        onChange={(e) => handlePreferenceChange('notifications', e.target.checked)}
                      />
                    }
                    label="Enable notifications"
                  />

                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={() => console.log('Saving preferences...')}
                    >
                      Save Preferences
                    </Button>
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
                API Keys
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setApiKeyDialog(true)}
              >
                Add API Key
              </Button>
            </Box>

            <List>
              {mockApiKeys.map((apiKey) => (
                <ListItem key={apiKey.id} divider>
                  <ListItemText
                    primary={apiKey.name}
                    secondary={`Key: ${apiKey.key} • Last used: ${apiKey.lastUsed}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton edge="end" aria-label="edit">
                      <EditIcon />
                    </IconButton>
                    <IconButton edge="end" aria-label="delete" color="error">
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Notification Settings
                  </Typography>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Email notifications"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Browser notifications"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="SMS notifications"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Notification Types
                  </Typography>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Search results ready"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Data processing complete"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Correlation analysis updates"
                  />
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
                    Theme Settings
                  </Typography>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Theme</InputLabel>
                    <Select
                      value={theme}
                      label="Theme"
                      onChange={(e) => handleThemeChange(e.target.value as 'light' | 'dark')}
                    >
                      <MenuItem value="light">Light</MenuItem>
                      <MenuItem value="dark">Dark</MenuItem>
                    </Select>
                  </FormControl>

                  <FormControlLabel
                    control={<Switch />}
                    label="Auto-detect system theme"
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Display Settings
                  </Typography>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Density</InputLabel>
                    <Select defaultValue="comfortable" label="Density">
                      <MenuItem value="compact">Compact</MenuItem>
                      <MenuItem value="comfortable">Comfortable</MenuItem>
                      <MenuItem value="spacious">Spacious</MenuItem>
                    </Select>
                  </FormControl>

                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Show animations"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={4}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Data Management
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    sx={{ mb: 2, mr: 2 }}
                  >
                    Refresh Cache
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DeleteIcon />}
                    color="error"
                    sx={{ mb: 2 }}
                  >
                    Clear Search History
                  </Button>

                  <Alert severity="warning" sx={{ mt: 2 }}>
                    Clearing data will remove all search history and cached results. This action cannot be undone.
                  </Alert>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Export Data
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<StorageIcon />}
                    sx={{ mb: 2, mr: 2 }}
                  >
                    Export Settings
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<StorageIcon />}
                    sx={{ mb: 2 }}
                  >
                    Export All Data
                  </Button>

                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    Export your settings and data for backup or migration purposes.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>

      {/* API Key Dialog */}
      <Dialog open={apiKeyDialog} onClose={() => setApiKeyDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add API Key</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API Key Name"
                placeholder="e.g., OpenAI API"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API Key"
                value={newApiKey}
                onChange={(e) => setNewApiKey(e.target.value)}
                placeholder="Enter your API key"
                type="password"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSaveApiKey}
            variant="contained"
            disabled={!newApiKey.trim()}
          >
            Save API Key
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Settings
