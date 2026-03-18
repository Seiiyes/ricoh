import { useState } from 'react';
import { Modal, Button, Input, Alert } from '@/components/ui';
import { Lock, AlertTriangle } from 'lucide-react';

interface CierreModalProps {
  printerId: number;
  printerName?: string;
  onClose: () => void;
  onSuccess: () => void;
}

const API_BASE = 'http://localhost:8000';

export const CierreModal: React.FC<CierreModalProps> = ({ printerId, printerName, onClose, onSuccess }) => {
  // Generar fecha actual en formato local YYYY-MM-DD
  const getLocalDate = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const hoyStr = getLocalDate();
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          printer_id: printerId,
          fecha_inicio: hoyStr,
          fecha_fin: hoyStr,
          cerrado_por: cerradoPor,
          notas: notas,
          tipo_periodo: 'personalizado'
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Error al crear el cierre');
      }

      onSuccess();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Crear Cierre"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
          
          {/* Fecha del Cierre - Estática */}
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
            <label className="block text-xs font-bold text-blue-500 uppercase tracking-wider mb-1">
              Fecha del Snapshot (Hoy)
            </label>
            <p className="text-lg font-bold text-blue-900">
              {new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric' })}
            </p>
            <p className="text-[10px] text-blue-600 mt-1">Los contadores se capturarán con fecha de hoy.</p>
          </div>

          {/* Cerrado por */}
          <Input
            label="Cerrado por (opcional)"
            type="text"
            value={cerradoPor}
            onChange={(e) => setCerradoPor(e.target.value)}
            placeholder="Nombre del responsable"
          />

          {/* Notas */}
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
              Notas <span className="text-gray-400 font-normal">(opcional)</span>
            </label>
            <textarea
              value={notas}
              onChange={(e) => setNotas(e.target.value)}
              placeholder="Ej: Cierre de quincena marzo 2026"
              rows={3}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent bg-gray-50/30 resize-none"
            />
          </div>

          {error && (
            <Alert variant="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Alert variant="warning">
            El cierre captura un <strong>snapshot</strong> de los contadores de la impresora y todos sus usuarios al momento actual.
          </Alert>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="primary"
              loading={loading}
              disabled={loading}
            >
              {loading ? 'Procesando...' : 'Crear Cierre de Hoy'}
            </Button>
          </div>
        </form>
      </Modal>
    );
};
