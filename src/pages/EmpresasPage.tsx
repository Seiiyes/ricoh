/**
 * Página de gestión de empresas (solo superadmin)
 */
import { useState, useEffect } from 'react';
import { Building2, Plus, Search, Edit2, Trash2 } from 'lucide-react';
import empresaService, { Empresa } from '../services/empresaService';
import EmpresaModal from '../components/EmpresaModal';

const EmpresasPage = () => {
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedEmpresa, setSelectedEmpresa] = useState<Empresa | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  useEffect(() => {
    loadEmpresas();
  }, [page, searchTerm]);
  
  const loadEmpresas = async () => {
    setLoading(true);
    try {
      const response = await empresaService.getAll({
        page,
        page_size: 20,
        search: searchTerm || undefined,
      });
      setEmpresas(response.items);
      setTotalPages(response.total_pages);
      setTotal(response.total);
    } catch (error) {
      console.error('Error al cargar empresas:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreate = () => {
    setSelectedEmpresa(null);
    setShowModal(true);
  };
  
  const handleEdit = (empresa: Empresa) => {
    setSelectedEmpresa(empresa);
    setShowModal(true);
  };
  
  const handleSave = async (data: any) => {
    if (selectedEmpresa) {
      await empresaService.update(selectedEmpresa.id, data);
    } else {
      await empresaService.create(data);
    }
    await loadEmpresas();
  };
  
  const handleDelete = async (empresa: Empresa) => {
    if (!confirm(`¿Está seguro de desactivar la empresa "${empresa.razon_social}"?`)) {
      return;
    }
    
    try {
      await empresaService.delete(empresa.id);
      await loadEmpresas();
    } catch (error: any) {
      if (error.response?.data?.detail) {
        alert(error.response.data.detail.message || 'Error al desactivar empresa');
      } else {
        alert('Error al desactivar empresa');
      }
    }
  };
  
  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    setPage(1);
  };
  
  return (
    <div className="h-full overflow-auto bg-gray-50">
      <div className="p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Building2 size={32} className="text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Gestión de Empresas</h1>
              <p className="text-gray-600">Administrar empresas del sistema</p>
            </div>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={20} />
            Nueva Empresa
          </button>
        </div>
        
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Buscar por razón social o nombre comercial..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          {loading ? (
            <div className="p-8 text-center text-gray-500">Cargando...</div>
          ) : empresas.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {searchTerm ? 'No se encontraron empresas' : 'No hay empresas registradas'}
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Razón Social
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Nombre Comercial
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        NIT
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contacto
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {empresas.map((empresa) => (
                      <tr key={empresa.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">{empresa.razon_social}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{empresa.nombre_comercial}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{empresa.nit || '-'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-600">{empresa.contacto_nombre || '-'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              empresa.is_active
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {empresa.is_active ? 'Activa' : 'Inactiva'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleEdit(empresa)}
                            className="text-blue-600 hover:text-blue-900 mr-3"
                            title="Editar"
                          >
                            <Edit2 size={18} />
                          </button>
                          {empresa.is_active && (
                            <button
                              onClick={() => handleDelete(empresa)}
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
                    Mostrando {empresas.length} de {total} empresas
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
        <EmpresaModal
          empresa={selectedEmpresa}
          onClose={() => setShowModal(false)}
          onSave={handleSave}
        />
      )}
    </div>
  );
};

export default EmpresasPage;
