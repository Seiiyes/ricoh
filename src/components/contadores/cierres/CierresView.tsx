import { useState, useEffect } from 'react';
import { CierreMensual, Printer, TipoPeriodo } from './types';
import { ListaCierres } from './ListaCierres';
import { CierreModal } from './CierreModal';
import { CierreDetalleModal } from './CierreDetalleModal';
import { ComparacionModal } from './ComparacionModal';

const API_BASE = 'http://localhost:8000';

export const CierresView: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedPrinter, setSelectedPrinter] = useState<number | null>(null);
  const [tipoPeriodo, setTipoPeriodo] = useState<TipoPeriodo>('mensual');
  const [printers, setPrinters] = useState<Printer[]>([]);
  const [cierres, setCierres] = useState<CierreMensual[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [cierreModalOpen, setCierreModalOpen] = useState(false);
  const [detalleModalOpen, setDetalleModalOpen] = useState(false);
  const [comparacionModalOpen, setComparacionModalOpen] = useState(false);

  // Selected data
  const [selectedCierre, setSelectedCierre] = useState<CierreMensual | null>(null);
  const [selectedFechaInicio, setSelectedFechaInicio] = useState<string | null>(null);
  const [selectedFechaFin, setSelectedFechaFin] = useState<string | null>(null);

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  // Load printers on mount
  useEffect(() => {
    loadPrinters();
  }, []);

  // Load cierres when filters change
  useEffect(() => {
    if (selectedPrinter) {
      loadCierres();
    }
  }, [selectedPrinter, selectedYear, tipoPeriodo]);

  const loadPrinters = async () => {
    try {
      console.log('Loading printers from:', `${API_BASE}/printers`);
      const response = await fetch(`${API_BASE}/printers`);
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error('Error al cargar impresoras');
      }
      const data = await response.json();
      console.log('Printers loaded:', data);
      setPrinters(data);
      if (data.length > 0 && !selectedPrinter) {
        setSelectedPrinter(data[0].id);
      }
    } catch (err: any) {
      console.error('Error loading printers:', err);
      setError('Error al cargar impresoras');
    }
  };

  const loadCierres = async () => {
    if (!selectedPrinter) return;

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        tipo_periodo: tipoPeriodo,
        year: selectedYear.toString(),
        limit: '1000'
      });

      const url = `${API_BASE}/api/counters/closes/${selectedPrinter}?${params}`;
      console.log('Loading cierres from:', url);

      const response = await fetch(url);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error('Error al cargar cierres');
      }

      const data = await response.json();
      console.log('Cierres loaded:', data);
      setCierres(data);
    } catch (err: any) {
      console.error('Error loading cierres:', err);
      setError(err.message || 'Error al cargar cierres');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCierre = (fechaInicio: string, fechaFin: string) => {
    setSelectedFechaInicio(fechaInicio);
    setSelectedFechaFin(fechaFin);
    setCierreModalOpen(true);
  };

  const handleViewDetalle = (cierre: CierreMensual) => {
    setSelectedCierre(cierre);
    setDetalleModalOpen(true);
  };

  const handleCierreSuccess = () => {
    loadCierres();
    setCierreModalOpen(false);
  };

  const selectedPrinterData = printers.find(p => p.id === selectedPrinter);

  return (
    <div className="p-6 space-y-6">
      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span className="text-sm font-medium text-gray-700">Filtros</span>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Impresora:</label>
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
            <label className="text-sm text-gray-600">Año:</label>
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Tipo:</label>
            <select
              value={tipoPeriodo}
              onChange={(e) => setTipoPeriodo(e.target.value as TipoPeriodo)}
              className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              <option value="mensual">Mensual</option>
              <option value="semanal">Semanal</option>
              <option value="diario">Diario</option>
              <option value="personalizado">Personalizado</option>
            </select>
          </div>

          <button
            onClick={loadCierres}
            disabled={!selectedPrinter || loading}
            className="ml-auto px-4 py-1.5 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Actualizar
          </button>

          <button
            onClick={() => setComparacionModalOpen(true)}
            disabled={!selectedPrinter || cierres.length < 2}
            className="px-4 py-1.5 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Comparar
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* Content */}
      {!selectedPrinter ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <svg className="w-16 h-16 text-blue-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Selecciona una impresora
          </h3>
          <p className="text-gray-600">
            Selecciona una impresora del filtro superior para ver sus cierres
          </p>
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
          tipoPeriodo={tipoPeriodo}
          cierres={cierres}
          onCreateCierre={handleCreateCierre}
          onViewDetalle={handleViewDetalle}
        />
      )}

      {/* Modals */}
      {cierreModalOpen && selectedPrinter && selectedFechaInicio && selectedFechaFin && (
        <CierreModal
          printerId={selectedPrinter}
          tipoPeriodo={tipoPeriodo}
          fechaInicio={selectedFechaInicio}
          fechaFin={selectedFechaFin}
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

      {comparacionModalOpen && selectedPrinter && (
        <ComparacionModal
          printerId={selectedPrinter}
          cierres={cierres}
          onClose={() => setComparacionModalOpen(false)}
        />
      )}
    </div>
  );
};
