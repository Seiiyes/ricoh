import React, { useMemo, useState } from 'react';
import { 
  Download, 
  Calendar, 
  ChevronDown, 
  FileText, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Layers,
  Loader2,
  Search,
  Edit2,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts';
import { KPICard } from '../components/analytics/KPICard';
import { ChartCard } from '../components/analytics/ChartCard';
import { chartColors } from '../utils/chartColors';
import { exportReportToPDF, exportTableToExcel } from '../utils/exportUtils';
import apiClient from '../services/apiClient';
import { cn } from '../lib/utils';
import { 
  useEvolucionConsumo, 
  useComparativa, 
  useGlobalUserConsumption, 
  useUpdateUserConsumption, 
  useTopUsers,
  GlobalCierreUsuario 
} from '../hooks/useAnalyticsData';

const AnalyticsPage = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'users'>('overview');

  // Default date ranges for demonstration
  const [dateRangeA] = useState({ start: '2026-01-01', end: '2026-03-31' });
  const [dateRangeB] = useState({ start: '2025-10-01', end: '2025-12-31' });

  // Tab 1: Overview hooks
  const { data: evolucionConsumo, isLoading: evoLoading } = useEvolucionConsumo(12);
  const { data: comparativa, isLoading: compLoading } = useComparativa(
    dateRangeA.start, 
    dateRangeA.end, 
    dateRangeB.start, 
    dateRangeB.end
  );

  const { data: topUsers, isLoading: topUsersLoading } = useTopUsers({
    fechaInicio: dateRangeA.start,
    fechaFin: dateRangeA.end,
    limit: 5
  });

  const pieData = useMemo(() => {
    if (!comparativa) return [];
    const copias = comparativa.find((r: any) => r.indicador === 'Páginas Copiadas')?.periodoA || 0;
    const impresiones = comparativa.find((r: any) => r.indicador === 'Páginas Impresas')?.periodoA || 0;
    const escaner = comparativa.find((r: any) => r.indicador === 'Páginas Escaneadas')?.periodoA || 0;
    const fax = comparativa.find((r: any) => r.indicador === 'Páginas de Fax')?.periodoA || 0;
    
    const list = [];
    if (impresiones > 0) list.push({ name: 'Impresión', value: impresiones });
    if (copias > 0) list.push({ name: 'Copiado', value: copias });
    if (escaner > 0) list.push({ name: 'Escáner', value: escaner });
    if (fax > 0) list.push({ name: 'Fax', value: fax });
    
    if (list.length === 0) {
      return [
        { name: 'Impresión', value: 0 },
        { name: 'Copiado', value: 0 },
        { name: 'Escáner', value: 0 },
        { name: 'Fax', value: 0 }
      ];
    }
    return list;
  }, [comparativa]);

  // Tab 2: User Consumption hooks and states
  const [userPage, setUserPage] = useState(1);
  const [userSearch, setUserSearch] = useState('');
  const [filterFechaInicio, setFilterFechaInicio] = useState('');
  const [filterFechaFin, setFilterFechaFin] = useState('');
  const [filterCentroCostos, setFilterCentroCostos] = useState('');
  const [editingRecord, setEditingRecord] = useState<GlobalCierreUsuario | null>(null);
  const [editTotal, setEditTotal] = useState<number>(0);
  const [editConsumo, setEditConsumo] = useState<number>(0);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [saveErrorMsg, setSaveErrorMsg] = useState<string | null>(null);
  const [isExportingUsers, setIsExportingUsers] = useState(false);
  const [exportUsersErrorMsg, setExportUsersErrorMsg] = useState<string | null>(null);

  const { data: globalUserConsumptionData, isLoading: userLoading } = useGlobalUserConsumption({
    page: userPage,
    pageSize: 15,
    search: userSearch || undefined,
    fechaInicio: filterFechaInicio || undefined,
    fechaFin: filterFechaFin || undefined,
    centroCostos: filterCentroCostos || undefined
  });
  const globalUserConsumption = globalUserConsumptionData as any;

  const updateMutation = useUpdateUserConsumption();

  const groupedCierres = useMemo(() => {
    const items = globalUserConsumption?.items || [];
    const map = new Map<number, {
      cierre_mensual_id: number;
      printer_id: number;
      printer_hostname: string;
      printer_ip: string;
      printer_location: string;
      fecha_inicio: string;
      fecha_fin: string;
      fecha_cierre: string;
      cerrado_por?: string;
      users: GlobalCierreUsuario[];
      total_consumo: number;
    }>();

    for (const r of items) {
      if (!map.has(r.cierre_mensual_id)) {
        map.set(r.cierre_mensual_id, {
          cierre_mensual_id: r.cierre_mensual_id,
          printer_id: r.printer_id,
          printer_hostname: r.printer_hostname,
          printer_ip: r.printer_ip,
          printer_location: r.printer_location,
          fecha_inicio: r.fecha_inicio,
          fecha_fin: r.fecha_fin,
          fecha_cierre: r.fecha_cierre,
          cerrado_por: r.cerrado_por,
          users: [],
          total_consumo: 0,
        });
      }
      const g = map.get(r.cierre_mensual_id)!;
      g.users.push(r);
      g.total_consumo += r.consumo_total || 0;
    }

    return Array.from(map.values()).sort(
      (a, b) => new Date(b.fecha_cierre).getTime() - new Date(a.fecha_cierre).getTime()
    );
  }, [globalUserConsumption?.items]);

  const [expandedCierres, setExpandedCierres] = useState<Record<number, boolean>>({});
  const toggleCierre = (cierreId: number) => {
    setExpandedCierres(prev => ({ ...prev, [cierreId]: !prev[cierreId] }));
  };

  const [expandedUserRows, setExpandedUserRows] = useState<Record<number, boolean>>({});
  const toggleUserRow = (recordId: number) => {
    setExpandedUserRows(prev => ({ ...prev, [recordId]: !prev[recordId] }));
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserSearch(e.target.value);
    setUserPage(1);
  };

  const handleOpenEdit = (record: GlobalCierreUsuario) => {
    setEditingRecord(record);
    setEditTotal(record.total_paginas);
    setEditConsumo(record.consumo_total);
    setSaveSuccessMsg(null);
    setSaveErrorMsg(null);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingRecord) return;

    try {
      await updateMutation.mutateAsync({
        id: editingRecord.id,
        total_paginas: editTotal,
        consumo_total: editConsumo,
      });
      setSaveSuccessMsg('Consumo de usuario actualizado correctamente.');
      setTimeout(() => {
        setEditingRecord(null);
        setSaveSuccessMsg(null);
      }, 1500);
    } catch (err: any) {
      setSaveErrorMsg(err.response?.data?.detail || 'Error al actualizar el consumo.');
    }
  };

  const handleExportPDF = () => {
    if (!comparativa) return;
    const columns = [
      { header: 'Indicador', dataKey: 'indicador' },
      { header: 'Período A', dataKey: 'periodoA' },
      { header: 'Período B', dataKey: 'periodoB' },
      { header: 'Variación (%)', dataKey: 'variacion' }
    ];
    exportReportToPDF('Reporte Analítico - Ricoh Equipment Manager', comparativa, columns, 'reporte_ricoh_analytics');
  };

  const handleExportExcel = () => {
    if (!comparativa) return;
    exportTableToExcel(comparativa, 'comparativa_ricoh_analytics');
  };

  const handleExportUsersExcel = async () => {
    setExportUsersErrorMsg(null);

    // Exportar TODOS los registros del filtro actual (no solo la página visible).
    const pageSize = 500;
    const baseParams = new URLSearchParams();
    baseParams.append('page_size', pageSize.toString());
    if (userSearch) baseParams.append('search', userSearch);

    const fetchPage = async (page: number) => {
      const params = new URLSearchParams(baseParams);
      params.set('page', page.toString());
      const { data } = await apiClient.get(`/api/counters/monthly/users/all?${params.toString()}`);
      return data as { items: GlobalCierreUsuario[]; pages: number };
    };

    try {
      setIsExportingUsers(true);
      const first = await fetchPage(1);
      let allItems: GlobalCierreUsuario[] = [...(first.items || [])];

      for (let p = 2; p <= (first.pages || 1); p++) {
        const next = await fetchPage(p);
        allItems = allItems.concat(next.items || []);
      }

      if (allItems.length === 0) return;

      const cleanDataForExport = allItems.map(item => ({
        'Usuario': item.nombre_usuario,
        'Código Usuario': item.codigo_usuario,
        'Impresora Hostname': item.printer_hostname,
        'Impresora IP': item.printer_ip,
        'Ubicación': item.printer_location,
        'Consumo del Período (págs)': item.consumo_total,
        'Total Acumulado (págs)': item.total_paginas,
        'Fecha Cierre': new Date(item.fecha_cierre).toLocaleDateString(),
        'Periodo': `${item.fecha_inicio} a ${item.fecha_fin}`,
        'Cerrado Por': item.cerrado_por || 'Sistema'
      }));

      exportTableToExcel(cleanDataForExport, `consumo_usuarios_cierre_${new Date().toISOString().slice(0, 10)}`);
    } catch (err: any) {
      console.error('Error al exportar consumo de usuarios:', err);
      setExportUsersErrorMsg(err?.response?.data?.detail || 'No se pudo exportar el Excel.');
    } finally {
      setIsExportingUsers(false);
    }
  };

  if (activeTab === 'overview' && (evoLoading || compLoading)) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-10 w-10 animate-spin text-ricoh-red mx-auto mb-4" />
          <p className="font-bold text-slate-500 uppercase tracking-widest text-sm">Analizando Datos...</p>
        </div>
      </div>
    );
  }

  // KPIs
  // Nota: la comparativa actual retorna 1 fila; evitar depender del texto del indicador
  // (puede venir con problemas de encoding según configuración de DB).
  const kpiTotalPaginas = comparativa?.[0]?.periodoA || 0;
  const kpiVariacion = comparativa?.[0]?.variacion || 0;

  return (
    <div className="flex flex-col h-full animate-fade-in custom-scrollbar overflow-y-auto pb-10">
      {/* Title Header */}
      <div className="mb-responsive flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-responsive-xl font-black text-slate-800 tracking-tight">Reportes & Analytics</h1>
          <p className="text-responsive-sm font-bold text-slate-500 uppercase tracking-widest mt-1">Business Intelligence</p>
        </div>
        {activeTab === 'overview' && (
          <button 
            onClick={handleExportPDF}
            className="bg-ricoh-red text-white btn-padding-sm rounded-xl font-bold shadow-lg shadow-red-500/20 hover:bg-red-700 transition-all flex items-center gap-2 text-responsive-sm"
          >
            <Download size={16} />
            <span className="hidden sm:inline">Exportar PDF</span>
            <span className="sm:hidden">PDF</span>
          </button>
        )}
      </div>

      {/* Tabs Selector */}
      <div className="flex border-b border-slate-200 mb-responsive gap-6">
        <button
          onClick={() => setActiveTab('overview')}
          className={cn(
            "pb-3 font-bold text-sm uppercase tracking-wider border-b-2 transition-all",
            activeTab === 'overview'
              ? "border-ricoh-red text-slate-800"
              : "border-transparent text-slate-400 hover:text-slate-600"
          )}
        >
          Resumen General
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={cn(
            "pb-3 font-bold text-sm uppercase tracking-wider border-b-2 transition-all",
            activeTab === 'users'
              ? "border-ricoh-red text-slate-800"
              : "border-transparent text-slate-400 hover:text-slate-600"
          )}
        >
          Consumo de Usuarios
        </button>
      </div>

      {/* Overview Tab Content */}
      {activeTab === 'overview' && (
        <>
          {/* Dynamic Date Filters */}
          <div className="flex flex-wrap gap-responsive-sm mb-responsive">
            <FilterPill icon={<FileText size={14} />} label="Empresa: Ricoh Global" />
            <FilterPill icon={<Calendar size={14} />} label="01 Ene 2026 - 31 Mar 2026" />
            <FilterPill label="Agrupar por: Mensual" />
            <FilterPill label="Comparar: Período Anterior" />
          </div>

          {/* KPIs Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-responsive mb-responsive">
            <KPICard 
              title="Total Páginas" 
              value={kpiTotalPaginas.toLocaleString()} 
              icon={<Layers size={20} />} 
              color={chartColors.primary} 
            />
            <KPICard 
              title="Promedio / Mes" 
              value={(kpiTotalPaginas / 3).toLocaleString(undefined, { maximumFractionDigits: 0 })} 
              icon={<TrendingUp size={20} />} 
              color={chartColors.info} 
            />
            <KPICard 
              title="Costo Estimado" 
              value={`$${(kpiTotalPaginas * 0.05).toLocaleString(undefined, { maximumFractionDigits: 2 })}`} 
              icon={<DollarSign size={20} />} 
              color={chartColors.warning} 
            />
            <KPICard 
              title="Variación vs Anterior" 
              value={""} 
              trend={kpiVariacion}
              trendLabel="vs Trimestre Anterior"
              icon={<TrendingUp size={20} />} 
              color={chartColors.success} 
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-responsive mb-responsive">
            {/* Line Chart */}
            <div className="lg:col-span-2 h-[350px] lg:h-[400px]">
              <ChartCard title="Evolución de Consumo" onExport={() => {}}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={evolucionConsumo} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      formatter={(value: any) => value?.toLocaleString() || ''}
                    />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Line 
                      type="monotone" 
                      dataKey="paginas" 
                      name="Páginas Impresas"
                      stroke={chartColors.primary} 
                      strokeWidth={3} 
                      dot={{ r: 4, strokeWidth: 2 }} 
                      activeDot={{ r: 6, strokeWidth: 0 }} 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Pie Chart */}
            <div className="lg:col-span-1 h-[350px] lg:h-[400px]">
              <ChartCard title="Distribución por Función" onExport={() => {}}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={80}
                      outerRadius={110}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {pieData.map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={chartColors.categorical[index % chartColors.categorical.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value: any) => value?.toLocaleString() || ''}
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend iconType="circle" layout="horizontal" verticalAlign="bottom" wrapperStyle={{ fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-responsive mb-responsive">
            {/* Comparative Table */}
            <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-100 card-padding-sm flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-bold text-slate-800">Comparativa Detallada</h3>
                <button 
                  onClick={handleExportExcel}
                  className="text-xs font-bold text-slate-500 hover:text-ricoh-red uppercase tracking-widest transition-colors flex items-center gap-1"
                >
                  <Download size={14} /> Excel
                </button>
              </div>
              
              <div className="overflow-x-auto rounded-lg border border-slate-100">
                <table className="w-full text-sm text-left">
                  <thead className="bg-slate-50 text-[10px] uppercase font-black tracking-widest text-slate-500">
                    <tr>
                      <th className="px-4 py-3">Indicador</th>
                      <th className="px-4 py-3 text-right">Período Actual</th>
                      <th className="px-4 py-3 text-right">Período Anterior</th>
                      <th className="px-4 py-3 text-right">Variación</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {comparativa?.map((row: any, index: number) => {
                      const isPositive = row.variacion > 0;
                      const isNegative = row.variacion < 0;
                      return (
                        <tr key={index} className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-4 py-3 font-bold text-slate-700">{row.indicador}</td>
                          <td className="px-4 py-3 text-right text-slate-600">{row.periodoA.toLocaleString()}</td>
                          <td className="px-4 py-3 text-right text-slate-600">{row.periodoB.toLocaleString()}</td>
                          <td className="px-4 py-3 text-right">
                            <span className={cn(
                              "inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold",
                              isPositive ? "bg-green-100 text-green-700" : 
                              isNegative ? "bg-red-100 text-red-700" : 
                              "bg-slate-100 text-slate-600"
                            )}>
                              {isPositive ? <TrendingUp size={12} /> : isNegative ? <TrendingDown size={12} /> : null}
                              {isPositive ? '+' : ''}{row.variacion}%
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Top 5 Consumers */}
            <div className="lg:col-span-1 bg-white rounded-xl shadow-sm border border-slate-100 card-padding-sm flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-sm font-bold text-slate-800">Top 5 Consumidores</h3>
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Rango Activo</span>
                </div>

                {topUsersLoading ? (
                  <div className="flex flex-1 items-center justify-center py-10">
                    <Loader2 className="h-6 w-6 animate-spin text-ricoh-red" />
                  </div>
                ) : !topUsers || topUsers.length === 0 ? (
                  <div className="flex flex-1 items-center justify-center py-10 text-center">
                    <p className="text-xs text-slate-400 font-bold">No hay consumos registrados en este período.</p>
                  </div>
                ) : (
                  <div className="flex flex-col gap-4">
                    {topUsers.map((user, idx) => {
                      const maxVal = topUsers[0]?.total_consumo_paginas || 1;
                      const percentage = Math.round((user.total_consumo_paginas / maxVal) * 100);
                      return (
                        <div key={user.user_id} className="flex flex-col gap-1">
                          <div className="flex justify-between items-center text-xs">
                            <span className="font-bold text-slate-700 truncate max-w-[150px]">
                              {idx + 1}. {user.nombre}
                            </span>
                            <span className="font-black text-slate-600 shrink-0">
                              {user.total_consumo_paginas.toLocaleString()} págs
                            </span>
                          </div>
                          
                          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-red-500 to-ricoh-red rounded-full transition-all duration-500" 
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          
                          <div className="flex justify-between items-center text-[8px] text-slate-400 font-semibold uppercase tracking-wider">
                            <span>{user.centro_costos || 'Sin Centro de Costos'}</span>
                            <span>{user.cierres_count} {user.cierres_count === 1 ? 'cierre' : 'cierres'}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {/* User Consumption Tab Content */}
      {activeTab === 'users' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 flex flex-col gap-6">
          {/* Controls Bar */}
          <div className="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Buscar por usuario, código, IP o ubicación..."
                value={userSearch}
                onChange={handleSearchChange}
                className="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red transition-all"
              />
            </div>
            
            <button
              onClick={() => void handleExportUsersExcel()}
              disabled={isExportingUsers || !globalUserConsumption?.items || globalUserConsumption.items.length === 0}
              className="bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed font-bold text-xs uppercase tracking-widest px-4 py-2.5 rounded-xl transition-all flex items-center justify-center gap-2"
            >
              {isExportingUsers ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download size={14} />}
              Exportar Excel
            </button>
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Fecha Inicio</label>
              <input
                type="date"
                value={filterFechaInicio}
                onChange={(e) => { setFilterFechaInicio(e.target.value); setUserPage(1); }}
                className="w-full px-4 py-2 text-sm bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red font-semibold text-slate-700 transition-all shadow-sm"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Fecha Fin</label>
              <input
                type="date"
                value={filterFechaFin}
                onChange={(e) => { setFilterFechaFin(e.target.value); setUserPage(1); }}
                className="w-full px-4 py-2 text-sm bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red font-semibold text-slate-700 transition-all shadow-sm"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Centro de Costos</label>
              <input
                type="text"
                placeholder="Ej: Contabilidad, Ventas..."
                value={filterCentroCostos}
                onChange={(e) => { setFilterCentroCostos(e.target.value); setUserPage(1); }}
                className="w-full px-4 py-2 text-sm bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red font-semibold text-slate-700 transition-all shadow-sm"
              />
            </div>
          </div>

          {exportUsersErrorMsg && (
            <div className="text-xs font-bold text-red-600 bg-red-50 border border-red-100 rounded-xl p-3">
              {exportUsersErrorMsg}
            </div>
          )}

          {/* Grouped content (por cierre) */}
          {userLoading && (!globalUserConsumption?.items || globalUserConsumption.items.length === 0) ? (
            <div className="flex justify-center items-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-ricoh-red" />
            </div>
          ) : !globalUserConsumption?.items || globalUserConsumption.items.length === 0 ? (
            <div className="text-center py-20 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
              <p className="text-slate-400 font-bold text-sm">No se encontraron registros de consumo de usuario.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {groupedCierres.map((g) => {
                const expanded = expandedCierres[g.cierre_mensual_id] ?? true;
                return (
                  <div key={g.cierre_mensual_id} className="rounded-xl border border-slate-100 overflow-hidden">
                    <button
                      type="button"
                      onClick={() => toggleCierre(g.cierre_mensual_id)}
                      className="w-full bg-slate-50 px-5 py-4 flex items-start sm:items-center justify-between gap-4 text-left hover:bg-slate-100 transition-colors"
                    >
                      <div className="min-w-0">
                        <div className="font-black text-slate-800 truncate">
                          {g.printer_hostname} <span className="text-slate-400 font-bold">·</span>{' '}
                          <span className="text-slate-600 font-bold">{g.printer_ip}</span>
                        </div>
                        <div className="text-xs text-slate-500 font-semibold truncate">
                          {g.printer_location || 'Ubicación no definida'} · Período {g.fecha_inicio} al {g.fecha_fin}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-1">
                          Cierre: {new Date(g.fecha_cierre).toLocaleDateString()} · Usuarios: {g.users.length} · Consumo total:{' '}
                          <span className="font-bold text-slate-600">{g.total_consumo.toLocaleString()} págs</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-500 hidden sm:inline">
                          {expanded ? 'Ocultar' : 'Ver'} usuarios
                        </span>
                        <ChevronDown
                          size={18}
                          className={cn('text-slate-400 transition-transform', expanded ? 'rotate-180' : 'rotate-0')}
                        />
                      </div>
                    </button>

                    {expanded && (
                      <div className="overflow-x-auto bg-white">
                        <table className="w-full text-sm text-left">
                          <thead className="bg-white text-[10px] uppercase font-black tracking-widest text-slate-500 border-t border-slate-100">
                            <tr>
                              <th className="px-5 py-4">Usuario</th>
                              <th className="px-5 py-4 text-center">Consumo</th>
                              <th className="px-5 py-4 text-center">Total</th>
                              <th className="px-5 py-4 text-center hidden md:table-cell">B/N</th>
                              <th className="px-5 py-4 text-center hidden md:table-cell">Color</th>
                              <th className="px-5 py-4 text-right">Acciones</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {g.users.map((record) => (
                              <React.Fragment key={record.id}>
                                <tr 
                                  onClick={() => toggleUserRow(record.id)}
                                  className="hover:bg-slate-50/30 transition-colors cursor-pointer"
                                >
                                  <td className="px-5 py-4">
                                    <div className="flex items-center gap-2">
                                      <ChevronDown 
                                        size={16} 
                                        className={cn("text-slate-400 transition-transform shrink-0", expandedUserRows[record.id] ? "rotate-180" : "rotate-0")} 
                                      />
                                      <div>
                                        <div className="font-bold text-slate-800">{record.nombre_usuario}</div>
                                        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{record.codigo_usuario}</div>
                                      </div>
                                    </div>
                                  </td>
                                  <td className="px-5 py-4 text-center">
                                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700">
                                      {record.consumo_total.toLocaleString()} págs
                                    </span>
                                  </td>
                                  <td className="px-5 py-4 text-center font-semibold text-slate-600">
                                    {record.total_paginas.toLocaleString()} págs
                                  </td>
                                  <td className="px-5 py-4 text-center hidden md:table-cell text-slate-600 font-semibold">
                                    {record.total_bn.toLocaleString()}
                                  </td>
                                  <td className="px-5 py-4 text-center hidden md:table-cell text-slate-600 font-semibold">
                                    {record.total_color.toLocaleString()}
                                  </td>
                                  <td className="px-5 py-4 text-right" onClick={(e) => e.stopPropagation()}>
                                    <button
                                      onClick={() => handleOpenEdit(record)}
                                      className="p-2 text-slate-400 hover:text-ricoh-red hover:bg-slate-50 rounded-lg transition-all"
                                      title="Editar consumo"
                                    >
                                      <Edit2 size={16} />
                                    </button>
                                  </td>
                                </tr>
                                {expandedUserRows[record.id] && (
                                  <tr className="bg-slate-50/40">
                                    <td colSpan={6} className="px-5 py-4 border-t border-slate-100">
                                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-white/70 backdrop-blur-md rounded-2xl border border-slate-100 shadow-sm animate-scale-in">
                                        
                                        {/* Copiadora */}
                                        <div className="flex flex-col gap-1 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                                          <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Copiadora</div>
                                          <div className="text-sm font-black text-slate-700">{(record.consumo_copiadora || 0).toLocaleString()} págs</div>
                                          <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider flex justify-between mt-1">
                                            <span>B/N: {(record.copiadora_bn || 0).toLocaleString()}</span>
                                            <span>Color: {(record.copiadora_color || 0).toLocaleString()}</span>
                                          </div>
                                        </div>

                                        {/* Impresora */}
                                        <div className="flex flex-col gap-1 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                                          <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Impresora</div>
                                          <div className="text-sm font-black text-slate-700">{(record.consumo_impresora || 0).toLocaleString()} págs</div>
                                          <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider flex justify-between mt-1">
                                            <span>B/N: {(record.impresora_bn || 0).toLocaleString()}</span>
                                            <span>Color: {(record.impresora_color || 0).toLocaleString()}</span>
                                          </div>
                                        </div>

                                        {/* Escáner */}
                                        <div className="flex flex-col gap-1 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                                          <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Escáner</div>
                                          <div className="text-sm font-black text-slate-700">{(record.consumo_escaner || 0).toLocaleString()} págs</div>
                                          <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider flex justify-between mt-1">
                                            <span>B/N: {(record.escaner_bn || 0).toLocaleString()}</span>
                                            <span>Color: {(record.escaner_color || 0).toLocaleString()}</span>
                                          </div>
                                        </div>

                                        {/* Fax & Totales */}
                                        <div className="flex flex-col gap-1 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                                          <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Fax</div>
                                          <div className="text-sm font-black text-slate-700">{(record.consumo_fax || 0).toLocaleString()} págs</div>
                                          <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider flex justify-between mt-1">
                                            <span>B/N: {(record.fax_bn || 0).toLocaleString()}</span>
                                            <span>Color: 0</span>
                                          </div>
                                        </div>

                                      </div>
                                    </td>
                                  </tr>
                                )}
                              </React.Fragment>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination */}
          {globalUserConsumption && globalUserConsumption.pages > 1 && (
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-slate-100">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Página {userPage} de {globalUserConsumption.pages} ({globalUserConsumption.total} registros)
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setUserPage((prev) => Math.max(prev - 1, 1))}
                  disabled={userPage === 1}
                  className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-transparent transition-all"
                >
                  <ChevronLeft size={16} />
                </button>
                <button
                  onClick={() => setUserPage((prev) => Math.min(prev + 1, globalUserConsumption.pages))}
                  disabled={userPage === globalUserConsumption.pages}
                  className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-transparent transition-all"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Editing Modal */}
      {editingRecord && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-100 max-w-md w-full p-6 relative animate-scale-in">
            {/* Close Button */}
            <button
              onClick={() => setEditingRecord(null)}
              className="absolute right-4 top-4 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X size={18} />
            </button>

            <h3 className="text-base font-black text-slate-800 mb-2">Modificar Consumo de Cierre</h3>
            
            {/* Info Card */}
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mb-6 text-xs text-slate-600 flex flex-col gap-1.5">
              <div>
                <span className="font-bold text-slate-800">Usuario: </span> 
                {editingRecord.nombre_usuario} ({editingRecord.codigo_usuario})
              </div>
              <div>
                <span className="font-bold text-slate-800">Impresora: </span> 
                {editingRecord.printer_hostname}
              </div>
              {editingRecord.printer_ip && (
                <div>
                  <span className="font-bold text-slate-800">Dirección IP: </span> 
                  {editingRecord.printer_ip}
                </div>
              )}
              {editingRecord.printer_location && (
                <div>
                  <span className="font-bold text-slate-800">Ubicación: </span> 
                  {editingRecord.printer_location}
                </div>
              )}
              <div className="mt-1 pt-1.5 border-t border-slate-200 text-slate-400 font-semibold uppercase tracking-wider text-[9px]">
                Período: {editingRecord.fecha_inicio} al {editingRecord.fecha_fin}
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSaveEdit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-black text-slate-600 uppercase tracking-widest">
                  Consumo del Período (Páginas)
                </label>
                <input
                  type="number"
                  min="0"
                  required
                  value={editConsumo}
                  onChange={(e) => setEditConsumo(parseInt(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red font-semibold text-slate-700"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-black text-slate-600 uppercase tracking-widest">
                  Total Acumulado al Cierre (Páginas)
                </label>
                <input
                  type="number"
                  min="0"
                  required
                  value={editTotal}
                  onChange={(e) => setEditTotal(parseInt(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red font-semibold text-slate-700"
                />
              </div>

              {saveErrorMsg && (
                <div className="text-xs font-bold text-red-600 bg-red-50 border border-red-100 rounded-xl p-3">
                  {saveErrorMsg}
                </div>
              )}

              {saveSuccessMsg && (
                <div className="text-xs font-bold text-green-600 bg-green-50 border border-green-100 rounded-xl p-3">
                  {saveSuccessMsg}
                </div>
              )}

              <div className="flex gap-3 justify-end mt-4">
                <button
                  type="button"
                  onClick={() => setEditingRecord(null)}
                  className="px-4 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={updateMutation.isPending || !!saveSuccessMsg}
                  className="bg-ricoh-red hover:bg-red-700 text-white disabled:bg-slate-300 font-bold text-xs uppercase tracking-widest px-4 py-2.5 rounded-xl transition-all flex items-center justify-center gap-2"
                >
                  {updateMutation.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  Guardar Cambios
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const FilterPill = ({ icon, label }: { icon?: React.ReactNode; label: string }) => (
  <button className="flex items-center gap-2 px-4 py-2 rounded-full border border-slate-200 bg-white text-xs font-bold text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm">
    {icon && <span className="text-ricoh-red">{icon}</span>}
    {label} 
    <ChevronDown size={14} className="text-slate-400 ml-1" />
  </button>
);

export default AnalyticsPage;
