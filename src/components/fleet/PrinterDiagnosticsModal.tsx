import { useState, useEffect } from 'react';
import { Shield, ShieldAlert, CheckCircle, XCircle, RefreshCw, Activity, Layers, Database, Compass } from 'lucide-react';
import { Modal, Button, Spinner, Badge } from '@/components/ui';
import type { PrinterDevice } from '@/types';
import { fetchPrinterDiagnostics } from '@/services/printerService';
import { useNotification } from '@/hooks/useNotification';

interface PrinterDiagnosticsModalProps {
  isOpen: boolean;
  onClose: () => void;
  printer: PrinterDevice | null;
}

export const PrinterDiagnosticsModal = ({ isOpen, onClose, printer }: PrinterDiagnosticsModalProps) => {
  const notify = useNotification();
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'ports' | 'metrics' | 'opportunities'>('ports');

  const loadDiagnostics = async () => {
    if (!printer) return;
    try {
      setIsLoading(true);
      setData(null);
      const res = await fetchPrinterDiagnostics(parseInt(printer.id));
      if (res && res.success) {
        setData(res);
      } else {
        notify.error('Error de diagnóstico', 'No se pudieron obtener los diagnósticos del equipo');
      }
    } catch (error) {
      console.error('Error al diagnosticar:', error);
      notify.error('Fallo de conexión', 'La impresora no respondió a las peticiones de diagnóstico en el tiempo de espera');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && printer) {
      loadDiagnostics();
      setActiveTab('ports');
    }
  }, [isOpen, printer]);

  if (!isOpen || !printer) return null;

  // Mapear descripción de oportunidades de integración basadas en puertos abiertos
  const getPortOpportunity = (portName: string, isOpen: boolean) => {
    switch (portName) {
      case 'port_21_ftp':
        return isOpen 
          ? { text: 'Direct PDF Print habilitado. Puedes enviar archivos directamente al puerto 21 para imprimir sin drivers.', type: 'success' }
          : { text: 'Direct PDF Print deshabilitado. No se puede imprimir enviando archivos vía FTP.', type: 'muted' };
      case 'port_22_ssh_sftp':
        return isOpen
          ? { text: 'SFTP Entrante habilitado. La impresora permite conexiones seguras directas.', type: 'success' }
          : { text: 'Puerto cerrado. La impresora no acepta SSH entrante (Normal en Ricoh). Se puede usar SFTP de salida.', type: 'info' };
      case 'port_23_telnet':
        return isOpen
          ? { text: 'Maintenance Shell activo. Permite reiniciar el equipo o ejecutar comandos de red rápidos vía CLI.', type: 'success' }
          : { text: 'Consola Telnet inactiva. No es posible enviar comandos de mantenimiento por consola.', type: 'muted' };
      case 'port_80_http':
      case 'port_443_https':
        return isOpen
          ? { text: 'Web Image Monitor (WIM) accesible. Lectura de tóners, contadores y edición de libreta de direcciones activa.', type: 'success' }
          : { text: 'Servicio Web bloqueado. La administración remota por navegador no está disponible.', type: 'error' };
      case 'port_445_smb':
        return isOpen
          ? { text: 'Direct SMB habilitado. Soporta envío de escaneos directo por carpetas de red de Windows.', type: 'success' }
          : { text: 'Carpeta SMB entrante cerrada. La impresora no actúa como servidor de carpetas de red.', type: 'muted' };
      case 'port_515_lpr':
      case 'port_631_ipp':
      case 'port_9100_raw':
        return isOpen
          ? { text: 'Cola de Impresión activa. Soporta redireccionamiento para Pull Printing (retención de trabajos).', type: 'success' }
          : { text: 'Cola de impresión local cerrada. Los drivers clásicos no pueden comunicarse por este canal.', type: 'error' };
      default:
        return { text: 'Puerto auxiliar del equipo.', type: 'muted' };
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Diagnóstico en Vivo: ${printer.hostname}`}
      size="lg"
    >
      <div className="space-y-6">
        {/* Cabecera de estado rápido */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-4 bg-slate-900 text-white rounded-2xl border border-slate-800 shadow-md relative overflow-hidden -mt-2">
          {/* Background Decor */}
          <div className="absolute right-0 top-0 w-32 h-32 bg-ricoh-red/10 rounded-full blur-2xl"></div>
          <div>
            <p className="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400">Dirección de Red</p>
            <p className="text-lg font-mono font-black text-white tracking-tight mt-0.5">{printer.ip_address}</p>
            <p className="text-xs text-slate-400 mt-1">{printer.location || 'Sin ubicación asignada'}</p>
          </div>
          <div className="mt-3 sm:mt-0 flex gap-2">
            {isLoading ? (
              <Badge variant="warning" className="px-3 py-1.5 font-black uppercase text-[10px] animate-pulse">
                Analizando...
              </Badge>
            ) : data ? (
              <Badge 
                variant={data.live_status === 'online' ? 'success' : data.live_status === 'limited' ? 'warning' : 'error'}
                className="px-3 py-1.5 font-black uppercase text-[10px]"
              >
                {data.live_status === 'online' ? '🟢 En Línea' : data.live_status === 'limited' ? '🟡 Con Limitaciones' : '🔴 Fuera de Línea'}
              </Badge>
            ) : (
              <Badge variant="neutral" className="px-3 py-1.5 font-black uppercase text-[10px]">
                Sin datos
              </Badge>
            )}
          </div>
        </div>

        {/* Carga del Diagnóstico */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20 bg-slate-50/50 rounded-2xl border border-slate-100">
            <Spinner size="lg" text="Ejecutando escaneo de puertos y scraping de suministros en vivo..." />
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-3">Esto puede tardar hasta 15 segundos</p>
          </div>
        )}

        {/* Error o Sin Datos */}
        {!isLoading && !data && (
          <div className="flex flex-col items-center justify-center py-16 bg-red-50/30 rounded-2xl border border-red-100">
            <ShieldAlert size={48} className="text-red-500 mb-3 opacity-80" />
            <p className="text-sm font-black text-slate-800 uppercase tracking-wider">Error de Conexión</p>
            <p className="text-xs text-slate-500 mt-1 px-10 text-center">
              No se pudo establecer comunicación con el equipo en {printer.ip_address}. 
              Verifica que esté encendido y que el servidor tenga acceso a su red local.
            </p>
            <Button
              variant="outline"
              size="sm"
              icon={<RefreshCw size={14} />}
              onClick={loadDiagnostics}
              className="mt-5 border-red-200 text-red-700 hover:bg-red-50"
            >
              Reintentar Diagnóstico
            </Button>
          </div>
        )}

        {/* Contenido de diagnóstico */}
        {!isLoading && data && (
          <div className="space-y-5 animate-slide-up">
            {/* Tabs de Navegación */}
            <div className="flex bg-slate-100/80 p-1 rounded-xl border border-slate-200/50">
              <button
                onClick={() => setActiveTab('ports')}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-[10px] font-black uppercase tracking-wider rounded-lg transition-all ${
                  activeTab === 'ports'
                    ? 'bg-white text-slate-800 shadow-sm border border-slate-200/20'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Layers size={14} />
                Puertos y Servicios
              </button>
              <button
                onClick={() => setActiveTab('metrics')}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-[10px] font-black uppercase tracking-wider rounded-lg transition-all ${
                  activeTab === 'metrics'
                    ? 'bg-white text-slate-800 shadow-sm border border-slate-200/20'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Activity size={14} />
                Tóners y Lecturas
              </button>
              <button
                onClick={() => setActiveTab('opportunities')}
                className={`flex-1 flex items-center justify-center gap-2 py-2.5 text-[10px] font-black uppercase tracking-wider rounded-lg transition-all ${
                  activeTab === 'opportunities'
                    ? 'bg-white text-slate-800 shadow-sm border border-slate-200/20'
                    : 'text-slate-500 hover:text-slate-700'
                }`}
              >
                <Compass size={14} />
                Oportunidades de Integración
              </button>
            </div>

            {/* TAB: Puertos y Servicios */}
            {activeTab === 'ports' && (
              <div className="bg-white rounded-2xl border border-slate-200/60 overflow-hidden shadow-sm">
                <div className="px-5 py-3 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-wider">Servicio</span>
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-wider">Puerto</span>
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-wider">Estado</span>
                </div>
                <div className="divide-y divide-slate-100 max-h-[350px] overflow-y-auto custom-scrollbar">
                  {Object.entries(data.ports_diagnostics).map(([key, portInfo]: any) => (
                    <div key={key} className="px-5 py-3.5 flex justify-between items-center hover:bg-slate-50/50 transition-colors">
                      <div className="flex flex-col">
                        <span className="text-xs font-black text-slate-700 uppercase tracking-tight">{portInfo.service}</span>
                        <span className="text-[9px] font-bold text-slate-400 mt-0.5">Protocolo TCP</span>
                      </div>
                      <span className="text-xs font-mono font-bold text-slate-500">{portInfo.port}</span>
                      <div>
                        {portInfo.open ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-100">
                            <CheckCircle size={10} /> Abierto
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider bg-slate-100 text-slate-400 border border-slate-200">
                            <XCircle size={10} /> Cerrado
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB: Tóners y Lecturas */}
            {activeTab === 'metrics' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Suministros en Vivo */}
                <div className="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm space-y-4">
                  <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] border-b border-slate-100 pb-2">Suministros en Tiempo Real</h3>
                  {data.toner_diagnostics.success ? (
                    <div className="space-y-3.5 pt-2">
                      {/* Cyan */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px] font-black text-slate-600 uppercase">
                          <span>Cyan</span>
                          <span>{data.toner_diagnostics.levels.cyan}%</span>
                        </div>
                        <div className="bg-slate-100 rounded-full h-2 overflow-hidden relative">
                          <div className="bg-[#00FFFF] absolute left-0 top-0 h-full transition-all duration-500" style={{ width: `${data.toner_diagnostics.levels.cyan}%` }} />
                        </div>
                      </div>
                      {/* Magenta */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px] font-black text-slate-600 uppercase">
                          <span>Magenta</span>
                          <span>{data.toner_diagnostics.levels.magenta}%</span>
                        </div>
                        <div className="bg-slate-100 rounded-full h-2 overflow-hidden relative">
                          <div className="bg-[#FF00FF] absolute left-0 top-0 h-full transition-all duration-500" style={{ width: `${data.toner_diagnostics.levels.magenta}%` }} />
                        </div>
                      </div>
                      {/* Yellow */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px] font-black text-slate-600 uppercase">
                          <span>Amarillo</span>
                          <span>{data.toner_diagnostics.levels.yellow}%</span>
                        </div>
                        <div className="bg-slate-100 rounded-full h-2 overflow-hidden relative">
                          <div className="bg-[#FFFF00] absolute left-0 top-0 h-full transition-all duration-500" style={{ width: `${data.toner_diagnostics.levels.yellow}%` }} />
                        </div>
                      </div>
                      {/* Black */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[10px] font-black text-slate-600 uppercase">
                          <span>Negro</span>
                          <span>{data.toner_diagnostics.levels.black}%</span>
                        </div>
                        <div className="bg-slate-100 rounded-full h-2 overflow-hidden relative">
                          <div className="bg-slate-900 absolute left-0 top-0 h-full transition-all duration-500" style={{ width: `${data.toner_diagnostics.levels.black}%` }} />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-red-500 p-3 bg-red-50 rounded-xl border border-red-100">
                      ⚠️ No se pudieron leer los tóners: {data.toner_diagnostics.levels.error}
                    </div>
                  )}
                </div>

                {/* Contadores Físicos en Vivo */}
                <div className="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm space-y-4">
                  <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] border-b border-slate-100 pb-2">Contadores del Dispositivo</h3>
                  {data.counter_diagnostics.success ? (
                    <div className="grid grid-cols-2 gap-3 pt-1">
                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <p className="text-[9px] font-bold text-slate-400 uppercase">Impresiones Totales</p>
                        <p className="text-lg font-black text-slate-900 font-mono mt-0.5">{data.counter_diagnostics.counters.total.toLocaleString()}</p>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <p className="text-[9px] font-bold text-slate-400 uppercase">Copias Negro</p>
                        <p className="text-sm font-black text-slate-900 font-mono mt-0.5">{data.counter_diagnostics.counters.copier_black.toLocaleString()}</p>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <p className="text-[9px] font-bold text-slate-400 uppercase">Copias Color</p>
                        <p className="text-sm font-black text-slate-900 font-mono mt-0.5">{data.counter_diagnostics.counters.copier_color.toLocaleString()}</p>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <p className="text-[9px] font-bold text-slate-400 uppercase">Impresora Negro</p>
                        <p className="text-sm font-black text-slate-900 font-mono mt-0.5">{data.counter_diagnostics.counters.printer_black.toLocaleString()}</p>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <p className="text-[9px] font-bold text-slate-400 uppercase">Impresora Color</p>
                        <p className="text-sm font-black text-slate-900 font-mono mt-0.5">{data.counter_diagnostics.counters.printer_color.toLocaleString()}</p>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                        <p className="text-[9px] font-bold text-slate-400 uppercase">Escáner Total</p>
                        <p className="text-sm font-black text-slate-900 font-mono mt-0.5">{(data.counter_diagnostics.counters.scanner_black + data.counter_diagnostics.counters.scanner_color).toLocaleString()}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-xs text-red-500 p-3 bg-red-50 rounded-xl border border-red-100">
                      ⚠️ No se pudieron leer los contadores: {data.counter_diagnostics.counters.error}
                    </div>
                  )}

                  {/* Libreta de Direcciones Diagnóstico */}
                  <div className="bg-slate-900/5 p-4 rounded-2xl border border-slate-200/40 flex items-center justify-between gap-3 mt-4">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 bg-slate-900/10 text-slate-700 rounded-xl">
                        <Database size={16} />
                      </div>
                      <div>
                        <p className="text-xs font-black text-slate-700 uppercase tracking-tight">Agenda Física</p>
                        <p className="text-[9px] font-bold text-slate-400 mt-0.5">Contactos registrados en WIM</p>
                      </div>
                    </div>
                    <div>
                      {data.address_book_diagnostics.success ? (
                        <span className="text-lg font-black text-slate-900 font-mono">
                          {data.address_book_diagnostics.registered_users_count} <span className="text-[10px] font-bold text-slate-400 uppercase">Slots</span>
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400 font-bold">No leído</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB: Oportunidades de Integración */}
            {activeTab === 'opportunities' && (
              <div className="space-y-4 max-h-[380px] overflow-y-auto pr-2 custom-scrollbar">
                {Object.entries(data.ports_diagnostics).map(([key, portInfo]: any) => {
                  const opp = getPortOpportunity(key, portInfo.open);
                  return (
                    <div 
                      key={key} 
                      className={`p-4 rounded-2xl border flex gap-3.5 transition-all ${
                        portInfo.open
                          ? 'bg-emerald-50/30 border-emerald-200/60 shadow-sm'
                          : 'bg-slate-50/50 border-slate-200/40'
                      }`}
                    >
                      <div className={`p-2 rounded-xl h-fit ${portInfo.open ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-400'}`}>
                        <Shield size={16} />
                      </div>
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-black text-slate-800 uppercase tracking-tight">{portInfo.service}</span>
                          <span className="text-[9px] font-bold text-slate-400 font-mono">TCP {portInfo.port}</span>
                        </div>
                        <p className={`text-[11px] leading-relaxed ${portInfo.open ? 'text-slate-700 font-semibold' : 'text-slate-500'}`}>
                          {opp.text}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-6 border-t border-slate-100 bg-slate-50/50 -mx-6 -mb-6 px-6 py-4 rounded-b-2xl">
        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          {data && `Actualizado: ${new Date(data.timestamp).toLocaleTimeString()}`}
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={onClose} className="font-bold text-slate-500 hover:text-slate-700">
            Cerrar
          </Button>
          <Button
            onClick={loadDiagnostics}
            disabled={isLoading}
            icon={<RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />}
            className="bg-slate-900 hover:bg-slate-800 text-white font-bold"
          >
            Re-diagnosticar
          </Button>
        </div>
      </div>
    </Modal>
  );
};
