import { useState, useEffect } from 'react';
import { CierreMensual, CierreMensualDetalle } from './types';

const API_BASE = 'http://localhost:8000';

interface CierreDetalleModalProps {
  cierre: CierreMensual;
  onClose: () => void;
}

export const CierreDetalleModal: React.FC<CierreDetalleModalProps> = ({
  cierre,
  onClose
}) => {
  const [detalle, setDetalle] = useState<CierreMensualDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<'nombre_usuario' | 'consumo_total'>('consumo_total');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    loadDetalle();
  }, [cierre.id]);

  const loadDetalle = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE}/api/counters/monthly/${cierre.id}/detail`
      );

      if (!response.ok) throw new Error('Error al cargar detalle');

      const data = await response.json();
      setDetalle(data);
    } catch (err: any) {
      console.error('Error loading detalle:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => num.toLocaleString('es-ES');
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredUsuarios = detalle?.usuarios.filter(u =>
    u.nombre_usuario.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.codigo_usuario.includes(searchTerm)
  ) || [];

  const sortedUsuarios = [...filteredUsuarios].sort((a, b) => {
    const aVal = sortField === 'nombre_usuario' ? a.nombre_usuario : a.consumo_total;
    const bVal = sortField === 'nombre_usuario' ? b.nombre_usuario : b.consumo_total;
    
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortDirection === 'asc' 
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    }
    
    return sortDirection === 'asc' 
      ? (aVal as number) - (bVal as number)
      : (bVal as number) - (aVal as number);
  });

  const handleSort = (field: 'nombre_usuario' | 'consumo_total') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Detalle del Cierre
              </h2>
              <p className="text-sm text-gray-600">
                {formatDate(cierre.fecha_inicio)}
                {cierre.fecha_inicio !== cierre.fecha_fin && <> - {formatDate(cierre.fecha_fin)}</>}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
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
                    Usuarios ({detalle.usuarios.length})
                  </h3>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Buscar usuario..."
                      className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th
                            onClick={() => handleSort('nombre_usuario')}
                            className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                          >
                            Usuario {sortField === 'nombre_usuario' && (sortDirection === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Código
                          </th>
                          <th
                            onClick={() => handleSort('consumo_total')}
                            className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                          >
                            Consumo {sortField === 'consumo_total' && (sortDirection === 'asc' ? '↑' : '↓')}
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Copiadora
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Impresora
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Escáner
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {sortedUsuarios.map((usuario) => (
                          <tr key={usuario.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm text-gray-900">{usuario.nombre_usuario}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{usuario.codigo_usuario}</td>
                            <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                              {formatNumber(usuario.consumo_total)}
                            </td>
                            <td className="px-4 py-3 text-sm text-right text-gray-600">
                              {formatNumber(usuario.consumo_copiadora)}
                            </td>
                            <td className="px-4 py-3 text-sm text-right text-gray-600">
                              {formatNumber(usuario.consumo_impresora)}
                            </td>
                            <td className="px-4 py-3 text-sm text-right text-gray-600">
                              {formatNumber(usuario.consumo_escaner)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {sortedUsuarios.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    No se encontraron usuarios
                  </div>
                )}
              </div>
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 border-t border-gray-200 px-6 py-4 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};
