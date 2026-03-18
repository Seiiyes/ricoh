import { useEffect, useState, useRef } from "react";
import { usePrinterStore } from "@/store/usePrinterStore";
import { PrinterCard } from "../fleet/PrinterCard";
import { DiscoveryModal } from "../discovery/DiscoveryModal";
import { EditPrinterModal } from "../fleet/EditPrinterModal";
import { Button, Input, Alert, Spinner } from "@/components/ui";
import { Terminal as TerminalIcon, UserPlus, Loader2, Wifi, Send } from "lucide-react";
import { printerDeviceToCardProps } from "@/utils/printerTransform";
import { fetchPrinters, createUser, provisionUser, connectWebSocket, updatePrinter, refreshPrinterSNMP } from "@/services/printerService";
import type { PrinterDevice } from "@/types";

export const ProvisioningPanel = ({ showDiscoveryOnly = false }: { showDiscoveryOnly?: boolean }) => {
  const { printers, isLoading, setPrinters, setLoading, selectedPrinters, clearSelection } = usePrinterStore();
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
      } catch (error) {
        console.error('Error al cargar impresoras:', error);
      } finally {
        setLoading(false);
      }
    };

    loadPrinters();

    // Connect to WebSocket for real-time logs
    const ws = connectWebSocket((event) => {
      // WebSocket events - no longer logging to UI
    });

    return () => {
      ws.close();
    };
  }, [setPrinters, setLoading]);

  const handleDiscoveryComplete = async () => {
    // Reload printers after discovery
    try {
      setLoading(true);
      const result = await fetchPrinters();
      setPrinters(result);
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
      await refreshPrinterSNMP(parseInt(printer.id));
      
      // Reload printers
      const result = await fetchPrinters();
      setPrinters(result);
    } catch (error) {
      console.error('Error al refrescar SNMP:', error);
    }
  };

  const handleProvision = async () => {
    if (!userName.trim() || !userPin.trim()) {
      return;
    }

    if (!networkPassword.trim()) {
      return;
    }

    if (!funcCopier && !funcPrinter && !funcDocumentServer && !funcFax && !funcScanner && !funcBrowser) {
      return;
    }

    if (selectedPrinters.length === 0) {
      return;
    }

    try {
      setIsProvisioning(true);

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
        return;
      }

      // Provision user to printers
      const result = await provisionUser(user.id, printerIds);

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
    } finally {
      setIsProvisioning(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      <div className="flex flex-1 overflow-hidden">
        {/* Left: User Form - Only show when not in discovery-only mode */}
        {!showDiscoveryOnly && (
        <div className="w-[400px] border-r bg-white p-6 space-y-6 shadow-[4px_0_24px_rgba(0,0,0,0.02)] overflow-y-auto">
          <div className="flex items-center gap-2 text-ricoh-red mb-8">
            <UserPlus size={20} />
            <h2 className="font-bold tracking-tight uppercase text-sm">Crear Usuario en Impresoras</h2>
          </div>
          
          <div className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-slate-600 uppercase border-b pb-1">Información Básica</h3>
              <Input
                label="Nombre Completo"
                placeholder="Nombre del Usuario"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                variant="underline"
              />
              <Input
                label="Código de Usuario"
                type="text"
                placeholder="1234"
                maxLength={8}
                value={userPin}
                onChange={(e) => setUserPin(e.target.value.replace(/\D/g, ''))}
                helperText="4-8 dígitos numéricos"
                variant="underline"
                className="font-mono"
              />
            </div>

            {/* Network Credentials */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-slate-600 uppercase border-b pb-1">Autenticación de Carpeta</h3>
              <Input
                label="Nombre de usuario de inicio de sesión"
                value={networkUsername}
                onChange={(e) => setNetworkUsername(e.target.value)}
                variant="underline"
                className="font-mono"
              />
              <Input
                label="Contraseña de inicio de sesión"
                type="password"
                placeholder="Contraseña"
                value={networkPassword}
                onChange={(e) => setNetworkPassword(e.target.value)}
                variant="underline"
                className="font-mono"
              />
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
              <Alert variant="warning" className="mt-3 text-[10px]">
                <span className="font-bold">⚠️ Importante:</span> Habilita color en Copiadora/Impresora solo cuando sea necesario. La mayoría de usuarios solo necesitan B/N.
              </Alert>
            </div>

            {/* SMB Configuration */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-bold text-slate-600 uppercase border-b pb-1">Carpeta SMB</h3>
              <Input
                label="Ruta"
                value={smbPath}
                onChange={(e) => setSmbPath(e.target.value)}
                placeholder="\\\\10.0.0.5\\scans\\"
                helperText="El servidor y puerto se extraen automáticamente"
                variant="underline"
                className="font-mono text-slate-500"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-200">
            <p className="text-xs text-slate-500 mb-2">
              Seleccionadas: <span className="font-bold text-ricoh-red">{selectedPrinters.length}</span> impresora(s)
            </p>
          </div>

          <Button
            variant="secondary"
            size="md"
            icon={<Send size={14} />}
            loading={isProvisioning}
            disabled={isProvisioning || selectedPrinters.length === 0 || !userName.trim() || !userPin.trim() || !networkPassword.trim()}
            onClick={handleProvision}
            className="w-full py-3 tracking-widest"
          >
            {isProvisioning ? 'Configurando...' : 'Enviar Configuración'}
          </Button>
        </div>
        )}

        {/* Right: Equipment Selection */}
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="flex justify-between items-center mb-6">
            <div className="flex gap-3 items-center">
              <Button
                variant="primary"
                size="sm"
                icon={<Wifi size={14} />}
                onClick={() => setIsDiscoveryOpen(true)}
                className="rounded-full"
              >
                Descubrir Impresoras
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {isLoading ? (
              <div className="col-span-full flex items-center justify-center py-16">
                <Spinner size="lg" text="Cargando impresoras..." />
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