export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const ENDPOINTS = {
  STANDUP: '/api/standup',
  STANDUP_GENERATE: '/api/standup/generate',
  REVIEWS: '/api/reviews',
  REVIEWS_GENERATE: '/api/reviews/generate',
  DOCS_GENERATE: '/api/docs/generate',
  TESTS_GENERATE: '/api/tests/generate',
  ACTIVITY: '/api/activity',
  ACTIVITY_AGGREGATE: '/api/activity/aggregate',
  HEALTH: '/health',
} as const;

export const SEVERITY_COLORS = {
  critical: 'text-red-600 bg-red-50',
  high: 'text-orange-600 bg-orange-50',
  medium: 'text-yellow-600 bg-yellow-50',
  low: 'text-blue-600 bg-blue-50',
  info: 'text-gray-600 bg-gray-50',
} as const;

export const SEVERITY_LABELS = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  info: 'Info',
} as const;

export const REFRESH_INTERVALS = {
  STANDUP: 30000, // 30 seconds
  REVIEWS: 60000, // 1 minute
  ACTIVITY: 120000, // 2 minutes
} as const;