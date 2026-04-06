import { useState } from 'react';
import { X, Wifi, AlertCircle, Loader2, Plus, Minus, Search, Trash2, MapPin, Printer } from 'lucide-react';
import { scanPrinters, registerDiscoveredPrinters } from '@/services/printerService';
import { Modal, Button, Input, Spinner } from '@/components/ui';
import discoveryService from '@/services/discoveryService';
import { useNotification } from '@/hooks/useNotification';
import { cn } from '@/lib/utils';

interface DiscoveredDevice {
  hostname: string;
  ip_address: string;
  status: string;
  detected_model: string;
  has_color: boolean;
  has_scanner: boolean;
  has_fax: boolean;
  toner_cyan: number;
  toner_magenta: number;
  toner_yellow: number;
  toner_black: number;
  location?: string;
}

interface EditableDevice extends DiscoveredDevice {
  editedHostname?: string;
  editedLocation?: string;
}

interface DiscoveryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

export const DiscoveryModal = ({ isOpen, onClose, onComplete }: DiscoveryModalProps) => {
  const notify = useNotification();
  const [ipRange, setIpRange] = useState('192.168.91.0/24');
  const [isScanning, setIsScanning] = useState(false);
  const [discoveredDevices, setDiscoveredDevices] = useState<EditableDevice[]>([]);
  const [selectedDevices, setSelectedDevices] = useState<Set<string>>(new Set());
  const [scanComplete, setScanComplete] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  
  // Manual add state
  const [showManualAdd, setShowManualAdd] = useState(false);
  const [manualIP, setManualIP] = useState('');
  const [manualPort, setManualPort] = useState('161');
  const [isCheckingManual, setIsCheckingManual] = useState(false);

  if (!isOpen) return null;

  const handleScan = async () => {
    try {
      setIsScanning(true);
      setScanComplete(false);
      setDiscoveredDevices([]);
      setSelectedDevices(new Set());
      
      const devices = await scanPrinters(ipRange);
      const editableDevices: EditableDevice[] = devices.map(d => ({
        ...d,
        editedHostname: d.hostname,
        editedLocation: d.location || ''
      }));
      setDiscoveredDevices(editableDevices);
      setScanComplete(true);
    } catch (error) {
      console.error('Escaneo fallido:', error);
      notify.error('Error en el escaneo', 'No se pudo completar el escaneo de red. Verifica el rango de IP e intenta nuevamente');
    } finally {
      setIsScanning(false);
    }
  };

  const toggleDevice = (ip: string) => {
    const newSelected = new Set(selectedDevices);
    if (newSelected.has(ip)) {
      newSelected.delete(ip);
    } else {
      newSelected.add(ip);
    }
    setSelectedDevices(newSelected);
  };

  const updateDeviceField = (ip: string, field: 'editedHostname' | 'editedLocation', value: string) => {
    setDiscoveredDevices(devices =>
      devices.map(d =>
        d.ip_address === ip ? { ...d, [field]: value } : d
      )
    );
  };

  const handleRegister = async () => {
    if (selectedDevices.size === 0) {
      notify.warning('Selecciona dispositivos', 'Debes seleccionar al menos una impresora para registrar');
      return;
    }

    try {
      setIsRegistering(true);
      const devicesToRegister = discoveredDevices
        .filter(d => selectedDevices.has(d.ip_address))
        .map(d => ({
          ...d,
          hostname: d.editedHostname || d.hostname,
          location: d.editedLocation || d.location
        }));
      
      await registerDiscoveredPrinters(devicesToRegister);
      notify.success(
        'Equipos guardados', 
        `${devicesToRegister.length} ${devicesToRegister.length === 1 ? 'equipo guardado' : 'equipos guardados'} exitosamente`
      );
      onComplete();
      onClose();
    } catch (error) {
      console.error('Registro fallido:', error);
      notify.error('Error al registrar', 'No se pudieron registrar las impresoras. Algunas pueden estar duplicadas');
    } finally {
      setIsRegistering(false);
    }
  };

  const handleManualAdd = async () => {
    if (!manualIP) {
      notify.warning('Ingresa una IP', 'Debes ingresar una dirección IP válida');
      return;
    }

    try {
      setIsCheckingManual(true);
      
      // Llamar al endpoint de escaneo con una sola IP
      const response = await discoveryService.checkPrinter(manualIP);

      if (!response.success || !response.printer) {
        notify.error('No se pudo verificar', response.message || 'La impresora no responde o no es accesible');
        return;
      }

      const device = response.printer;
      
      // Agregar a la lista de dispositivos descubiertos
      const editableDevice: EditableDevice = {
        ...device,
        status: 'online',
        toner_cyan: 0,
        toner_magenta: 0,
        toner_yellow: 0,
        toner_black: 0,
        editedHostname: device.hostname,
        editedLocation: ''
      };
      
      setDiscoveredDevices(prev => [...prev, editableDevice]);
      setSelectedDevices(prev => new Set([...prev, device.ip]));
      setScanComplete(true);
      setShowManualAdd(false);
      setManualIP('');
      setManualPort('161');
      notify.success('Impresora agregada', `${device.hostname} se agregó correctamente al sistema`);
      
    } catch (error) {
      console.error('Error agregando impresora manual:', error);
      notify.error('Error de conexión', 'No se pudo conectar con la impresora. Verifica la dirección IP y el puerto SNMP');
    } finally {
      setIsCheckingManual(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Búsqueda de Equipos"
      size="xl"
    >
      <div className="space-y-6">
      <div className="space-y-8">
          {/* Scan Controls */}
          <div className="bg-slate-50/50 p-6 rounded-2xl border border-slate-100 flex flex-col gap-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="p-1.5 bg-ricoh-red/10 rounded-lg text-ricoh-red">
                <Search size={16} />
              </div>
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Rango de Escaneo</h3>
            </div>
            
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <Input
                  variant="underline"
                  type="text"
                  value={ipRange}
                  onChange={(e) => setIpRange(e.target.value)}
                  placeholder="192.168.91.0/24"
                  disabled={isScanning}
                  className="font-mono text-slate-600 pb-3"
                  label="Notación CIDR"
                />
              </div>
              <Button
                variant="primary"
                size="lg"
                icon={isScanning ? <Loader2 size={18} className="animate-spin" /> : <Wifi size={18} />}
                loading={isScanning}
                disabled={isScanning}
                onClick={handleScan}
                className="px-8 shadow-lg shadow-red-500/20 bg-ricoh-red hover:bg-red-700"
              >
                {isScanning ? 'Buscando...' : 'Iniciar Búsqueda'}
              </Button>
            </div>
          </div>
            
            {/* Manual Add Button */}
            <div className="flex justify-center">
              <button
                onClick={() => setShowManualAdd(!showManualAdd)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 text-xs font-black uppercase tracking-widest transition-all rounded-full border",
                  showManualAdd 
                    ? "bg-slate-800 text-white border-slate-800" 
                    : "text-slate-500 hover:text-ricoh-red border-slate-200 hover:border-ricoh-red bg-white"
                )}
              >
                {showManualAdd ? <Minus size={14} /> : <Plus size={14} />}
                {showManualAdd ? 'Ocultar Manual' : 'Ingresar IP Manual'}
              </button>
            </div>

            {/* Manual Add Form */}
            {showManualAdd && (
              <div className="mt-2 p-6 bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl animate-fade-in">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center text-blue-400">
                    <Plus size={18} />
                  </div>
                  <h3 className="text-xs font-black text-white uppercase tracking-widest">Entrada Manual</h3>
                </div>
                
                <div className="grid grid-cols-2 gap-6 mb-6">
                  <Input
                    variant="underline"
                    label="Dirección IP"
                    type="text"
                    value={manualIP}
                    onChange={(e) => setManualIP(e.target.value)}
                    placeholder="192.168.1.100"
                    disabled={isCheckingManual}
                    className="text-slate-300 font-mono"
                  />
                  <Input
                    variant="underline"
                    label="Puerto SNMP"
                    type="text"
                    value={manualPort}
                    onChange={(e) => setManualPort(e.target.value)}
                    placeholder="161"
                    disabled={isCheckingManual}
                    className="text-slate-300 font-mono"
                  />
                </div>
                
                <Button
                  variant="primary"
                  icon={isCheckingManual ? <Loader2 size={16} className="animate-spin" /> : <Printer size={16} />}
                  loading={isCheckingManual}
                  disabled={isCheckingManual || !manualIP}
                  onClick={handleManualAdd}
                  className="w-full py-4 tracking-widest uppercase text-[10px] bg-blue-600 hover:bg-blue-700"
                >
                  {isCheckingManual ? 'Verificando con SNMP...' : 'Verificar e Incluir'}
                </Button>
              </div>
            )}
          </div>

          {/* Results */}
          {isScanning && (
            <div className="flex flex-col items-center justify-center py-12">
              <Spinner size="lg" text="Buscando equipos en la red..." />
            </div>
          )}

          {scanComplete && discoveredDevices.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <AlertCircle size={48} className="mb-4" />
              <p className="text-sm">No se encontraron equipos en el rango especificado</p>
            </div>
          )}

          {discoveredDevices.length > 0 && (
            <div className="animate-fade-in">
              <div className="flex items-center justify-between mb-6 px-2">
                <div className="flex items-center gap-3">
                   <div className="px-3 py-1 bg-red-50 rounded-full border border-red-100">
                    <p className="text-[10px] font-black text-ricoh-red uppercase tracking-tight">
                      {discoveredDevices.length} Equipos encontrados
                    </p>
                  </div>
                </div>
                <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                  {selectedDevices.size} Seleccionadas
                </div>
              </div>
              <div className="space-y-4 max-h-[50vh] overflow-y-auto pr-2 custom-scrollbar">
                {discoveredDevices.map((device) => (
                  <div
                    key={device.ip_address}
                    className={cn(
                      "group relative border rounded-2xl p-6 transition-all duration-300",
                      selectedDevices.has(device.ip_address)
                        ? 'border-ricoh-red bg-red-50/50 shadow-lg shadow-red-500/5'
                        : 'border-slate-100 hover:border-slate-300 hover:bg-slate-50 shadow-sm'
                    )}
                  >
                    <div className="flex items-start gap-6">
                      {/* Checkbox */}
                      <div className="pt-1">
                        <label className="relative flex items-center justify-center w-6 h-6 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={selectedDevices.has(device.ip_address)}
                            onChange={() => toggleDevice(device.ip_address)}
                            className="sr-only"
                          />
                          <div className={cn(
                            "w-6 h-6 rounded-lg border-2 flex items-center justify-center transition-all",
                            selectedDevices.has(device.ip_address)
                              ? "bg-ricoh-red border-ricoh-red"
                              : "border-slate-300 group-hover:border-slate-400 bg-white"
                          )}>
                            {selectedDevices.has(device.ip_address) && (
                              <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="4">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                          </div>
                        </label>
                      </div>
                      
                      {/* Device Info */}
                      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                          <Input
                            variant="underline"
                            label="Nombre de Red"
                            type="text"
                            value={device.editedHostname || device.hostname}
                            onChange={(e) => updateDeviceField(device.ip_address, 'editedHostname', e.target.value)}
                            placeholder="Nombre dispositivo"
                            className="font-bold text-slate-800"
                          />
                          
                          <div className="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-100/50 px-2.5 py-1 rounded-md w-fit">
                            <span className="w-1.5 h-1.5 bg-slate-400 rounded-full"></span>
                            IP: {device.ip_address}
                          </div>
                        </div>
 
                        <div className="space-y-4">
                          <Input
                            variant="underline"
                            label="Ubicación Física"
                            type="text"
                            value={device.editedLocation || ''}
                            onChange={(e) => updateDeviceField(device.ip_address, 'editedLocation', e.target.value)}
                            placeholder="Ej: Recepción"
                            icon={<MapPin size={14} />}
                          />
 
                          <div className="flex flex-wrap gap-2 pt-1">
                            <div className="px-2 py-0.5 bg-slate-100 rounded text-[10px] font-bold text-slate-600 border border-slate-200">
                              {device.detected_model || 'Genérico'}
                            </div>
                            {device.has_color && (
                               <div className="px-2 py-0.5 bg-cyan-50 rounded text-[10px] font-bold text-cyan-700 border border-cyan-100">
                                Color
                              </div>
                            )}
                            {device.has_scanner && (
                              <div className="px-2 py-0.5 bg-emerald-50 rounded text-[10px] font-bold text-emerald-700 border border-emerald-100">
                                Escáner
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
 
                      {/* Status indicator */}
                      <div className="hidden lg:block pt-1">
                        <div className={cn(
                          "flex items-center gap-1.5 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-tighter shadow-sm",
                          device.status === 'online'
                            ? 'bg-emerald-500 text-white'
                            : 'bg-slate-400 text-white'
                        )}>
                          <span className={cn(
                            "w-1 h-1 rounded-full bg-white",
                            device.status === 'online' ? "animate-pulse" : ""
                          )}></span>
                          {device.status === 'online' ? 'Online' : 'Offline'}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        
        {/* Footer */}
        {discoveredDevices.length > 0 && (
          <div className="flex items-center justify-between pt-8 mt-4 border-t border-slate-100">
            <Button
              variant="ghost"
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 font-bold"
            >
              Cerrar sin guardar
            </Button>
            <Button
              variant="primary"
              size="lg"
              icon={isRegistering ? <Loader2 size={18} className="animate-spin" /> : undefined}
              loading={isRegistering}
              disabled={selectedDevices.size === 0 || isRegistering}
              onClick={handleRegister}
              className="px-10 py-5 tracking-[0.2em] uppercase text-[11px] bg-slate-900 hover:bg-slate-800"
            >
              {isRegistering ? 'Procesando...' : `Guardar ${selectedDevices.size} equipos`}
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
};
