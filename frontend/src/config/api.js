/**
 * Centralized API Configuration & Endpoint Resolver
 *
 * Supports:
 * 1. Netlify Production with VITE_API_BASE_URL (points to external backend)
 * 2. Netlify Production with Reverse Proxy (relative /api requests rewritten in netlify.toml)
 * 3. Local Vite development server (port 5173 -> http://localhost:8000)
 * 4. Local FastAPI all-in-one server (same origin /)
 */

const envBase = import.meta.env.VITE_API_BASE_URL;

export const API_BASE = (envBase && typeof envBase === 'string')
  ? envBase.replace(/\/+$/, '')
  : (typeof window !== 'undefined' && window.location.port === '5173'
      ? 'http://localhost:8000'
      : '');

/**
 * Returns the fully qualified or relative URL for a given API endpoint.
 *
 * @param {string} endpoint - The endpoint path, e.g. '/api/chat' or 'api/status'
 * @returns {string} The resolved URL
 */
export const getApiUrl = (endpoint) => {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_BASE}${cleanEndpoint}`;
};

export default {
  API_BASE,
  getApiUrl,
};
