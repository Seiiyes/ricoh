import { useState, useEffect } from 'react';
import { RefreshCw, BarChart3 } from 'lucide-react';
import { fetchPrinters } from '@/services/printerService';
import { fetchLatestCounter, triggerReadAll } from '@/services/counterService';
import { PrinterCounterCard } from './PrinterCounterCard';
import { LoadingIndicator } from '../shared/LoadingIndicator';
import { ErrorHandler } from '../shared/ErrorHandler';
import { Button } from '@/components/ui';
import type { PrinterDevice } from '@/types';
import type { TotalCounter } from '@/types/counter';
import { useNotification } from '@/hooks/useNotification';
import { cn } from '@/lib/utils';

interface DashboardViewProps {
  onNavigateToPrinter: (printerId: number) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigateToPrinter }) => {
  const notify = useNotification();
  const [printers, setPrinters] = useState<PrinterDevice[]>([]);
  const [counters, setCounters] = useState<Map<number, TotalCounter>>(new Map());
  const [loading, setLoading] = useState(true);
  const [readingAll, setReadingAll] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load printers and their latest counters
  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 60000); // Refresh every 60s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const printerList = await fetchPrinters();
      setPrinters(printerList);
      
      // Fetch latest counter for each printer
      const counterMap = new Map<number, TotalCounter>();
      await Promise.all(
        printerList.map(async (printer) => {
          try {
            const counter = await fetchLatestCounter(Number(printer.id));
            counterMap.set(Number(printer.id), counter);
          } catch (err) {
            console.error(`Failed to fetch counter for printer ${printer.id}:`, err);
          }
        })
      );
      setCounters(counterMap);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cargar indicadores de lectura';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleReadAll = async () => {
    try {
      setReadingAll(true);
      setError(null);
      const result = await triggerReadAll();
      notify.success('Lectura completada', `Exitosas: ${result.successful} | Con errores: ${result.failed}`);
      await loadDashboardData(); // Refresh data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al leer todos los equipos';
      setError(message);
    } finally {
      setReadingAll(false);
    }
  };

  return (
    <div className="flex flex-col min-h-0 bg-transparent">
      {/* Actions Row */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-slate-800 rounded-lg text-white shadow-lg">
            <BarChart3 size={18} />
          </div>
          <div>
            <h2 className="text-sm font-black text-slate-800 uppercase tracking-widest">Estado de Lecturas</h2>
            <p className="text-[10px] text-slate-400 font-bold uppercase">Última actualización sincronizada</p>
          </div>
        </div>
 
        <Button
          variant="primary"
          onClick={handleReadAll}
          loading={readingAll || loading}
          icon={<RefreshCw size={14} className={cn(readingAll && "animate-spin")} />}
          className="rounded-xl px-6 py-2.5 text-[10px] font-black uppercase tracking-widest bg-slate-900 shadow-xl shadow-slate-200"
        >
          {readingAll ? 'Actualizando...' : 'Leer todos los equipos'}
        </Button>
      </div>
 
      {/* Content */}
      <div className="flex-1">
        {loading && !readingAll ? (
          <div className="flex items-center justify-center py-20 bg-white/40 backdrop-blur-md rounded-3xl border border-slate-100">
             <LoadingIndicator message="Cargando datos de equipos..." />
          </div>
        ) : error ? (
          <ErrorHandler message={error} onDismiss={() => setError(null)} />
        ) : printers.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 bg-white/40 backdrop-blur-md rounded-3xl border border-slate-100 text-slate-400">
            <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-6">
              <BarChart3 size={32} className="opacity-20" />
            </div>
            <p className="text-xs font-black uppercase tracking-[0.2em] mb-2 text-slate-500">Sin Equipos</p>
            <p className="text-[10px] uppercase font-bold text-slate-400">Busca equipos desde el botón "Buscar Equipos"</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {printers.map((printer) => (
              <PrinterCounterCard
                key={printer.id}
                printer={printer}
                counter={counters.get(Number(printer.id))}
                onClick={() => onNavigateToPrinter(Number(printer.id))}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
