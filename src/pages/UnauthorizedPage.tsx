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
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4 relative overflow-hidden">
      {/* Decorative blobs for premium aesthetic */}
      <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] rounded-full bg-red-100 mix-blend-multiply filter blur-3xl opacity-50 animate-pulse-subtle"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40vw] h-[40vw] rounded-full bg-slate-200 mix-blend-multiply filter blur-3xl opacity-50 animate-pulse-subtle" style={{ animationDelay: '2s' }}></div>

      <div className="max-w-md w-full text-center relative z-10 bg-white/70 backdrop-blur-xl p-10 rounded-3xl shadow-2xl border border-white/50 animate-slide-up">
        <div className="inline-flex items-center justify-center w-24 h-24 bg-red-50 rounded-full mb-8 shadow-inner border border-red-100">
          <ShieldAlert className="w-12 h-12 text-ricoh-red" />
        </div>
        
        <h1 className="text-3xl font-bold text-slate-900 mb-4 tracking-tight">
          Acceso Denegado
        </h1>
        
        <p className="text-slate-600 mb-8 leading-relaxed font-medium">
          No tienes permisos para acceder a esta página. Si crees que esto es un error, contacta al administrador del sistema.
        </p>
        
        <button
          onClick={() => navigate('/')}
          className="relative overflow-hidden w-full bg-ricoh-red text-white font-semibold py-3.5 px-6 rounded-xl hover:bg-red-700 transition-all shadow-[0_4px_14px_0_rgba(227,6,19,0.2)] hover:shadow-[0_6px_20px_rgba(227,6,19,0.3)] hover:-translate-y-0.5 active:translate-y-0"
        >
          Volver al Inicio
        </button>
      </div>
    </div>
  );
};

export default UnauthorizedPage;
