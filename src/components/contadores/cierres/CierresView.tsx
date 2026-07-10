import { useState, useEffect } from 'react';
import { CierreMensual, Printer, ComparacionGuardada } from './types';
import { ListaCierres } from './ListaCierres';
import { CierreModal } from './CierreModal';
import { CierreDetalleModal } from './CierreDetalleModal';
import { ComparacionPage } from './ComparacionPage';
import { Button, Spinner, Alert } from '@/components/ui';
import { RefreshCw, BarChart3, Filter, SlidersHorizontal, Calculator, Printer as PrinterIcon, ChevronDown, ChevronUp, Trash2, FileText, ChevronRight } from 'lucide-react';
import closeService from '@/services/closeService';
import apiClient from '@/services/apiClient';
import { parseApiError } from '@/utils/errorHandler';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { useNotification } from '@/hooks/useNotification';

export const CierresView: React.FC = () => {
  const { user: _user } = useAuth();
  const notify = useNotification();
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedPrinter, setSelectedPrinter] = useState<number | null>(null);
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [cierres, setCierres] = useState<CierreMensual[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Historial de comparaciones
  const [savedComparaciones, setSavedComparaciones] = useState<ComparacionGuardada[]>([]);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [comparacionInicial, setComparacionInicial] = useState<{ c1: number; c2: number } | null>(null);

  // Sub-vista
  const [vistaActual, setVistaActual] = useState<'lista' | 'comparacion'>('lista');

  // Modals
  const [cierreModalOpen, setCierreModalOpen] = useState(false);
  const [cierreModalFechas, setCierreModalFechas] = useState<{ inicio: string; fin: string } | null>(null);
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

  const handleCierreSuccess = () => { loadCierres(); setCierreModalOpen(false); setCierreModalFechas(null); };
  const selectedPrinterData = printers.find(p => p.id === selectedPrinter);

  const handleCreateCierre = (fechaInicio: string, fechaFin: string) => {
    setCierreModalFechas({ inicio: fechaInicio, fin: fechaFin });
    setCierreModalOpen(true);
  };

  const handleDeleteCierre = async (cierreId: number) => {
    try {
      await closeService.deleteMonthlyClose(cierreId);
      notify.success('Cierre de contadores eliminado correctamente.');
      loadCierres();
    } catch (err: any) {
      console.error('Error al eliminar cierre:', err);
      notify.error(parseApiError(err, 'Error al eliminar el cierre'));
    }
  };

  const loadSavedComparaciones = async () => {
    setLoadingHistory(true);
    try {
      const data = await closeService.getComparacionesGuardadas();
      setSavedComparaciones(data);
    } catch (err) {
      console.error('Error al cargar comparaciones guardadas:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleDeleteSavedComparacion = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta comparación guardada?')) return;
    try {
      await closeService.deleteComparacion(id);
      notify.success('Comparación eliminada', 'La comparación ha sido eliminada correctamente');
      loadSavedComparaciones();
    } catch (err: any) {
      console.error('Error al eliminar comparación:', err);
      notify.error('Error al eliminar', parseApiError(err, 'No se pudo eliminar la comparación'));
    }
  };

  const handleCargarComparacion = (c1: number, c2: number) => {
    setComparacionInicial({ c1, c2 });
    setVistaActual('comparacion');
  };

  const handleVolverLista = () => {
    setComparacionInicial(null);
    setVistaActual('lista');
  };

  useEffect(() => {
    if (vistaActual === 'lista') {
      loadSavedComparaciones();
    }
  }, [vistaActual]);

  // Si estamos en modo comparación, mostrar la sub-vista completa
  if (vistaActual === 'comparacion') {
    return (
      <ComparacionPage
        cierres={cierres}
        onVolver={handleVolverLista}
        initialCierre1Id={comparacionInicial?.c1}
        initialCierre2Id={comparacionInicial?.c2}
      />
    );
  }

  return (
    <div className="space-y-6 lg:space-y-10 animate-fade-in">
      {/* Barra de filtros Premium */}
      <div className="bg-white/70 backdrop-blur-md rounded-3xl border border-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] card-padding">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-responsive">
          <div className="flex flex-wrap items-end gap-responsive-sm flex-1">
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
 
          <div className="flex items-center gap-responsive-sm">
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
              Cierre Individual
            </Button>
          </div>
        </div>
      </div>
 
      {error && (
        <Alert variant="error" onClose={() => setError(null)} className="rounded-2xl border-none shadow-lg">
          {error}
        </Alert>
      )}

      {/* Historial de Comparaciones Guardadas Accordion */}
      <div className="bg-white/60 backdrop-blur-md rounded-3xl border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.02)] overflow-hidden transition-all duration-300">
        <button
          onClick={() => setIsHistoryOpen(!isHistoryOpen)}
          className="w-full px-8 py-5 flex items-center justify-between text-left hover:bg-slate-50/50 transition-colors focus:outline-none"
        >
          <div className="flex items-center gap-4">
            <div className="w-9 h-9 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 shadow-sm shadow-indigo-100">
              <BarChart3 size={18} />
            </div>
            <div>
              <h3 className="font-bold text-slate-800 text-sm">Comparaciones Guardadas</h3>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-0.5">Historial de reportes y análisis guardados ({savedComparaciones.length})</p>
            </div>
          </div>
          <div className="text-slate-400">
            {isHistoryOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
        </button>
        
        {isHistoryOpen && (
          <div className="px-8 pb-6 border-t border-slate-50/50 pt-4 divide-y divide-slate-100 max-h-80 overflow-y-auto animate-slide-down">
            {loadingHistory ? (
              <div className="py-8 flex justify-center items-center">
                <Spinner size="sm" text="Cargando comparaciones..." />
              </div>
            ) : savedComparaciones.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-400 font-medium">
                No hay comparaciones guardadas en este momento.
              </div>
            ) : (
              savedComparaciones.map((comp) => (
                <div
                  key={comp.id}
                  onClick={() => handleCargarComparacion(comp.cierre1_id, comp.cierre2_id)}
                  className="py-4 flex items-center justify-between hover:bg-slate-50/30 -mx-4 px-4 rounded-2xl cursor-pointer transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-500 transition-colors">
                      <FileText size={18} />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-700 group-hover:text-indigo-600 transition-colors">{comp.titulo}</h4>
                      {comp.descripcion && <p className="text-[10px] text-slate-400 mt-0.5 max-w-md truncate">{comp.descripcion}</p>}
                      <div className="flex items-center gap-2 mt-1 text-[9px] font-bold text-slate-400 uppercase tracking-wider">
                        <span>Creado por: {comp.creado_por || 'Sistema'}</span>
                        <span>•</span>
                        <span>{new Date(comp.created_at).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => handleDeleteSavedComparacion(comp.id, e)}
                      icon={<Trash2 size={14} />}
                      className="h-8 w-8 p-0 rounded-xl text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                      title="Eliminar comparación"
                    />
                    <ChevronRight size={16} className="text-slate-300 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all" />
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

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
              onCreateCierre={handleCreateCierre}
              onViewDetalle={(cierre) => { setSelectedCierre(cierre); setDetalleModalOpen(true); }}
              onDeleteCierre={handleDeleteCierre}
            />
          </div>
        )}
      </div>
 
      {cierreModalOpen && selectedPrinter && (
        <CierreModal
          printerId={selectedPrinter}
          printerName={selectedPrinterData?.hostname}
          fechaInicio={cierreModalFechas?.inicio}
          fechaFin={cierreModalFechas?.fin}
          onClose={() => { setCierreModalOpen(false); setCierreModalFechas(null); }}
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
