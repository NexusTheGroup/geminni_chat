import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { FeedbackListItem } from '../api'

interface FeedbackState {
  items: FeedbackListItem[]
  filters: {
    status?: string
    type?: string
    dateRange?: {
      start: string
      end: string
    }
  }
  pagination: {
    page: number
    limit: number
    total: number
  }
  isSubmitting: boolean
  lastSubmissionTime?: number
}

const initialState: FeedbackState = {
  items: [],
  filters: {},
  pagination: {
    page: 1,
    limit: 50,
    total: 0,
  },
  isSubmitting: false,
}

const feedbackSlice = createSlice({
  name: 'feedback',
  initialState,
  reducers: {
    setItems: (state, action: PayloadAction<FeedbackListItem[]>) => {
      state.items = action.payload
      state.pagination.total = action.payload.length
    },
    addItem: (state, action: PayloadAction<FeedbackListItem>) => {
      state.items.unshift(action.payload)
      state.pagination.total += 1
    },
    updateItem: (state, action: PayloadAction<{ id: string; updates: Partial<FeedbackListItem> }>) => {
      const index = state.items.findIndex(item => item.feedbackId === action.payload.id)
      if (index !== -1) {
        state.items[index] = { ...state.items[index], ...action.payload.updates }
      }
    },
    setFilters: (state, action: PayloadAction<Partial<FeedbackState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload }
    },
    clearFilters: (state) => {
      state.filters = {}
    },
    setPagination: (state, action: PayloadAction<Partial<FeedbackState['pagination']>>) => {
      state.pagination = { ...state.pagination, ...action.payload }
    },
    setSubmitting: (state, action: PayloadAction<boolean>) => {
      state.isSubmitting = action.payload
    },
    setLastSubmissionTime: (state, action: PayloadAction<number>) => {
      state.lastSubmissionTime = action.payload
    },
    clearFeedback: (state) => {
      state.items = []
      state.filters = {}
      state.pagination = {
        page: 1,
        limit: 50,
        total: 0,
      }
      state.isSubmitting = false
    },
  },
})

export const {
  setItems,
  addItem,
  updateItem,
  setFilters,
  clearFilters,
  setPagination,
  setSubmitting,
  setLastSubmissionTime,
  clearFeedback,
} = feedbackSlice.actions

export default feedbackSlice.reducer
