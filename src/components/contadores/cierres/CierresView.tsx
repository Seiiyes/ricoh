import { useState, useEffect } from 'react';
import { CierreMensual } from './types';
import { ListaCierres } from './ListaCierres';
import { CierreModal } from './CierreModal';
import { CierreDetalleModal } from './CierreDetalleModal';
import { ComparacionPage } from './ComparacionPage';
import { Button, Spinner, Alert } from '@/components/ui';
import { RefreshCw, Plus, BarChart3, Filter, SlidersHorizontal, Calculator, Printer as PrinterIcon } from 'lucide-react';
import closeService from '@/services/closeService';
import apiClient from '@/services/apiClient';
import { parseApiError } from '@/utils/errorHandler';
import { cn } from '@/lib/utils';
import type { Printer } from '@/types';

export const CierresView: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedPrinter, setSelectedPrinter] = useState<number | null>(null);
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [cierres, setCierres] = useState<CierreMensual[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sub-vista
  const [vistaActual, setVistaActual] = useState<'lista' | 'comparacion'>('lista');

  // Modals
  const [cierreModalOpen, setCierreModalOpen] = useState(false);
  const [detalleModalOpen, setDetalleModalOpen] = useState(false);
  const [selectedCierre, setSelectedCierre] = useState<CierreMensual | null>(null);

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  useEffect(() => { loadPrinters(); }, []);

  useEffect(() => {
    if (selectedPrinter) loadCierres();
  }, [selectedPrinter, selectedYear]);

  const loadPrinters = async () => {
    try {
      const response = await apiClient.get('/printers/');
      const data = response.data.items || response.data;
      setPrinters(data);
      if (data.length > 0 && !selectedPrinter) setSelectedPrinter(data[0].id);
    } catch (error) {
      console.error('Error al cargar impresoras:', error);
      setError('Error al cargar impresoras');
    }
  };

  const loadCierres = async () => {
    if (!selectedPrinter) return;
    setLoading(true);
    setError(null);
    try {
      const data = await closeService.getClosesByPrinter(selectedPrinter);
      setCierres(data);
    } catch (err: any) {
      console.error('Error al cargar cierres:', err);
      setError(parseApiError(err, 'Error al cargar cierres'));
    } finally {
      setLoading(false);
    }
  };

  const handleCierreSuccess = () => { loadCierres(); setCierreModalOpen(false); };
  const selectedPrinterData = printers.find(p => p.id === selectedPrinter);

  // Si estamos en modo comparación, mostrar la sub-vista completa
  if (vistaActual === 'comparacion') {
    return (
      <ComparacionPage
        cierres={cierres}
        onVolver={() => setVistaActual('lista')}
      />
    );
  }

  return (
    <div className="space-y-10 animate-fade-in">
      {/* Barra de filtros Premium */}
      <div className="bg-white/70 backdrop-blur-md rounded-3xl border border-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
          <div className="flex flex-wrap items-end gap-6 flex-1">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Dispositivo Escaneado</label>
              <div className="relative group">
                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-ricoh-red transition-colors">
                  <PrinterIcon size={16} />
                </div>
                <select
                  value={selectedPrinter || ''}
                  onChange={(e) => setSelectedPrinter(e.target.value ? Number(e.target.value) : null)}
                  className="pl-11 pr-10 py-3 bg-slate-50 border border-slate-100 rounded-2xl text-sm font-bold text-slate-700 appearance-none focus:outline-none focus:ring-4 focus:ring-red-500/5 focus:border-ricoh-red transition-all min-w-[280px]"
                >
                  <option value="">Seleccionar Impresora...</option>
                  {printers.map(printer => (
                    <option key={printer.id} value={printer.id}>
                      {printer.hostname} ({printer.ip_address})
                    </option>
                  ))}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                  <SlidersHorizontal size={14} />
                </div>
              </div>
            </div>
 
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Periodo Anual</label>
              <div className="relative group">
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(Number(e.target.value))}
                  className="px-6 py-3 bg-slate-50 border border-slate-100 rounded-2xl text-sm font-bold text-slate-700 appearance-none focus:outline-none focus:ring-4 focus:ring-red-500/5 focus:border-ricoh-red transition-all min-w-[120px]"
                >
                  {years.map(year => <option key={year} value={year}>{year}</option>)}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                   <Filter size={14} />
                </div>
              </div>
            </div>
 
            <Button
              variant="ghost"
              size="lg"
              onClick={loadCierres}
              loading={loading}
              disabled={!selectedPrinter}
              icon={<RefreshCw size={16} className={cn(loading && "animate-spin")} />}
              className="rounded-2xl h-[46px] px-6 text-slate-400 hover:text-ricoh-red hover:bg-red-50"
            >
              Recargar
            </Button>
          </div>
 
          <div className="flex items-center gap-4">
            {cierres.length >= 2 && (
              <Button
                variant="outline"
                size="lg"
                onClick={() => setVistaActual('comparacion')}
                icon={<BarChart3 size={18} />}
                className="rounded-2xl border-slate-200 text-slate-600 font-bold hover:bg-slate-50 h-[52px] px-8"
              >
                Comparativa ({cierres.length})
              </Button>
            )}
 
            <Button
              variant="primary"
              size="lg"
              onClick={() => setCierreModalOpen(true)}
              disabled={!selectedPrinter}
              icon={<Calculator size={18} />}
              className="rounded-2xl bg-slate-900 border-none text-white shadow-xl shadow-slate-200 h-[52px] px-10 font-black uppercase tracking-widest text-[11px]"
            >
              Nuevo Cierre
            </Button>
          </div>
        </div>
      </div>
 
      {error && (
        <Alert variant="error" onClose={() => setError(null)} className="rounded-2xl border-none shadow-lg">
          {error}
        </Alert>
      )}
 
      {/* Contenido Principal */}
      <div className="min-h-[400px]">
        {!selectedPrinter ? (
          <div className="flex flex-col items-center justify-center py-32 bg-white/40 backdrop-blur-md rounded-[3rem] border border-dashed border-slate-200">
            <div className="w-20 h-20 bg-slate-100 rounded-3xl flex items-center justify-center mb-6 text-slate-300">
              <Calculator size={32} />
            </div>
            <p className="text-sm font-black uppercase tracking-[0.2em] text-slate-400">Selección Requerida</p>
            <p className="text-[10px] font-bold text-slate-400 uppercase mt-2">Elige una impresora para visualizar el historial de cierres</p>
          </div>
        ) : loading ? (
          <div className="flex flex-col items-center justify-center py-32">
            <Spinner size="lg" text="Procesando datos históricos..." />
          </div>
        ) : (
          <div className="animate-slide-up">
            <ListaCierres
              printer={selectedPrinterData!}
              year={selectedYear}
              tipoPeriodo="personalizado"
              cierres={cierres}
              onCreateCierre={() => setCierreModalOpen(true)}
              onViewDetalle={(cierre) => { setSelectedCierre(cierre); setDetalleModalOpen(true); }}
            />
          </div>
        )}
      </div>
 
      {cierreModalOpen && selectedPrinter && (
        <CierreModal
          printerId={selectedPrinter}
          printerName={selectedPrinterData?.hostname}
          onClose={() => setCierreModalOpen(false)}
          onSuccess={handleCierreSuccess}
        />
      )}
 
      {detalleModalOpen && selectedCierre && (
        <CierreDetalleModal
          cierre={selectedCierre}
          onClose={() => setDetalleModalOpen(false)}
        />
      )}
    </div>
  );
};
