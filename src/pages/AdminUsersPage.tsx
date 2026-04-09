/**
 * Página de gestión de usuarios admin (solo superadmin)
 */
import { useState, useEffect } from 'react';
import { Users, Plus, Search, Edit2, Trash2, Filter } from 'lucide-react';
import adminUserService from '../services/adminUserService';
import empresaService, { Empresa } from '../services/empresaService';
import { AdminUser } from '../services/authService';
import AdminUserModal from '../components/AdminUserModal';
import { useNotification } from '../hooks/useNotification';

const AdminUsersPage = () => {
  const notify = useNotification();
  const [adminUsers, setAdminUsers] = useState<AdminUser[]>([]);
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedAdminUser, setSelectedAdminUser] = useState<AdminUser | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    rol: '',
    empresa_id: '',
  });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  useEffect(() => {
    loadEmpresas();
  }, []);
  
  useEffect(() => {
    loadAdminUsers();
  }, [page, searchTerm, filters]);
  
  const loadEmpresas = async () => {
    try {
      const response = await empresaService.getAll({ page_size: 100 });
      setEmpresas(response.items);
    } catch (error) {
      console.error('Error al cargar empresas:', error);
    }
  };
  
  const loadAdminUsers = async () => {
    setLoading(true);
    try {
      const response = await adminUserService.getAll({
        page,
        page_size: 20,
        search: searchTerm || undefined,
        rol: filters.rol || undefined,
        empresa_id: filters.empresa_id ? Number(filters.empresa_id) : undefined,
      });
      setAdminUsers(response.items);
      setTotalPages(response.total_pages);
      setTotal(response.total);
    } catch (error) {
      console.error('Error al cargar usuarios admin:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreate = () => {
    setSelectedAdminUser(null);
    setShowModal(true);
  };
  
  const handleEdit = (adminUser: AdminUser) => {
    setSelectedAdminUser(adminUser);
    setShowModal(true);
  };
  
  const handleSave = async (data: any) => {
    if (selectedAdminUser) {
      await adminUserService.update(selectedAdminUser.id, data);
    } else {
      await adminUserService.create(data);
    }
    await loadAdminUsers();
  };
  
  const handleDelete = async (adminUser: AdminUser) => {
    if (!confirm(`¿Está seguro de desactivar el usuario "${adminUser.username}"?`)) {
      return;
    }
    
    try {
      await adminUserService.delete(adminUser.id);
      notify.success('Usuario desactivado', `${adminUser.username} ha sido desactivado correctamente`);
      await loadAdminUsers();
    } catch (error: any) {
      const message = error.response?.data?.detail?.message || error.response?.data?.detail || 'No se pudo desactivar el usuario';
      notify.error('Error al desactivar', message);
    }
  };
  
  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    setPage(1);
  };
  
  const handleFilterChange = (key: string, value: string) => {
    setFilters({ ...filters, [key]: value });
    setPage(1);
  };
  
  const getRoleBadgeColor = (rol: string) => {
    switch (rol) {
      case 'superadmin':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'admin':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'viewer':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'operator':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };
  
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };
  
  return (
    <div className="h-full overflow-auto bg-slate-50 animate-fade-in relative">
      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white rounded-xl shadow-sm border border-slate-100">
              <Users size={24} className="text-ricoh-red" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Gestión de Usuarios</h1>
              <p className="text-slate-500 text-sm mt-0.5">Administrar roles y accesos</p>
            </div>
          </div>
          <button
            onClick={handleCreate}
            className="relative overflow-hidden group flex items-center gap-2 px-5 py-2.5 bg-ricoh-red text-white font-semibold rounded-xl hover:bg-red-700 transition-all shadow-[0_4px_14px_0_rgba(227,6,19,0.39)] hover:shadow-[0_6px_20px_rgba(227,6,19,0.23)] hover:-translate-y-0.5 active:translate-y-0"
          >
            <Plus size={18} className="transform group-hover:rotate-90 transition-transform" />
            Nuevo Usuario Admin
          </button>
        </div>
        
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/40 border border-slate-100 overflow-hidden">
          <div className="p-5 border-b border-slate-100 bg-slate-50/50 space-y-5">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input
                type="text"
                placeholder="Buscar por username, nombre o email..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 border border-slate-200 bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent transition-all shadow-sm hover:border-slate-300 placeholder-slate-400"
              />
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">
                  <Filter size={14} className="inline mr-1 text-slate-400" />
                  Rol
                </label>
                <select
                  value={filters.rol}
                  onChange={(e) => handleFilterChange('rol', e.target.value)}
                  className="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-ricoh-red shadow-sm hover:border-slate-300 transition-colors"
                >
                  <option value="">Todos los roles</option>
                  <option value="superadmin">Superadmin</option>
                  <option value="admin">Admin</option>
                  <option value="viewer">Viewer</option>
                  <option value="operator">Operator</option>
                </select>
              </div>
              
              <div className="flex-1">
                <label className="block text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">
                  <Filter size={14} className="inline mr-1 text-slate-400" />
                  Empresa
                </label>
                <select
                  value={filters.empresa_id}
                  onChange={(e) => handleFilterChange('empresa_id', e.target.value)}
                  className="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-ricoh-red shadow-sm hover:border-slate-300 transition-colors"
                >
                  <option value="">Todas las empresas</option>
                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>
                      {empresa.razon_social}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
          
          {loading ? (
            <div className="p-8 text-center text-gray-500">Cargando...</div>
          ) : adminUsers.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {searchTerm || filters.rol || filters.empresa_id
                ? 'No se encontraron usuarios'
                : 'No hay usuarios admin registrados'}
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full table-fixed">
                  <thead className="bg-slate-50 border-b border-slate-100">
                    <tr>
                      <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest w-[12%]">
                        Username
                      </th>
                      <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest w-[16%]">
                        Nombre Completo
                      </th>
                      <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest w-[16%]">
                        Email
                      </th>
                      <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest w-[10%]">
                        Rol
                      </th>
                      <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest w-[14%]">
                        Empresa
                      </th>
                      <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest w-[9%]">
                        Estado
                      </th>
                      <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest w-[15%]">
                        Último Login
                      </th>
                      <th className="px-4 py-4 text-center text-[11px] font-bold text-slate-500 uppercase tracking-widest w-[8%]">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-100">
                    {adminUsers.map((user) => (
                      <tr key={user.id} className="hover:bg-slate-50/80 transition-colors group">
                        <td className="px-4 py-4">
                          <div className="text-sm font-semibold text-slate-800 truncate" title={user.username}>{user.username}</div>
                        </td>
                        <td className="px-4 py-4">
                          <div className="text-sm text-slate-500 truncate" title={user.nombre_completo}>{user.nombre_completo}</div>
                        </td>
                        <td className="px-4 py-4">
                          <div className="text-sm text-slate-500 truncate" title={user.email}>{user.email}</div>
                        </td>
                        <td className="px-4 py-4">
                          <span
                            className={`inline-flex px-2 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md border ${getRoleBadgeColor(
                              user.rol
                            )} shadow-sm`}
                          >
                            {user.rol}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <div className="text-sm text-slate-500 truncate" title={user.empresa?.razon_social || '-'}>
                            {user.empresa?.razon_social || '-'}
                          </div>
                        </td>
                        <td className="px-4 py-4">
                          <span
                            className={`inline-flex items-center px-2 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md border ${
                              user.is_active
                                ? 'bg-green-50 text-green-700 border-green-200'
                                : 'bg-red-50 text-red-700 border-red-200'
                            } shadow-sm`}
                          >
                            {user.is_active ? 'Activo' : 'Inactivo'}
                          </span>
                        </td>
                        <td className="px-4 py-4">
                          <div className="text-xs text-slate-500 truncate" title={formatDate(user.last_login)}>{formatDate(user.last_login)}</div>
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleEdit(user)}
                              className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Editar"
                            >
                              <Edit2 size={15} />
                            </button>
                            {user.is_active && (
                              <button
                                onClick={() => handleDelete(user)}
                                className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Desactivar"
                              >
                                <Trash2 size={15} />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {totalPages > 1 && (
                <div className="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between">
                  <div className="text-sm font-medium text-slate-500">
                    Mostrando <span className="text-slate-900">{adminUsers.length}</span> de <span className="text-slate-900">{total}</span> usuarios
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage(page - 1)}
                      disabled={page === 1}
                      className="px-4 py-2 border border-slate-200 font-medium text-sm rounded-lg bg-white hover:bg-slate-50 text-slate-600 focus:outline-none focus:ring-2 focus:ring-ricoh-red disabled:opacity-50 disabled:bg-transparent transition-colors shadow-sm"
                    >
                      Anterior
                    </button>
                    <span className="px-4 py-2 text-sm font-bold text-slate-700">
                      Página {page} de {totalPages}
                    </span>
                    <button
                      onClick={() => setPage(page + 1)}
                      disabled={page === totalPages}
                      className="px-4 py-2 border border-slate-200 font-medium text-sm rounded-lg bg-white hover:bg-slate-50 text-slate-600 focus:outline-none focus:ring-2 focus:ring-ricoh-red disabled:opacity-50 disabled:bg-transparent transition-colors shadow-sm"
                    >
                      Siguiente
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
      
      {showModal && (
        <AdminUserModal
          adminUser={selectedAdminUser}
          onClose={() => setShowModal(false)}
          onSave={handleSave}
        />
      )}
    </div>
  );
};

export default AdminUsersPage;
