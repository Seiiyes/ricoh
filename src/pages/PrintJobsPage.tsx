import { useState, useEffect, useMemo } from 'react';
import { Printer, Search, RefreshCw, AlertCircle, FileText, User, Calendar, Layers, Trash2, Loader2 } from 'lucide-react';
import { fetchPrinters, fetchPrinterJobs, fetchConsolidatedPrinterJobs, deletePrinterJob } from '../services/printerService';
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
  printer_id?: number;
  printer_ip?: string;
  printer_hostname?: string;
  printer_serial?: string;
}

const PrintJobsPage = () => {
  const notify = useNotification();
  const [printers, setPrinters] = useState<PrinterDevice[]>([]);
  const [selectedPrinterIds, setSelectedPrinterIds] = useState<(string | number)[]>([]);
  const [jobs, setJobs] = useState<PrintJob[]>([]);
  const [loadingPrinters, setLoadingPrinters] = useState(true);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deletingJobId, setDeletingJobId] = useState<string | null>(null);
  
  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUserFilter, setSelectedUserFilter] = useState<string | null>(null);
  const [showOnlyWithUser, setShowOnlyWithUser] = useState(false);

  // Paginación
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

  // Derivados
  const showPrinterColumn = useMemo(() => {
    return selectedPrinterIds.includes('consolidated') || selectedPrinterIds.length > 1;
  }, [selectedPrinterIds]);

  // Cargar impresoras al montar el componente
  useEffect(() => {
    const loadPrinters = async () => {
      try {
        setLoadingPrinters(true);
        const data = await fetchPrinters();
        setPrinters(data);
        
        // Seleccionar "consolidated" por defecto si hay impresoras
        if (data.length > 0) {
          setSelectedPrinterIds(['consolidated']);
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

  // Cargar trabajos de impresión para los equipos seleccionados
  const loadJobs = async (printerIds: (string | number)[]) => {
    if (!printerIds || printerIds.length === 0) return;
    try {
      setLoadingJobs(true);
      setError(null);
      let data;
      if (printerIds.includes('consolidated')) {
        data = await fetchConsolidatedPrinterJobs();
      } else {
        // Consultar de forma concurrente solo las impresoras seleccionadas
        const promises = printerIds.map(async (id) => {
          const printerObj = printers.find(p => p.id === id);
          const jobsData = await fetchPrinterJobs(Number(id));
          // Inyectamos metadatos de la impresora en cada registro para homogeneizar columnas
          return jobsData.map(job => ({
            ...job,
            printer_id: Number(id),
            printer_ip: printerObj?.ip_address,
            printer_hostname: printerObj?.hostname || "Sin Hostname",
            printer_serial: printerObj?.serial_number || "Sin Serial"
          }));
        });
        const results = await Promise.all(promises);
        data = results.flat();
      }
      setJobs(data);
    } catch (err: any) {
      console.error('Error al cargar trabajos de impresión:', err);
      const detail = err.response?.data?.detail || 'No se pudo conectar con alguna de las impresoras seleccionadas para verificar sus trabajos activos.';
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail));
      notify.error('Error', 'No se pudieron recuperar los trabajos de las impresoras seleccionadas.');
    } finally {
      setLoadingJobs(false);
    }
  };

  const selectedPrinterIdsStr = selectedPrinterIds.join(',');

  useEffect(() => {
    if (selectedPrinterIds.length > 0) {
      loadJobs(selectedPrinterIds);
      // Resetear filtros al cambiar de impresora
      setSearchTerm('');
      setSelectedUserFilter(null);
      setCurrentPage(1);
    }
  }, [selectedPrinterIdsStr]);

  // Resetear página al cambiar filtros
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, selectedUserFilter, showOnlyWithUser]);



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

  // Total de páginas
  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(filteredJobs.length / itemsPerPage));
  }, [filteredJobs.length, itemsPerPage]);

  // Trabajos paginados para mostrar en la vista
  const paginatedJobs = useMemo(() => {
    const startIdx = (currentPage - 1) * itemsPerPage;
    return filteredJobs.slice(startIdx, startIdx + itemsPerPage);
  }, [filteredJobs, currentPage, itemsPerPage]);

  // Índice inicial de fila para el contador
  const startIndex = useMemo(() => {
    return (currentPage - 1) * itemsPerPage;
  }, [currentPage, itemsPerPage]);

  const handleRefresh = () => {
    if (selectedPrinterIds.length > 0) {
      loadJobs(selectedPrinterIds);
    }
  };

  const handleDeleteJob = async (jobId: string, jobPrinterId?: number) => {
    const firstSelectedPrinterId = selectedPrinterIds.find(id => id !== 'consolidated');
    const targetPrinterId = jobPrinterId || Number(firstSelectedPrinterId);
    if (!targetPrinterId || isNaN(targetPrinterId)) {
      notify.error('Error', 'No se pudo determinar el ID de la impresora para eliminar el trabajo.');
      return;
    }
    
    const confirmDelete = window.confirm('¿Está seguro de que desea eliminar este trabajo de impresión de la impresora? Esta acción no se puede deshacer.');
    if (!confirmDelete) return;

    try {
      setDeletingJobId(jobId);
      await deletePrinterJob(targetPrinterId, jobId);
      notify.success('Trabajo eliminado', 'El trabajo de impresión ha sido cancelado y eliminado con éxito.');
      // Refrescar lista de trabajos
      loadJobs(selectedPrinterIds);
    } catch (err: any) {
      console.error('Error al eliminar trabajo de impresión:', err);
      const detail = err.response?.data?.detail || 'No se pudo eliminar el trabajo de impresión de la impresora.';
      notify.error('Error al eliminar', typeof detail === 'string' ? detail : JSON.stringify(detail));
    } finally {
      setDeletingJobId(null);
    }
  };

  return (
    <div className="h-full overflow-auto bg-slate-50 animate-fade-in relative pb-12">
      <div className="container-padding container-padding-y w-full">
        
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
            disabled={loadingJobs || selectedPrinterIds.length === 0}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-slate-200 hover:border-slate-300 font-semibold text-sm rounded-xl text-slate-700 shadow-sm hover:shadow transition-all disabled:opacity-50"
          >
            <RefreshCw size={16} className={cn(loadingJobs && 'animate-spin')} />
            Actualizar
          </button>
        </div>

        {/* Panel Superior: Selección de Impresora (Tarjetas/Grid) */}
        <div className="mb-6">
          <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-3">
            Seleccionar Impresora Ricoh (Seleccione un equipo para ver su cola de trabajos)
          </label>
          {loadingPrinters ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="h-32 bg-slate-100 rounded-xl animate-pulse" />
              <div className="h-32 bg-slate-100 rounded-xl animate-pulse" />
              <div className="h-32 bg-slate-100 rounded-xl animate-pulse" />
            </div>
          ) : printers.length === 0 ? (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-sm">
              No hay impresoras registradas en el sistema. Vaya a la sección de "Buscar Equipos" para agregar impresoras.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[290px] overflow-y-auto pr-1">
              {/* Tarjeta de Consolidado */}
              <button
                onClick={() => setSelectedPrinterIds(['consolidated'])}
                className={cn(
                  "text-left p-4 rounded-xl border-2 transition-all duration-200 shadow-sm flex flex-col justify-between h-32 relative overflow-hidden",
                  selectedPrinterIds.includes('consolidated')
                    ? 'border-ricoh-red bg-red-50/10 ring-2 ring-red-500/5'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                )}
              >
                <div className="w-full">
                  <div className="flex justify-between items-start mb-1">
                    <span className={cn(
                      "text-sm font-bold flex items-center gap-1.5",
                      selectedPrinterIds.includes('consolidated') ? 'text-ricoh-red' : 'text-slate-800'
                    )}>
                      📋 Consolidado de Trabajos
                    </span>
                    {selectedPrinterIds.includes('consolidated') && (
                      <span className="text-[9px] bg-ricoh-red text-white px-2.5 py-0.5 rounded-full font-black uppercase tracking-wider">
                        Activo
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-400 font-semibold">Vista de toda la flota en un solo lugar</p>
                </div>
                <div className="text-[11px] text-slate-500 space-y-0.5 w-full">
                  <p><span className="font-semibold text-slate-600">IP:</span> Varias / Flota completa</p>
                  <p><span className="font-semibold text-slate-600">Equipos:</span> {printers.length} registrados</p>
                  <p className="truncate"><span className="font-semibold text-slate-600">Ubicación:</span> Todas las áreas</p>
                </div>
              </button>

              {/* Tarjetas de Impresoras */}
              {printers.map((printer) => {
                const isSelected = selectedPrinterIds.includes(printer.id);
                return (
                  <button
                    key={printer.id}
                    onClick={() => {
                      setSelectedPrinterIds(prev => {
                        if (prev.includes('consolidated')) {
                          return [printer.id];
                        }
                        if (prev.includes(printer.id)) {
                          const next = prev.filter(id => id !== printer.id);
                          return next.length === 0 ? ['consolidated'] : next;
                        }
                        return [...prev, printer.id];
                      });
                    }}
                    className={cn(
                      "text-left p-4 rounded-xl border-2 transition-all duration-200 shadow-sm flex flex-col justify-between h-32 relative overflow-hidden",
                      isSelected
                        ? 'border-ricoh-red bg-red-50/10 ring-2 ring-red-500/5'
                        : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                    )}
                  >
                    <div className="w-full">
                      <div className="flex justify-between items-start mb-1">
                        <span className={cn(
                          "font-mono text-sm font-bold truncate block max-w-[170px]",
                          isSelected ? 'text-ricoh-red' : 'text-slate-800'
                        )}>
                          {printer.hostname || 'Sin Hostname'}
                        </span>
                        {isSelected && (
                          <span className="text-[9px] bg-ricoh-red text-white px-2.5 py-0.5 rounded-full font-black uppercase tracking-wider">
                            Activo
                          </span>
                        )}
                      </div>
                      {printer.detected_model && printer.detected_model.toLowerCase() !== 'desconocido' ? (
                        <p className="text-[10px] text-slate-400 font-semibold">Modelo: {printer.detected_model}</p>
                      ) : (
                        <div className="h-4" />
                      )}
                    </div>
                    
                    <div className="text-[11px] text-slate-500 space-y-0.5 w-full">
                      <p><span className="font-semibold text-slate-600">IP:</span> {printer.ip_address}</p>
                      <p><span className="font-semibold text-slate-600">Serial:</span> {printer.serial_number || 'Sin Serial'}</p>
                      <p className="truncate"><span className="font-semibold text-slate-600">Ubicación:</span> {printer.location || 'Sin ubicación'}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Panel Principal de Trabajos */}
        {selectedPrinterIds.length > 0 && (
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

              {/* Controles de Paginación Superiores */}
              {!loadingJobs && !error && filteredJobs.length > 0 && (
                <div className="pt-4 border-t border-slate-100/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-semibold text-slate-500">
                  <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-1.5">
                      <span>Mostrar</span>
                      <select
                        value={itemsPerPage}
                        onChange={(e) => {
                          setItemsPerPage(Number(e.target.value));
                          setCurrentPage(1);
                        }}
                        className="bg-white border border-slate-200 rounded-lg px-2 py-1 text-slate-700 font-bold focus:outline-none focus:ring-1 focus:ring-ricoh-red focus:border-transparent transition-all shadow-sm cursor-pointer"
                      >
                        <option value={10}>10</option>
                        <option value={25}>25</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                      </select>
                      <span>registros</span>
                    </div>
                    
                    <div className="h-4 w-px bg-slate-200 hidden sm:block" />
                    
                    <div>
                      Mostrando <span className="text-slate-800 font-bold">{filteredJobs.length > 0 ? startIndex + 1 : 0}</span>-
                      <span className="text-slate-800 font-bold">{Math.min(startIndex + itemsPerPage, filteredJobs.length)}</span> de 
                      <span className="text-slate-800 font-bold"> {filteredJobs.length}</span> ({jobs.length} en total)
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4">
                    <div className="text-right">
                      Total Páginas en Cola: <span className="text-ricoh-red font-black text-sm font-mono">{filteredJobs.reduce((acc, job) => acc + (job.paginas || 0) * (job.copias || 1), 0)}</span>
                    </div>

                    {totalPages > 1 && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                          disabled={currentPage === 1}
                          className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm font-bold flex items-center gap-1"
                          aria-label="Página anterior"
                        >
                          ← Anterior
                        </button>
                        <span className="px-3 py-1.5 text-slate-700 bg-white border border-slate-100 rounded-lg shadow-sm font-bold font-mono">
                          {currentPage} / {totalPages}
                        </span>
                        <button
                          onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                          disabled={currentPage === totalPages}
                          className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm font-bold flex items-center gap-1"
                          aria-label="Página siguiente"
                        >
                          Siguiente →
                        </button>
                      </div>
                    )}
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
                        ? (selectedPrinterIds.includes('consolidated') 
                            ? 'Ninguna impresora de la flota reporta trabajos en cola o almacenados en este momento.'
                            : 'Ninguna de las impresoras seleccionadas reporta trabajos en cola o almacenados en este momento.')
                        : 'Ajuste los filtros de búsqueda para ver otros resultados.'}
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-50 border-b border-slate-100">
                        <tr>
                          {showPrinterColumn && (
                            <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[150px] hidden md:table-cell">
                              Impresora
                            </th>
                          )}
                          <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">
                            Documento
                          </th>
                          <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[120px]">
                            Usuario
                          </th>
                          <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[120px] hidden sm:table-cell">
                            Tipo
                          </th>
                          <th className="px-4 py-4 text-left text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[160px] hidden md:table-cell">
                            Fecha / Hora
                          </th>
                          <th className="px-4 py-4 text-center text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[70px]">
                            Páginas
                          </th>
                          <th className="px-4 py-4 text-center text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[70px] hidden sm:table-cell">
                            Copias
                          </th>
                          <th className="px-4 py-4 text-center text-[11px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap w-[80px]">
                            Acciones
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-slate-100">
                        {paginatedJobs.map((job, idx) => (
                          <tr key={job.job_id || idx} className="hover:bg-slate-50/80 transition-colors group">
                            {showPrinterColumn && (
                              <td className="px-4 py-4 whitespace-nowrap hidden md:table-cell">
                                <div className="text-xs text-slate-700 font-bold">
                                  {job.printer_hostname || 'Sin Hostname'}
                                </div>
                                <div className="text-[10px] text-slate-500 font-mono font-semibold">
                                  IP: {job.printer_ip}
                                </div>
                                {job.printer_serial && job.printer_serial !== 'Sin Serial' && (
                                  <div className="text-[9px] text-slate-400 font-mono">
                                    S/N: {job.printer_serial}
                                  </div>
                                )}
                              </td>
                            )}
                            <td className="px-4 py-4">
                              <div className="flex flex-col">
                                <div className="flex items-center gap-2 max-w-xs sm:max-w-md md:max-w-[400px]">
                                  <FileText size={16} className="text-slate-400 shrink-0" />
                                  <div className="text-sm font-semibold text-slate-800 truncate" title={job.documento}>
                                    {job.documento || 'Documento sin nombre'}
                                  </div>
                                </div>
                                
                                {/* Info secundaria responsiva bajo el documento */}
                                <div className="flex flex-col gap-0.5 mt-1">
                                  {/* Hostname e IP de Impresora (vista consolidada) en móviles/tablets */}
                                  {showPrinterColumn && (
                                    <div className="md:hidden text-[10px] text-slate-500 font-medium">
                                      <span className="font-bold text-slate-600">{job.printer_hostname || 'Sin Hostname'}</span>
                                      <span className="font-mono ml-1">({job.printer_ip})</span>
                                    </div>
                                  )}
                                  
                                  {/* Tipo, fecha/hora y copias en pantallas pequeñas */}
                                  <div className="flex flex-wrap items-center gap-1.5 mt-0.5">
                                    {/* Tipo de trabajo (oculto en sm:table-cell) */}
                                    <span className="sm:hidden inline-flex items-center gap-0.5 px-1 py-0.2 text-[9px] font-bold uppercase tracking-wider rounded bg-slate-100 text-slate-600 border border-slate-200">
                                      {job.tipo || 'Impresión'}
                                    </span>
                                    
                                    {/* Copias (oculto en sm:table-cell) */}
                                    <span className="sm:hidden text-[10px] text-slate-500 font-medium font-mono">
                                      {job.copias !== undefined && job.copias !== null ? job.copias : 1} {job.copias === 1 ? 'copia' : 'copias'}
                                    </span>
                                    
                                    {/* Fecha/Hora (oculto en md:table-cell) */}
                                    <span className="md:hidden text-[10px] text-slate-400 font-medium font-mono">
                                      {job.fecha || 'Desconocida'}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-4 whitespace-nowrap">
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
                            <td className="px-4 py-4 whitespace-nowrap hidden sm:table-cell">
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
                            <td className="px-4 py-4 whitespace-nowrap text-xs text-slate-600 font-medium hidden md:table-cell">
                              <div className="flex items-center gap-1.5">
                                <Calendar size={12} className="text-slate-400" />
                                {job.fecha || 'Desconocida'}
                              </div>
                            </td>
                            <td className="px-4 py-4 whitespace-nowrap text-center text-sm font-black text-slate-800 font-mono">
                              {job.paginas}
                            </td>
                            <td className="px-4 py-4 whitespace-nowrap text-center text-sm font-bold text-slate-600 font-mono hidden sm:table-cell">
                              {job.copias !== undefined && job.copias !== null ? job.copias : 1}
                            </td>
                            <td className="px-4 py-4 whitespace-nowrap text-center text-sm">
                              {job.job_id ? (
                                <button
                                  onClick={() => handleDeleteJob(job.job_id!, job.printer_id)}
                                  disabled={deletingJobId !== null}
                                  className={cn(
                                    "p-1.5 rounded-lg border text-rose-600 hover:text-rose-700 hover:bg-rose-50 transition-all shadow-sm",
                                    deletingJobId === job.job_id
                                      ? "bg-slate-100 border-slate-200 text-slate-400"
                                      : "bg-white border-slate-200"
                                  )}
                                  title="Eliminar Trabajo"
                                >
                                  {deletingJobId === job.job_id ? (
                                    <Loader2 size={16} className="animate-spin text-slate-400" />
                                  ) : (
                                    <Trash2 size={16} />
                                  )}
                                </button>
                              ) : (
                                <span className="text-slate-300 italic text-xs">—</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
                
                {/* Paginador y Totalizador al pie */}
                <div className="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-semibold text-slate-500">
                  <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-1.5">
                      <span>Mostrar</span>
                      <select
                        value={itemsPerPage}
                        onChange={(e) => {
                          setItemsPerPage(Number(e.target.value));
                          setCurrentPage(1);
                        }}
                        className="bg-white border border-slate-200 rounded-lg px-2 py-1 text-slate-700 font-bold focus:outline-none focus:ring-1 focus:ring-ricoh-red focus:border-transparent transition-all shadow-sm cursor-pointer"
                      >
                        <option value={10}>10</option>
                        <option value={25}>25</option>
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                      </select>
                      <span>registros</span>
                    </div>
                    
                    <div className="h-4 w-px bg-slate-200 hidden sm:block" />
                    
                    <div>
                      Mostrando <span className="text-slate-800 font-bold">{filteredJobs.length > 0 ? startIndex + 1 : 0}</span>-
                      <span className="text-slate-800 font-bold">{Math.min(startIndex + itemsPerPage, filteredJobs.length)}</span> de 
                      <span className="text-slate-800 font-bold"> {filteredJobs.length}</span> ({jobs.length} en total)
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4">
                    <div className="text-right">
                      Total Páginas en Cola: <span className="text-ricoh-red font-black text-sm font-mono">{filteredJobs.reduce((acc, job) => acc + (job.paginas || 0) * (job.copias || 1), 0)}</span>
                    </div>

                    {totalPages > 1 && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                          disabled={currentPage === 1}
                          className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm font-bold flex items-center gap-1"
                          aria-label="Página anterior"
                        >
                          ← Anterior
                        </button>
                        <span className="px-3 py-1.5 text-slate-700 bg-white border border-slate-100 rounded-lg shadow-sm font-bold font-mono">
                          {currentPage} / {totalPages}
                        </span>
                        <button
                          onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                          disabled={currentPage === totalPages}
                          className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm font-bold flex items-center gap-1"
                          aria-label="Página siguiente"
                        >
                          Siguiente →
                        </button>
                      </div>
                    )}
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
