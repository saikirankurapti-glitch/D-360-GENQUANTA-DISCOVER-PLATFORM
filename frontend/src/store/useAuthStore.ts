import { create } from 'zustand';

interface User {
  email: string;
  role: string;
  name?: string;
}

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, refreshToken: string, role: string, email: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => {
  // Try to load initial state from localStorage
  const savedToken = localStorage.getItem('discover_token');
  const savedRefreshToken = localStorage.getItem('discover_refresh_token');
  const savedRole = localStorage.getItem('discover_role');
  const savedEmail = localStorage.getItem('discover_email');

  return {
    token: savedToken,
    refreshToken: savedRefreshToken,
    user: savedToken && savedRole && savedEmail ? { email: savedEmail, role: savedRole } : null,
    isAuthenticated: !!savedToken,

    login: (token: string, refreshToken: string, role: string, email: string) => {
      localStorage.setItem('discover_token', token);
      localStorage.setItem('discover_refresh_token', refreshToken);
      localStorage.setItem('discover_role', role);
      localStorage.setItem('discover_email', email);
      
      set({
        token,
        refreshToken,
        user: { email, role },
        isAuthenticated: true
      });
    },

    logout: () => {
      localStorage.removeItem('discover_token');
      localStorage.removeItem('discover_refresh_token');
      localStorage.removeItem('discover_role');
      localStorage.removeItem('discover_email');
      
      set({
        token: null,
        refreshToken: null,
        user: null,
        isAuthenticated: false
      });
    }
  };
});
