/**
 * Página de gestión de usuarios admin (solo superadmin)
 */
import { useState, useEffect } from 'react';
import { Users, Plus, Search, Edit2, Trash2, Filter } from 'lucide-react';
import adminUserService from '../services/adminUserService';
import empresaService, { Empresa } from '../services/empresaService';
import { AdminUser } from '../services/authService';
import AdminUserModal from '../components/AdminUserModal';

const AdminUsersPage = () => {
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
      await loadAdminUsers();
    } catch (error: any) {
      if (error.response?.data?.detail) {
        alert(error.response.data.detail.message || 'Error al desactivar usuario');
      } else {
        alert('Error al desactivar usuario');
      }
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
    <div className="h-full overflow-auto bg-gray-50">
      <div className="p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Users size={32} className="text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestión de Usuarios Admin</h1>
              <p className="text-gray-600">Administrar usuarios administradores del sistema</p>
            </div>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            Nuevo Usuario Admin
          </button>
        </div>
        
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200 space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Buscar por username, nombre o email..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Filter size={16} className="inline mr-1" />
                  Rol
                </label>
                <select
                  value={filters.rol}
                  onChange={(e) => handleFilterChange('rol', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Todos los roles</option>
                  <option value="superadmin">Superadmin</option>
                  <option value="admin">Admin</option>
                  <option value="viewer">Viewer</option>
                  <option value="operator">Operator</option>
                </select>
              </div>
              
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Filter size={16} className="inline mr-1" />
                  Empresa
                </label>
                <select
                  value={filters.empresa_id}
                  onChange={(e) => handleFilterChange('empresa_id', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Username
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Nombre Completo
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Rol
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Empresa
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Último Login
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {adminUsers.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{user.username}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{user.nombre_completo}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{user.email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleBadgeColor(
                              user.rol
                            )}`}
                          >
                            {user.rol}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">
                            {user.empresa?.razon_social || '-'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              user.is_active
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {user.is_active ? 'Activo' : 'Inactivo'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{formatDate(user.last_login)}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleEdit(user)}
                            className="text-blue-600 hover:text-blue-900 mr-3"
                            title="Editar"
                          >
                            <Edit2 size={18} />
                          </button>
                          {user.is_active && (
                            <button
                              onClick={() => handleDelete(user)}
                              className="text-red-600 hover:text-red-900"
                              title="Desactivar"
                            >
                              <Trash2 size={18} />
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {totalPages > 1 && (
                <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                  <div className="text-sm text-gray-700">
                    Mostrando {adminUsers.length} de {total} usuarios
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage(page - 1)}
                      disabled={page === 1}
                      className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    <span className="px-3 py-1 text-gray-700">
                      Página {page} de {totalPages}
                    </span>
                    <button
                      onClick={() => setPage(page + 1)}
                      disabled={page === totalPages}
                      className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
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
