import { AnalysisRequest, AnalysisResponse } from '@/types';

const API_BASE_URL = '/api';

// Custom API Error class
export class ApiError extends Error {
  public status?: number;
  public code?: string;

  constructor(message: string, status?: number, code?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          errorData.error || `HTTP error! status: ${response.status}`,
          response.status
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle network errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new ApiError(
          'Network error: Unable to connect to the server. Please check your connection.'
        );
      }
      
      throw new ApiError('An unexpected error occurred');
    }
  }

  async analyzeRepository(request: AnalysisRequest): Promise<AnalysisResponse> {
    return this.request<AnalysisResponse>('/analyze', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async checkHealth(): Promise<{ status: string; services: Record<string, boolean> }> {
    return this.request('/health');
  }

  async getExampleRequest(): Promise<{ example_request: AnalysisRequest }> {
    return this.request('/analyze/example');
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export the class for testing
export default ApiService;