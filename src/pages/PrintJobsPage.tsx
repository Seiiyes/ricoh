import React, { useState, useEffect, useMemo } from 'react';
import { Printer, Search, RefreshCw, AlertCircle, FileText, User, Calendar, Layers, Hash } from 'lucide-react';
import { fetchPrinters, fetchPrinterJobs } from '../services/printerService';
import type { PrinterDevice } from '../types';
import { useNotification } from '../hooks/useNotification';
import { cn } from '../lib/utils';

interface PrintJob {
  job_id?: string;
  tipo: string;
  usuario: string;
  documento: string;
  fecha: string;
  paginas: number;
  copias?: number;
}

const PrintJobsPage = () => {
  const notify = useNotification();
  const [printers, setPrinters] = useState<PrinterDevice[]>([]);
  const [selectedPrinterId, setSelectedPrinterId] = useState<string>('');
  const [jobs, setJobs] = useState<PrintJob[]>([]);
  const [loadingPrinters, setLoadingPrinters] = useState(true);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUserFilter, setSelectedUserFilter] = useState<string | null>(null);
  const [showOnlyWithUser, setShowOnlyWithUser] = useState(false);

  // Cargar impresoras al montar el componente
  useEffect(() => {
    const loadPrinters = async () => {
      try {
        setLoadingPrinters(true);
        const data = await fetchPrinters();
        setPrinters(data);
        
        // Seleccionar la primera por defecto si hay
        if (data.length > 0) {
          setSelectedPrinterId(data[0].id);
        }
      } catch (err) {
        console.error('Error al cargar impresoras:', err);
        notify.error('Error', 'No se pudieron cargar las impresoras registradas.');
      } finally {
        setLoadingPrinters(false);
      }
    };
    loadPrinters();
  }, []);

  // Cargar trabajos de impresión al cambiar de impresora
  const loadJobs = async (printerId: string) => {
    if (!printerId) return;
    try {
      setLoadingJobs(true);
      setError(null);
      const data = await fetchPrinterJobs(Number(printerId));
      setJobs(data);
    } catch (err: any) {
      console.error('Error al cargar trabajos de impresión:', err);
      const detail = err.response?.data?.detail || 'No se pudo conectar con la impresora o verificar sus trabajos activos.';
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail));
      notify.error('Error', 'No se pudieron recuperar los trabajos de la impresora.');
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    if (selectedPrinterId) {
      loadJobs(selectedPrinterId);
      // Resetear filtros al cambiar de impresora
      setSearchTerm('');
      setSelectedUserFilter(null);
    }
  }, [selectedPrinterId]);

  const selectedPrinter = useMemo(() => {
    return printers.find(p => p.id === selectedPrinterId);
  }, [printers, selectedPrinterId]);

  // Lista de usuarios únicos que tienen trabajos activos en esta impresora
  const usersWithJobs = useMemo(() => {
    const users = new Set<string>();
    jobs.forEach(job => {
      if (job.usuario && job.usuario.trim() !== '') {
        users.add(job.usuario.trim());
      }
    });
    return Array.from(users).sort();
  }, [jobs]);

  // Filtrado de trabajos
  const filteredJobs = useMemo(() => {
    return jobs.filter(job => {
      const matchSearch = 
        job.documento?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.usuario?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.tipo?.toLowerCase().includes(searchTerm.toLowerCase());
        
      const matchUser = selectedUserFilter ? job.usuario === selectedUserFilter : true;
      const matchHasUser = showOnlyWithUser ? (job.usuario && job.usuario.trim() !== '' && job.usuario.toLowerCase() !== 'unknown' && job.usuario.toLowerCase() !== 'anónimo') : true;

      return matchSearch && matchUser && matchHasUser;
    });
  }, [jobs, searchTerm, selectedUserFilter, showOnlyWithUser]);

  const handleRefresh = () => {
    if (selectedPrinterId) {
      loadJobs(selectedPrinterId);
    }
  };

  return (
    <div className="h-full overflow-auto bg-slate-50 animate-fade-in relative pb-12">
      <div className="container-padding container-padding-y max-w-7xl mx-auto">
        
        {/* Cabecera Premium */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white rounded-xl shadow-sm border border-slate-100">
              <Printer size={24} className="text-ricoh-red" />
            </div>
            <div>
              <h1 className="text-responsive-xl font-bold text-slate-900 tracking-tight">Trabajos de Impresión</h1>
              <p className="text-slate-500 text-responsive-sm mt-0.5">Monitoreo y consulta de cola de trabajos en tiempo real</p>
            </div>
          </div>
          
          <button
            onClick={handleRefresh}
            disabled={loadingJobs || !selectedPrinterId}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-slate-200 hover:border-slate-300 font-semibold text-sm rounded-xl text-slate-700 shadow-sm hover:shadow transition-all disabled:opacity-50"
          >
            <RefreshCw size={16} className={cn(loadingJobs && 'animate-spin')} />
            Actualizar
          </button>
        </div>

        {/* Panel Superior: Selección de Impresora */}
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/40 border border-slate-100 p-6 mb-6">
          <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3">
            Seleccionar Impresora Ricoh
          </label>
          {loadingPrinters ? (
            <div className="h-12 bg-slate-100 rounded-xl animate-pulse" />
          ) : printers.length === 0 ? (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-sm">
              No hay impresoras registradas en el sistema. Vaya a la sección de "Buscar Equipos" para agregar impresoras.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <select
                  value={selectedPrinterId}
                  onChange={(e) => setSelectedPrinterId(e.target.value)}
                  className="w-full px-4 py-3 border border-slate-200 bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent transition-all shadow-sm hover:border-slate-300"
                >
                  {printers.map((printer) => (
                    <option key={printer.id} value={printer.id}>
                      {printer.hostname || 'Sin Hostname'} — {printer.ip_address} {printer.serial_number ? `(${printer.serial_number})` : ''}
                    </option>
                  ))}
                </select>
              </div>
              
              {selectedPrinter && (
                <div className="flex flex-col justify-center px-4 py-2 bg-slate-50 border border-slate-100 rounded-xl text-xs space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-400 font-semibold">IP:</span>
                    <span className="font-mono text-slate-700 font-bold">{selectedPrinter.ip_address}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400 font-semibold">Serial:</span>
                    <span className="font-mono text-slate-700 font-bold">{selectedPrinter.serial_number || 'No especificado'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400 font-semibold">Ubicación:</span>
                    <span className="text-slate-700 font-bold">{selectedPrinter.location || 'Sin ubicación'}</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Panel Principal de Trabajos */}
        {selectedPrinterId && (
          <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/40 border border-slate-100 overflow-hidden">
            
            {/* Barra de Filtros y Búsqueda */}
            <div className="p-6 border-b border-slate-100 space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                {/* Caja de Búsqueda */}
                <div className="relative max-w-md w-full">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                  <input
                    type="text"
                    placeholder="Buscar por documento, usuario, tipo..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-11 pr-4 py-2.5 border border-slate-200 bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent transition-all shadow-sm hover:border-slate-300 placeholder-slate-400"
                  />
                </div>
                
                {/* Opciones de Filtrado */}
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={showOnlyWithUser}
                      onChange={(e) => {
                        setShowOnlyWithUser(e.target.checked);
                        if (e.target.checked && selectedUserFilter === 'unknown') {
                          setSelectedUserFilter(null);
                        }
                      }}
                      className="rounded text-ricoh-red focus:ring-ricoh-red border-slate-300 w-4 h-4"
                    />
                    <span className="text-sm font-semibold text-slate-600 group-hover:text-slate-800 transition-colors">
                      Solo usuarios con trabajos asignados
                    </span>
                  </label>
                </div>
              </div>

              {/* Filtros Rápidos por Usuario (si hay trabajos) */}
              {usersWithJobs.length > 0 && (
                <div className="pt-2">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">
                    Filtrar por usuario con trabajos activos
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => setSelectedUserFilter(null)}
                      className={cn(
                        "px-3 py-1.5 rounded-lg text-xs font-bold transition-all border",
                        selectedUserFilter === null
                          ? "bg-slate-900 border-slate-900 text-white shadow-sm"
                          : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                      )}
                    >
                      Todos ({jobs.length})
                    </button>
                    {usersWithJobs.map(user => {
                      const userCount = jobs.filter(j => j.usuario === user).length;
                      return (
                        <button
                          key={user}
                          onClick={() => setSelectedUserFilter(user === selectedUserFilter ? null : user)}
                          className={cn(
                            "px-3 py-1.5 rounded-lg text-xs font-bold transition-all border flex items-center gap-1.5",
                            selectedUserFilter === user
                              ? "bg-ricoh-red border-ricoh-red text-white shadow-sm"
                              : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                          )}
                        >
                          <User size={12} />
                          {user} ({userCount})
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Error View */}
            {error && (
              <div className="p-8 text-center">
                <div className="max-w-md mx-auto p-6 bg-red-50 border border-red-200 rounded-2xl flex flex-col items-center">
                  <AlertCircle className="text-red-500 mb-3" size={36} />
                  <h3 className="text-sm font-bold text-red-800 uppercase tracking-widest">Error al conectar</h3>
                  <p className="text-sm text-red-900 mt-2 break-all">{error}</p>
                  <button
                    onClick={handleRefresh}
                    className="mt-4 px-4 py-2 bg-white border border-red-200 hover:bg-red-50 text-red-800 font-semibold text-xs rounded-xl transition-all shadow-sm"
                  >
                    Reintentar conexión
                  </button>
                </div>
              </div>
            )}

            {/* Loading jobs skeleton */}
            {loadingJobs && !error && (
              <div className="p-8 space-y-4">
                <div className="h-8 bg-slate-100 rounded-lg animate-pulse" />
                <div className="h-12 bg-slate-100 rounded-lg animate-pulse" />
                <div className="h-12 bg-slate-100 rounded-lg animate-pulse" />
                <div className="h-12 bg-slate-100 rounded-lg animate-pulse" />
              </div>
            )}

            {/* Jobs Table */}
            {!loadingJobs && !error && (
              <>
                {filteredJobs.length === 0 ? (
                  <div className="p-12 text-center text-slate-500">
                    <FileText className="h-12 w-12 opacity-20 mx-auto mb-3" />
                    <p className="text-sm font-bold text-slate-700">No se encontraron trabajos de impresión</p>
                    <p className="text-xs mt-1.5 max-w-sm mx-auto">
                      {jobs.length === 0 
                        ? 'La impresora seleccionada no reporta trabajos en cola o almacenados en este momento.'
                        : 'Ajuste los filtros de búsqueda para ver otros resultados.'}
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-50 border-b border-slate-100">
                        <tr>
                          <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[120px]">
                            ID Trabajo
                          </th>
                          <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
                            Documento
                          </th>
                          <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[150px]">
                            Usuario
                          </th>
                          <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[130px]">
                            Tipo
                          </th>
                          <th className="px-6 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[180px]">
                            Fecha / Hora
                          </th>
                          <th className="px-6 py-4 text-center text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[80px]">
                            Páginas
                          </th>
                          <th className="px-6 py-4 text-center text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[80px]">
                            Copias
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-slate-100">
                        {filteredJobs.map((job, idx) => (
                          <tr key={job.job_id || idx} className="hover:bg-slate-50/80 transition-colors group">
                            <td className="px-6 py-4 whitespace-nowrap font-mono text-xs text-slate-500">
                              <div className="flex items-center gap-1.5">
                                <Hash size={12} className="text-slate-400" />
                                {job.job_id || `—`}
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-2 max-w-md md:max-w-lg lg:max-w-xl">
                                <FileText size={16} className="text-slate-400 shrink-0" />
                                <div className="text-sm font-semibold text-slate-800 truncate" title={job.documento}>
                                  {job.documento || 'Documento sin nombre'}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-2">
                                <div className={cn(
                                  "w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-black uppercase shadow-sm",
                                  job.usuario && job.usuario.trim() !== '' && job.usuario.toLowerCase() !== 'unknown'
                                    ? "bg-red-50 text-ricoh-red border border-red-100"
                                    : "bg-slate-100 text-slate-400"
                                )}>
                                  {job.usuario ? job.usuario.slice(0, 2).toUpperCase() : 'AN'}
                                </div>
                                <span className={cn(
                                  "text-sm font-semibold",
                                  job.usuario && job.usuario.trim() !== '' && job.usuario.toLowerCase() !== 'unknown'
                                    ? "text-slate-800"
                                    : "text-slate-400 italic"
                                )}>
                                  {job.usuario || 'Anónimo'}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={cn(
                                "inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider rounded-md border shadow-sm",
                                job.tipo?.toLowerCase().includes('color')
                                  ? "bg-purple-50 text-purple-700 border-purple-200"
                                  : job.tipo?.toLowerCase().includes('copia')
                                  ? "bg-blue-50 text-blue-700 border-blue-200"
                                  : "bg-slate-50 text-slate-600 border-slate-200"
                              )}>
                                <Layers size={10} />
                                {job.tipo || 'Impresión'}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-600 font-medium">
                              <div className="flex items-center gap-1.5">
                                <Calendar size={12} className="text-slate-400" />
                                {job.fecha || 'Desconocida'}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-black text-slate-800 font-mono">
                              {job.paginas}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-bold text-slate-600 font-mono">
                              {job.copias !== undefined && job.copias !== null ? job.copias : 1}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                
                {/* Totalizador al pie */}
                <div className="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-between text-xs font-semibold text-slate-500">
                  <div>
                    Mostrando <span className="text-slate-800 font-bold">{filteredJobs.length}</span> de <span className="text-slate-800 font-bold">{jobs.length}</span> trabajos activos
                  </div>
                  <div>
                    Total Páginas en Cola: <span className="text-ricoh-red font-black text-sm font-mono">{filteredJobs.reduce((acc, job) => acc + (job.paginas || 0) * (job.copias || 1), 0)}</span>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PrintJobsPage;
