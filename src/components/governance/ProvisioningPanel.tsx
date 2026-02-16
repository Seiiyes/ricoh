import { useEffect, useState, useRef } from "react";
import { usePrinterStore } from "@/store/usePrinterStore";
import { PrinterCard } from "../fleet/PrinterCard";
import { DiscoveryModal } from "../discovery/DiscoveryModal";
import { EditPrinterModal } from "../fleet/EditPrinterModal";
import { Terminal as TerminalIcon, UserPlus, Loader2, Wifi, Send } from "lucide-react";
import { printerDeviceToCardProps } from "@/utils/printerTransform";
import { fetchPrinters, createUser, provisionUser, connectWebSocket, updatePrinter, refreshPrinterSNMP } from "@/services/printerService";
import type { PrinterDevice } from "@/types";

export const ProvisioningPanel = () => {
  const { logs, addLog, printers, isLoading, setPrinters, setLoading, selectedPrinters, clearSelection } = usePrinterStore();
  const [isDiscoveryOpen, setIsDiscoveryOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingPrinter, setEditingPrinter] = useState<PrinterDevice | null>(null);
  const [userName, setUserName] = useState('');
  const [userPin, setUserPin] = useState('');
  const [smbPath, setSmbPath] = useState('');
  const [isProvisioning, setIsProvisioning] = useState(false);
  
  // New fields
  const [networkUsername, setNetworkUsername] = useState('reliteltda\\scaner');
  const [networkPassword, setNetworkPassword] = useState('');
  const [funcCopier, setFuncCopier] = useState(false);
  const [funcCopierColor, setFuncCopierColor] = useState(false); // Color option for copier
  const [funcPrinter, setFuncPrinter] = useState(false);
  const [funcPrinterColor, setFuncPrinterColor] = useState(false); // Color option for printer
  const [funcDocumentServer, setFuncDocumentServer] = useState(false);
  const [funcFax, setFuncFax] = useState(false);
  const [funcScanner, setFuncScanner] = useState(true); // Default enabled
  const [funcBrowser, setFuncBrowser] = useState(false);
  
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Extract server from SMB path automatically
  const extractServerFromPath = (path: string): string => {
    // Extract server from path like \\10.0.0.5\scans\
    if (path.startsWith('\\\\')) {
      const parts = path.substring(2).split('\\');
      return parts[0] || '10.0.0.5';
    }
    return '10.0.0.5';
  };

  useEffect(() => {
    const loadPrinters = async () => {
      try {
        setLoading(true);
        const result = await fetchPrinters();
        setPrinters(result);
        if (result.length > 0) {
          addLog(`Cargadas ${result.length} impresora(s) desde la base de datos`, 'success');
        }
      } catch (error) {
        console.error('Error al cargar impresoras:', error);
        addLog('Error al cargar impresoras desde la base de datos', 'error');
      } finally {
        setLoading(false);
      }
    };

    loadPrinters();

    // Connect to WebSocket for real-time logs
    const ws = connectWebSocket((event) => {
      addLog(event.message, event.type);
    });

    // Add initial connection log
    addLog('Sistema listo para configurar usuarios', 'success');

    return () => {
      ws.close();
    };
  }, [setPrinters, setLoading, addLog]);

  // Auto-scroll to bottom when new logs arrive
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleDiscoveryComplete = async () => {
    // Reload printers after discovery
    try {
      setLoading(true);
      const result = await fetchPrinters();
      setPrinters(result);
      addLog(`Flota actualizada: ${result.length} impresora(s) disponible(s)`, 'success');
    } catch (error) {
      console.error('Error al recargar impresoras:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditPrinter = (printer: PrinterDevice) => {
    setEditingPrinter(printer);
    setIsEditOpen(true);
  };

  const handleSavePrinter = async (printerId: string, updates: any) => {
    try {
      await updatePrinter(parseInt(printerId), updates);
      addLog(`Impresora actualizada: ${updates.hostname || 'Sin nombre'}`, 'success');
      
      // Reload printers
      const result = await fetchPrinters();
      setPrinters(result);
    } catch (error) {
      console.error('Error al actualizar impresora:', error);
      throw error;
    }
  };

  const handleRefreshPrinter = async (printer: PrinterDevice) => {
    try {
      addLog(`Consultando SNMP para ${printer.hostname}...`, 'info');
      await refreshPrinterSNMP(parseInt(printer.id));
      addLog(`Datos SNMP actualizados para ${printer.hostname}`, 'success');
      
      // Reload printers
      const result = await fetchPrinters();
      setPrinters(result);
    } catch (error) {
      console.error('Error al refrescar SNMP:', error);
      addLog(`Error al consultar SNMP: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    }
  };

  const handleProvision = async () => {
    if (!userName.trim() || !userPin.trim()) {
      addLog('Por favor ingresa nombre de usuario y código de usuario', 'error');
      return;
    }

    if (!networkPassword.trim()) {
      addLog('Por favor ingresa la contraseña de autenticación de carpeta', 'error');
      return;
    }

    if (!funcCopier && !funcPrinter && !funcDocumentServer && !funcFax && !funcScanner && !funcBrowser) {
      addLog('Por favor selecciona al menos una función disponible', 'error');
      return;
    }

    if (selectedPrinters.length === 0) {
      addLog('Por favor selecciona al menos una impresora', 'error');
      return;
    }

    try {
      setIsProvisioning(true);
      addLog(`Creando usuario: ${userName}...`, 'info');

      // Create user with new fields
      const smbServer = extractServerFromPath(smbPath);
      const user = await createUser({
        name: userName,
        codigo_de_usuario: userPin,
        network_credentials: {
          username: networkUsername,
          password: networkPassword,
        },
        smb_config: {
          server: smbServer,
          port: 21, // Fixed port
          path: smbPath,
        },
        available_functions: {
          copier: funcCopier,
          printer: funcPrinter,
          document_server: funcDocumentServer,
          fax: funcFax,
          scanner: funcScanner,
          browser: funcBrowser,
        },
      });

      addLog(`Usuario creado: ${user.name} (ID: ${user.id})`, 'success');
      addLog(`Enviando configuración a ${selectedPrinters.length} impresora(s)...`, 'info');

      // Convert selected printer IDs to numbers
      const printerIds = selectedPrinters.map(id => {
        // If ID is string like "192-168-1-100", find the actual printer ID
        const printer = printers.find(p => p.id === id);
        return printer ? parseInt(printer.id) : null;
      }).filter(id => id !== null) as number[];

      console.log('🔍 Debug - Selected printers:', selectedPrinters);
      console.log('🔍 Debug - Converted printer IDs:', printerIds);
      console.log('🔍 Debug - User ID:', user.id);

      if (printerIds.length === 0) {
        addLog('❌ Error: No se pudieron convertir los IDs de impresoras', 'error');
        return;
      }

      // Provision user to printers
      const result = await provisionUser(user.id, printerIds);

      addLog(result.message, 'success');
      addLog(`✓ Configuración enviada exitosamente`, 'success');

      // Clear form
      setUserName('');
      setUserPin('');
      setNetworkPassword('');
      setSmbPath('');
      setFuncCopier(false);
      setFuncCopierColor(false);
      setFuncPrinter(false);
      setFuncPrinterColor(false);
      setFuncDocumentServer(false);
      setFuncFax(false);
      setFuncScanner(true);
      setFuncBrowser(false);
      clearSelection();

    } catch (error) {
      console.error('Configuración fallida:', error);
      addLog(`Error al configurar usuario: ${error instanceof Error ? error.message : 'Error desconocido'}`, 'error');
    } finally {
      setIsProvisioning(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      <div className="flex flex-1 overflow-hidden">
        {/* Left: User Form */}
        <div className="w-[400px] border-r bg-white p-6 space-y-6 shadow-[4px_0_24px_rgba(0,0,0,0.02)] overflow-y-auto">
          <div className="flex items-center gap-2 text-ricoh-red mb-8">
            <UserPlus size={20} />
            <h2 className="font-bold tracking-tight uppercase text-sm">Crear Usuario en Impresoras</h2>
          </div>
          
          <div className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-slate-600 uppercase border-b pb-1">Información Básica</h3>
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase">Nombre Completo</label>
                <input 
                  className="w-full border-b border-slate-200 py-1 focus:border-ricoh-red outline-none text-sm" 
                  placeholder="Nombre del Usuario"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase">Código de Usuario</label>
                <input 
                  className="w-full border-b border-slate-200 py-1 focus:border-ricoh-red outline-none text-sm font-mono" 
                  type="text" 
                  placeholder="1234"
                  maxLength={8}
                  value={userPin}
                  onChange={(e) => setUserPin(e.target.value.replace(/\D/g, ''))}
                />
                <p className="text-[9px] text-slate-400">4-8 dígitos numéricos</p>
              </div>
            </div>

            {/* Network Credentials */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-slate-600 uppercase border-b pb-1">Autenticación de Carpeta</h3>
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase">Nombre de usuario de inicio de sesión</label>
                <input 
                  className="w-full border-b border-slate-200 py-1 focus:border-ricoh-red outline-none text-sm font-mono" 
                  value={networkUsername}
                  onChange={(e) => setNetworkUsername(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase">Contraseña de inicio de sesión</label>
                <input 
                  className="w-full border-b border-slate-200 py-1 focus:border-ricoh-red outline-none text-sm font-mono" 
                  type="password" 
                  placeholder="Contraseña"
                  value={networkPassword}
                  onChange={(e) => setNetworkPassword(e.target.value)}
                />
              </div>
            </div>

            {/* Available Functions */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-slate-600 uppercase border-b pb-1">Funciones Disponibles</h3>
              <div className="space-y-3">
                {/* Copier */}
                <div className="border-l-2 border-slate-200 pl-3">
                  <label className="flex items-center gap-2 cursor-pointer mb-2">
                    <input 
                      type="checkbox" 
                      checked={funcCopier}
                      onChange={(e) => setFuncCopier(e.target.checked)}
                      className="w-4 h-4 text-ricoh-red focus:ring-ricoh-red"
                    />
                    <span className="text-xs font-bold">Copiadora</span>
                  </label>
                  {funcCopier && (
                    <div className="ml-6 space-y-1 bg-slate-50 p-2 rounded">
                      <p className="text-[9px] text-slate-500 mb-1">Limitación modo copia color:</p>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input 
                          type="radio" 
                          name="copierColor"
                          checked={funcCopierColor}
                          onChange={() => setFuncCopierColor(true)}
                          className="w-3 h-3 text-ricoh-red focus:ring-ricoh-red"
                        />
                        <span className="text-[11px] text-slate-600">A todo color</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input 
                          type="radio" 
                          name="copierColor"
                          checked={!funcCopierColor}
                          onChange={() => setFuncCopierColor(false)}
                          className="w-3 h-3 text-ricoh-red focus:ring-ricoh-red"
                        />
                        <span className="text-[11px] text-slate-600">Blanco y Negro</span>
                      </label>
                    </div>
                  )}
                </div>

                {/* Printer */}
                <div className="border-l-2 border-slate-200 pl-3">
                  <label className="flex items-center gap-2 cursor-pointer mb-2">
                    <input 
                      type="checkbox" 
                      checked={funcPrinter}
                      onChange={(e) => setFuncPrinter(e.target.checked)}
                      className="w-4 h-4 text-ricoh-red focus:ring-ricoh-red"
                    />
                    <span className="text-xs font-bold">Impresora</span>
                  </label>
                  {funcPrinter && (
                    <div className="ml-6 space-y-1 bg-slate-50 p-2 rounded">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input 
                          type="radio" 
                          name="printerColor"
                          checked={funcPrinterColor}
                          onChange={() => setFuncPrinterColor(true)}
                          className="w-3 h-3 text-ricoh-red focus:ring-ricoh-red"
                        />
                        <span className="text-[11px] text-slate-600">Color</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input 
                          type="radio" 
                          name="printerColor"
                          checked={!funcPrinterColor}
                          onChange={() => setFuncPrinterColor(false)}
                          className="w-3 h-3 text-ricoh-red focus:ring-ricoh-red"
                        />
                        <span className="text-[11px] text-slate-600">Blanco y Negro</span>
                      </label>
                    </div>
                  )}
                </div>

                {/* Other functions - Simple checkboxes */}
                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <p className="text-[9px] text-slate-500 uppercase font-bold mb-2">Otras funciones:</p>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={funcDocumentServer}
                      onChange={(e) => setFuncDocumentServer(e.target.checked)}
                      className="w-4 h-4 text-ricoh-red focus:ring-ricoh-red"
                    />
                    <span className="text-xs">Document Server</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={funcFax}
                      onChange={(e) => setFuncFax(e.target.checked)}
                      className="w-4 h-4 text-ricoh-red focus:ring-ricoh-red"
                    />
                    <span className="text-xs">Fax</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={funcScanner}
                      onChange={(e) => setFuncScanner(e.target.checked)}
                      className="w-4 h-4 text-ricoh-red focus:ring-ricoh-red"
                    />
                    <span className="text-xs font-bold text-ricoh-red">Escáner</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={funcBrowser}
                      onChange={(e) => setFuncBrowser(e.target.checked)}
                      className="w-4 h-4 text-ricoh-red focus:ring-ricoh-red"
                    />
                    <span className="text-xs">Navegador</span>
                  </label>
                </div>
              </div>
              <div className="bg-amber-50 border-l-4 border-amber-400 p-3 mt-3">
                <p className="text-[10px] text-amber-800">
                  <span className="font-bold">⚠️ Importante:</span> Habilita color en Copiadora/Impresora solo cuando sea necesario. La mayoría de usuarios solo necesitan B/N.
                </p>
              </div>
            </div>

            {/* SMB Configuration */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-slate-600 uppercase border-b pb-1">Carpeta SMB</h3>
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase">Ruta</label>
                <input 
                  className="w-full border-b border-slate-200 py-1 focus:border-ricoh-red outline-none text-sm font-mono text-slate-500" 
                  value={smbPath}
                  onChange={(e) => setSmbPath(e.target.value)}
                  placeholder="\\\\10.0.0.5\\scans\\"
                />
                <p className="text-[9px] text-slate-400">El servidor y puerto se extraen automáticamente</p>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-200">
            <p className="text-xs text-slate-500 mb-2">
              Seleccionadas: <span className="font-bold text-ricoh-red">{selectedPrinters.length}</span> impresora(s)
            </p>
          </div>

          <button 
            onClick={handleProvision}
            disabled={isProvisioning || selectedPrinters.length === 0 || !userName.trim() || !userPin.trim() || !networkPassword.trim()}
            className="w-full bg-industrial-gray text-white py-3 text-xs font-bold uppercase tracking-widest hover:bg-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isProvisioning ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Configurando...
              </>
            ) : (
              <>
                <Send size={14} />
                Enviar Configuración
              </>
            )}
          </button>
        </div>

        {/* Right: Fleet Selection */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <div className="flex gap-3 items-center">
              <button
                onClick={() => setIsDiscoveryOpen(true)}
                className="flex items-center gap-2 bg-ricoh-red text-white px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide hover:bg-red-700 transition-colors"
              >
                <Wifi size={14} />
                Descubrir Impresoras
              </button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {isLoading ? (
              <div className="col-span-full flex flex-col items-center justify-center py-16 text-slate-400">
                <Loader2 className="animate-spin mb-3" size={32} />
                <p className="text-sm">Cargando impresoras...</p>
              </div>
            ) : printers.length === 0 ? (
              <div className="col-span-full flex flex-col items-center justify-center py-16 text-slate-400">
                <p className="text-sm mb-4">No hay impresoras en la base de datos</p>
                <button
                  onClick={() => setIsDiscoveryOpen(true)}
                  className="text-ricoh-red hover:underline text-sm font-bold"
                >
                  Haz clic en "Descubrir Impresoras" para escanear tu red
                </button>
              </div>
            ) : (
              printers.map(printer => (
                <PrinterCard 
                  key={printer.id} 
                  {...printerDeviceToCardProps(printer)}
                  onEdit={() => handleEditPrinter(printer)}
                  onRefresh={() => handleRefreshPrinter(printer)}
                />
              ))
            )}
          </div>
        </div>
      </div>

      {/* Bottom: Live Console */}
      <div className="h-48 bg-industrial-gray text-emerald-400 font-mono text-[11px] p-4 overflow-hidden border-t-4 border-ricoh-red">
        <div className="flex items-center gap-2 mb-2 text-slate-400 border-b border-slate-700 pb-2">
          <TerminalIcon size={14} />
          <span className="uppercase tracking-widest text-[9px]">Registro de Actividad</span>
        </div>
        <div className="overflow-y-auto h-32 space-y-1 custom-scrollbar">
          {logs.length === 0 && <div className="text-slate-600 italic">No hay actividad registrada. Esperando configuración...</div>}
          {logs.map(log => (
            <div key={log.id} className="flex gap-3">
              <span className="text-slate-500">[{log.timestamp}]</span>
              <span className={
                log.type === 'error' ? 'text-red-400' : 
                log.type === 'success' ? 'text-emerald-400' :
                log.type === 'warning' ? 'text-yellow-400' : ''
              }>{log.message}</span>
            </div>
          ))}
          <div ref={logsEndRef} />
        </div>
      </div>

      {/* Discovery Modal */}
      <DiscoveryModal
        isOpen={isDiscoveryOpen}
        onClose={() => setIsDiscoveryOpen(false)}
        onComplete={handleDiscoveryComplete}
      />

      {/* Edit Printer Modal */}
      <EditPrinterModal
        isOpen={isEditOpen}
        onClose={() => {
          setIsEditOpen(false);
          setEditingPrinter(null);
        }}
        onSave={handleSavePrinter}
        printer={editingPrinter}
      />
    </div>
  );
};