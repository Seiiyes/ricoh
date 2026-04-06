import { Printer, Hash, Calendar, Zap, MapPin } from 'lucide-react';
import type { PrinterDevice } from '@/types';
import type { TotalCounter } from '@/types/counter';
import { cn } from '@/lib/utils';

interface PrinterCounterCardProps {
  printer: PrinterDevice;
  counter?: TotalCounter;
  onClick: () => void;
}

export const PrinterCounterCard: React.FC<PrinterCounterCardProps> = ({
  printer,
  counter,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className={cn(
        "group relative bg-white rounded-[2rem] p-6 border border-slate-100 transition-all duration-500 cursor-pointer overflow-hidden",
        "hover:shadow-[0_20px_50px_rgba(0,0,0,0.04)] hover:-translate-y-1 hover:border-slate-200"
      )}
      data-testid="printer-card"
    >
      {/* Background Decor */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-slate-50 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-red-50 transition-colors duration-500"></div>
 
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-6">
          <div className="space-y-1">
            <h3 className="text-sm font-black text-slate-800 uppercase tracking-tight group-hover:text-ricoh-red transition-colors">
              {printer.hostname}
            </h3>
            <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400">
              <Hash size={10} />
              <span className="font-mono">{printer.ip_address}</span>
            </div>
            {printer.location && (
              <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400">
                <MapPin size={10} />
                <span>{printer.location}</span>
              </div>
            )}
          </div>
          <div className="w-10 h-10 bg-slate-50 group-hover:bg-red-50 rounded-xl flex items-center justify-center text-slate-400 group-hover:text-ricoh-red transition-all duration-500 rotate-3 group-hover:rotate-0">
            <Printer size={20} />
          </div>
        </div>
        
        {counter ? (
          <div className="space-y-4">
            <div className="bg-slate-50/50 group-hover:bg-white p-4 rounded-2xl border border-slate-100 group-hover:border-red-100 transition-all duration-500">
              <div className="flex justify-between items-center mb-1">
                <span className="text-[9px] font-black text-slate-400 uppercase tracking-widest">Contador Total</span>
                <div className="p-1 bg-emerald-500/10 rounded text-emerald-600">
                  <Zap size={10} />
                </div>
              </div>
              <div className="text-2xl font-black text-slate-900 tracking-tighter">
                {counter.total.toLocaleString()}
                <span className="text-[10px] text-slate-400 font-bold ml-1 uppercase tracking-widest">Lecturas</span>
              </div>
            </div>
 
            <div className="flex items-center gap-2 px-1">
              <Calendar size={12} className="text-slate-300" />
              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-tight">
                Sincronizado: {new Date(counter.fecha_lectura).toLocaleDateString()} {new Date(counter.fecha_lectura).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ) : (
          <div className="py-6 px-4 bg-slate-50 rounded-2xl border border-dashed border-slate-200 flex flex-col items-center justify-center text-center">
            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center mb-2">
               <Activity className="text-slate-300" size={14} />
            </div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-tight">Sin Datos<br/>Registrados</p>
          </div>
        )}
      </div>
 
      {/* Hover Action Indicator */}
      <div className="absolute bottom-4 right-6 opacity-0 group-hover:opacity-100 transition-all duration-500 translate-x-4 group-hover:translate-x-0">
        <div className="flex items-center gap-2 text-[9px] font-black text-ricoh-red uppercase tracking-widest">
          Ver Detalles
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </div>
      </div>
    </div>
  );
};
