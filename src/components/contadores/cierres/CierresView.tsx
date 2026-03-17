import { useState, useEffect } from 'react';
import { CierreMensual, Printer } from './types';
import { ListaCierres } from './ListaCierres';
import { CierreModal } from './CierreModal';
import { CierreDetalleModal } from './CierreDetalleModal';
import { ComparacionPage } from './ComparacionPage';

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

          <button
            onClick={loadCierres}
            disabled={!selectedPrinter || loading}
            className="px-3 py-1.5 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-1.5 disabled:opacity-40"
          >
            <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Actualizar
          </button>

          <div className="flex-1" />

          {cierres.length >= 2 && (
            <button
              onClick={() => setVistaActual('comparacion')}
              className="px-4 py-1.5 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Comparar cierres ({cierres.length})
            </button>
          )}

          <button
            onClick={() => setCierreModalOpen(true)}
            disabled={!selectedPrinter}
            className="px-5 py-1.5 bg-red-600 text-white rounded-md text-sm font-bold hover:bg-red-700 transition-colors flex items-center gap-2 disabled:opacity-40"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Crear Cierre
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">{error}</div>
      )}

      {!selectedPrinter ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <p className="text-gray-600">Selecciona una impresora para ver sus cierres</p>
        </div>
      ) : loading ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Cargando cierres...</p>
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
