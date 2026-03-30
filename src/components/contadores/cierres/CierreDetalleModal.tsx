import { useState, useEffect } from 'react';
import { CierreMensual, CierreMensualDetalle } from './types';
import { useColumnVisibility } from '@/hooks/useColumnVisibility';
import { Modal, Button, Input, Spinner } from '@/components/ui';
import { Download, FileSpreadsheet } from 'lucide-react';
import closeService from '@/services/closeService';
import exportService from '@/services/exportService';
import { parseApiError } from '@/utils/errorHandler';
import { useNotification } from '@/hooks/useNotification';

interface CierreDetalleModalProps {
  cierre: CierreMensual;
  onClose: () => void;
}

export const CierreDetalleModal: React.FC<CierreDetalleModalProps> = ({
  cierre,
  onClose
}) => {
  const notify = useNotification();
  const [detalle, setDetalle] = useState<CierreMensualDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<'nombre_usuario' | 'total_paginas' | 'consumo_total'>('total_paginas');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // Get column visibility based on printer capabilities
  const { isColumnVisible } = useColumnVisibility(detalle?.printer?.capabilities);
  
  // Determine if printer uses ecological format
  const isEcologicalFormat = detalle?.printer?.capabilities?.formato_contadores === 'ecologico';

  useEffect(() => {
    loadDetalle();
  }, [cierre.id]); // Solo recargar cuando cambia el cierre

  // Resetear a página 1 cuando cambia el término de búsqueda
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  const loadDetalle = async () => {
    setLoading(true);
    setError(null);

    try {
      // Cargar TODOS los usuarios sin paginación para que la búsqueda funcione en todos
      const data = await closeService.getCloseDetail(cierre.id, 1, 10000);
      setDetalle(data);
    } catch (err: any) {
      console.error('Error loading detalle:', err);
      setError(parseApiError(err, 'Error al cargar detalle'));
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => num.toLocaleString('es-ES');
  const formatDate = (dateStr: string, includeTime: boolean = false) => {
    // Para evitar el desfase de zona horaria con YYYY-MM-DD, reemplazamos guiones por barras 
    // o forzamos que no se interprete como UTC
    const date = new Date(dateStr.includes('T') ? dateStr : `${dateStr}T00:00:00`);
    
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      ...(includeTime ? { hour: '2-digit', minute: '2-digit' } : {})
    });
  };

  const filteredUsuarios = (detalle?.usuarios || []).filter(usuario => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      usuario.nombre_usuario.toLowerCase().includes(searchLower) ||
      usuario.codigo_usuario.toLowerCase().includes(searchLower)
    );
  });

  const sortedUsuarios = [...filteredUsuarios].sort((a, b) => {
    let aVal: string | number;
    let bVal: string | number;
    
    if (sortField === 'nombre_usuario') {
      aVal = a.nombre_usuario;
      bVal = b.nombre_usuario;
    } else if (sortField === 'total_paginas') {
      aVal = a.total_paginas;
      bVal = b.total_paginas;
    } else {
      aVal = a.consumo_total;
      bVal = b.consumo_total;
    }
    
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortDirection === 'asc' 
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    }
    
    return sortDirection === 'asc' 
      ? (aVal as number) - (bVal as number)
      : (bVal as number) - (aVal as number);
  });

  const handleSort = (field: 'nombre_usuario' | 'total_paginas' | 'consumo_total') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Paginación del lado del cliente
  const pageSize = 50;
  const totalFilteredUsers = sortedUsuarios.length;
  const totalPages = Math.ceil(totalFilteredUsers / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedUsuarios = sortedUsuarios.slice(startIndex, endIndex);

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={`Detalle del Cierre - ${formatDate(cierre.fecha_inicio)}`}
      size="xl"
    >
      <div className="space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Spinner size="lg" text="Cargando detalle..." />
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700">{error}</p>
            </div>
          ) : detalle ? (
            <>
              {/* Resumen de totales */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-xs text-gray-600 mb-1">Total Páginas</p>
                  <p className="text-2xl font-bold text-gray-900">{formatNumber(detalle.total_paginas)}</p>
                  <p className="text-xs text-green-600 mt-1">+{formatNumber(detalle.diferencia_total)}</p>
                </div>
                {!isEcologicalFormat && (
                  <>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-xs text-gray-600 mb-1">Copiadora</p>
                      <p className="text-2xl font-bold text-gray-900">{formatNumber(detalle.total_copiadora)}</p>
                      <p className="text-xs text-green-600 mt-1">+{formatNumber(detalle.diferencia_copiadora)}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-xs text-gray-600 mb-1">Impresora</p>
                      <p className="text-2xl font-bold text-gray-900">{formatNumber(detalle.total_impresora)}</p>
                      <p className="text-xs text-green-600 mt-1">+{formatNumber(detalle.diferencia_impresora)}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-xs text-gray-600 mb-1">Escáner</p>
                      <p className="text-2xl font-bold text-gray-900">{formatNumber(detalle.total_escaner)}</p>
                      <p className="text-xs text-green-600 mt-1">+{formatNumber(detalle.diferencia_escaner)}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-xs text-gray-600 mb-1">Fax</p>
                      <p className="text-2xl font-bold text-gray-900">{formatNumber(detalle.total_fax)}</p>
                      <p className="text-xs text-green-600 mt-1">+{formatNumber(detalle.diferencia_fax)}</p>
                    </div>
                  </>
                )}
              </div>

              {/* Información adicional */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Cerrado por:</span>
                    <span className="ml-2 font-medium text-gray-900">{detalle.cerrado_por || 'Sistema'}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Fecha de cierre:</span>
                    <span className="ml-2 font-medium text-gray-900">{formatDate(detalle.fecha_cierre)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Usuarios:</span>
                    <span className="ml-2 font-medium text-gray-900">{detalle.usuarios.length}</span>
                  </div>
                </div>
                {detalle.notas && (
                  <div className="mt-3 pt-3 border-t border-blue-300">
                    <p className="text-xs text-gray-600 mb-1">Notas:</p>
                    <p className="text-sm text-gray-900">{detalle.notas}</p>
                  </div>
                )}
              </div>

              {/* Tabla de usuarios */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Usuarios ({detalle.total_usuarios})
                  </h3>
                  <Input
                    type="search"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Buscar usuario..."
                    className="w-64"
                  />
                </div>

                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 text-xs">
                      <thead className="bg-gray-50">
                        {isEcologicalFormat ? (
                          // Tabla simplificada para formato ecológico
                          <tr className="border-b border-gray-200">
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Usuario
                            </th>
                            <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Código
                            </th>
                            <th
                              onClick={() => handleSort('total_paginas')}
                              className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider bg-blue-50/50 cursor-pointer hover:bg-blue-100/50"
                            >
                              Total {sortField === 'total_paginas' && (sortDirection === 'asc' ? '↑' : '↓')}
                            </th>
                            <th
                              onClick={() => handleSort('consumo_total')}
                              className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                            >
                              Consumo {sortField === 'consumo_total' && (sortDirection === 'asc' ? '↑' : '↓')}
                            </th>
                          </tr>
                        ) : (
                          // Tabla completa para formato estándar y simplificado
                          <>
                            <tr className="border-b border-gray-300">
                              <th rowSpan={2} className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Usuario
                              </th>
                              <th rowSpan={2} className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Código
                              </th>
                              <th rowSpan={2}
                                onClick={() => handleSort('total_paginas')}
                                className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider bg-blue-50/50 cursor-pointer hover:bg-blue-100/50"
                              >
                                Total {sortField === 'total_paginas' && (sortDirection === 'asc' ? '↑' : '↓')}
                              </th>
                              <th rowSpan={2}
                                onClick={() => handleSort('consumo_total')}
                                className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                              >
                                Consumo {sortField === 'consumo_total' && (sortDirection === 'asc' ? '↑' : '↓')}
                              </th>
                              <th colSpan={isColumnVisible('color') ? 2 : 1} className="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-slate-100 border-r border-gray-300">
                                Total
                              </th>
                              <th colSpan={isColumnVisible('color') ? 2 : 1} className="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-blue-50 border-r border-gray-300">
                                Copiadora
                              </th>
                              <th colSpan={isColumnVisible('color') ? 2 : 1} className="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-green-50 border-r border-gray-300">
                                Impresora
                              </th>
                              <th colSpan={isColumnVisible('color') ? 2 : 1} className="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider bg-purple-50">
                                Escáner
                              </th>
                            </tr>
                            <tr className="border-b border-gray-200">
                              <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase bg-slate-100">B/N</th>
                              {isColumnVisible('color') && (
                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase bg-slate-100 border-r border-gray-300">Color</th>
                              )}
                              <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase bg-blue-50">B/N</th>
                              {isColumnVisible('color') && (
                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase bg-blue-50 border-r border-gray-300">Color</th>
                              )}
                              <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase bg-green-50">B/N</th>
                              {isColumnVisible('color') && (
                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase bg-green-50 border-r border-gray-300">Color</th>
                              )}
                              <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase bg-purple-50">B/N</th>
                              {isColumnVisible('color') && (
                                <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase bg-purple-50">Color</th>
                              )}
                            </tr>
                          </>
                        )}
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {paginatedUsuarios.map((usuario) => (
                          <tr key={usuario.id} className="hover:bg-gray-50">
                            <td className="px-3 py-2 text-xs text-gray-900">{usuario.nombre_usuario}</td>
                            <td className="px-3 py-2 text-xs text-gray-600">{usuario.codigo_usuario}</td>
                            <td className="px-3 py-2 text-xs text-right font-semibold text-blue-700 bg-blue-50/30">
                              {formatNumber(usuario.total_paginas)}
                            </td>
                            <td className="px-3 py-2 text-xs text-right font-medium text-gray-900">
                              {formatNumber(usuario.consumo_total)}
                            </td>
                            {!isEcologicalFormat && (
                              <>
                                <td className="px-3 py-2 text-xs text-right text-gray-600 bg-slate-50">
                                  {formatNumber(usuario.total_bn)}
                                </td>
                                {isColumnVisible('color') && (
                                  <td className="px-3 py-2 text-xs text-right text-gray-600 bg-slate-50 border-r border-gray-200">
                                    {formatNumber(usuario.total_color)}
                                  </td>
                                )}
                                <td className="px-3 py-2 text-xs text-right text-gray-600">
                                  {formatNumber(usuario.copiadora_bn)}
                                </td>
                                {isColumnVisible('color') && (
                                  <td className="px-3 py-2 text-xs text-right text-gray-600 border-r border-gray-200">
                                    {formatNumber(usuario.copiadora_color)}
                                  </td>
                                )}
                                <td className="px-3 py-2 text-xs text-right text-gray-600">
                                  {formatNumber(usuario.impresora_bn)}
                                </td>
                                {isColumnVisible('color') && (
                                  <td className="px-3 py-2 text-xs text-right text-gray-600 border-r border-gray-200">
                                    {formatNumber(usuario.impresora_color)}
                                  </td>
                                )}
                                <td className="px-3 py-2 text-xs text-right text-gray-600">
                                  {formatNumber(usuario.escaner_bn)}
                                </td>
                                {isColumnVisible('color') && (
                                  <td className="px-3 py-2 text-xs text-right text-gray-600">
                                    {formatNumber(usuario.escaner_color)}
                                  </td>
                                )}
                              </>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Paginación del lado del cliente */}
                {totalPages > 1 && (
                  <div className="mt-4 flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Mostrando {startIndex + 1} - {Math.min(endIndex, totalFilteredUsers)} de {totalFilteredUsers} usuarios
                      {searchTerm && ` (filtrados de ${detalle?.total_usuarios || 0} totales)`}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                      >
                        Anterior
                      </Button>
                      <span className="text-sm text-gray-600">
                        Página {currentPage} de {totalPages}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                      >
                        Siguiente
                      </Button>
                    </div>
                  </div>
                )}

                {paginatedUsuarios.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    {searchTerm ? `No se encontraron usuarios que coincidan con "${searchTerm}"` : 'No se encontraron usuarios'}
                  </div>
                )}
              </div>
            </>
          ) : null}
        </div>

      {/* Footer */}
      {detalle && (
        <div className="flex items-center justify-end gap-3 pt-6 border-t border-gray-200">
          <Button
            variant="outline"
            size="sm"
            icon={<FileSpreadsheet size={16} />}
            onClick={async () => {
              try {
                await exportService.exportCierreExcel(cierre.id);
                notify.success('Archivo descargado', 'El archivo Excel se descargó correctamente');
              } catch (error: any) {
                console.error('Error al exportar:', error);
                notify.error('Error al exportar', error.message || 'No se pudo generar el archivo Excel');
              }
            }}
          >
            Exportar Excel
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={<Download size={16} />}
            onClick={async () => {
              try {
                await exportService.exportCierreCSV(cierre.id);
                notify.success('Archivo descargado', 'El archivo CSV se descargó correctamente');
              } catch (error: any) {
                console.error('Error al exportar:', error);
                notify.error('Error al exportar', error.message || 'No se pudo generar el archivo CSV');
              }
            }}
          >
            Exportar CSV
          </Button>
          <Button
            variant="ghost"
            onClick={onClose}
          >
            Cerrar
          </Button>
        </div>
      )}
    </Modal>
  );
};
