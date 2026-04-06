/**
 * Dashboard principal
 * Contiene el layout con sidebar y las rutas internas de la aplicación
 */
import React, { useState } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ProvisioningPanel } from '../components/governance/ProvisioningPanel';
import { AdministracionUsuarios } from '../components/usuarios/AdministracionUsuarios';
import { ContadoresModule } from '../components/contadores/ContadoresModule';
import { UserCog, UserPlus, Search, BarChart3, Building2, Users, LogOut, ChevronDown } from 'lucide-react';
import ProtectedRoute from '../components/ProtectedRoute';
import EmpresasPage from './EmpresasPage';
import AdminUsersPage from './AdminUsersPage';
import { cn } from '../lib/utils';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };
  
  const getRoleBadgeColor = (rol: string) => {
    switch (rol) {
      case 'superadmin':
        return 'bg-red-100 text-red-800';
      case 'admin':
        return 'bg-blue-100 text-blue-800';
      case 'viewer':
        return 'bg-green-100 text-green-800';
      case 'operator':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  return (
    <div className="flex h-screen bg-[#FDFDFD] font-sans overflow-hidden">
      {/* Menú lateral Premium */}
      <nav className="w-80 bg-slate-900 border-r border-slate-800 text-white shadow-[10px_0_40px_rgba(0,0,0,0.08)] flex flex-col z-20 relative overflow-hidden">
        {/* Background Decor for Sidebar */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none opacity-30">
          <div className="absolute top-[-10%] right-[-10%] w-64 h-64 bg-ricoh-red/20 rounded-full blur-[80px]"></div>
          <div className="absolute bottom-[-5%] left-[-5%] w-48 h-48 bg-slate-700/30 rounded-full blur-[60px]"></div>
        </div>

        <div className="relative z-10 px-8 py-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 bg-ricoh-red rounded-lg flex items-center justify-center shadow-lg shadow-red-900/20">
               <div className="w-4 h-4 border-2 border-white rounded-sm rotate-45"></div>
            </div>
            <h1 className="text-lg font-black tracking-tighter uppercase">
              Ricoh<span className="text-ricoh-red shadow-sm ml-0.5">.</span>
            </h1>
          </div>
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] ml-1">Equipment Manager</p>
        </div>
        
        <div className="relative z-10 flex-1 py-6 overflow-y-auto custom-scrollbar px-4 space-y-2">
          <div className="px-4 pb-4">
             <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Operaciones</p>
          </div>
          
          <NavButton
            to="/descubrimiento"
            icon={<Search size={20} />}
            label="Buscar Equipos"
          />
          
          <NavButton
            to="/aprovisionamiento"
            icon={<UserPlus size={20} />}
            label="Asignar Usuarios"
          />
          
          <NavButton
            to="/administracion"
            icon={<UserCog size={20} />}
            label="Mis Impresoras"
          />
          
          <NavButton
            to="/contadores"
            icon={<BarChart3 size={20} />}
            label="Lectura de Contadores"
          />
          
          {/* Opciones solo para superadmin */}
          {user?.rol === 'superadmin' && (
            <div className="pt-8 space-y-2">
              <div className="px-4 pb-4">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                  Sistema & Control
                </p>
              </div>
              
              <NavButton
                to="/empresas"
                icon={<Building2 size={20} />}
                label="Mis Empresas"
              />
              
              <NavButton
                to="/admin-users"
                icon={<Users size={20} />}
                label="Administradores"
              />
            </div>
          )}
        </div>
        
        {/* Usuario info Premium */}
        <div className="relative z-10 p-6">
          <div className="bg-slate-800/40 backdrop-blur-md rounded-3xl border border-slate-700/50 p-2">
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="w-full flex items-center gap-3 p-2 rounded-2xl hover:bg-slate-700/50 transition-all group"
              >
                <div className="w-10 h-10 bg-gradient-to-br from-ricoh-red to-red-600 rounded-full flex items-center justify-center text-xs font-black shadow-[0_0_15px_rgba(227,6,19,0.3)] group-hover:scale-105 transition-all outline outline-2 outline-transparent group-hover:outline-white/10">
                  {user?.nombre_completo.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
                </div>
                <div className="flex-1 text-left overflow-hidden">
                  <p className="text-xs font-black truncate text-white uppercase tracking-tight">{user?.nombre_completo}</p>
                  <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">{user?.rol}</p>
                </div>
                <ChevronDown size={14} className={`text-slate-500 transition-transform duration-500 ${showUserMenu ? 'rotate-180 text-white' : ''}`} />
              </button>
              
              {showUserMenu && (
                <div className="absolute bottom-full left-0 right-0 mb-4 bg-[#111827] rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] border border-slate-800 py-2 text-slate-300 z-50 animate-slide-up transform origin-bottom">
                  {user?.empresa && (
                    <div className="px-4 py-3 border-b border-slate-800/50 bg-white/5">
                      <p className="text-[8px] font-black uppercase tracking-widest text-slate-500 mb-1">Corporación</p>
                      <p className="text-xs font-bold text-slate-200 truncate">{user.empresa.razon_social}</p>
                    </div>
                  )}
                  <div className="p-1.5">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-3 py-2.5 text-[11px] font-black uppercase tracking-widest hover:bg-red-500/10 hover:text-red-500 rounded-xl transition-all group"
                    >
                      <LogOut size={14} className="text-slate-500 group-hover:text-red-500 transition-colors" />
                      Cerrar Sesión
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Contenido principal Premium */}
      <div className="flex-1 overflow-hidden relative flex flex-col h-full bg-[#FDFDFD]">
        {/* Top Header Placeholder (can be added later) */}
        <div className="flex-1 overflow-y-auto px-10 py-10 relative">
          {/* Subtle Page Background Pattern */}
          <div className="absolute inset-0 opacity-[0.015] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '30px 30px' }}></div>
          
          <div className="max-w-[1600px] mx-auto relative z-10 min-h-full">
            <Routes>
              <Route path="/" element={<Navigate to="/descubrimiento" replace />} />
              <Route path="/descubrimiento" element={<ProvisioningPanel showDiscoveryOnly={true} />} />
              <Route path="/aprovisionamiento" element={<ProvisioningPanel showDiscoveryOnly={false} />} />
              <Route path="/administracion" element={<AdministracionUsuarios />} />
              <Route path="/contadores" element={<ContadoresModule />} />
              
              {/* Rutas solo para superadmin */}
              <Route
                path="/empresas"
                element={
                  <ProtectedRoute requiredRole={['superadmin']}>
                    <EmpresasPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin-users"
                element={
                  <ProtectedRoute requiredRole={['superadmin']}>
                    <AdminUsersPage />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </div>
        </div>
      </div>
    </div>
  );
};

// Componente auxiliar para botones de navegación
const NavButton = ({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) => {
  const navigate = useNavigate();
  const location = window.location.pathname;
  const isActive = location === to || (to !== '/' && location.startsWith(to));
  
  return (
    <button
      onClick={() => navigate(to)}
      className={`w-full flex items-center gap-4 px-5 py-4 text-[11px] font-black uppercase tracking-widest rounded-2xl transition-all duration-500 group relative overflow-hidden ${
        isActive
          ? 'bg-gradient-to-r from-ricoh-red/20 to-transparent text-white'
          : 'text-slate-500 hover:text-slate-200 hover:bg-white/5'
      }`}
    >
      {/* Active side indicator */}
      {isActive && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-6 bg-ricoh-red rounded-r-full shadow-[0_0_15px_rgba(227,6,19,0.8)] animate-pulse" />
      )}
      
      <span className={cn(
        "transition-all duration-500 relative z-10",
        isActive ? "text-ricoh-red scale-110" : "text-slate-600 group-hover:text-slate-300"
      )}>
        {icon}
      </span>
      <span className="relative z-10">{label}</span>

      {/* Hover Light Effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
    </button>
  );
};

export default Dashboard;
