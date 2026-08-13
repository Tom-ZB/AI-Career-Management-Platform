import apiClient, { setTokens, clearTokens } from './api';
import type { User, Token, LoginCredentials, RegisterData } from '../types';

export const authService = {
  // Login with email/password (OAuth2 form)
  async login(credentials: LoginCredentials): Promise<Token> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post<Token>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    setTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  },

  // Register new user
  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  // Logout
  logout(): void {
    clearTokens();
    window.location.href = '/login';
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  // Refresh token
  async refreshToken(): Promise<Token> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token');

    const response = await apiClient.post<Token>('/auth/refresh', null, {
      params: { refresh_token: refreshToken },
    });

    setTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  },

  // Check if authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};
