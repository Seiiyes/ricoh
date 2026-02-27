import { useState } from 'react';
import { X, Wifi, AlertCircle, Loader2 } from 'lucide-react';
import { scanPrinters, registerDiscoveredPrinters } from '@/services/printerService';

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
      alert('Escaneo fallido. Por favor verifica el rango de IP e intenta de nuevo.');
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
      alert('Por favor selecciona al menos un dispositivo para registrar');
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
      alert(`Se registraron exitosamente ${devicesToRegister.length} impresora(s)`);
      onComplete();
      onClose();
    } catch (error) {
      console.error('Registro fallido:', error);
      alert('Error al registrar impresoras. Algunas pueden ya existir.');
    } finally {
      setIsRegistering(false);
    }
  };

  const handleManualAdd = async () => {
    if (!manualIP) {
      alert('Por favor ingresa una dirección IP');
      return;
    }

    try {
      setIsCheckingManual(true);
      
      // Llamar al endpoint de escaneo con una sola IP
      const response = await fetch(`http://localhost:8000/discovery/check-printer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ip_address: manualIP,
          snmp_port: parseInt(manualPort) || 161
        })
      });

      if (!response.ok) {
        throw new Error('No se pudo conectar con la impresora');
      }

      const device = await response.json();
      
      // Agregar a la lista de dispositivos descubiertos
      const editableDevice: EditableDevice = {
        ...device,
        editedHostname: device.hostname,
        editedLocation: device.location || ''
      };
      
      setDiscoveredDevices(prev => [...prev, editableDevice]);
      setSelectedDevices(prev => new Set([...prev, device.ip_address]));
      setScanComplete(true);
      setShowManualAdd(false);
      setManualIP('');
      setManualPort('161');
      
    } catch (error) {
      console.error('Error agregando impresora manual:', error);
      alert('No se pudo conectar con la impresora. Verifica la IP y el puerto SNMP.');
    } finally {
      setIsCheckingManual(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <Wifi className="text-ricoh-red" size={24} />
            <div>
              <h2 className="text-lg font-bold text-industrial-gray uppercase tracking-tight">
                Descubrimiento de Red
              </h2>
              <p className="text-xs text-slate-500">Escanear y registrar impresoras Ricoh</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Scan Controls */}
          <div className="mb-6">
            <label className="block text-xs font-bold text-slate-400 uppercase mb-2">
              Rango de IP (Notación CIDR)
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={ipRange}
                onChange={(e) => setIpRange(e.target.value)}
                placeholder="192.168.91.0/24"
                className="flex-1 border border-slate-300 rounded px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red"
                disabled={isScanning}
              />
              <button
                onClick={handleScan}
                disabled={isScanning}
                className="flex items-center gap-2 bg-ricoh-red text-white px-6 py-2 rounded font-bold text-sm uppercase tracking-wide hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isScanning ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Escaneando...
                  </>
                ) : (
                  <>
                    <Wifi size={16} />
                    Escanear Red
                  </>
                )}
              </button>
            </div>
            
            {/* Manual Add Button */}
            <div className="mt-3">
              <button
                onClick={() => setShowManualAdd(!showManualAdd)}
                className="text-sm text-blue-600 hover:text-blue-800 font-semibold transition-colors"
              >
                {showManualAdd ? '− Ocultar' : '+ Agregar impresora manualmente'}
              </button>
            </div>

            {/* Manual Add Form */}
            {showManualAdd && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="text-sm font-bold text-blue-900 mb-3">Agregar Impresora por IP</h3>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1">
                      Dirección IP
                    </label>
                    <input
                      type="text"
                      value={manualIP}
                      onChange={(e) => setManualIP(e.target.value)}
                      placeholder="192.168.91.250"
                      className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      disabled={isCheckingManual}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-600 mb-1">
                      Puerto SNMP
                    </label>
                    <input
                      type="text"
                      value={manualPort}
                      onChange={(e) => setManualPort(e.target.value)}
                      placeholder="161"
                      className="w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                      disabled={isCheckingManual}
                    />
                  </div>
                </div>
                <button
                  onClick={handleManualAdd}
                  disabled={isCheckingManual || !manualIP}
                  className="mt-3 w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded font-bold text-sm uppercase tracking-wide hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isCheckingManual ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Verificando...
                    </>
                  ) : (
                    'Agregar Impresora'
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Results */}
          {isScanning && (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <Loader2 size={48} className="animate-spin mb-4" />
              <p className="text-sm">Escaneando la red en busca de impresoras...</p>
            </div>
          )}

          {scanComplete && discoveredDevices.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400">
              <AlertCircle size={48} className="mb-4" />
              <p className="text-sm">No se encontraron impresoras en el rango especificado</p>
            </div>
          )}

          {discoveredDevices.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm text-slate-600">
                  Se encontraron <span className="font-bold text-ricoh-red">{discoveredDevices.length}</span> dispositivo(s)
                </p>
                <p className="text-xs text-slate-500">
                  {selectedDevices.size} seleccionado(s)
                </p>
              </div>

              <div className="space-y-3 max-h-96 overflow-y-auto">
                {discoveredDevices.map((device) => (
                  <div
                    key={device.ip_address}
                    className={`border rounded-lg p-4 transition-all ${
                      selectedDevices.has(device.ip_address)
                        ? 'border-ricoh-red bg-red-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {/* Checkbox */}
                      <input
                        type="checkbox"
                        checked={selectedDevices.has(device.ip_address)}
                        onChange={() => toggleDevice(device.ip_address)}
                        className="mt-1 w-4 h-4 text-ricoh-red border-slate-300 rounded focus:ring-ricoh-red"
                      />
                      
                      {/* Device Info */}
                      <div className="flex-1 space-y-2">
                        {/* Hostname editable */}
                        <div>
                          <label className="block text-xs font-bold text-slate-400 uppercase mb-1">
                            Nombre
                          </label>
                          <input
                            type="text"
                            value={device.editedHostname || device.hostname}
                            onChange={(e) => updateDeviceField(device.ip_address, 'editedHostname', e.target.value)}
                            className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red"
                            placeholder="Nombre de la impresora"
                          />
                        </div>

                        {/* IP Address */}
                        <p className="text-xs text-slate-500 font-mono">
                          IP: {device.ip_address}
                        </p>

                        {/* Location editable */}
                        <div>
                          <label className="block text-xs font-bold text-slate-400 uppercase mb-1">
                            Ubicación
                          </label>
                          <input
                            type="text"
                            value={device.editedLocation || ''}
                            onChange={(e) => updateDeviceField(device.ip_address, 'editedLocation', e.target.value)}
                            className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red"
                            placeholder="Ej: Oficina Principal - Piso 2"
                          />
                        </div>

                        {/* Model and capabilities */}
                        <div className="flex gap-4 text-xs text-slate-600">
                          <span>{device.detected_model || 'Modelo Desconocido'}</span>
                          {device.has_color && <span className="text-cyan-600">Color</span>}
                          {device.has_scanner && <span className="text-green-600">Escáner</span>}
                        </div>
                      </div>

                      {/* Status badge */}
                      <div className={`px-2 py-1 rounded text-xs font-bold ${
                        device.status === 'online'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-slate-100 text-slate-600'
                      }`}>
                        {device.status === 'online' ? 'En línea' : 'Fuera de línea'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {discoveredDevices.length > 0 && (
          <div className="flex items-center justify-between p-6 border-t border-slate-200 bg-slate-50">
            <button
              onClick={onClose}
              className="px-6 py-2 text-sm font-bold text-slate-600 hover:text-slate-800 transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleRegister}
              disabled={selectedDevices.size === 0 || isRegistering}
              className="flex items-center gap-2 bg-industrial-gray text-white px-6 py-2 rounded font-bold text-sm uppercase tracking-wide hover:bg-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRegistering ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Registrando...
                </>
              ) : (
                <>
                  Registrar {selectedDevices.size} Impresora(s)
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
