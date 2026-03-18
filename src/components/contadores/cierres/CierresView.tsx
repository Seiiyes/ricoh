import { useState, useEffect } from 'react';
import { CierreMensual, Printer } from './types';
import { ListaCierres } from './ListaCierres';
import { CierreModal } from './CierreModal';
import { CierreDetalleModal } from './CierreDetalleModal';
import { ComparacionPage } from './ComparacionPage';
import { Button, Spinner, Alert } from '@/components/ui';
import { RefreshCw, Plus, BarChart3 } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

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
      const response = await fetch(`${API_BASE}/printers`);
      if (!response.ok) throw new Error('Error al cargar impresoras');
      const data = await response.json();
      setPrinters(data);
      if (data.length > 0 && !selectedPrinter) setSelectedPrinter(data[0].id);
    } catch {
      setError('Error al cargar impresoras');
    }
  };

  const loadCierres = async () => {
    if (!selectedPrinter) return;
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ year: selectedYear.toString(), limit: '500' });
      const response = await fetch(`${API_BASE}/api/counters/monthly/${selectedPrinter}?${params}`);
      if (!response.ok) throw new Error('Error al cargar cierres');
      const data = await response.json();
      setCierres(data);
    } catch (err: any) {
      setError(err.message || 'Error al cargar cierres');
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
    <div className="p-6 space-y-6">

      {/* Barra de filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-3">

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600 font-medium">Impresora:</label>
            <select
              value={selectedPrinter || ''}
              onChange={(e) => setSelectedPrinter(e.target.value ? Number(e.target.value) : null)}
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="">Seleccionar...</option>
              {printers.map(printer => (
                <option key={printer.id} value={printer.id}>
                  {printer.hostname} ({printer.ip_address})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600 font-medium">Año:</label>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              {years.map(year => <option key={year} value={year}>{year}</option>)}
            </select>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={loadCierres}
            loading={loading}
            disabled={!selectedPrinter}
            icon={<RefreshCw size={16} />}
          >
            Actualizar
          </Button>

          <div className="flex-1" />

          {cierres.length >= 2 && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setVistaActual('comparacion')}
              icon={<BarChart3 size={16} />}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              Comparar cierres ({cierres.length})
            </Button>
          )}

          <Button
            size="sm"
            onClick={() => setCierreModalOpen(true)}
            disabled={!selectedPrinter}
            icon={<Plus size={16} />}
          >
            Crear Cierre
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!selectedPrinter ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <p className="text-gray-600">Selecciona una impresora para ver sus cierres</p>
        </div>
      ) : loading ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <Spinner size="lg" text="Cargando cierres..." />
        </div>
      ) : (
        <ListaCierres
          printer={selectedPrinterData!}
          year={selectedYear}
          tipoPeriodo="personalizado"
          cierres={cierres}
          onCreateCierre={() => setCierreModalOpen(true)}
          onViewDetalle={(cierre) => { setSelectedCierre(cierre); setDetalleModalOpen(true); }}
        />
      )}

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
