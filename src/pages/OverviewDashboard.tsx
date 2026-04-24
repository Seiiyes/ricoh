import React from 'react';
import { 
  Printer, 
  Wifi, 
  Users, 
  FileCheck,
  Activity,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import { KPICard } from '../components/analytics/KPICard';
import { ChartCard } from '../components/analytics/ChartCard';
import { mockOverviewData } from '../mocks/overviewData';
import { chartColors } from '../utils/chartColors';
import { cn } from '../lib/utils';

const OverviewDashboard = () => {
  const { kpis, actividadReciente, topImpresoras } = mockOverviewData;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle2 size={16} className="text-green-500" />;
      case 'error': return <XCircle size={16} className="text-red-500" />;
      case 'warning': return <AlertCircle size={16} className="text-yellow-500" />;
      default: return <Activity size={16} className="text-slate-500" />;
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-50 border-green-100';
      case 'error': return 'bg-red-50 border-red-100';
      case 'warning': return 'bg-yellow-50 border-yellow-100';
      default: return 'bg-slate-50 border-slate-100';
    }
  };

  return (
    <div className="flex flex-col h-full animate-fade-in custom-scrollbar overflow-y-auto pb-10">
      <div className="mb-8">
        <h1 className="text-2xl font-black text-slate-800 tracking-tight">Overview Dashboard</h1>
        <p className="text-sm font-bold text-slate-500 uppercase tracking-widest mt-1">Visión General del Sistema</p>
      </div>

      {/* KPIs Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard 
          title="Total Equipos" 
          value={kpis.totalEquipos} 
          icon={<Printer size={20} />} 
          color={chartColors.primary} 
        />
        <KPICard 
          title="Equipos Online" 
          value={kpis.equiposOnline} 
          icon={<Wifi size={20} />} 
          color={chartColors.success} 
        />
        <KPICard 
          title="Usuarios Provisionados" 
          value={kpis.usuariosProvisionados} 
          icon={<Users size={20} />} 
          color={chartColors.info} 
        />
        <KPICard 
          title="Cierres Pendientes" 
          value={kpis.cierresPendientes} 
          icon={<FileCheck size={20} />} 
          color={chartColors.warning} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Impresoras Chart */}
        <div className="lg:col-span-1 h-[400px]">
          <ChartCard title="Top 5 Impresoras (Mes Actual)">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={topImpresoras}
                margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
                layout="vertical"
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis type="number" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 11, fill: '#334155' }} width={120} axisLine={false} tickLine={false} />
                <Tooltip 
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  formatter={(value: number) => [`${value.toLocaleString()} páginas`, 'Consumo']}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={28}>
                  {topImpresoras.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={chartColors.categorical[index % chartColors.categorical.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        {/* Actividad Reciente Table */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-5 h-full flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-bold text-slate-800">Actividad Reciente</h3>
              <button className="text-xs font-bold text-ricoh-red hover:text-red-700 uppercase tracking-widest transition-colors">
                Ver todo
              </button>
            </div>
            
            <div className="flex-1 overflow-auto custom-scrollbar pr-2">
              <div className="space-y-3">
                {actividadReciente.map((actividad) => (
                  <div 
                    key={actividad.id} 
                    className={cn(
                      "p-4 rounded-lg border flex gap-4 items-start transition-all hover:shadow-sm",
                      getStatusBg(actividad.status)
                    )}
                  >
                    <div className="mt-1 bg-white p-1 rounded-full shadow-sm">
                      {getStatusIcon(actividad.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-start mb-1">
                        <p className="text-sm font-bold text-slate-800 truncate">{actividad.tipo}</p>
                        <span className="text-[10px] font-bold text-slate-500 whitespace-nowrap ml-2">
                          {new Date(actividad.fecha).toLocaleDateString()} {new Date(actividad.fecha).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mb-2 truncate">{actividad.descripcion}</p>
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1">
                        <Activity size={10} /> Por: {actividad.usuario}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverviewDashboard;
