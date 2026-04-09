import { useState } from 'react';
import { Modal, Button, Alert } from '@/components/ui';
import { Printer, FileText } from 'lucide-react';
import closeService from '@/services/closeService';
import { useAuth } from '@/contexts/AuthContext';

interface CierreModalProps {
  printerId: number;
  printerName?: string;
  fechaInicio?: string; // YYYY-MM-DD opcional
  fechaFin?: string; // YYYY-MM-DD opcional
  onClose: () => void;
  onSuccess: () => void;
}

export const CierreModal: React.FC<CierreModalProps> = ({ printerId, printerName, fechaInicio, fechaFin, onClose, onSuccess }) => {
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
  // Usar las fechas proporcionadas o la fecha de hoy por defecto
  const [fechaInicioState] = useState(fechaInicio || hoyStr);
  const [fechaFinState] = useState(fechaFin || hoyStr);
  const [notas, setNotas] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Obtener nombre del usuario automáticamente
  const nombreUsuario = user?.nombre_completo || user?.username || 'Usuario';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Usar las fechas del estado (que pueden venir de props o ser hoy)
      await closeService.createClose({
        printer_id: printerId,
        tipo_periodo: 'diario',
        fecha_inicio: fechaInicioState,
        fecha_fin: fechaFinState,
        cerrado_por: nombreUsuario,
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
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <Alert variant="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Información del cierre */}
        <div className="bg-slate-50 rounded-lg p-6 space-y-4">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Fecha del Cierre
              </label>
              <div className="px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-900 font-bold">
                {new Date(fechaInicioState + 'T00:00:00').toLocaleDateString('es-ES', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
                {fechaInicioState !== fechaFinState && (
                  <> → {new Date(fechaFinState + 'T00:00:00').toLocaleDateString('es-ES', { 
                    day: 'numeric', 
                    month: 'long', 
                    year: 'numeric' 
                  })}</>
                )}
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
              Cierre {fechaInicioState === fechaFinState ? 'Diario' : 'Personalizado'}
            </div>
          </div>
        </div>

        {/* Notas */}
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

        <Alert variant="warning">
          El cierre captura un <strong>snapshot</strong> de los contadores de la impresora y todos sus usuarios al momento actual.
        </Alert>

        {/* Footer Actions */}
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
            Crear Cierre
          </Button>
        </div>
      </form>
      </Modal>
    );
};
