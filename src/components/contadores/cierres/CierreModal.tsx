import { useState, useEffect } from 'react';
import { Modal, Button, Input, Alert } from '@/components/ui';
import { Lock, AlertTriangle } from 'lucide-react';
import closeService from '@/services/closeService';
import { useAuth } from '@/contexts/AuthContext';

interface CierreModalProps {
  printerId: number;
  printerName?: string;
  onClose: () => void;
  onSuccess: () => void;
}

export const CierreModal: React.FC<CierreModalProps> = ({ printerId, printerName, onClose, onSuccess }) => {
  const { user } = useAuth();
  
  // Generar fecha actual en formato local YYYY-MM-DD
  const getLocalDate = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const hoyStr = getLocalDate();
  const [cerradoPor, setCerradoPor] = useState('');
  const [notas, setNotas] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Establecer el usuario actual automáticamente
  useEffect(() => {
    if (user) {
      setCerradoPor(user.nombre_completo || user.username);
    }
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Usar la fecha de HOY como período de un solo día
      const hoy = getLocalDate();

      await closeService.createClose({
        printer_id: printerId,
        tipo_periodo: 'diario',
        fecha_inicio: hoy,
        fecha_fin: hoy,
        cerrado_por: cerradoPor || undefined,
        notas: notas || undefined
      });

      onSuccess();
    } catch (err: any) {
      console.error('Error al crear cierre:', err);
      
      // Manejar diferentes tipos de errores
      let errorMessage = 'Error al crear el cierre';
      
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        
        // Si detail es un array de errores de validación (422)
        if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => {
            if (typeof e === 'object' && e.msg) {
              return `${e.loc ? e.loc.join('.') + ': ' : ''}${e.msg}`;
            }
            return String(e);
          }).join(', ');
        } 
        // Si detail es un string
        else if (typeof detail === 'string') {
          errorMessage = detail;
        }
        // Si detail es un objeto con message
        else if (typeof detail === 'object' && detail.message) {
          errorMessage = detail.message;
        }
        // Cualquier otro caso
        else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
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
