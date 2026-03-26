/**
 * Dashboard principal
 * Contiene el layout con sidebar y las rutas internas de la aplicación
 */
import { useState } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ProvisioningPanel } from '../components/governance/ProvisioningPanel';
import { AdministracionUsuarios } from '../components/usuarios/AdministracionUsuarios';
import { ContadoresModule } from '../components/contadores/ContadoresModule';
import { UserCog, UserPlus, Search, BarChart3, Building2, Users, LogOut, ChevronDown } from 'lucide-react';
import ProtectedRoute from '../components/ProtectedRoute';
import EmpresasPage from './EmpresasPage';
import AdminUsersPage from './AdminUsersPage';

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
    <div className="flex h-screen">
      {/* Menú lateral */}
      <nav className="w-64 bg-industrial-gray text-white shadow-lg flex flex-col">
        <div className="px-6 py-4 border-b border-slate-700">
          <h1 className="text-sm font-bold uppercase tracking-tight">
            Ricoh Equipment Manager
          </h1>
        </div>
        
        <div className="flex-1 py-4 overflow-y-auto">
          <NavButton
            to="/descubrimiento"
            icon={<Search size={18} />}
            label="Descubrir Impresoras"
          />
          
          <NavButton
            to="/aprovisionamiento"
            icon={<UserPlus size={18} />}
            label="Crear Usuarios"
          />
          
          <NavButton
            to="/administracion"
            icon={<UserCog size={18} />}
            label="Administrar Usuarios"
          />
          
          <NavButton
            to="/contadores"
            icon={<BarChart3 size={18} />}
            label="Contadores"
          />
          
          {/* Opciones solo para superadmin */}
          {user?.rol === 'superadmin' && (
            <>
              <div className="px-6 py-2 mt-4">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Administración
                </p>
              </div>
              
              <NavButton
                to="/empresas"
                icon={<Building2 size={18} />}
                label="Gestión de Empresas"
              />
              
              <NavButton
                to="/admin-users"
                icon={<Users size={18} />}
                label="Usuarios Admin"
              />
            </>
          )}
        </div>
        
        {/* Usuario info */}
        <div className="border-t border-slate-700 p-4">
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-sm font-bold">
                {user?.nombre_completo.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 text-left">
                <p className="text-sm font-medium truncate">{user?.nombre_completo}</p>
                <span className={`inline-block text-xs px-2 py-0.5 rounded-full ${getRoleBadgeColor(user?.rol || '')}`}>
                  {user?.rol}
                </span>
              </div>
              <ChevronDown size={16} className={`transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
            </button>
            
            {showUserMenu && (
              <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-lg py-2 text-gray-700">
                {user?.empresa && (
                  <div className="px-4 py-2 border-b border-gray-200">
                    <p className="text-xs text-gray-500">Empresa</p>
                    <p className="text-sm font-medium">{user.empresa.razon_social}</p>
                  </div>
                )}
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-100 transition-colors"
                >
                  <LogOut size={16} />
                  Cerrar Sesión
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Contenido */}
      <div className="flex-1 overflow-hidden">
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
  );
};

// Componente auxiliar para botones de navegación
const NavButton = ({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) => {
  const navigate = useNavigate();
  const isActive = window.location.pathname === to;
  
  return (
    <button
      onClick={() => navigate(to)}
      className={`w-full flex items-center gap-3 px-6 py-3 text-sm font-bold uppercase tracking-wide transition-colors ${
        isActive
          ? 'bg-ricoh-red text-white border-l-4 border-white'
          : 'text-slate-300 hover:bg-slate-800'
      }`}
    >
      {icon}
      {label}
    </button>
  );
};

export default Dashboard;
