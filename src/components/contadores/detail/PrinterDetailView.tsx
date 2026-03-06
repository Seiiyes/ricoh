import { useState, useEffect } from 'react';
import { ArrowLeft, RefreshCw, Loader2 } from 'lucide-react';
import { fetchPrinters } from '@/services/printerService';
import { 
  fetchLatestCounter, 
  fetchUserCounters, 
  triggerManualRead 
} from '@/services/counterService';
import { PrinterIdentification } from './PrinterIdentification';
import { CounterBreakdown } from './CounterBreakdown';
import { UserCounterTable } from './UserCounterTable';
import { LoadingIndicator } from '../shared/LoadingIndicator';
import { ErrorHandler } from '../shared/ErrorHandler';
import type { PrinterDevice } from '@/types';
import type { TotalCounter, UserCounter } from '@/types/counter';

interface PrinterDetailViewProps {
  printerId: number;
  onNavigateBack: () => void;
}

export const PrinterDetailView: React.FC<PrinterDetailViewProps> = ({
  printerId,
  onNavigateBack,
}) => {
  const [printer, setPrinter] = useState<PrinterDevice | null>(null);
  const [counter, setCounter] = useState<TotalCounter | null>(null);
  const [userCounters, setUserCounters] = useState<UserCounter[]>([]);
  const [loading, setLoading] = useState(true);
  const [reading, setReading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPrinterData();
  }, [printerId]);

  const loadPrinterData = async () => {
    try {
      setLoading(true);
      const [printerList, latestCounter, users] = await Promise.all([
        fetchPrinters(),
        fetchLatestCounter(printerId),
        fetchUserCounters(printerId),
      ]);
      
      const printerData = printerList.find(p => Number(p.id) === printerId);
      setPrinter(printerData || null);
      setCounter(latestCounter);
      setUserCounters(users);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cargar datos de la impresora';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleManualRead = async () => {
    if (!printer) return;
    
    try {
      setReading(true);
      setError(null);
      await triggerManualRead(printerId);
      await loadPrinterData(); // Refresh data
      alert(`✅ Lectura completada exitosamente para ${printer.hostname}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al leer contadores';
      setError(message);
    } finally {
      setReading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      {/* Header */}
      <div className="bg-white border-b shadow-sm px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onNavigateBack}
              className="text-slate-600 hover:text-slate-900 transition-colors"
              aria-label="Volver al dashboard"
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="text-xl font-bold text-industrial-gray uppercase tracking-tight">
              {printer?.hostname || 'Cargando...'}
            </h1>
          </div>
          <button
            onClick={handleManualRead}
            disabled={reading || loading}
            className="flex items-center gap-2 bg-ricoh-red text-white px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Ejecutar lectura manual de contadores"
          >
            {reading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Leyendo...
              </>
            ) : (
              <>
                <RefreshCw size={14} />
                Lectura Manual
              </>
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 space-y-6">
        {loading ? (
          <LoadingIndicator message="Cargando datos de la impresora..." />
        ) : error ? (
          <ErrorHandler message={error} onDismiss={() => setError(null)} />
        ) : !printer || !counter ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400">
            <p className="text-lg font-bold mb-2">Impresora no encontrada</p>
            <button
              onClick={onNavigateBack}
              className="text-ricoh-red hover:underline"
            >
              Volver al dashboard
            </button>
          </div>
        ) : (
          <>
            {/* Printer Identification */}
            <PrinterIdentification printer={printer} counter={counter} />
            
            {/* Counter Breakdown */}
            <CounterBreakdown counter={counter} />
            
            {/* User Counter Table */}
            <UserCounterTable userCounters={userCounters} />
          </>
        )}
      </div>
    </div>
  );
};
