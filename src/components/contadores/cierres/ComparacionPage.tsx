import { useState, useEffect, useMemo } from 'react';
import { CierreMensual, ComparacionCierres } from './types';
import { TablaComparacionSimplificada } from './TablaComparacionSimplificada';
import { Button, Input, Spinner, Alert } from '@/components/ui';
import { ArrowLeft, RefreshCw, Download, FileSpreadsheet, FileText } from 'lucide-react';

const API_BASE = 'http://localhost:8000';
const ROWS_PER_PAGE = 25;

type SortKey = 'nombre' | 'codigo' | 'total1' | 'total2' | 'diferencia' | 'copia' | 'impre' | 'escan' | 'fax';
type SortDir = 'asc' | 'desc';

interface ComparacionPageProps {
  cierres: CierreMensual[];
  onVolver: () => void;
}

const SortIcon = ({ active, dir }: { active: boolean; dir: SortDir }) => (
  <span className={`ml-1 inline-flex flex-col leading-none ${active ? 'text-indigo-600' : 'text-gray-300'}`}>
    <span style={{ fontSize: 8, lineHeight: '9px' }}>{!active || dir === 'asc' ? '▲' : ''}</span>
    <span style={{ fontSize: 8, lineHeight: '9px' }}>{!active || dir === 'desc' ? '▼' : ''}</span>
  </span>
);

