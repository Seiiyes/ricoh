import { useState, useEffect } from 'react';
import { X, Save, Loader2 } from 'lucide-react';
import type { PrinterDevice } from '@/types';

interface EditPrinterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (printerId: string, updates: any) => Promise<void>;
  printer: PrinterDevice | null;
}

export const EditPrinterModal = ({ isOpen, onClose, onSave, printer }: EditPrinterModalProps) => {
  const [hostname, setHostname] = useState('');
  const [location, setLocation] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (printer) {
      setHostname(printer.hostname);
      setLocation(printer.location || '');
    }
  }, [printer]);

  if (!isOpen || !printer) return null;

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await onSave(printer.id, {
        hostname,
        location: location || null,
      });
      onClose();
    } catch (error) {
      console.error('Error al guardar:', error);
      alert('Error al actualizar la impresora');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <h2 className="text-lg font-bold text-industrial-gray uppercase tracking-tight">
            Editar Impresora
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Hostname */}
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">
              Nombre
            </label>
            <input
              type="text"
              value={hostname}
              onChange={(e) => setHostname(e.target.value)}
              className="w-full border border-slate-300 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red"
              placeholder="Nombre de la impresora"
            />
          </div>

          {/* IP Address (read-only) */}
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">
              Dirección IP
            </label>
            <input
              type="text"
              value={printer.ip_address}
              disabled
              className="w-full border border-slate-300 rounded px-4 py-2 text-sm bg-slate-50 text-slate-500 cursor-not-allowed"
            />
          </div>

          {/* Location */}
          <div>
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">
              Ubicación
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full border border-slate-300 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red"
              placeholder="Ej: Oficina Principal - Piso 2"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-slate-200 bg-slate-50">
          <button
            onClick={onClose}
            className="px-6 py-2 text-sm font-bold text-slate-600 hover:text-slate-800 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || !hostname.trim()}
            className="flex items-center gap-2 bg-ricoh-red text-white px-6 py-2 rounded font-bold text-sm uppercase tracking-wide hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Guardando...
              </>
            ) : (
              <>
                <Save size={16} />
                Guardar
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
