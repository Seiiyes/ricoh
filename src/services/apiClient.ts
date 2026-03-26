/**
 * API Client con interceptores para autenticación
 * Maneja automáticamente tokens JWT y renovación
 */
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Crear instancia de axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Agregar token y CSRF token a todas las peticiones
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = sessionStorage.getItem('access_token');
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Agregar CSRF token para requests mutables
    const csrfToken = sessionStorage.getItem('csrf_token');
    if (csrfToken && config.method && ['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Manejar errores y guardar CSRF token - SIMPLIFICADO
apiClient.interceptors.response.use(
  (response) => {
    // Guardar nuevo CSRF token si viene en el header
    const newCsrfToken = response.headers['x-csrf-token'];
    if (newCsrfToken) {
      sessionStorage.setItem('csrf_token', newCsrfToken);
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // SIMPLIFICADO: Solo manejar 401 en rutas NO-auth, sin reintentos automáticos
    const isAuthRoute = originalRequest.url?.includes('/auth/');
    
    if (error.response?.status === 401 && !isAuthRoute && !originalRequest._retry) {
      console.log('❌ 401 Unauthorized - redirigiendo a login');
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
