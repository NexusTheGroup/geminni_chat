import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export interface StatusResponse {
  status: string
  version: string
}

export interface SearchResult {
  turnId: string
  conversationId: string
  turnIndex: number
  timestamp: string
  snippet: string
  score: number
  sentiment?: string
}

export interface FeedbackRequest {
  type: string
  message: string
  userId?: string
}

export interface FeedbackResponse {
  message: string
  feedbackId: string
}

export interface FeedbackListItem {
  feedbackId: string
  feedbackType: string
  message: string
  status: string
  submittedAt: string
  userId?: string
}

export interface IngestionRequest {
  sourceType: string
  content: any
  metadata?: Record<string, any>
  sourceId?: string
}

export interface IngestionResponse {
  message: string
  rawDataId: string
}

export interface IngestionStatusResponse {
  rawDataId: string
  status: string
}

export interface AnalysisRequest {
  rawDataId: string
}

export interface AnalysisResponse {
  message: string
  rawDataId: string
}

export interface AnalysisStatusResponse {
  rawDataId: string
  status: string
}

export interface CorrelationRequest {
  rawDataId: string
}

export interface CorrelationQueuedResponse {
  message: string
  rawDataId: string
}

export interface CorrelationCandidateResponse {
  id: string
  rawDataId: string
  sourceEntityId: string
  targetEntityId: string
  score: number
  status: string
  rationale?: string
}

export interface CorrelationFusionResponse {
  message: string
  rawDataId: string
}

export interface ObsidianExportRequest {
  rawDataId: string
  exportPath: string
}

export interface ObsidianExportResponse {
  message: string
  rawDataId: string
}

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: API_BASE_URL,
    prepareHeaders: (headers) => {
      headers.set('Content-Type', 'application/json')
      return headers
    },
  }),
  tagTypes: [
    'Status',
    'Search',
    'Feedback',
    'Ingestion',
    'Analysis',
    'Correlation',
    'Export',
  ],
  endpoints: (builder) => ({
    // System status
    getStatus: builder.query<StatusResponse, void>({
      query: () => '/status',
      providesTags: ['Status'],
    }),

    // Search
    search: builder.query<SearchResult[], { q: string; limit?: number }>({
      query: ({ q, limit = 10 }) => ({
        url: '/search',
        params: { q, limit },
      }),
      providesTags: ['Search'],
    }),

    // Feedback
    submitFeedback: builder.mutation<FeedbackResponse, FeedbackRequest>({
      query: (body) => ({
        url: '/feedback',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Feedback'],
    }),

    getFeedback: builder.query<FeedbackResponse, string>({
      query: (feedbackId) => `/feedback/${feedbackId}`,
      providesTags: ['Feedback'],
    }),

    listFeedback: builder.query<FeedbackListItem[], { status?: string; limit?: number }>({
      query: ({ status, limit = 50 }) => ({
        url: '/feedback',
        params: { status, limit },
      }),
      providesTags: ['Feedback'],
    }),

    updateFeedback: builder.mutation<FeedbackListItem, { feedbackId: string; status: string }>({
      query: ({ feedbackId, status }) => ({
        url: `/feedback/${feedbackId}`,
        method: 'PATCH',
        body: { status },
      }),
      invalidatesTags: ['Feedback'],
    }),

    // Ingestion
    ingest: builder.mutation<IngestionResponse, IngestionRequest>({
      query: (body) => ({
        url: '/ingest',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Ingestion'],
    }),

    getIngestionStatus: builder.query<IngestionStatusResponse, string>({
      query: (rawDataId) => `/ingest/${rawDataId}`,
      providesTags: ['Ingestion'],
    }),

    // Analysis
    queueAnalysis: builder.mutation<AnalysisResponse, AnalysisRequest>({
      query: (body) => ({
        url: '/analysis',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Analysis'],
    }),

    getAnalysisStatus: builder.query<AnalysisStatusResponse, string>({
      query: (rawDataId) => `/analysis/${rawDataId}`,
      providesTags: ['Analysis'],
    }),

    // Correlation
    queueCorrelation: builder.mutation<CorrelationQueuedResponse, CorrelationRequest>({
      query: (body) => ({
        url: '/correlation',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Correlation'],
    }),

    getCorrelationCandidates: builder.query<CorrelationCandidateResponse[], string>({
      query: (rawDataId) => `/correlation/${rawDataId}`,
      providesTags: ['Correlation'],
    }),

    fuseCorrelation: builder.mutation<CorrelationFusionResponse, string>({
      query: (rawDataId) => ({
        url: `/correlation/${rawDataId}/fuse`,
        method: 'POST',
      }),
      invalidatesTags: ['Correlation'],
    }),

    // Export
    queueObsidianExport: builder.mutation<ObsidianExportResponse, ObsidianExportRequest>({
      query: (body) => ({
        url: '/export/obsidian',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Export'],
    }),
  }),
})

export const {
  useGetStatusQuery,
  useSearchQuery,
  useSubmitFeedbackMutation,
  useGetFeedbackQuery,
  useListFeedbackQuery,
  useUpdateFeedbackMutation,
  useIngestMutation,
  useGetIngestionStatusQuery,
  useQueueAnalysisMutation,
  useGetAnalysisStatusQuery,
  useQueueCorrelationMutation,
  useGetCorrelationCandidatesQuery,
  useFuseCorrelationMutation,
  useQueueObsidianExportMutation,
} = api
