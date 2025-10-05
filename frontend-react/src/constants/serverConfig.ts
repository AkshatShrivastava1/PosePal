// Server configuration constants
export const SERVER_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000',
  API_ENDPOINTS: {
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
    },
    FRAMES: '/frames',
    SESSIONS: '/sessions',
    HEALTH: '/health',
    ANALYSIS: '/analysis',
  }
} as const;

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string): string => {
  return `${SERVER_CONFIG.BASE_URL}${endpoint}`;
};

// Export individual endpoints for convenience
export const API_URLS = {
  LOGIN: buildApiUrl(SERVER_CONFIG.API_ENDPOINTS.AUTH.LOGIN),
  REGISTER: buildApiUrl(SERVER_CONFIG.API_ENDPOINTS.AUTH.REGISTER),
  FRAMES: buildApiUrl(SERVER_CONFIG.API_ENDPOINTS.FRAMES),
  SESSIONS: buildApiUrl(SERVER_CONFIG.API_ENDPOINTS.SESSIONS),
  HEALTH: buildApiUrl(SERVER_CONFIG.API_ENDPOINTS.HEALTH),
  ANALYSIS: buildApiUrl(SERVER_CONFIG.API_ENDPOINTS.ANALYSIS),
} as const;
