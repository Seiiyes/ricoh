import { useState, useEffect } from 'react';
import { CierreMensual, ComparacionCierres } from './types';
import { UsuarioComparacionRow } from './UsuarioComparacionRow';

const API_BASE = 'http://localhost:8000';

interface ComparacionModalProps {
  printerId: number;
  cierres: CierreMensual[];
  onClose: () => void;
}

export const ComparacionModal: React.FC<ComparacionModalProps> = ({
  cierres,
  onClose
}) => {
  const [cierre1Id, setCierre1Id] = useState<number | null>(null);
  const [cierre2Id, setCierre2Id] = useState<number | null>(null);
  const [comparacion, setComparacion] = useState<ComparacionCierres | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<'nombre' | 'codigo' | 'diferencia' | 'consumo1' | 'consumo2'>('diferencia');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    if (cierres.length >= 2) {
      setCierre1Id(cierres[1].id);
      setCierre2Id(cierres[0].id);
    }
  }, [cierres]);

  useEffect(() => {
    if (cierre1Id && cierre2Id) {
      loadComparacion();
    }
  }, [cierre1Id, cierre2Id]);

  const loadComparacion = async () => {
    if (!cierre1Id || !cierre2Id) return;

    setLoading(true);
    setError(null);

    try {
      // Cargar todos los usuarios sin límite
      const response = await fetch(
        `${API_BASE}/api/counters/monthly/compare/${cierre1Id}/${cierre2Id}`
      );

      if (!response.ok) throw new Error('Error al comparar cierres');

      const data = await response.json();
      setComparacion(data);
    } catch (err: any) {
      console.error('Error loading comparacion:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => num.toLocaleString('es-ES');
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatDiferencia = (num: number) => {
    const sign = num >= 0 ? '+' : '';
    return `${sign}${formatNumber(num)}`;
  };

  const getDiferenciaColor = (num: number) => {
    if (num > 0) return 'text-green-600';
    if (num < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const handleSort = (field: 'nombre' | 'codigo' | 'diferencia' | 'consumo1' | 'consumo2') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const SortIcon = ({ active }: { active: boolean }) => (
    <span className={`ml-1 ${active ? 'text-purple-600' : 'text-gray-300'}`}>
      {sortDirection === 'asc' ? '↑' : '↓'}
    </span>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Comparación de Cierres
              </h2>
              <p className="text-sm text-gray-600">
                Compara dos períodos para ver diferencias
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
          {/* Selectores */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Período 1 (Base)
              </label>
              <select
                value={cierre1Id || ''}
                onChange={(e) => setCierre1Id(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Seleccionar...</option>
                {cierres.map((cierre) => (
                  <option key={cierre.id} value={cierre.id}>
                    {cierre.tipo_periodo.charAt(0).toUpperCase() + cierre.tipo_periodo.slice(1)} - {formatDate(cierre.fecha_inicio)}
                    {cierre.fecha_inicio !== cierre.fecha_fin && <> a {formatDate(cierre.fecha_fin)}</>}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Período 2 (Comparar)
              </label>
              <select
                value={cierre2Id || ''}
                onChange={(e) => setCierre2Id(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Seleccionar...</option>
                {cierres.map((cierre) => (
                  <option key={cierre.id} value={cierre.id}>
                    {cierre.tipo_periodo.charAt(0).toUpperCase() + cierre.tipo_periodo.slice(1)} - {formatDate(cierre.fecha_inicio)}
                    {cierre.fecha_inicio !== cierre.fecha_fin && <> a {formatDate(cierre.fecha_fin)}</>}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Loading/Error */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700">{error}</p>
            </div>
          ) : !cierre1Id || !cierre2Id ? (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
              <svg className="w-12 h-12 text-blue-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-gray-600">Selecciona dos períodos para comparar</p>
            </div>
          ) : comparacion ? (
            <>
              {/* Información de períodos comparados */}
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-xs font-medium text-gray-500 uppercase mb-1">Período Base</p>
                    <p className="font-semibold text-gray-900">
                      {comparacion.cierre1.tipo_periodo.charAt(0).toUpperCase() + comparacion.cierre1.tipo_periodo.slice(1)}
                    </p>
                    <p className="text-gray-600">
                      {formatDate(comparacion.cierre1.fecha_inicio)}
                      {comparacion.cierre1.fecha_inicio !== comparacion.cierre1.fecha_fin && 
                        <> - {formatDate(comparacion.cierre1.fecha_fin)}</>
                      }
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Total: {formatNumber(comparacion.cierre1.total_paginas)} páginas
                    </p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-gray-500 uppercase mb-1">Período Comparado</p>
                    <p className="font-semibold text-gray-900">
                      {comparacion.cierre2.tipo_periodo.charAt(0).toUpperCase() + comparacion.cierre2.tipo_periodo.slice(1)}
                    </p>
                    <p className="text-gray-600">
                      {formatDate(comparacion.cierre2.fecha_inicio)}
                      {comparacion.cierre2.fecha_inicio !== comparacion.cierre2.fecha_fin && 
                        <> - {formatDate(comparacion.cierre2.fecha_fin)}</>
                      }
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Total: {formatNumber(comparacion.cierre2.total_paginas)} páginas
                    </p>
                  </div>
                </div>
              </div>

              {/* Resumen de diferencias */}
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="text-center">
                    <p className="text-xs text-gray-600 mb-1">Total</p>
                    <p className={`text-2xl font-bold ${getDiferenciaColor(comparacion.diferencia_total)}`}>
                      {formatDiferencia(comparacion.diferencia_total)}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600 mb-1">Copiadora</p>
                    <p className={`text-2xl font-bold ${getDiferenciaColor(comparacion.diferencia_copiadora)}`}>
                      {formatDiferencia(comparacion.diferencia_copiadora)}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600 mb-1">Impresora</p>
                    <p className={`text-2xl font-bold ${getDiferenciaColor(comparacion.diferencia_impresora)}`}>
                      {formatDiferencia(comparacion.diferencia_impresora)}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600 mb-1">Escáner</p>
                    <p className={`text-2xl font-bold ${getDiferenciaColor(comparacion.diferencia_escaner)}`}>
                      {formatDiferencia(comparacion.diferencia_escaner)}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600 mb-1">Fax</p>
                    <p className={`text-2xl font-bold ${getDiferenciaColor(comparacion.diferencia_fax)}`}>
                      {formatDiferencia(comparacion.diferencia_fax)}
                    </p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-purple-200 grid grid-cols-3 gap-4 text-center text-sm">
                  <div>
                    <span className="text-gray-600">Días entre cierres:</span>
                    <span className="ml-2 font-semibold text-gray-900">{comparacion.dias_entre_cierres}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Usuarios activos:</span>
                    <span className="ml-2 font-semibold text-gray-900">{comparacion.total_usuarios_activos}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Promedio por usuario:</span>
                    <span className="ml-2 font-semibold text-gray-900">{formatNumber(Math.round(comparacion.promedio_consumo_por_usuario))}</span>
                  </div>
                </div>
              </div>

              {/* Explicación de columnas */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="text-sm text-blue-900">
                    <p className="font-semibold mb-2">Cómo leer la tabla:</p>
                    <ul className="space-y-1 text-blue-800">
                      <li>• <strong>📄 Consumo Período 1/2:</strong> Páginas impresas en cada período con desglose por función</li>
                      <li>• <strong>📈 Diferencia:</strong> Cambio entre períodos (Período 2 - Período 1) con desglose por función</li>
                      <li>• Los valores en verde indican aumento, en rojo disminución</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Todos los usuarios */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    Comparación Detallada por Usuario ({comparacion.top_usuarios_aumento.length + comparacion.top_usuarios_disminucion.length})
                  </h3>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Buscar usuario..."
                    className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                {(() => {
                  // Combinar todos los usuarios
                  const allUsers = [
                    ...comparacion.top_usuarios_aumento,
                    ...comparacion.top_usuarios_disminucion
                  ].filter(u => 
                    u.nombre_usuario.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    u.codigo_usuario.includes(searchTerm)
                  ).sort((a, b) => {
                    let aVal: string | number;
                    let bVal: string | number;
                    
                    switch (sortField) {
                      case 'nombre':
                        aVal = a.nombre_usuario;
                        bVal = b.nombre_usuario;
                        break;
                      case 'codigo':
                        aVal = a.codigo_usuario;
                        bVal = b.codigo_usuario;
                        break;
                      case 'consumo1':
                        aVal = a.consumo_cierre1;
                        bVal = b.consumo_cierre1;
                        break;
                      case 'consumo2':
                        aVal = a.consumo_cierre2;
                        bVal = b.consumo_cierre2;
                        break;
                      case 'diferencia':
                      default:
                        aVal = a.diferencia;
                        bVal = b.diferencia;
                        break;
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

                  return (
                    <div className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="max-h-[500px] overflow-y-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50 sticky top-0">
                            <tr>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase" rowSpan={2}>#</th>
                              <th 
                                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100" 
                                rowSpan={2}
                                onClick={() => handleSort('nombre')}
                              >
                                Usuario {sortField === 'nombre' && <SortIcon active={true} />}
                              </th>
                              <th 
                                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100" 
                                rowSpan={2}
                                onClick={() => handleSort('codigo')}
                              >
                                Código {sortField === 'codigo' && <SortIcon active={true} />}
                              </th>
                              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase border-l border-gray-300" colSpan={5}>
                                📄 Consumo Período 1
                              </th>
                              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase border-l border-gray-300" colSpan={5}>
                                📄 Consumo Período 2
                              </th>
                              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase border-l border-gray-300" colSpan={5}>
                                📈 Diferencia
                              </th>
                            </tr>
                            <tr>
                              <th 
                                className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase border-l border-gray-300 cursor-pointer hover:bg-gray-100"
                                onClick={() => handleSort('consumo1')}
                              >
                                Total {sortField === 'consumo1' && <SortIcon active={true} />}
                              </th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Copia</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Impre</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Escán</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Fax</th>
                              <th 
                                className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase border-l border-gray-300 cursor-pointer hover:bg-gray-100"
                                onClick={() => handleSort('consumo2')}
                              >
                                Total {sortField === 'consumo2' && <SortIcon active={true} />}
                              </th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Copia</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Impre</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Escán</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Fax</th>
                              <th 
                                className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase border-l border-gray-300 cursor-pointer hover:bg-gray-100"
                                onClick={() => handleSort('diferencia')}
                              >
                                Total {sortField === 'diferencia' && <SortIcon active={true} />}
                              </th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Copia</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Impre</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Escán</th>
                              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Fax</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {allUsers.map((usuario, index) => (
                              <UsuarioComparacionRow
                                key={usuario.codigo_usuario}
                                usuario={usuario}
                                index={index}
                                formatNumber={formatNumber}
                                formatDiferencia={formatDiferencia}
                                getDiferenciaColor={getDiferenciaColor}
                              />
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {allUsers.length === 0 && (
                        <div className="text-center py-8 text-gray-500">
                          No se encontraron usuarios
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
            </>
          ) : null}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 border-t border-gray-200 px-6 py-4 flex items-center justify-end gap-3">
          {comparacion && (
            <>
              <button
                onClick={() => {
                  const url = `${API_BASE}/api/export/comparacion/${cierre1Id}/${cierre2Id}/excel-ricoh`;
                  window.open(url, '_blank');
                }}
                className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
                title="Exportar en formato Ricoh (52 columnas, 3 hojas)"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Excel Ricoh
              </button>
              <button
                onClick={() => {
                  const url = `${API_BASE}/api/export/comparacion/${cierre1Id}/${cierre2Id}/excel`;
                  window.open(url, '_blank');
                }}
                className="px-4 py-2 text-white bg-green-600 rounded-md hover:bg-green-700 transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Excel Simple
              </button>
              <button
                onClick={() => {
                  const url = `${API_BASE}/api/export/comparacion/${cierre1Id}/${cierre2Id}`;
                  window.open(url, '_blank');
                }}
                className="px-4 py-2 text-white bg-purple-600 rounded-md hover:bg-purple-700 transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                CSV
              </button>
            </>
          )}
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
