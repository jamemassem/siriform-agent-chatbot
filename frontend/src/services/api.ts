/**
 * API service for communicating with the backend.
 */
import type {
  ChatRequest,
  ChatResponse,
  FormSchemaResponse,
  HealthResponse,
  APIError,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  statusCode: number;
  detail?: string;
  
  constructor(
    message: string,
    statusCode: number,
    detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.detail = detail;
  }
}

/**
 * Handle API response and throw error if not ok
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    
    try {
      const errorData: APIError = await response.json();
      errorDetail = errorData.detail || errorDetail;
    } catch {
      // If parsing fails, use default error message
    }
    
    throw new ApiError(errorDetail, response.status, errorDetail);
  }
  
  return response.json();
}

/**
 * Check backend health
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse<HealthResponse>(response);
}

/**
 * Get form schema by name
 */
export async function getFormSchema(formName: string): Promise<FormSchemaResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/form-schema/${formName}`);
  return handleResponse<FormSchemaResponse>(response);
}

/**
 * Send chat message and get agent response
 */
export async function sendChatMessage(
  request: ChatRequest,
  authToken?: string | null
): Promise<ChatResponse> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add authentication token if available
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify(request),
  });

  return handleResponse<ChatResponse>(response);
}

/**
 * Generate a unique session ID
 */
export function generateSessionId(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 15);
  return `sess_${timestamp}_${random}`;
}
