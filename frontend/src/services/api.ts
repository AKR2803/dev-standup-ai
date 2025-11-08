import axios, { AxiosResponse } from 'axios';
import { API_BASE_URL, ENDPOINTS } from '@/utils/constants';
import type {
  TeamStandup,
  CodeReview,
  DeveloperActivity,
  DocstringGeneration,
  TestGeneration,
  ApiResponse,
  GenerateRequest,
} from './types';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class ApiService {
  // Health check
  static async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get(ENDPOINTS.HEALTH);
    return response.data;
  }

  // Standup endpoints
  static async getStandup(): Promise<TeamStandup | null> {
    try {
      const response = await api.get(ENDPOINTS.STANDUP);
      return response.data.standup || null;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  static async generateStandup(sinceHours: number = 24): Promise<TeamStandup> {
    const response = await api.post(`${ENDPOINTS.STANDUP_GENERATE}?since_hours=${sinceHours}`);
    return response.data.standup;
  }

  // Code review endpoints
  static async getCodeReview(prNumber?: number): Promise<CodeReview | CodeReview[]> {
    const url = prNumber ? `${ENDPOINTS.REVIEWS}?pr_number=${prNumber}` : ENDPOINTS.REVIEWS;
    const response = await api.get(url);
    return prNumber ? response.data.review : response.data.reviews;
  }

  static async generateCodeReview(prNumber?: number, sinceHours: number = 24): Promise<CodeReview[]> {
    const params = new URLSearchParams();
    params.append('since_hours', sinceHours.toString());
    if (prNumber) {
      params.append('pr_number', prNumber.toString());
    }

    const response = await api.post(`${ENDPOINTS.REVIEWS_GENERATE}?${params}`);
    return response.data.reviews || [response.data.review];
  }

  // Documentation generation
  static async generateDocstring(
    filePath: string,
    functionName: string,
    code: string
  ): Promise<DocstringGeneration> {
    const request: GenerateRequest = {
      type: 'docstring',
      data: {
        file_path: filePath,
        function_name: functionName,
        code: code,
      },
    };

    const response = await api.post(ENDPOINTS.DOCS_GENERATE, request);
    return response.data.docstring;
  }

  // Test generation
  static async generateTest(
    filePath: string,
    functionName: string,
    code: string
  ): Promise<TestGeneration> {
    const request: GenerateRequest = {
      type: 'test',
      data: {
        file_path: filePath,
        function_name: functionName,
        code: code,
      },
    };

    const response = await api.post(ENDPOINTS.TESTS_GENERATE, request);
    return response.data.test;
  }

  // Activity endpoints
  static async getActivity(startDate?: Date, endDate?: Date): Promise<DeveloperActivity[]> {
    const params = new URLSearchParams();
    if (startDate) {
      params.append('start_date', startDate.toISOString());
    }
    if (endDate) {
      params.append('end_date', endDate.toISOString());
    }

    const url = params.toString() ? `${ENDPOINTS.ACTIVITY}?${params}` : ENDPOINTS.ACTIVITY;
    const response = await api.get(url);
    return response.data.activities;
  }

  static async aggregateActivity(sinceHours: number = 24): Promise<{ message: string; activities_count: number }> {
    const response = await api.post(`${ENDPOINTS.ACTIVITY_AGGREGATE}?since_hours=${sinceHours}`);
    return response.data;
  }
}

export default ApiService;