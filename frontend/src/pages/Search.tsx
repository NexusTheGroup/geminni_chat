import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  Divider,
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
  History as HistoryIcon,
} from '@mui/icons-material'
import { useSearchQuery } from '../store/api'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../store'
import { setQuery, setResults, setSearching } from '../store/slices/searchSlice'

const Search: React.FC = () => {
  const dispatch = useDispatch()
  const { query, results, isSearching, searchSuggestions } = useSelector((state: RootState) => state.search)
  const [searchQuery, setSearchQuery] = useState(query)
  const [limit, setLimit] = useState(10)
  const [showFilters, setShowFilters] = useState(false)

  const { data: searchResults, isLoading, error } = useSearchQuery(
    { q: searchQuery, limit },
    { skip: !searchQuery.trim() }
  )

  useEffect(() => {
    if (searchResults) {
      dispatch(setResults(searchResults))
      dispatch(setSearching(false))
    }
  }, [searchResults, dispatch])

  const handleSearch = () => {
    if (searchQuery.trim()) {
      dispatch(setQuery(searchQuery))
      dispatch(setSearching(true))
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch()
    }
  }

  const handleHistorySelect = (query: string) => {
    setSearchQuery(query)
    dispatch(setQuery(query))
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  const getSentimentColor = (sentiment?: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive':
        return 'success'
      case 'negative':
        return 'error'
      case 'neutral':
        return 'info'
      default:
        return 'default'
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom data-testid="search-title">
        Advanced Search
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Search through conversations and knowledge base with advanced filtering
      </Typography>

      {/* Search Interface */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <Autocomplete
              freeSolo
              options={searchSuggestions}
              value={searchQuery}
              onChange={(_, newValue) => setSearchQuery(newValue || '')}
              onInputChange={(_, newInputValue) => setSearchQuery(newInputValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Search query"
                  placeholder="Enter your search terms..."
                  fullWidth
                  onKeyPress={handleKeyPress}
                  data-testid="search-input"
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {isLoading && <CircularProgress size={20} />}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Limit</InputLabel>
              <Select
                value={limit}
                label="Limit"
                onChange={(e) => setLimit(Number(e.target.value))}
              >
                <MenuItem value={5}>5 results</MenuItem>
                <MenuItem value={10}>10 results</MenuItem>
                <MenuItem value={25}>25 results</MenuItem>
                <MenuItem value={50}>50 results</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              variant="contained"
              startIcon={<SearchIcon />}
              onClick={handleSearch}
              disabled={!searchQuery.trim() || isLoading}
              fullWidth
              size="large"
              data-testid="search-button"
            >
              Search
            </Button>
          </Grid>
        </Grid>

        {/* Search History */}
        {searchSuggestions.length > 0 && (
          <Box sx={{ mt: 2 }} data-testid="search-history">
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Recent searches:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {searchSuggestions.slice(0, 5).map((query, index) => (
                <Chip
                  key={index}
                  label={query}
                  size="small"
                  icon={<HistoryIcon />}
                  onClick={() => handleHistorySelect(query)}
                  variant="outlined"
                  data-testid="history-chip"
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            Filters & Options
          </Typography>
          <Button
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
            data-testid="filters-toggle"
          >
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </Button>
        </Box>

        {showFilters && (
          <Box sx={{ mt: 2 }} data-testid="filters-panel">
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Sort by</InputLabel>
                  <Select defaultValue="score" label="Sort by">
                    <MenuItem value="score">Relevance Score</MenuItem>
                    <MenuItem value="timestamp">Date</MenuItem>
                    <MenuItem value="turnIndex">Turn Index</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Sentiment</InputLabel>
                  <Select defaultValue="" label="Sentiment">
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="positive">Positive</MenuItem>
                    <MenuItem value="negative">Negative</MenuItem>
                    <MenuItem value="neutral">Neutral</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Date Range</InputLabel>
                  <Select defaultValue="" label="Date Range">
                    <MenuItem value="">All time</MenuItem>
                    <MenuItem value="today">Today</MenuItem>
                    <MenuItem value="week">This week</MenuItem>
                    <MenuItem value="month">This month</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Search Results */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Search failed: {error.toString()}
        </Alert>
      )}

      {results.length > 0 && (
        <Box data-testid="search-results">
          <Typography variant="h6" gutterBottom>
            Search Results ({results.length})
          </Typography>

          <Grid container spacing={2}>
            {results.map((result, index) => (
              <Grid item xs={12} key={index}>
                <Card data-testid="result-card">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography variant="h6" component="div">
                        Turn {result.turnIndex}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Chip
                          label={`Score: ${result.score.toFixed(2)}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                        {result.sentiment && (
                          <Chip
                            label={result.sentiment}
                            size="small"
                            color={getSentimentColor(result.sentiment) as any}
                          />
                        )}
                      </Box>
                    </Box>

                    <Typography variant="body1" sx={{ mb: 2 }}>
                      {result.snippet}
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
                      <Typography variant="body2" color="text.secondary">
                        Conversation: {result.conversationId.slice(0, 8)}...
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {formatTimestamp(result.timestamp)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {!isLoading && !error && results.length === 0 && query && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <SearchIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No results found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search terms or filters
          </Typography>
        </Paper>
      )}
    </Box>
  )
}

export default Search
