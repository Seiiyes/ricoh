import { useState } from 'react';
import { TipoPeriodo } from './types';

const API_BASE = 'http://localhost:8000';

interface CierreModalProps {
  printerId: number;
  tipoPeriodo: TipoPeriodo;
  fechaInicio: string;
  fechaFin: string;
  onClose: () => void;
  onSuccess: () => void;
}

export const CierreModal: React.FC<CierreModalProps> = ({
  printerId,
  tipoPeriodo,
  fechaInicio,
  fechaFin,
  onClose,
  onSuccess
}) => {
  const [cerradoPor, setCerradoPor] = useState('admin');
  const [notas, setNotas] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/counters/close`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          printer_id: printerId,
          tipo_periodo: tipoPeriodo,
          fecha_inicio: fechaInicio,
          fecha_fin: fechaFin,
          cerrado_por: cerradoPor || undefined,
          notas: notas || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al crear cierre');
      }

      const data = await response.json();
      console.log('Cierre creado:', data);
      onSuccess();
    } catch (err: any) {
      console.error('Error creating cierre:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Crear Cierre {tipoPeriodo.charAt(0).toUpperCase() + tipoPeriodo.slice(1)}
              </h2>
              <p className="text-sm text-gray-600">
                {formatDate(fechaInicio)}
                {fechaInicio !== fechaFin && <> - {formatDate(fechaFin)}</>}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Warning */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
            <svg className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-yellow-800">
                Importante: El cierre es irreversible
              </p>
              <p className="text-sm text-yellow-700 mt-1">
                Una vez creado el cierre, se guardará un snapshot inmutable de todos los contadores y usuarios.
                Esta operación no se puede deshacer.
              </p>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm font-medium text-red-800">Error al crear cierre</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Información del período */}
          <div className="bg-gray-50 rounded-lg p-4 space-y-3">
            <h3 className="text-sm font-semibold text-gray-900">Información del Período</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Tipo:</span>
                <span className="ml-2 font-medium text-gray-900 capitalize">{tipoPeriodo}</span>
              </div>
              <div>
                <span className="text-gray-600">Impresora:</span>
                <span className="ml-2 font-medium text-gray-900">ID {printerId}</span>
              </div>
              <div>
                <span className="text-gray-600">Fecha inicio:</span>
                <span className="ml-2 font-medium text-gray-900">{formatDate(fechaInicio)}</span>
              </div>
              <div>
                <span className="text-gray-600">Fecha fin:</span>
                <span className="ml-2 font-medium text-gray-900">{formatDate(fechaFin)}</span>
              </div>
            </div>
          </div>

          {/* Form fields */}
          <div className="space-y-4">
            <div>
              <label htmlFor="cerradoPor" className="block text-sm font-medium text-gray-700 mb-1">
                Cerrado por
              </label>
              <input
                type="text"
                id="cerradoPor"
                value={cerradoPor}
                onChange={(e) => setCerradoPor(e.target.value)}
                maxLength={100}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                placeholder="Nombre del usuario"
              />
              <p className="mt-1 text-xs text-gray-500">
                Opcional. Nombre del usuario que realiza el cierre.
              </p>
            </div>

            <div>
              <label htmlFor="notas" className="block text-sm font-medium text-gray-700 mb-1">
                Notas
              </label>
              <textarea
                id="notas"
                value={notas}
                onChange={(e) => setNotas(e.target.value)}
                maxLength={1000}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                placeholder="Notas adicionales sobre este cierre (opcional)"
              />
              <p className="mt-1 text-xs text-gray-500">
                {notas.length}/1000 caracteres
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Creando...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <span>Crear Cierre</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
