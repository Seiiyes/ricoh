import { useState } from 'react';
import { Modal, Button, Alert } from '@/components/ui';
import { Printer, CheckCircle, XCircle, FileText } from 'lucide-react';
import closeService from '@/services/closeService';
import { parseApiError } from '@/utils/errorHandler';
import { useAuth } from '@/contexts/AuthContext';

interface CierreMasivoModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

interface CierreResult {
  printer_id: number;
  printer_name: string;
  success: boolean;
  cierre_id?: number;
  total_paginas: number;
  usuarios_count: number;
  error?: string;
}

export const CierreMasivoModal: React.FC<CierreMasivoModalProps> = ({ onClose, onSuccess }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<CierreResult[] | null>(null);
  const [summary, setSummary] = useState<{ successful: number; failed: number; total: number } | null>(null);

  const [notas, setNotas] = useState('');

  // Fecha actual
  const fechaActual = new Date().toISOString().split('T')[0];
  const nombreUsuario = user?.name || user?.username || 'Usuario';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    setSummary(null);

    try {
      const response = await closeService.createCloseAllPrinters({
        tipo_periodo: 'diario',
        fecha_inicio: fechaActual,
        fecha_fin: fechaActual,
        cerrado_por: nombreUsuario,
        notas: notas || undefined
      });

      setResults(response.results);
      setSummary({
        successful: response.successful,
        failed: response.failed,
        total: response.total
      });

      if (response.successful > 0) {
        onSuccess();
      }
    } catch (err: any) {
      console.error('Error al crear cierres masivos:', err);
      setError(parseApiError(err, 'Error al crear cierres masivos'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Crear Cierre Diario en Todas las Impresoras"
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <Alert variant="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {!results ? (
          <>
            {/* Información del cierre */}
            <div className="bg-slate-50 rounded-lg p-6 space-y-4">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Fecha del Cierre
                  </label>
                  <div className="px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-900 font-bold">
                    {new Date(fechaActual).toLocaleDateString('es-ES', { 
                      weekday: 'long', 
                      year: 'numeric', 
                      month: 'long', 
                      day: 'numeric' 
                    })}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Realizado Por
                  </label>
                  <div className="px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-900 font-bold">
                    {nombreUsuario}
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Tipo de Cierre
                </label>
                <div className="px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-900 font-bold">
                  Cierre Diario
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <FileText className="inline mr-2" size={16} />
                Notas (Opcional)
              </label>
              <textarea
                value={notas}
                onChange={(e) => setNotas(e.target.value)}
                placeholder="Notas adicionales sobre este cierre..."
                rows={3}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-ricoh-red focus:border-transparent"
                maxLength={1000}
              />
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-sm text-yellow-800">
                <strong>⚠️ Advertencia:</strong> Esta acción creará un cierre diario en TODAS las impresoras activas a las que tienes acceso.
                Los contadores se leerán automáticamente antes de crear los cierres.
              </p>
              <p className="text-sm text-yellow-800 mt-2">
                <strong>Nota:</strong> Si ya existe un cierre diario para hoy en alguna impresora, esa impresora será omitida.
              </p>
            </div>

            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                variant="primary"
                loading={loading}
                icon={<Printer size={18} />}
              >
                Crear Cierres en Todas las Impresoras
              </Button>
            </div>
          </>
        ) : (
          <>
            {/* Resultados */}
            <div className="space-y-4">
              {summary && (
                <div className="bg-slate-50 rounded-lg p-6">
                  <h3 className="text-lg font-bold text-slate-900 mb-4">Resumen de Operación</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-slate-900">{summary.total}</div>
                      <div className="text-sm text-slate-600">Total</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">{summary.successful}</div>
                      <div className="text-sm text-slate-600">Exitosos</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-red-600">{summary.failed}</div>
                      <div className="text-sm text-slate-600">Fallidos</div>
                    </div>
                  </div>
                </div>
              )}

              <div className="max-h-96 overflow-y-auto space-y-2">
                {results.map((result, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border ${
                      result.success
                        ? 'bg-green-50 border-green-200'
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        {result.success ? (
                          <CheckCircle className="text-green-600 mt-1" size={20} />
                        ) : (
                          <XCircle className="text-red-600 mt-1" size={20} />
                        )}
                        <div>
                          <div className="font-bold text-slate-900">{result.printer_name}</div>
                          <div className="text-sm text-slate-600">ID: {result.printer_id}</div>
                          {result.success && (
                            <div className="text-sm text-slate-600 mt-1">
                              {result.total_paginas.toLocaleString()} páginas • {result.usuarios_count} usuarios
                            </div>
                          )}
                          {result.error && (
                            <div className="text-sm text-red-600 mt-1">{result.error}</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                type="button"
                variant="primary"
                onClick={onClose}
              >
                Cerrar
              </Button>
            </div>
          </>
        )}
      </form>
    </Modal>
  );
};
