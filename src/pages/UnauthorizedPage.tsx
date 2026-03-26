/**
 * Página de Acceso No Autorizado
 * Se muestra cuando el usuario no tiene permisos para acceder a una ruta
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert } from 'lucide-react';

const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
          <ShieldAlert className="w-10 h-10 text-red-600" />
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Acceso Denegado
        </h1>
        
        <p className="text-gray-600 mb-8">
          No tienes permisos para acceder a esta página. Si crees que esto es un error, contacta al administrador.
        </p>
        
        <button
          onClick={() => navigate('/')}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition-colors"
        >
          Volver al Inicio
        </button>
      </div>
    </div>
  );
};

export default UnauthorizedPage;
