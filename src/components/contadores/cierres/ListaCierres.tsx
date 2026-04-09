import { CierreMensual, Printer, TipoPeriodo } from './types';
import { Button } from '@/components/ui';

interface ListaCierresProps {
  printer: Printer;
  year: number;
  tipoPeriodo: TipoPeriodo;
  cierres: CierreMensual[];
  onCreateCierre: (fechaInicio: string, fechaFin: string) => void;
  onViewDetalle: (cierre: CierreMensual) => void;
}

export const ListaCierres: React.FC<ListaCierresProps> = ({
  printer,
  year,
  tipoPeriodo,
  cierres,
  onCreateCierre,
  onViewDetalle
}) => {
  const formatNumber = (num: number) => num.toLocaleString('es-ES');
  const formatDate = (dateStr: string) => {
    // Para evitar el desfase de zona horaria con YYYY-MM-DD (que JS asume como UTC)
    // forzamos la interpretación como hora local añadiendo T00:00:00
    const date = new Date(dateStr.includes('T') ? dateStr : `${dateStr}T00:00:00`);
    return date.toLocaleDateString('es-ES');
  };

  console.log('ListaCierres rendered with:', { printer, year, tipoPeriodo, cierresCount: cierres.length });


  if (cierres.length === 0) {
    return (
      <div className="bg-white/40 backdrop-blur-md border border-dashed border-slate-200 rounded-[2rem] p-12 text-center animate-fade-in shadow-sm">
        <div className="w-20 h-20 bg-slate-100 text-slate-300 rounded-3xl flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="text-xl font-black text-slate-800 mb-2 tracking-tight">
          No hay cierres {tipoPeriodo}s para {year}
        </h3>
        <p className="text-sm font-bold text-slate-400 mb-8 max-w-md mx-auto">
          No se encontraron registros de cierres en la base de datos para la impresora <span className="text-slate-600">{printer.hostname}</span> durante el año seleccionado.
        </p>
        <Button
          size="lg"
          variant="primary"
          className="rounded-2xl bg-slate-900 border-none text-white shadow-xl shadow-slate-200 h-[52px] px-10 font-black uppercase tracking-widest text-[11px]"
          onClick={() => {
            const hoy = new Date();
            const year = hoy.getFullYear();
            const month = String(hoy.getMonth() + 1).padStart(2, '0');
            const day = String(hoy.getDate()).padStart(2, '0');
            const fechaHoy = `${year}-${month}-${day}`;
            onCreateCierre(fechaHoy, fechaHoy);
          }}
        >
          Crear Primer Cierre
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl shadow-sm border border-slate-100 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-black text-slate-900 tracking-tight">
            {printer.hostname}
          </h2>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs font-bold text-ricoh-red bg-red-50 px-2 py-0.5 rounded-md">{printer.ip_address}</span>
            <span className="text-xs font-semibold text-slate-400">•</span>
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">{printer.location || 'Sin ubicación'}</span>
          </div>
        </div>
        <div className="text-left md:text-right bg-slate-50 rounded-2xl px-6 py-4 border border-slate-100">
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Cierres {tipoPeriodo}s</p>
          <p className="text-3xl font-black text-slate-900 leading-none">{cierres.length}</p>
        </div>
      </div>

      {/* Lista de cierres */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cierres.map((cierre) => (
          <div
            key={cierre.id}
            className="group bg-white rounded-3xl shadow-sm hover:shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-slate-100 transition-all duration-300 hover:-translate-y-1 cursor-pointer overflow-hidden flex flex-col"
            onClick={() => onViewDetalle(cierre)}
          >
            <div className="p-6 flex-1 flex flex-col">
              {/* Header del cierre */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-100">
                  <div className={`w-2.5 h-2.5 rounded-full shadow-sm ${
                    cierre.diferencia_total > 0 ? 'bg-emerald-500 shadow-emerald-500/20' : 'bg-slate-300'
                  }`}></div>
                  <span className="text-[10px] font-black text-slate-600 uppercase tracking-widest">
                    {cierre.tipo_periodo}
                  </span>
                </div>
                <span className="text-[10px] font-bold text-slate-400 bg-slate-50 px-2 py-1 rounded-lg">
                  ID: {cierre.id}
                </span>
              </div>

              {/* Período */}
              <div className="mb-6">
                <p className="text-lg font-black text-slate-800 tracking-tight">
                  {formatDate(cierre.fecha_inicio)}
                  {cierre.fecha_inicio !== cierre.fecha_fin && (
                    <span className="text-slate-400"> → {formatDate(cierre.fecha_fin)}</span>
                  )}
                </p>
                <p className="text-[11px] font-semibold text-slate-400 mt-1">
                  Emitido: {formatDate(cierre.fecha_cierre)}
                </p>
              </div>

              {/* Totales Acumulados */}
              <div className="bg-slate-50/50 rounded-2xl p-4 mb-4 border border-slate-100 flex-1">
                <div className="flex items-center gap-2 mb-3">
                  <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Contador Global</span>
                </div>
                <div className="flex justify-between items-baseline mb-4">
                  <span className="text-xs font-bold text-slate-500">Páginas tot:</span>
                  <span className="text-2xl font-black text-slate-800 tracking-tight">
                    {formatNumber(cierre.total_paginas)}
                  </span>
                </div>

                {/* Desglose de Totales Acumulados */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-white rounded-xl p-2.5 border border-slate-100 shadow-sm flex justify-between items-center">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Cop</span>
                    <span className="font-black text-slate-700">{formatNumber(cierre.total_copiadora)}</span>
                  </div>
                  <div className="bg-white rounded-xl p-2.5 border border-slate-100 shadow-sm flex justify-between items-center">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Imp</span>
                    <span className="font-black text-slate-700">{formatNumber(cierre.total_impresora)}</span>
                  </div>
                  <div className="bg-white rounded-xl p-2.5 border border-slate-100 shadow-sm flex justify-between items-center">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Esc</span>
                    <span className="font-black text-slate-700">{formatNumber(cierre.total_escaner)}</span>
                  </div>
                  <div className="bg-white rounded-xl p-2.5 border border-slate-100 shadow-sm flex justify-between items-center">
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Fax</span>
                    <span className="font-black text-slate-700">{formatNumber(cierre.total_fax)}</span>
                  </div>
                </div>
              </div>

              {/* Consumo del Período */}
              <div className="bg-blue-50/50 rounded-2xl p-4 border border-blue-100/50 relative overflow-hidden group-hover:bg-blue-50 transition-colors">
                <div className="absolute -right-4 -top-4 w-16 h-16 bg-blue-100 rounded-full blur-xl opacity-50 group-hover:opacity-100 transition-opacity"></div>
                <div className="relative z-10">
                  <div className="flex items-center gap-2 mb-2">
                    <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Gasto en Período</span>
                  </div>
                  <div className="flex justify-between items-baseline">
                    <span className="text-xs font-bold text-blue-800">Costo páginas:</span>
                    <span className={`text-xl font-black ${
                      cierre.diferencia_total > 0 ? 'text-ricoh-red' : 'text-slate-400'
                    }`}>
                      {cierre.diferencia_total > 0 ? '+' : ''}{formatNumber(cierre.diferencia_total)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-slate-50 bg-slate-50/50 flex items-center justify-between group-hover:bg-slate-50 transition-colors">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                {cierre.cerrado_por || 'Sistema'}
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onViewDetalle(cierre);
                }}
                className="text-[11px] font-black text-slate-900 hover:text-white hover:bg-ricoh-red uppercase tracking-widest transition-all flex items-center gap-1 bg-white px-3 py-1.5 rounded-lg border border-slate-300 hover:border-ricoh-red shadow-sm"
              >
                Ver Detalles <span className="text-lg leading-none transform group-hover:translate-x-1 transition-transform">→</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
