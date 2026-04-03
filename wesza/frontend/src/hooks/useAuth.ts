import { create } from 'zustand';
import apiClient from '../lib/api';

interface User {
  id: string;
  email: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuth = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem('wesza_token'),
  isAuthenticated: !!localStorage.getItem('wesza_token'),
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      const { access_token, user_id, email: userEmail } = response.data;
      
      localStorage.setItem('wesza_token', access_token);
      set({
        user: { id: user_id, email: userEmail },
        token: access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      await apiClient.post('/auth/register', { email, password });
      // After registration, auto-login
      await get().login(email, password);
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('wesza_token');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  checkAuth: async () => {
    const token = localStorage.getItem('wesza_token');
    if (!token) {
      set({ isAuthenticated: false, user: null });
      return;
    }

    try {
      // Decode JWT to get user info (simplified - in prod, verify with backend)
      const payload = JSON.parse(atob(token.split('.')[1]));
      set({
        user: { id: payload.sub, email: payload.email || '' },
        isAuthenticated: true,
      });
    } catch {
      get().logout();
    }
  },
}));
