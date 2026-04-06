/**
 * Página de gestión de empresas (solo superadmin)
 */
import { useState, useEffect } from 'react';
import { Building2, Plus, Search, Edit2, Trash2 } from 'lucide-react';
import empresaService, { Empresa } from '../services/empresaService';
import EmpresaModal from '../components/EmpresaModal';
import { useNotification } from '../hooks/useNotification';

const EmpresasPage = () => {
  const notify = useNotification();
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
      notify.success('Empresa desactivada', `${empresa.razon_social} ha sido desactivada correctamente`);
      await loadEmpresas();
    } catch (error: any) {
      const message = error.response?.data?.detail?.message || error.response?.data?.detail || 'No se pudo desactivar la empresa';
      notify.error('Error al desactivar', message);
    }
  };
  
  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    setPage(1);
  };
  
  return (
    <div className="h-full overflow-auto bg-slate-50 animate-fade-in relative">
      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white rounded-xl shadow-sm border border-slate-100">
              <Building2 size={24} className="text-ricoh-red" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Mis Empresas</h1>
              <p className="text-slate-500 text-sm mt-0.5">Administrar empresas del sistema</p>
            </div>
          </div>
          <button
            onClick={handleCreate}
            className="relative overflow-hidden group flex items-center gap-2 px-5 py-2.5 bg-ricoh-red text-white font-semibold rounded-xl hover:bg-red-700 transition-all shadow-[0_4px_14px_0_rgba(227,6,19,0.39)] hover:shadow-[0_6px_20px_rgba(227,6,19,0.23)] hover:-translate-y-0.5 active:translate-y-0"
          >
            <Plus size={18} className="transform group-hover:rotate-90 transition-transform" />
            Nueva Empresa
          </button>
        </div>
        
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/40 border border-slate-100 overflow-hidden">
          <div className="p-5 border-b border-slate-100 bg-slate-50/50">
            <div className="relative max-w-md">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input
                type="text"
                placeholder="Buscar por razón social o nombre comercial..."
                value={searchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="w-full pl-11 pr-4 py-2.5 border border-slate-200 bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent transition-all shadow-sm hover:border-slate-300 placeholder-slate-400"
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
                  <thead className="bg-slate-50 border-b border-slate-100">
                    <tr>
                      <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
                        Razón Social
                      </th>
                      <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
                        Nombre Comercial
                      </th>
                      <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
                        NIT
                      </th>
                      <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
                        Contacto
                      </th>
                      <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
                        Estado
                      </th>
                      <th className="px-6 py-4 text-right text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-100">
                    {empresas.map((empresa) => (
                      <tr key={empresa.id} className="hover:bg-slate-50/80 transition-colors group">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-semibold text-slate-800">{empresa.razon_social}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-500">{empresa.nombre_comercial}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-500 font-mono text-xs">{empresa.nit || '-'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-500">{empresa.contacto_nombre || '-'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider rounded-md border ${
                              empresa.is_active
                                ? 'bg-green-50 text-green-700 border-green-200'
                                : 'bg-red-50 text-red-700 border-red-200'
                            } shadow-sm`}
                          >
                            {empresa.is_active ? 'Activa' : 'Inactiva'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleEdit(empresa)}
                              className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Editar"
                            >
                              <Edit2 size={16} />
                            </button>
                            {empresa.is_active && (
                              <button
                                onClick={() => handleDelete(empresa)}
                                className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Desactivar"
                              >
                                <Trash2 size={16} />
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
                    Mostrando <span className="text-slate-900">{empresas.length}</span> de <span className="text-slate-900">{total}</span> empresas
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
