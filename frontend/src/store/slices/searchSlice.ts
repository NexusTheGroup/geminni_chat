import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { SearchResult } from '../api'

interface SearchState {
  query: string
  results: SearchResult[]
  filters: {
    sentiment?: string
    dateRange?: {
      start: string
      end: string
    }
    conversationId?: string
    minScore?: number
  }
  sortBy: 'score' | 'timestamp' | 'turnIndex'
  sortOrder: 'asc' | 'desc'
  pagination: {
    page: number
    limit: number
    total: number
  }
  isSearching: boolean
  lastSearchTime?: number
  searchSuggestions: string[]
}

const initialState: SearchState = {
  query: '',
  results: [],
  filters: {},
  sortBy: 'score',
  sortOrder: 'desc',
  pagination: {
    page: 1,
    limit: 10,
    total: 0,
  },
  isSearching: false,
  searchSuggestions: [],
}

const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    setQuery: (state, action: PayloadAction<string>) => {
      state.query = action.payload
    },
    setResults: (state, action: PayloadAction<SearchResult[]>) => {
      state.results = action.payload
      state.pagination.total = action.payload.length
    },
    setFilters: (state, action: PayloadAction<Partial<SearchState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload }
    },
    clearFilters: (state) => {
      state.filters = {}
    },
    setSortBy: (state, action: PayloadAction<SearchState['sortBy']>) => {
      state.sortBy = action.payload
    },
    setSortOrder: (state, action: PayloadAction<SearchState['sortOrder']>) => {
      state.sortOrder = action.payload
    },
    setPagination: (state, action: PayloadAction<Partial<SearchState['pagination']>>) => {
      state.pagination = { ...state.pagination, ...action.payload }
    },
    setSearching: (state, action: PayloadAction<boolean>) => {
      state.isSearching = action.payload
    },
    setLastSearchTime: (state, action: PayloadAction<number>) => {
      state.lastSearchTime = action.payload
    },
    setSearchSuggestions: (state, action: PayloadAction<string[]>) => {
      state.searchSuggestions = action.payload
    },
    clearSearch: (state) => {
      state.query = ''
      state.results = []
      state.filters = {}
      state.pagination = {
        page: 1,
        limit: 10,
        total: 0,
      }
      state.isSearching = false
    },
  },
})

export const {
  setQuery,
  setResults,
  setFilters,
  clearFilters,
  setSortBy,
  setSortOrder,
  setPagination,
  setSearching,
  setLastSearchTime,
  setSearchSuggestions,
  clearSearch,
} = searchSlice.actions

export default searchSlice.reducer
