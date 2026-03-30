/**
 * Servicio de autenticación
 * Maneja login, logout, refresh token y cambio de contraseña
 */
import apiClient from './apiClient';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: AdminUser;
}

export interface AdminUser {
  id: number;
  username: string;
  nombre_completo: string;
  email: string;
  rol: 'superadmin' | 'admin' | 'viewer' | 'operator';
  empresa_id: number | null;
  empresa?: {
    id: number;
    razon_social: string;
    nombre_comercial: string;
  };
  is_active: boolean;
  last_login: string | null;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

class AuthService {
  /**
   * Iniciar sesión
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    // Usar axios directamente sin interceptores para evitar intentos de renovación de token
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const axios = (await import('axios')).default;
    
    const response = await axios.post<LoginResponse>(`${API_BASE_URL}/auth/login`, {
      username,
      password,
    });
    
    const { access_token, refresh_token, user } = response.data;
    
    // Guardar tokens en localStorage (persiste al cerrar pestaña)
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    return response.data;
  }
  
  /**
   * Cerrar sesión
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      // Limpiar localStorage siempre
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }
  
  /**
   * Renovar token de acceso
   */
  async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      throw new Error('No hay refresh token disponible');
    }
    
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    
    const { access_token } = response.data;
    
    // Actualizar token en localStorage
    localStorage.setItem('access_token', access_token);
    
    return access_token;
  }
  
  /**
   * Obtener información del usuario actual
   */
  async getCurrentUser(): Promise<AdminUser> {
    const response = await apiClient.get<AdminUser>('/auth/me');
    return response.data;
  }
  
  /**
   * Cambiar contraseña
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }
  
  /**
   * Verificar si hay un token válido
   */
  hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }
}

export default new AuthService();
