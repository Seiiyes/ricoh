import { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import { Modal, Button, Input, EmpresaAutocomplete } from '@/components/ui';
import type { PrinterDevice } from '@/types';
import { useNotification } from '@/hooks/useNotification';

interface EditPrinterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (printerId: string, updates: any) => Promise<void>;
  printer: PrinterDevice | null;
}

export const EditPrinterModal = ({ isOpen, onClose, onSave, printer }: EditPrinterModalProps) => {
  const notify = useNotification();
  const [hostname, setHostname] = useState('');
  const [location, setLocation] = useState('');
  const [empresa, setEmpresa] = useState('');
  const [empresaId, setEmpresaId] = useState<number | undefined>(undefined);
  const [serialNumber, setSerialNumber] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (printer) {
      setHostname(printer.hostname);
      setLocation(printer.location || '');
      setEmpresa(printer.empresa || '');
      setEmpresaId(printer.empresa_id);
      setSerialNumber(printer.serial_number || '');
    }
  }, [printer]);

  if (!isOpen || !printer) return null;

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await onSave(printer.id, {
        hostname,
        location: location || null,
        empresa_id: empresaId || null,
        serial_number: serialNumber || null,
      });
      notify.success('Impresora actualizada', `Los datos de ${hostname} se guardaron correctamente`);
      onClose();
    } catch (error) {
      console.error('Error al guardar:', error);
      notify.error('Error al actualizar', 'No se pudieron guardar los cambios de la impresora');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Editar Impresora"
      size="md"
    >
      <div className="space-y-4">
        {/* Hostname */}
        <Input
          label="Nombre"
          value={hostname}
          onChange={(e) => setHostname(e.target.value)}
          placeholder="Nombre de la impresora"
        />

        {/* IP Address (read-only) */}
        <Input
          label="Dirección IP"
          value={printer.ip_address}
          disabled
        />

        {/* Location */}
        <Input
          label="Ubicación"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Ej: Oficina Principal - Piso 2"
        />

        {/* Empresa */}
        <EmpresaAutocomplete
          label="Empresa"
          value={empresa}
          onChange={(value, id) => {
            setEmpresa(value);
            setEmpresaId(id);
          }}
          placeholder="Buscar o seleccionar empresa..."
        />

        {/* Serial Number / ID Máquina */}
        <div>
          <Input
            label="ID Máquina (Serial)"
            value={serialNumber}
            onChange={(e) => setSerialNumber(e.target.value)}
            placeholder="Ej: E174M210096"
          />
          <p className="text-xs text-slate-500 mt-1">
            💡 No confundir con el hostname. El ID máquina aparece en la web de la impresora.
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-6 border-t border-slate-200 bg-slate-50 -mx-6 -mb-6 px-6 py-4 rounded-b-lg">
        <Button variant="ghost" onClick={onClose}>
          Cancelar
        </Button>
        <Button
          variant="primary"
          icon={<Save size={16} />}
          onClick={handleSave}
          loading={isSaving}
          disabled={!hostname.trim()}
        >
          Guardar
        </Button>
      </div>
    </Modal>
  );
};
