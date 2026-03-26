/**
 * Componente ProtectedRoute
 * Protege rutas que requieren autenticación y/o roles específicos
 */
import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { user, isAuthenticated, loading } = useAuth();
  
  // Mostrar loading mientras se verifica la autenticación
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  // Si no está autenticado, redirigir a login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  // Si requiere un rol específico y el usuario no lo tiene, redirigir a unauthorized
  if (requiredRole && user && !requiredRole.includes(user.rol)) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  // Si está autenticado y tiene el rol requerido, mostrar el contenido
  return <>{children}</>;
};

export default ProtectedRoute;
