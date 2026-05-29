import { useNavigate } from 'react-router-dom';
import {
  Printer,
  Wifi,
  WifiOff,
  Users,
  FileCheck,
  Activity,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
  UserCircle,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { KPICard } from '../components/analytics/KPICard';
import { ChartCard } from '../components/analytics/ChartCard';
import { chartColors } from '../utils/chartColors';
import { cn } from '../lib/utils';
import {
  useDashboardKPIs,
  useTopImpresoras,
  useActividadReciente,
  useTopUsuariosConsumo,
  useConsumoResumen,
  useTonerAlertas,
  type TopImpresoraMes,
} from '../hooks/useDashboardData';

function QueryErrorBanner({
  title,
  message,
  onRetry,
}: {
  title: string;
  message: string;
  onRetry: () => void;
}) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50/90 p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <div>
        <p className="text-xs font-black text-red-800 uppercase tracking-widest">{title}</p>
        <p className="text-sm text-red-900 mt-1">{message}</p>
      </div>
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex items-center justify-center gap-2 shrink-0 rounded-xl bg-white border border-red-200 px-4 py-2 text-xs font-black uppercase tracking-widest text-red-800 hover:bg-red-100 transition-colors"
      >
        <RefreshCw size={14} />
        Reintentar
      </button>
    </div>
  );
}

function KpiRowSkeleton() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 lg:gap-4 mb-6 lg:mb-8">
      {Array.from({ length: 5 }).map((_, i) => (
        <div
          key={i}
          className="h-[110px] rounded-xl bg-slate-100 border border-slate-200/80 animate-pulse"
        />
      ))}
    </div>
  );
}

/** Modelo genérico que suele repetirse en varios equipos (no sirve para distinguirlos en el eje Y). */
const GENERIC_MODEL_PATTERN = /network\s+printer|port\s*9100|^unknown$/i;

function trimSafe(s: string | null | undefined) {
  return (s ?? '').trim();
}

function tailChars(s: string, maxLen: number) {
  const t = s.trim();
  if (t.length <= maxLen) return t;
  return `…${t.slice(-(maxLen - 1))}`;
}

type ChartRow = {
  printerId: number;
  rank: number;
  /** Debe ser único por fila: Recharts usa `name` como categoría; duplicados rompen el hover. */
  name: string;
  /** Título legible en el tooltip */
  fullLabel: string;
  value: number;
  ubicacion: string | null;
  hostname: string;
  modelo: string;
};

function buildTopConsumoChartRows(items: TopImpresoraMes[]): ChartRow[] {
  return items.map((p, index) => {
    const ubic = trimSafe(p.ubicacion);
    const host = trimSafe(p.hostname);
    const mod = trimSafe(p.modelo);
    const generic = !mod || GENERIC_MODEL_PATTERN.test(mod);

    let axisLine: string;
    if (ubic && host) {
      axisLine = `${ubic} · ${tailChars(host, 16)}`;
    } else if (ubic) {
      axisLine = ubic;
    } else if (host) {
      axisLine = tailChars(host, 30);
    } else if (!generic) {
      axisLine = mod.length > 34 ? `${mod.slice(0, 32)}…` : mod;
    } else {
      axisLine = `Equipo #${p.printer_id}`;
    }

    const rank = index + 1;
    const name = `${rank}. ${axisLine}`.slice(0, 58);

    const fullLabel = !generic
      ? mod
      : [mod || 'Impresora de red', host ? `(${host})` : `(#${p.printer_id})`].filter(Boolean).join(' ');

    return {
      printerId: p.printer_id,
      rank,
      name,
      fullLabel: fullLabel || `Equipo ${p.printer_id}`,
      value: Number(p.total_paginas) || 0,
      ubicacion: p.ubicacion,
      hostname: host,
      modelo: mod,
    };
  });
}

type TooltipPayloadEntry = { payload?: ChartRow; value?: number };

function TopConsumoTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: readonly TooltipPayloadEntry[];
}) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload;
  if (!row) return null;
  const pages = Number(row.value);
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 shadow-lg text-xs max-w-[min(100vw-2rem,22rem)] z-50">
      <p className="font-bold text-slate-800 leading-snug">
        {row.rank}. {row.fullLabel}
      </p>
      {row.hostname ? (
        <p className="text-slate-500 mt-1 font-mono text-[11px] break-all">{row.hostname}</p>
      ) : null}
      {row.ubicacion ? <p className="text-slate-600 mt-1.5 text-[11px]">{row.ubicacion}</p> : null}
      <p className="text-slate-900 font-black mt-2 border-t border-slate-100 pt-2">
        Total: {Number.isFinite(pages) ? pages.toLocaleString('es') : '—'} páginas
      </p>
    </div>
  );
}