export const ComparacionPage: React.FC<ComparacionPageProps> = ({ cierres, onVolver }) => {
  const [cierre1Id, setCierre1Id] = useState<number | null>(null);
  const [cierre2Id, setCierre2Id] = useState<number | null>(null);
  const [comparacion, setComparacion] = useState<ComparacionCierres | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('diferencia');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [page, setPage] = useState(1);

  useEffect(() => {
    // Ordenar cierres por fecha (más antiguo primero)
    const cierresOrdenados = [...cierres].sort((a, b) => 
      new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()
    );
    // Cierre1 = más antiguo (base), Cierre2 = más reciente (comparado)
    if (cierresOrdenados.length >= 2) { 
      setCierre1Id(cierresOrdenados[0].id); 
      setCierre2Id(cierresOrdenados[1].id); 
    }
  }, [cierres]);

  useEffect(() => { if (cierre1Id && cierre2Id) loadComparacion(); }, [cierre1Id, cierre2Id]);
  useEffect(() => { setPage(1); }, [searchTerm, sortKey, sortDir]);

  const loadComparacion = async () => {
    if (!cierre1Id || !cierre2Id) return;
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/counters/monthly/compare/${cierre1Id}/${cierre2Id}`);
      if (!res.ok) throw new Error('Error al comparar cierres');
      const data = await res.json();
      setComparacion(data);
    } catch (err: any) { setError(err.message); }
    finally { setLoading(false); }
  };

  // Detectar capacidades de la impresora y funciones con datos
  const printerCapabilities = useMemo(() => {
    if (!comparacion?.printer) return { 
      has_color: true, 
      has_scanner: true, 
      has_fax: true,
      has_copier: true,
      has_printer: true,
      has_scanner_data: true,
    };
    
    // Detectar si hay datos reales en cada función
    const allUsers = [...comparacion.top_usuarios_aumento, ...comparacion.top_usuarios_disminucion];
    
    // Función helper para verificar si un valor es mayor a 0
    const hasValue = (val: any) => val != null && val > 0;
    
    const hasCopierData = allUsers.some(u => 
      hasValue(u.copiadora_bn_cierre1) || 
      hasValue(u.copiadora_color_cierre1) ||
      hasValue(u.copiadora_bn_cierre2) || 
      hasValue(u.copiadora_color_cierre2)
    );
    
    const hasPrinterData = allUsers.some(u => 
      hasValue(u.impresora_bn_cierre1) || 
      hasValue(u.impresora_color_cierre1) ||
      hasValue(u.impresora_bn_cierre2) || 
      hasValue(u.impresora_color_cierre2)
    );
    
    const hasScannerData = allUsers.some(u => 
      hasValue(u.escaner_bn_cierre1) || 
      hasValue(u.escaner_color_cierre1) ||
      hasValue(u.escaner_bn_cierre2) || 
      hasValue(u.escaner_color_cierre2)
    );
    
    return {
      has_color: comparacion.printer.has_color ?? true,
      has_scanner: comparacion.printer.has_scanner ?? true,
      has_fax: comparacion.printer.has_fax ?? true,
      has_copier: hasCopierData,
      has_printer: hasPrinterData,
      has_scanner_data: hasScannerData,
    };
  }, [comparacion]);

  const fmt = (n: number) => n.toLocaleString('es-ES');
  const fmtDiff = (n: number) => {
    if (n === 0) return '0';
    return `${n >= 0 ? '+' : ''}${fmt(n)}`;
  };
  const diffColor = (n: number) => n > 0 ? 'text-emerald-600 font-semibold' : n < 0 ? 'text-red-500 font-semibold' : 'text-gray-400';
  const fmtDate = (d: string) => {
    const date = new Date(d.includes('T') ? d : `${d}T00:00:00`);
    return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  const handleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortKey(key); setSortDir('desc'); }
  };

  const allUsers = useMemo(() => {
    if (!comparacion) return [];
    const raw = [...comparacion.top_usuarios_aumento, ...comparacion.top_usuarios_disminucion];
    
    const filtered = raw.filter(u =>
      u.nombre_usuario.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.codigo_usuario.includes(searchTerm)
    ).map(u => ({
      ...u,
      difCopia: (u.consumo_copiadora_cierre2 || 0) - (u.consumo_copiadora_cierre1 || 0),
      difImpre: (u.consumo_impresora_cierre2 || 0) - (u.consumo_impresora_cierre1 || 0),
      difEscan: (u.consumo_escaner_cierre2 || 0) - (u.consumo_escaner_cierre1 || 0),
      difFax:   (u.consumo_fax_cierre2 || 0) - (u.consumo_fax_cierre1 || 0),
      // Diferencias B/N y Color - pueden ser negativas si hay correcciones
      difCopiaBN: (u.copiadora_bn_cierre2 || 0) - (u.copiadora_bn_cierre1 || 0),
      difCopiaColor: (u.copiadora_color_cierre2 || 0) - (u.copiadora_color_cierre1 || 0),
      difImpreBN: (u.impresora_bn_cierre2 || 0) - (u.impresora_bn_cierre1 || 0),
      difImpreColor: (u.impresora_color_cierre2 || 0) - (u.impresora_color_cierre1 || 0),
      difEscanBN: (u.escaner_bn_cierre2 || 0) - (u.escaner_bn_cierre1 || 0),
      difEscanColor: (u.escaner_color_cierre2 || 0) - (u.escaner_color_cierre1 || 0),
    }));

    const mul = sortDir === 'asc' ? 1 : -1;
    filtered.sort((a, b) => {
      switch (sortKey) {
        case 'nombre': return mul * a.nombre_usuario.localeCompare(b.nombre_usuario);
        case 'codigo': return mul * a.codigo_usuario.localeCompare(b.codigo_usuario);
        case 'total1': return mul * ((a.consumo_cierre1 || 0) - (b.consumo_cierre1 || 0));
        case 'total2': return mul * ((a.consumo_cierre2 || 0) - (b.consumo_cierre2 || 0));
        case 'diferencia': return mul * (a.diferencia - b.diferencia);
        case 'copia': return mul * (a.difCopia - b.difCopia);
        case 'impre': return mul * (a.difImpre - b.difImpre);
        case 'escan': return mul * (a.difEscan - b.difEscan);
        case 'fax':   return mul * (a.difFax - b.difFax);
        default: return 0;
      }
    });
    return filtered;
  }, [comparacion, searchTerm, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(allUsers.length / ROWS_PER_PAGE));
  const pageUsers = allUsers.slice((page - 1) * ROWS_PER_PAGE, page * ROWS_PER_PAGE);

  const SortTh = ({ label, sKey, align = 'right', className = '', rowSpan = 1 }: { label: string; sKey: SortKey; align?: string; className?: string; rowSpan?: number }) => (
    <th
      rowSpan={rowSpan}
      className={`px-3 py-2 text-${align} text-gray-600 font-medium cursor-pointer select-none hover:bg-gray-200/50 whitespace-nowrap transition-colors ${className}`}
      onClick={() => handleSort(sKey)}
    >
      {label}<SortIcon active={sortKey === sKey} dir={sortDir} />
    </th>
  );

  return (
    <div className="flex flex-col h-full bg-[#F8FAFC]">

      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={onVolver}
          icon={<ArrowLeft size={16} />}
        >
          Volver a Cierres
        </Button>
        <div className="h-5 w-px bg-gray-300" />
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
          </div>
          <div>
            <h1 className="text-base font-bold text-gray-900">Comparación de Cierres</h1>
            <p className="text-xs text-gray-500">Diferencias entre dos períodos</p>
          </div>
        </div>
      </div>

      {/* Selectores */}
      <div className="bg-white border-b border-gray-100 px-6 py-4">
        <div className="max-w-5xl mx-auto">
          {/* Información de la impresora */}
          {comparacion?.printer && (
            <div className="mb-4 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg shadow-sm">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                  </svg>
                </div>
                <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-2">
                  <div>
                    <span className="text-xs font-medium text-blue-700">Hostname:</span>
                    <p className="text-sm font-semibold text-blue-900">{comparacion.printer.hostname}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-blue-700">IP:</span>
                    <p className="text-sm font-semibold text-blue-900">{comparacion.printer.ip_address}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-blue-700">Ubicación:</span>
                    <p className="text-sm font-semibold text-blue-900">{comparacion.printer.location || 'N/A'}</p>
                  </div>
                  {comparacion.printer.serial_number && (
                    <div>
                      <span className="text-xs font-medium text-blue-700">Serial:</span>
                      <p className="text-sm font-semibold text-blue-900">{comparacion.printer.serial_number}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-700 mb-2">Período Base (Inicial - Más Antiguo)</label>
              <select value={cierre1Id || ''} onChange={e => setCierre1Id(Number(e.target.value))}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white shadow-sm hover:border-gray-400 transition-colors">
                <option value="">Seleccionar período...</option>
                {[...cierres].sort((a, b) => new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()).map(c => <option key={c.id} value={c.id}>{fmtDate(c.fecha_inicio)}{c.fecha_inicio !== c.fecha_fin && ` → ${fmtDate(c.fecha_fin)}`}</option>)}
              </select>
            </div>
            
            <div className="flex items-center justify-center pt-6">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </div>
            </div>
            
            <div className="flex-1">
              <label className="block text-xs font-medium text-gray-700 mb-2">Período a Comparar (Final - Más Reciente)</label>
              <select value={cierre2Id || ''} onChange={e => setCierre2Id(Number(e.target.value))}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white shadow-sm hover:border-gray-400 transition-colors">
                <option value="">Seleccionar período...</option>
                {[...cierres].sort((a, b) => new Date(a.fecha_inicio).getTime() - new Date(b.fecha_inicio).getTime()).map(c => <option key={c.id} value={c.id}>{fmtDate(c.fecha_inicio)}{c.fecha_inicio !== c.fecha_fin && ` → ${fmtDate(c.fecha_fin)}`}</option>)}
              </select>
            </div>
            
            <Button
              size="sm"
              onClick={loadComparacion}
              loading={loading}
              disabled={!cierre1Id || !cierre2Id}
              icon={<RefreshCw size={16} />}
              className="mt-6"
            >
              Comparar
            </Button>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        {error ? (
          <div className="p-6">
            <Alert variant="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </div>
        ) : !comparacion ? (
          <div className="flex items-center justify-center h-64 text-gray-400 text-sm">Selecciona dos períodos para ver la comparación</div>
        ) : (
          <>
            {/* Tarjetas de resumen */}
            <div className="p-6 pb-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Total páginas', val: comparacion.diferencia_total, icon: '📄', show: true },
                  { label: 'Copiadora', val: comparacion.diferencia_copiadora, icon: '📋', show: printerCapabilities.has_copier },
                  { label: 'Impresora', val: comparacion.diferencia_impresora, icon: '🖨️', show: printerCapabilities.has_printer },
                  { label: 'Escáner', val: comparacion.diferencia_escaner, icon: '📷', show: printerCapabilities.has_scanner_data },
                ].filter(item => item.show).map(({ label, val, icon }) => (
                  <div key={label} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs font-medium text-gray-600">{label}</p>
                      <span className="text-lg">{icon}</span>
                    </div>
                    <p className={`text-2xl font-bold ${diffColor(val)}`}>{fmtDiff(val)}</p>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { label: 'Días entre cierres', val: `${comparacion.dias_entre_cierres}`, icon: '📅', color: 'text-gray-900' },
                  { label: 'Usuarios activos', val: `${comparacion.total_usuarios_activos}`, icon: '👥', color: 'text-indigo-600' },
                  { label: 'Promedio por usuario', val: fmt(Math.round(comparacion.promedio_consumo_por_usuario)), icon: '📊', color: 'text-emerald-600' },
                ].map(({ label, val, icon, color }) => (
                  <div key={label} className="bg-gradient-to-br from-white to-gray-50 rounded-xl border border-gray-200 p-5 shadow-sm">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center text-xl">
                        {icon}
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 mb-0.5">{label}</p>
                        <p className={`text-xl font-bold ${color}`}>{val}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tabla */}
            <div className="px-6 pb-6">
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm">

                {/* Encabezado de tabla */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-indigo-100 flex items-center justify-center">
                      <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900">Desglose por usuario</h3>
                      <p className="text-xs text-gray-500">{allUsers.length} usuarios encontrados</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Buscar usuario o código..."
                      className="w-64"
                    />
                  </div>
                </div>

                {/* Tabla scrollable - Desktop */}
                <div className="hidden md:block">
                  <TablaComparacionSimplificada 
                    usuarios={pageUsers}
                    onSort={handleSort}
                    sortKey={sortKey}
                    sortDir={sortDir}
                    hasColor={printerCapabilities.has_color}
                    hasCopier={printerCapabilities.has_copier}
                    hasPrinter={printerCapabilities.has_printer}
                    hasScanner={printerCapabilities.has_scanner_data}
                  />
                </div>

                {/* Vista Móvil - Tarjetas */}
                <div className="md:hidden p-4 space-y-4">
                  {pageUsers.map((u) => (
                    <div key={u.codigo_usuario} className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-semibold text-sm text-gray-900">{u.nombre_usuario}</h3>
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700 mt-1">
                            {u.codigo_usuario}
                          </span>
                        </div>
                        <div className={`text-right`}>
                          <p className="text-xs text-gray-500">Diferencia</p>
                          <p className={`text-lg font-bold ${diffColor(u.diferencia)}`}>{fmtDiff(u.diferencia)}</p>
                        </div>
                      </div>
                      
                      <div className="space-y-2 text-xs">
                        <div className="flex justify-between py-1 border-b border-gray-100">
                          <span className="text-gray-600">Total Base:</span>
                          <span className="font-medium">{fmt(u.consumo_cierre1)}</span>
                        </div>
                        <div className="flex justify-between py-1 border-b border-gray-100">
                          <span className="text-gray-600">Total Comparado:</span>
                          <span className="font-medium">{fmt(u.consumo_cierre2)}</span>
                        </div>
                        
                        <div className="pt-2">
                          <p className="text-gray-500 font-medium mb-1">Consumo por función:</p>
                          <div className="grid grid-cols-2 gap-2">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Copiadora:</span>
                              <span className={diffColor(u.difCopia)}>{fmtDiff(u.difCopia)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Impresora:</span>
                              <span className={diffColor(u.difImpre)}>{fmtDiff(u.difImpre)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Escáner:</span>
                              <span className={diffColor(u.difEscan)}>{fmtDiff(u.difEscan)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {pageUsers.length === 0 && (
                    <div className="text-center py-12">
                      <div className="flex flex-col items-center gap-3">
                        <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
                          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                          </svg>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">No se encontraron usuarios</p>
                          <p className="text-xs text-gray-500 mt-1">Intenta con otro término de búsqueda</p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer: info + paginación */}
                <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <p className="text-xs text-gray-400">
                      Mostrando {allUsers.length === 0 ? 0 : (page - 1) * ROWS_PER_PAGE + 1}–{Math.min(page * ROWS_PER_PAGE, allUsers.length)} de {allUsers.length} usuarios
                    </p>
                    <div className="h-4 w-px bg-gray-300"></div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-gray-500">Leyenda:</span>
                      <span className="text-gray-600">Los primeros 2 bloques muestran <strong>totales acumulados</strong></span>
                      <div className="h-4 w-px bg-gray-300"></div>
                      <span className="text-gray-600">El último bloque muestra el <strong>consumo del período</strong></span>
                      <div className="h-4 w-px bg-gray-300"></div>
                      <span className="text-emerald-600 font-semibold">Verde = aumento</span>
                      <span className="text-red-500 font-semibold">Rojo = disminución</span>
                    </div>
                    {comparacion && (
                      <div className="flex items-center gap-2 ml-2">
                        <div className="h-4 w-px bg-gray-300"></div>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            const url = `${API_BASE}/api/export/comparacion/${cierre1Id}/${cierre2Id}/excel-ricoh`;
                            window.open(url, '_blank');
                          }}
                          icon={<FileSpreadsheet size={14} />}
                          className="bg-blue-600 hover:bg-blue-700"
                          title="Exportar en formato Ricoh (52 columnas, 3 hojas)"
                        >
                          Excel Ricoh
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            const url = `${API_BASE}/api/export/comparacion/${cierre1Id}/${cierre2Id}/excel`;
                            window.open(url, '_blank');
                          }}
                          icon={<Download size={14} />}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          Excel Simple
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            const url = `${API_BASE}/api/export/comparacion/${cierre1Id}/${cierre2Id}`;
                            window.open(url, '_blank');
                          }}
                          icon={<FileText size={14} />}
                          className="bg-indigo-600 hover:bg-indigo-700"
                        >
                          CSV
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* Controles paginación */}
                  {totalPages > 1 && (
                    <div className="flex items-center gap-1">
                      <button onClick={() => setPage(1)} disabled={page === 1}
                        className="px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed">«</button>
                      <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                        className="px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed">‹ Ant.</button>

                      {/* Páginas numéricas */}
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        const startPage = Math.max(1, Math.min(page - 2, totalPages - 4));
                        const p = startPage + i;
                        return (
                          <button key={p} onClick={() => setPage(p)}
                            className={`w-7 h-7 text-xs rounded border transition-colors ${page === p ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 hover:bg-gray-50'}`}>
                            {p}
                          </button>
                        );
                      })}

                      <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                        className="px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed">Sig. ›</button>
                      <button onClick={() => setPage(totalPages)} disabled={page === totalPages}
                        className="px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed">»</button>

                      <span className="text-xs text-gray-400 ml-2">Pág. {page} de {totalPages}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
