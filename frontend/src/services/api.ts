import { useAuthStore } from '../store/useAuthStore';

const AUTH_SERVICE_URL = 'http://localhost:8001/api/v1';
const METADATA_SERVICE_URL = 'http://localhost:8002/api/v1';
const CONNECTOR_SERVICE_URL = 'http://localhost:8005/api/v1';
const CHEMISTRY_SERVICE_URL = 'http://localhost:8004/api/v1';
const QUERY_SERVICE_URL = 'http://localhost:8003/api/v1';
const AUDIT_SERVICE_URL = 'http://localhost:8006/api/v1';
const LINEAGE_SERVICE_URL = 'http://localhost:8007/api/v1';
const BIOINFORMATICS_SERVICE_URL = 'http://localhost:8008/api/v1';
const AI_SERVICE_URL = 'http://localhost:8010/api/v1';
const WORKFLOW_SERVICE_URL = 'http://localhost:8009/api/v1';

interface RequestOptions extends RequestInit {
  service?: 'auth' | 'metadata' | 'connectors' | 'chemistry' | 'query' | 'audit' | 'lineage' | 'bioinformatics' | 'ai' | 'workflow';
}

interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  role: string;
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('discover_refresh_token');
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${AUTH_SERVICE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Refresh failed');
    }

    const data: RefreshTokenResponse = await response.json();
    const email = localStorage.getItem('discover_email') || '';
    
    // Update store
    useAuthStore.getState().login(data.access_token, data.refresh_token, data.role, email);
    return data.access_token;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    useAuthStore.getState().logout();
    return null;
  }
}

export async function apiRequest(path: string, options: RequestOptions = {}) {
  const { service = 'metadata', ...init } = options;
  const baseUrl = 
    service === 'auth' 
      ? AUTH_SERVICE_URL 
      : service === 'connectors'
      ? CONNECTOR_SERVICE_URL
      : service === 'chemistry'
      ? CHEMISTRY_SERVICE_URL
      : service === 'query'
      ? QUERY_SERVICE_URL
      : service === 'audit'
      ? AUDIT_SERVICE_URL
      : service === 'lineage'
      ? LINEAGE_SERVICE_URL
      : service === 'bioinformatics'
      ? BIOINFORMATICS_SERVICE_URL
      : service === 'ai'
      ? AI_SERVICE_URL
      : service === 'workflow'
      ? WORKFLOW_SERVICE_URL
      : METADATA_SERVICE_URL;
  
  const headers = new Headers(init.headers || {});
  if (!headers.has('Content-Type') && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  // Inject token
  const token = useAuthStore.getState().token;
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  init.headers = headers;

  const maxRetries = 3;
  let delay = 200;
  let response: Response | undefined;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      response = await fetch(`${baseUrl}${path}`, init);
      break;
    } catch (err: any) {
      if (attempt === maxRetries) {
        console.error(`Fetch failure on ${baseUrl}${path}:`, err);
        throw err;
      }
      await new Promise((resolve) => setTimeout(resolve, delay));
      delay *= 2;
    }
  }

  if (!response) {
    throw new Error('No response received');
  }

  // If 401, try to refresh
  if (response.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      // Retry with new token
      headers.set('Authorization', `Bearer ${newToken}`);
      init.headers = headers;
      
      delay = 200;
      for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
          response = await fetch(`${baseUrl}${path}`, init);
          break;
        } catch (err: any) {
          if (attempt === maxRetries) {
            console.error(`Fetch failure after refresh on ${baseUrl}${path}:`, err);
            throw err;
          }
          await new Promise((resolve) => setTimeout(resolve, delay));
          delay *= 2;
        }
      }
      if (!response) {
        throw new Error('No response received after refresh');
      }
    } else {
      // Refresh failed, redirect or logout is triggered by store
      throw new Error('Unauthorized');
    }
  }

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: 'API Error' }));
    throw new Error(errorBody.detail || 'API Error');
  }

  return response.json();
}
