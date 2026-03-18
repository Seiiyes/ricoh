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

interface DashboardViewProps {
  onNavigateToPrinter: (printerId: number) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigateToPrinter }) => {
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
      const message = err instanceof Error ? err.message : 'Error al cargar datos del dashboard';
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
      alert(`✅ Lectura completada\nExitosas: ${result.successful}\nFallidas: ${result.failed}`);
      await loadDashboardData(); // Refresh data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al leer todas las impresoras';
      setError(message);
    } finally {
      setReadingAll(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      {/* Header */}
      <div className="bg-white border-b shadow-sm px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BarChart3 className="text-ricoh-red" size={24} />
            <h1 className="text-xl font-bold text-industrial-gray uppercase tracking-tight">
              Resumen de Contadores
            </h1>
          </div>
          <Button
            onClick={handleReadAll}
            loading={readingAll || loading}
            icon={<RefreshCw size={14} />}
            className="rounded-full"
            aria-label="Leer contadores de todas las impresoras"
          >
            {readingAll ? 'Leyendo...' : 'Leer Todas'}
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <LoadingIndicator message="Cargando contadores..." />
        ) : error ? (
          <ErrorHandler message={error} onDismiss={() => setError(null)} />
        ) : printers.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400">
            <BarChart3 size={64} className="mb-4 opacity-20" />
            <p className="text-lg font-bold mb-2">No hay impresoras registradas</p>
            <p className="text-sm">Registra impresoras desde el módulo de descubrimiento</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