const OverviewDashboard = () => {
  const navigate = useNavigate();
  const kpisQ = useDashboardKPIs();
  const topQ = useTopImpresoras(5);
  const topUsersQ = useTopUsuariosConsumo(5);
  const actQ = useActividadReciente(4);
  const consumoResumenQ = useConsumoResumen();
  const tonerQ = useTonerAlertas();

  const chartData: ChartRow[] = buildTopConsumoChartRows(topQ.data ?? []);

  const formatFecha = (iso: string) => {
    try {
      const d = new Date(iso);
      return d.toLocaleString('es', {
        day: '2-digit',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return iso;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 size={14} className="text-green-500" />;
      case 'error':
        return <XCircle size={14} className="text-red-500" />;
      case 'warning':
        return <AlertCircle size={14} className="text-yellow-500" />;
      default:
        return <Activity size={14} className="text-slate-500" />;
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-50 border-green-100';
      case 'error':
        return 'bg-red-50 border-red-100';
      case 'warning':
        return 'bg-yellow-50 border-yellow-100';
      default:
        return 'bg-slate-50 border-slate-100';
    }
  };

  const kpisPending = kpisQ.isPending;
  const kpisReady = !kpisPending && !kpisQ.isError && kpisQ.data;

  return (
    <div className="flex flex-col h-full animate-fade-in custom-scrollbar overflow-y-auto pb-10">
      <div className="mb-6 lg:mb-8 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-xl lg:text-2xl font-black text-slate-800 tracking-tight">Resumen</h1>
          <p className="text-xs lg:text-sm font-bold text-slate-500 mt-1 max-w-xl">
            Indicadores de impresoras, usuarios asignados y cierres del mes. Los datos se actualizan desde el servidor.
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            void kpisQ.refetch();
            void topQ.refetch();
            void topUsersQ.refetch();
            void actQ.refetch();
            void consumoResumenQ.refetch();
            void tonerQ.refetch();
          }}
          disabled={kpisQ.isFetching || topQ.isFetching || topUsersQ.isFetching || actQ.isFetching || consumoResumenQ.isFetching || tonerQ.isFetching}
          className="inline-flex items-center gap-2 self-start sm:self-auto rounded-xl border border-slate-200 bg-white px-4 py-2 text-[10px] font-black uppercase tracking-widest text-slate-600 hover:border-ricoh-red/40 hover:text-ricoh-red transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={cn((kpisQ.isFetching || topQ.isFetching || topUsersQ.isFetching || actQ.isFetching || consumoResumenQ.isFetching || tonerQ.isFetching) && 'animate-spin')} />
          Actualizar
        </button>
      </div>

      {kpisQ.isError && (
        <div className="mb-4">
          <QueryErrorBanner
            title="No se pudieron cargar los indicadores"
            message={
              kpisQ.error instanceof Error
                ? kpisQ.error.message
                : 'Compruebe la conexión y que el servicio esté disponible.'
            }
            onRetry={() => void kpisQ.refetch()}
          />
        </div>
      )}

      {kpisPending ? (
        <KpiRowSkeleton />
      ) : kpisReady ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 lg:gap-4 mb-6 lg:mb-8 min-w-0">
          <KPICard
            title="Impresoras registradas"
            value={kpisQ.data.total_equipos}
            icon={<Printer size={18} />}
            color={chartColors.primary}
          />
          <KPICard
            title="Conectadas"
            value={kpisQ.data.equipos_online}
            icon={<Wifi size={18} />}
            color={chartColors.success}
          />
          <KPICard
            title="Sin conexión"
            value={kpisQ.data.equipos_offline}
            icon={<WifiOff size={18} />}
            color={chartColors.categorical[3] ?? chartColors.primary}
          />
          <KPICard
            title="Usuarios en equipos"
            value={kpisQ.data.usuarios_provisionados}
            icon={<Users size={18} />}
            color={chartColors.info}
          />
          <KPICard
            title="Cierres del mes pendientes"
            value={kpisQ.data.cierres_pendientes}
            icon={<FileCheck size={18} />}
            color={chartColors.warning}
            className="col-span-2 sm:col-span-1"
          />
        </div>
      ) : null}

      <div className="grid grid-cols-1 md:grid-cols-6 xl:grid-cols-12 gap-4 lg:gap-5 items-stretch min-w-0">
        <div className="md:col-span-6 xl:col-span-5 min-h-0 min-w-0 h-[260px] sm:h-[300px] md:min-h-[300px] md:h-[320px] xl:h-[380px] flex flex-col gap-2">
          {topQ.isError ? (
            <QueryErrorBanner
              title="Consumo por equipo"
              message={
                topQ.error instanceof Error
                  ? topQ.error.message
                  : 'No se pudo cargar el ranking de impresoras.'
              }
              onRetry={() => void topQ.refetch()}
            />
          ) : (
            <ChartCard
              title="Mayor volumen de copias este mes"
              description="Según cierres mensuales registrados"
            >
              {topQ.isPending ? (
                <div className="flex h-full items-center justify-center text-slate-400">
                  <Loader2 className="h-8 w-8 animate-spin text-ricoh-red" />
                </div>
              ) : chartData.length === 0 ? (
                <div className="flex h-full flex-col items-center justify-center text-center px-4 text-slate-500">
                  <Printer className="h-10 w-10 opacity-20 mb-3" />
                  <p className="text-sm font-bold text-slate-700">Aún no hay datos de consumo</p>
                  <p className="text-xs mt-2 max-w-[240px]">
                    Cuando existan cierres mensuales en el mes en curso, aquí aparecerán las impresoras con más páginas
                    contabilizadas.
                  </p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 12, right: 16, left: 8, bottom: 4 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 11, fill: '#64748b' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      dataKey="name"
                      type="category"
                      tick={{ fontSize: 9, fill: '#334155' }}
                      width={148}
                      axisLine={false}
                      tickLine={false}
                      interval={0}
                    />
                    <Tooltip
                      cursor={{ fill: 'rgba(248, 250, 252, 0.92)' }}
                      content={(tipProps) => (
                        <TopConsumoTooltip active={tipProps.active} payload={tipProps.payload} />
                      )}
                      allowEscapeViewBox={{ x: true, y: true }}
                      wrapperStyle={{ zIndex: 50 }}
                    />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={22} isAnimationActive={false}>
                      {chartData.map((row) => (
                        <Cell
                          key={row.printerId}
                          fill={
                            chartColors.categorical[
                              (row.rank - 1) % chartColors.categorical.length
                            ]
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </ChartCard>
          )}
          <button
            type="button"
            onClick={() => navigate('/analytics')}
            className="text-left text-[10px] font-bold text-ricoh-red hover:text-red-700 uppercase tracking-widest transition-colors px-1"
          >
            Ver tendencias y exportar en Reportes y análisis →
          </button>
        </div>

        <div className="md:col-span-3 xl:col-span-3 flex flex-col min-h-0 min-w-0">
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-3 lg:p-4 flex flex-col flex-1 min-h-[220px] max-h-[320px] md:max-h-[360px] xl:max-h-none xl:h-[380px]">
            <div className="flex items-start gap-2 mb-2 shrink-0">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600 shrink-0">
                <UserCircle size={16} />
              </div>
              <div className="min-w-0">
                <h3 className="text-xs font-bold text-slate-800 leading-tight">Más copias por usuario</h3>
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">
                  Mes actual (suma del consumo en cierres)
                </p>
              </div>
            </div>

            {topUsersQ.isError ? (
              <QueryErrorBanner
                title="Ranking usuarios"
                message={(() => {
                  const base =
                    topUsersQ.error instanceof Error
                      ? topUsersQ.error.message
                      : 'No se pudo cargar el consumo por usuario.';
                  const hint =
                    /network error|failed to fetch|load failed/i.test(base)
                      ? ' Revise CORS en el backend (reinicie la API tras actualizar) y que exista la migración 015 (función get_top_consumo_usuarios).'
                      : '';
                  return `${base}${hint}`;
                })()}
                onRetry={() => void topUsersQ.refetch()}
              />
            ) : topUsersQ.isPending ? (
              <div className="flex flex-1 items-center justify-center py-12 text-slate-400">
                <Loader2 className="h-7 w-7 animate-spin text-ricoh-red" />
              </div>
            ) : (
              <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar -mx-1 px-1">
                {(topUsersQ.data ?? []).length === 0 ? (
                  <p className="text-center text-[11px] text-slate-500 py-6 px-2">
                    Sin datos aún. Cuando haya cierres con desglose por usuario Ricoh, verá aquí quién acumuló más
                    páginas en el mes.
                  </p>
                ) : (
                  <ul className="space-y-0 divide-y divide-slate-100">
                    {(topUsersQ.data ?? []).map((u, idx) => (
                      <li key={u.user_id} className="flex items-center justify-between gap-2 py-2 first:pt-0">
                        <div className="flex items-center gap-2 min-w-0">
                          <span className="text-[10px] font-black text-slate-400 w-4 shrink-0 tabular-nums">
                            {idx + 1}
                          </span>
                          <div className="min-w-0">
                            <p className="text-[11px] font-bold text-slate-800 truncate">{u.nombre}</p>
                            <p className="text-[9px] text-slate-500 font-mono truncate">Cód. {u.codigo_usuario}</p>
                          </div>
                        </div>
                        <span className="text-[11px] font-black text-slate-800 tabular-nums shrink-0">
                          {u.total_consumo_paginas.toLocaleString('es')}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
                {(topUsersQ.data ?? []).length > 0 ? (
                  <p className="text-[9px] text-slate-400 mt-2 pt-2 border-t border-slate-100">
                    Número de páginas del período según cada cierre (campo consumo).
                  </p>
                ) : null}
              </div>
            )}
          </div>
        </div>

        <div className="md:col-span-3 xl:col-span-4 flex flex-col min-h-0 min-w-0">
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-3 flex flex-col flex-1 min-h-[220px] max-h-[300px] sm:max-h-[340px] md:max-h-[360px] xl:max-h-none xl:h-[380px]">
            <div className="shrink-0 mb-2">
              <h3 className="text-xs font-bold text-slate-800">Últimos movimientos</h3>
              <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-0.5 leading-snug">
                Aprovisionamientos, cierres y otras acciones
              </p>
            </div>

            {actQ.isError ? (
              <QueryErrorBanner
                title="Actividad"
                message={
                  actQ.error instanceof Error
                    ? actQ.error.message
                    : 'No se pudo cargar el historial reciente.'
                }
                onRetry={() => void actQ.refetch()}
              />
            ) : actQ.isPending ? (
              <div className="flex flex-1 items-center justify-center py-10 text-slate-400">
                <Loader2 className="h-7 w-7 animate-spin text-ricoh-red" />
              </div>
            ) : (
              <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar pr-0.5 -mr-0.5">
                <div className="space-y-1.5">
                  {actQ.data?.map((actividad) => (
                    <div
                      key={actividad.id}
                      className={cn(
                        'rounded-lg border px-2 py-1.5 flex gap-2 items-start transition-colors hover:bg-white/80',
                        getStatusBg(actividad.status)
                      )}
                    >
                      <div className="mt-0.5 bg-white p-0.5 rounded-full shadow-sm shrink-0">
                        {getStatusIcon(actividad.status)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-baseline gap-2">
                          <p className="text-[11px] font-bold text-slate-800 truncate">{actividad.tipo}</p>
                          <span className="text-[9px] font-bold text-slate-500 shrink-0 tabular-nums">
                            {formatFecha(actividad.fecha)}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-600 truncate mt-0.5">{actividad.descripcion}</p>
                        <p className="text-[9px] font-semibold text-slate-400 truncate mt-0.5">
                          {actividad.usuario || 'Sistema'}
                        </p>
                      </div>
                    </div>
                  ))}
                  {(!actQ.data || actQ.data.length === 0) && (
                    <div className="text-center py-6 text-slate-400 text-[11px]">
                      No hay eventos recientes registrados.
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* SECCIÓN ADICIONAL COMPLEMENTARIA: MONITOREO DE SUMINISTROS Y CONSUMO MENSUAL POR FUNCIÓN */}
      <div className="mt-8 mb-4">
        <h2 className="text-sm font-black text-slate-800 tracking-wider uppercase">Suministros y Operación Detallada</h2>
        <p className="text-[10px] font-bold text-slate-400 mt-0.5 uppercase tracking-widest">
          Monitoreo en tiempo real de niveles de tóner y contadores de consumo acumulados
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 lg:gap-5 items-stretch min-w-0">
        {/* WIDGET 1: DISTRIBUCIÓN DE CONSUMO POR FUNCIÓN (MÓDULO CONTADORES) */}
        <div className="md:col-span-12 xl:col-span-5 bg-white rounded-xl shadow-sm border border-slate-100 p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xs font-bold text-slate-800">Distribución de Consumo del Período</h3>
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">
                  Mes actual según lecturas de contadores
                </p>
              </div>
              <span className="inline-flex rounded-lg bg-red-50 text-red-600 px-2 py-0.5 text-[9px] font-black uppercase tracking-wider">
                {consumoResumenQ.data?.mes_nombre || 'ACTUAL'}
              </span>
            </div>

            {consumoResumenQ.isPending ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-6 w-6 animate-spin text-ricoh-red" />
              </div>
            ) : consumoResumenQ.isError ? (
              <p className="text-xs text-red-500 text-center py-6">No se pudo cargar el resumen de consumo</p>
            ) : consumoResumenQ.data ? (
              <div className="space-y-4">
                {/* Total general impreso */}
                <div className="bg-slate-50/70 rounded-xl p-3 border border-slate-100 flex items-center justify-between">
                  <div>
                    <span className="text-[9px] font-black text-slate-400 uppercase tracking-wider">Páginas Totales</span>
                    <p className="text-xl font-black text-slate-800 tracking-tight mt-0.5 leading-none">
                      {consumoResumenQ.data.total_paginas.toLocaleString('es')}
                    </p>
                  </div>
                  <span className="text-slate-400">
                    <Activity size={24} />
                  </span>
                </div>

                {/* Desglose por función con barras de progreso estilizadas */}
                <div className="space-y-3">
                  {/* Impresora */}
                  <div>
                    <div className="flex justify-between items-baseline mb-1">
                      <span className="text-[10px] font-bold text-slate-700">Impresora (PC/Red)</span>
                      <span className="text-[10px] font-black text-slate-800 tabular-nums">
                        {consumoResumenQ.data.impresora.toLocaleString('es')} págs
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full transition-all duration-500" 
                        style={{ width: `${Math.min(100, (consumoResumenQ.data.impresora / (consumoResumenQ.data.total_paginas || 1)) * 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Copiadora */}
                  <div>
                    <div className="flex justify-between items-baseline mb-1">
                      <span className="text-[10px] font-bold text-slate-700">Copiadora (Físico)</span>
                      <span className="text-[10px] font-black text-slate-800 tabular-nums">
                        {consumoResumenQ.data.copiadora.toLocaleString('es')} págs
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-emerald-500 to-teal-500 h-full rounded-full transition-all duration-500" 
                        style={{ width: `${Math.min(100, (consumoResumenQ.data.copiadora / (consumoResumenQ.data.total_paginas || 1)) * 100)}%` }}
                      />
                    </div>
                  </div>

                  {/* Escáner */}
                  <div>
                    <div className="flex justify-between items-baseline mb-1">
                      <span className="text-[10px] font-bold text-slate-700">Escáner (Digitalización)</span>
                      <span className="text-[10px] font-black text-slate-800 tabular-nums">
                        {consumoResumenQ.data.escaner.toLocaleString('es')} págs
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-amber-500 to-orange-500 h-full rounded-full transition-all duration-500" 
                        style={{ width: `${Math.min(100, (consumoResumenQ.data.escaner / (consumoResumenQ.data.total_paginas || 1)) * 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-[9px] text-slate-400">
            <span>Diferencias calculadas vs cierres anteriores</span>
            <span>Estadística del período</span>
          </div>
        </div>

        {/* WIDGET 2: MONITOREO DE SUMINISTROS (TÓNER Y CONSUMIBLES) */}
        <div className="md:col-span-12 xl:col-span-7 bg-white rounded-xl shadow-sm border border-slate-100 p-4 flex flex-col justify-between min-w-0">
          <div>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xs font-bold text-slate-800">Niveles de Suministro de Tóner (CMYK)</h3>
                <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">
                  Porcentaje de consumibles remanentes reportados por el hardware
                </p>
              </div>
              <span className="inline-flex rounded-lg bg-blue-50 text-blue-600 px-2 py-0.5 text-[9px] font-black uppercase tracking-wider">
                Monitoreo SNMP
              </span>
            </div>

            {tonerQ.isPending ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-6 w-6 animate-spin text-ricoh-red" />
              </div>
            ) : tonerQ.isError ? (
              <p className="text-xs text-red-500 text-center py-6">No se pudieron cargar los niveles de tóner</p>
            ) : tonerQ.data ? (
              <div className="space-y-4">
                {tonerQ.data.slice(0, 3).map((p) => {
                  return (
                    <div key={p.printer_id} className="rounded-xl border border-slate-100 p-3 bg-slate-50/40 hover:bg-slate-50 transition-colors">
                      <div className="flex justify-between items-start mb-2">
                        <div className="min-w-0">
                          <p className="text-[11px] font-black text-slate-800 truncate leading-none">{p.modelo}</p>
                          <p className="text-[9px] text-slate-400 font-mono mt-1 leading-none">{p.hostname} · {p.ubicacion}</p>
                        </div>
                        {p.alerta ? (
                          <span className="inline-flex items-center gap-1 rounded-full bg-red-100 text-red-800 text-[8px] font-black uppercase px-2 py-0.5 leading-none">
                            <AlertCircle size={8} /> {p.alerta_mensaje}
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded-full bg-green-100 text-green-800 text-[8px] font-black uppercase px-2 py-0.5 leading-none">
                            Optimo
                          </span>
                        )}
                      </div>

                      {/* Gráficos de barras horizontales compactos para CMYK */}
                      <div className="grid grid-cols-4 gap-2 mt-2">
                        {/* Negro */}
                        <div className="flex flex-col">
                          <div className="flex justify-between text-[8px] font-bold text-slate-600 mb-0.5 leading-none">
                            <span>K (Negro)</span>
                            <span className="tabular-nums font-black">{p.toner_black}%</span>
                          </div>
                          <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                            <div className="bg-slate-900 h-full rounded-full" style={{ width: `${p.toner_black}%` }} />
                          </div>
                        </div>

                        {/* Cian */}
                        {p.is_color ? (
                          <div className="flex flex-col">
                            <div className="flex justify-between text-[8px] font-bold text-slate-600 mb-0.5 leading-none">
                              <span>C (Cian)</span>
                              <span className="tabular-nums font-black">{p.toner_cyan}%</span>
                            </div>
                            <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                              <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${p.toner_cyan}%` }} />
                            </div>
                          </div>
                        ) : (
                          <div className="flex flex-col opacity-20">
                            <span className="text-[8px] font-bold text-slate-300 leading-none">C (N/A)</span>
                            <div className="w-full bg-slate-100 h-1.5 rounded-full" />
                          </div>
                        )}

                        {/* Magenta */}
                        {p.is_color ? (
                          <div className="flex flex-col">
                            <div className="flex justify-between text-[8px] font-bold text-slate-600 mb-0.5 leading-none">
                              <span>M (Mag)</span>
                              <span className="tabular-nums font-black">{p.toner_magenta}%</span>
                            </div>
                            <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                              <div className="bg-pink-500 h-full rounded-full" style={{ width: `${p.toner_magenta}%` }} />
                            </div>
                          </div>
                        ) : (
                          <div className="flex flex-col opacity-20">
                            <span className="text-[8px] font-bold text-slate-300 leading-none">M (N/A)</span>
                            <div className="w-full bg-slate-100 h-1.5 rounded-full" />
                          </div>
                        )}

                        {/* Amarillo */}
                        {p.is_color ? (
                          <div className="flex flex-col">
                            <div className="flex justify-between text-[8px] font-bold text-slate-600 mb-0.5 leading-none">
                              <span>Y (Amar)</span>
                              <span className="tabular-nums font-black">{p.toner_yellow}%</span>
                            </div>
                            <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                              <div className="bg-yellow-400 h-full rounded-full" style={{ width: `${p.toner_yellow}%` }} />
                            </div>
                          </div>
                        ) : (
                          <div className="flex flex-col opacity-20">
                            <span className="text-[8px] font-bold text-slate-300 leading-none">Y (N/A)</span>
                            <div className="w-full bg-slate-100 h-1.5 rounded-full" />
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : null}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-[9px] text-slate-400">
            <span>Última lectura: hace unos instantes</span>
            <span className="text-ricoh-red font-bold uppercase tracking-wider">Flota Activa</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewDashboard;
