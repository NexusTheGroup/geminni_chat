import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UIState {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    timestamp: number
  }>
  loading: {
    search: boolean
    feedback: boolean
    ingestion: boolean
    analysis: boolean
    correlation: boolean
    export: boolean
  }
  searchHistory: string[]
  userPreferences: {
    searchLimit: number
    autoRefresh: boolean
    notifications: boolean
  }
}

const initialState: UIState = {
  sidebarOpen: true,
  theme: 'light',
  notifications: [],
  loading: {
    search: false,
    feedback: false,
    ingestion: false,
    analysis: false,
    correlation: false,
    export: false,
  },
  searchHistory: [],
  userPreferences: {
    searchLimit: 10,
    autoRefresh: true,
    notifications: true,
  },
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload
    },
    addNotification: (state, action: PayloadAction<{
      type: 'success' | 'error' | 'warning' | 'info'
      message: string
    }>) => {
      const notification = {
        id: Date.now().toString(),
        ...action.payload,
        timestamp: Date.now(),
      }
      state.notifications.push(notification)
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      )
    },
    clearNotifications: (state) => {
      state.notifications = []
    },
    setLoading: (state, action: PayloadAction<{
      key: keyof UIState['loading']
      value: boolean
    }>) => {
      state.loading[action.payload.key] = action.payload.value
    },
    addSearchToHistory: (state, action: PayloadAction<string>) => {
      const query = action.payload.trim()
      if (query && !state.searchHistory.includes(query)) {
        state.searchHistory.unshift(query)
        // Keep only the last 20 searches
        if (state.searchHistory.length > 20) {
          state.searchHistory = state.searchHistory.slice(0, 20)
        }
      }
    },
    clearSearchHistory: (state) => {
      state.searchHistory = []
    },
    updateUserPreferences: (state, action: PayloadAction<Partial<UIState['userPreferences']>>) => {
      state.userPreferences = { ...state.userPreferences, ...action.payload }
    },
  },
})

export const {
  toggleSidebar,
  setSidebarOpen,
  setTheme,
  addNotification,
  removeNotification,
  clearNotifications,
  setLoading,
  addSearchToHistory,
  clearSearchHistory,
  updateUserPreferences,
} = uiSlice.actions

export default uiSlice.reducer
