/**
 * Contexto de autenticación
 * Proporciona estado y funciones de autenticación a toda la aplicación
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService, { AdminUser } from '../services/authService';

interface AuthContextType {
  user: AdminUser | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Verificar si hay un token válido al montar
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token) {
        try {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          console.error('Error al obtener usuario:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      
      setLoading(false);
    };
    
    initAuth();
  }, []);
  
  // Renovar token automáticamente cada 25 minutos
  useEffect(() => {
    if (!user) return;
    
    const interval = setInterval(async () => {
      try {
        await authService.refreshToken();
        console.log('Token renovado automáticamente');
      } catch (error) {
        console.error('Error al renovar token:', error);
        // Si falla la renovación, cerrar sesión
        await logout();
      }
    }, 25 * 60 * 1000); // 25 minutos
    
    return () => clearInterval(interval);
  }, [user]);
  
  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const response = await authService.login(username, password);
      setUser(response.user);
    } finally {
      setLoading(false);
    }
  };
  
  const logout = async () => {
    setLoading(true);
    try {
      await authService.logout();
    } finally {
      setUser(null);
      setLoading(false);
    }
  };
  
  const refreshToken = async () => {
    await authService.refreshToken();
  };
  
  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    logout,
    refreshToken,
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  
  return context;
};
