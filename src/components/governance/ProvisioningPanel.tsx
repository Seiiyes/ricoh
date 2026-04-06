import { useEffect, useState } from "react";
import { usePrinterStore } from "@/store/usePrinterStore";
import { PrinterCard } from "../fleet/PrinterCard";
import { DiscoveryModal } from "../discovery/DiscoveryModal";
import { EditPrinterModal } from "../fleet/EditPrinterModal";
import { Button, Input, Alert, Spinner } from "@/components/ui";
import { UserPlus, Wifi, Send } from "lucide-react";
import { printerDeviceToCardProps } from "@/utils/printerTransform";
import { fetchPrinters, createUser, provisionUser, connectWebSocket, updatePrinter, refreshPrinterSNMP } from "@/services/printerService";
import type { PrinterDevice } from "@/types";
import { cn } from "@/lib/utils";

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
      const printerIds = selectedPrinters.map((id: string) => {
        // If ID is string like "192-168-1-100", find the actual printer ID
        const printer = printers.find((p: PrinterDevice) => p.id === id);
        return printer ? parseInt(printer.id) : null;
      }).filter((id: number | null): id is number => id !== null);

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
    <div className="flex flex-col h-screen bg-slate-50 relative">
      {/* Background Blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-50">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] bg-red-100 rounded-full blur-[120px] animate-pulse-subtle"></div>
        <div className="absolute bottom-[-10%] left-[-5%] w-[400px] h-[400px] bg-slate-200 rounded-full blur-[100px]"></div>
      </div>
      <div className="flex flex-1 overflow-hidden">
        {/* Left: User Form - Only show when not in discovery-only mode */}
        {!showDiscoveryOnly && (
        <div className="w-[420px] bg-white/70 backdrop-blur-md border-r border-slate-200/60 p-8 space-y-8 shadow-[10px_0_40px_rgba(0,0,0,0.03)] overflow-y-auto relative z-20">
          <div className="flex items-center gap-3 text-ricoh-red mb-8">
            <div className="p-2 bg-red-50 rounded-lg">
              <UserPlus size={20} />
            </div>
            <h2 className="font-black tracking-widest uppercase text-xs text-slate-800">Nuevo Usuario</h2>
          </div>
          
          <div className="space-y-8">
            {/* Basic Information */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] border-b border-slate-100 pb-2">Información de Identidad</h3>
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
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] border-b border-slate-100 pb-2">Credenciales de Red</h3>
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
            <div className="space-y-5">
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] border-b border-slate-100 pb-2">Permisos de Uso</h3>
              <div className="space-y-3">
                {/* Copier */}
                <div className={cn("pl-4 border-l-2 transition-all", funcCopier ? "border-ricoh-red bg-red-50/30 p-3 rounded-r-xl" : "border-slate-100")}>
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className={cn("w-4 h-4 rounded border flex items-center justify-center transition-all", funcCopier ? "bg-ricoh-red border-ricoh-red" : "border-slate-300 group-hover:border-slate-400")}>
                      <input 
                        type="checkbox" 
                        checked={funcCopier}
                        onChange={(e) => setFuncCopier(e.target.checked)}
                        className="sr-only"
                      />
                      {funcCopier && <div className="w-1.5 h-1.5 bg-white rounded-full"></div>}
                    </div>
                    <span className={cn("text-xs font-bold transition-colors", funcCopier ? "text-slate-900" : "text-slate-500")}>Copiadora</span>
                  </label>
                  {funcCopier && (
                    <div className="mt-3 space-y-2 pl-2">
                      <p className="text-[9px] font-bold text-slate-400 uppercase mb-2">Restricción de Color:</p>
                      <div className="flex gap-4">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input 
                            type="radio" 
                            name="copierColor"
                            checked={funcCopierColor}
                            onChange={() => setFuncCopierColor(true)}
                            className="w-3 h-3 text-ricoh-red focus:ring-ricoh-red"
                          />
                          <span className="text-[11px] font-bold text-slate-600">Full Color</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input 
                            type="radio" 
                            name="copierColor"
                            checked={!funcCopierColor}
                            onChange={() => setFuncCopierColor(false)}
                            className="w-3 h-3 text-ricoh-red focus:ring-ricoh-red"
                          />
                          <span className="text-[11px] font-bold text-slate-600">B/N Only</span>
                        </label>
                      </div>
                    </div>
                  )}
                </div>

                {/* Printer */}
                <div className={cn("pl-4 border-l-2 transition-all", funcPrinter ? "border-ricoh-red bg-red-50/30 p-3 rounded-r-xl" : "border-slate-100")}>
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className={cn("w-4 h-4 rounded border flex items-center justify-center transition-all", funcPrinter ? "bg-ricoh-red border-ricoh-red" : "border-slate-300 group-hover:border-slate-400")}>
                      <input 
                        type="checkbox" 
                        checked={funcPrinter}
                        onChange={(e) => setFuncPrinter(e.target.checked)}
                        className="sr-only"
                      />
                      {funcPrinter && <div className="w-1.5 h-1.5 bg-white rounded-full"></div>}
                    </div>
                    <span className={cn("text-xs font-bold transition-colors", funcPrinter ? "text-slate-900" : "text-slate-500")}>Impresora</span>
                  </label>
                  {funcPrinter && (
                    <div className="mt-3 space-y-2 pl-2">
                       <div className="flex gap-4">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input 
                            type="radio" 
                            name="printerColor"
                            checked={funcPrinterColor}
                            onChange={() => setFuncPrinterColor(true)}
                            className="w-3 h-3 text-ricoh-red focus:ring-ricoh-red"
                          />
                          <span className="text-[11px] font-bold text-slate-600">Color</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input 
                            type="radio" 
                            name="printerColor"
                            checked={!funcPrinterColor}
                            onChange={() => setFuncPrinterColor(false)}
                            className="w-3 h-3 text-ricoh-red focus:ring-ricoh-red"
                          />
                          <span className="text-[11px] font-bold text-slate-600">B/N</span>
                        </label>
                      </div>
                    </div>
                  )}
                </div>

                {/* Other functions */}
                <div className="space-y-3 pt-4 border-t border-slate-100">
                  <p className="text-[9px] text-slate-400 uppercase font-black tracking-widest mb-2">Funciones Auxiliares:</p>
                  <div className="grid grid-cols-2 gap-3">
                    <label className="flex items-center gap-2 cursor-pointer group">
                      <input 
                        type="checkbox" 
                        checked={funcDocumentServer}
                        onChange={(e) => setFuncDocumentServer(e.target.checked)}
                        className="w-4 h-4 text-ricoh-red rounded border-slate-300 focus:ring-ricoh-red"
                      />
                      <span className="text-[11px] font-bold text-slate-600 group-hover:text-slate-900 transition-colors">Doc. Server</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer group">
                      <input 
                        type="checkbox" 
                        checked={funcFax}
                        onChange={(e) => setFuncFax(e.target.checked)}
                        className="w-4 h-4 text-ricoh-red rounded border-slate-300 focus:ring-ricoh-red"
                      />
                      <span className="text-[11px] font-bold text-slate-600 group-hover:text-slate-900 transition-colors">Fax</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer group bg-red-50/50 p-1.5 rounded-lg border border-red-100">
                      <input 
                        type="checkbox" 
                        checked={funcScanner}
                        onChange={(e) => setFuncScanner(e.target.checked)}
                        className="w-4 h-4 text-ricoh-red rounded border-slate-300 focus:ring-ricoh-red"
                      />
                      <span className="text-[11px] font-black text-ricoh-red uppercase tracking-tighter">Escáner</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer group">
                      <input 
                        type="checkbox" 
                        checked={funcBrowser}
                        onChange={(e) => setFuncBrowser(e.target.checked)}
                        className="w-4 h-4 text-ricoh-red rounded border-slate-300 focus:ring-ricoh-red"
                      />
                      <span className="text-[11px] font-bold text-slate-600 group-hover:text-slate-900 transition-colors">Navegador</span>
                    </label>
                  </div>
                </div>
              </div>
              <Alert variant="warning" className="mt-3 text-[10px]">
                <span className="font-bold">⚠️ Importante:</span> Habilita color en Copiadora/Impresora solo cuando sea necesario. La mayoría de usuarios solo necesitan B/N.
              </Alert>
            </div>

            {/* SMB Configuration */}
            <div className="space-y-4">
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] border-b border-slate-100 pb-2">Destino de Red (SMB)</h3>
              <Input
                label="Ruta de Carpeta"
                value={smbPath}
                onChange={(e) => setSmbPath(e.target.value)}
                placeholder="\\\\10.0.0.5\\scans\\"
                helperText="Servidor y puerto se extraen de la ruta"
                variant="underline"
                className="font-mono text-slate-500"
              />
            </div>
          </div>

          <div className="pt-6 border-t border-slate-200">
            <div className="flex items-center justify-between mb-4 px-4 py-3 bg-slate-50 rounded-xl border border-slate-100">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Seleccionadas</span>
              <span className="text-sm font-black text-ricoh-red">{selectedPrinters.length} Equipos</span>
            </div>
            <Button
              variant="primary"
              size="lg"
              icon={<Send size={18} />}
              loading={isProvisioning}
              disabled={isProvisioning || selectedPrinters.length === 0 || !userName.trim() || !userPin.trim() || !networkPassword.trim()}
              onClick={handleProvision}
              className="w-full py-6 tracking-[0.2em] uppercase text-xs shadow-xl shadow-red-500/20 bg-ricoh-red hover:bg-red-700"
            >
              {isProvisioning ? 'Procesando ' : 'Enviar a Equipos'}
            </Button>
          </div>
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
                Agregar Equipos
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
                  Haz clic en "Agregar Equipos" para escanear tu red
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