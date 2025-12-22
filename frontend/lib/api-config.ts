/**
 * API Configuration
 * Central configuration for backend API endpoints
 */

// Backend API base URL
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001/api';

// API endpoints
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    REGISTER: `${API_BASE_URL}/auth/register`,
    LOGIN: `${API_BASE_URL}/auth/login`,
    LOGOUT: `${API_BASE_URL}/auth/logout`,
    ME: `${API_BASE_URL}/auth/me`,
  },
  // Files
  FILES: {
    UPLOAD: `${API_BASE_URL}/files/upload`,
    LIST: `${API_BASE_URL}/files`,
    GET: (id: number) => `${API_BASE_URL}/files/${id}`,
    DELETE: (id: number) => `${API_BASE_URL}/files/${id}`,
  },
  // Questions
  ASK: {
    QUESTION: `${API_BASE_URL}/ask`,
    HISTORY: `${API_BASE_URL}/ask/history`,
  },
  // Health check
  HEALTH: `${API_BASE_URL}/health`,
};

// Default fetch options
export const DEFAULT_FETCH_OPTIONS: RequestInit = {
  credentials: 'include', // Important! Sends cookies for session authentication
  headers: {
    'Content-Type': 'application/json',
  },
};
