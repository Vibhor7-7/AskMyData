/**
 * API Client
 * Handles all API requests to the Flask backend
 */

import { API_ENDPOINTS, DEFAULT_FETCH_OPTIONS } from './api-config';

// Types
export interface User {
  username: string;
  fullname: string;
  email: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  fullname: string;
  username: string;
  email: string;
  password: string;
}

export interface FileInfo {
  file_id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  upload_date: string;
  num_rows: number;
  num_columns: number;
  num_chunks?: number;
}

export interface ChatMessage {
  id: number;
  question: string;
  answer: string;
  timestamp: string;
  file_id?: number;
}

export interface AskResponse {
  success: boolean;
  chat_id: number;
  question: string;
  answer: string;
  num_chunks_used: number;
  sources: string[];
  timestamp: string;
}

// Error handling
class ApiError extends Error {
  constructor(public status: number, message: string, public details?: any) {
    super(message);
    this.name = 'ApiError';
  }
}

// Helper function to handle API responses
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new ApiError(
      response.status,
      error.error || `HTTP ${response.status}`,
      error.details
    );
  }
  return response.json();
}

// Authentication API
export const authApi = {
  /**
   * Register a new user
   */
  register: async (data: RegisterData): Promise<{ success: boolean; user: User }> => {
    const response = await fetch(API_ENDPOINTS.AUTH.REGISTER, {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'POST',
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Login user
   */
  login: async (credentials: LoginCredentials): Promise<{ success: boolean; user: User }> => {
    const response = await fetch(API_ENDPOINTS.AUTH.LOGIN, {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    return handleResponse(response);
  },

  /**
   * Logout current user
   */
  logout: async (): Promise<{ success: boolean }> => {
    const response = await fetch(API_ENDPOINTS.AUTH.LOGOUT, {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'POST',
    });
    return handleResponse(response);
  },

  /**
   * Get current user info
   */
  getCurrentUser: async (): Promise<{ authenticated: boolean; user?: User }> => {
    const response = await fetch(API_ENDPOINTS.AUTH.ME, {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'GET',
    });
    return handleResponse(response);
  },
};

// Files API
export const filesApi = {
  /**
   * Upload a file
   */
  upload: async (file: File): Promise<{ success: boolean; file: FileInfo }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(API_ENDPOINTS.FILES.UPLOAD, {
      method: 'POST',
      credentials: 'include',
      // Don't set Content-Type header - browser sets it automatically with boundary
      body: formData,
    });
    return handleResponse(response);
  },

  /**
   * Get all files for current user
   */
  list: async (): Promise<{ success: boolean; files: FileInfo[]; count: number }> => {
    const response = await fetch(API_ENDPOINTS.FILES.LIST, {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'GET',
    });
    return handleResponse(response);
  },

  /**
   * Get specific file details
   */
  get: async (id: number): Promise<{ success: boolean; file: FileInfo }> => {
    const response = await fetch(API_ENDPOINTS.FILES.GET(id), {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'GET',
    });
    return handleResponse(response);
  },

  /**
   * Delete a file
   */
  delete: async (id: number): Promise<{ success: boolean }> => {
    const response = await fetch(API_ENDPOINTS.FILES.DELETE(id), {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'DELETE',
    });
    return handleResponse(response);
  },
};

// Ask API
export const askApi = {
  /**
   * Ask a question about uploaded data
   */
  ask: async (question: string, fileId?: number): Promise<AskResponse> => {
    const response = await fetch(API_ENDPOINTS.ASK.QUESTION, {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'POST',
      body: JSON.stringify({ question, file_id: fileId }),
    });
    return handleResponse(response);
  },

  /**
   * Get chat history
   */
  getHistory: async (): Promise<{ success: boolean; history: ChatMessage[]; count: number }> => {
    const response = await fetch(API_ENDPOINTS.ASK.HISTORY, {
      ...DEFAULT_FETCH_OPTIONS,
      method: 'GET',
    });
    return handleResponse(response);
  },
};

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string; message: string }> => {
    const response = await fetch(API_ENDPOINTS.HEALTH, {
      method: 'GET',
    });
    return handleResponse(response);
  },
};

// Export everything as a single API object
export const api = {
  auth: authApi,
  files: filesApi,
  ask: askApi,
  health: healthApi,
};

export default api;
