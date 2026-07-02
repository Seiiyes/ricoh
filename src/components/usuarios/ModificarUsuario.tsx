import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Save, Printer, ShieldCheck, Settings, Globe, Trash2, Plus, RefreshCw } from 'lucide-react';
import { actualizarUsuario, obtenerUsuarioConEquipos, actualizarPermisosAsignacion, crearUsuario, obtenerDetallesUsuarioImpresora, sincronizarUsuarioTodasImpresoras, desasignarEquipos } from '@/services/servicioUsuarios';
import { EditorPermisos } from './EditorPermisos';
import { GestorEquipos } from './GestorEquipos';
import { Button, Alert, Spinner, Input, EmpresaAutocomplete, CentroCostosAutocomplete } from '@/components/ui';
import type { Usuario, ImpresoraUsuario } from '@/types/usuario';

interface ModificarUsuarioProps {
  usuario: Usuario | null;
  onCerrar: () => void;
  onUsuarioGuardado?: () => void;
}

export const ModificarUsuario = ({
  usuario,
  onCerrar,
  onUsuarioGuardado,
}: ModificarUsuarioProps) => {
  const [idLocal, setIdLocal] = useState<number | string>(usuario?.id || '');
  const [cargandoDatos, setCargandoDatos] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [sincronizandoImpresoras, setSincronizandoImpresoras] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);

  // Control de cambios sin guardar
  const [tieneCambiosSinGuardar, setTieneCambiosSinGuardar] = useState(false);

  // Tabs de navegación interna
  const [tabActiva, setTabActiva] = useState<'info' | 'permisos' | 'equipos'>('info');
  const [impresoraSeleccionada, setImpresoraSeleccionada] = useState<ImpresoraUsuario | null>(null);
  const [cargandoPermisos, setCargandoPermisos] = useState(false);
  // Track which printer_ids are currently loading permissions from physical device
  const [cargandoPermisoIds, setCargandoPermisoIds] = useState<Set<number>>(new Set());
  // Track which printer_ids have already been loaded from the physical device
  const [permisosYaCargados, setPermisosYaCargados] = useState<Set<number>>(new Set());

  // Datos del formulario
  const [nombre, setNombre] = useState('');
  const [codigo, setCodigo] = useState('');
  const [empresa, setEmpresa] = useState('');
  const [centroCostos, setCentroCostos] = useState('');
  const [usuarioRed, setUsuarioRed] = useState('reliteltda\\scaner');
  const [carpeta, setCarpeta] = useState('');

  // Permisos (Por Impresora)
  const [permisos, setPermisos] = useState({
    func_copier: false,
    func_copier_color: false,
    func_printer: false,
    func_printer_color: false,
    func_document_server: false,
    func_fax: false,
    func_scanner: false,
    func_browser: false,
  });

  // Permisos Base (Maestros)
  const [permisosBase, setPermisosBase] = useState({
    func_copier: false,
    func_copier_color: false,
    func_printer: false,
    func_printer_color: false,
    func_document_server: false,
    func_fax: false,
    func_scanner: false,
    func_browser: false,
  });

  // Equipos asignados (con sus metadatos)
  const [impresorasAsignadas, setImpresorasAsignadas] = useState<ImpresoraUsuario[]>([]);
  const [equipoIds, setEquipoIds] = useState<number[]>([]);
  const [sincronizarPermisosBase, setSincronizarPermisosBase] = useState(false);

  // Cargar datos al abrir
  useEffect(() => {
    if (usuario) {
      setIdLocal(usuario.id);
      cargarDatosIniciales(usuario.id);
    }
  }, [usuario]);

  const cargarDatosIniciales = async (userId = usuario?.id) => {
    if (!usuario || !userId) return;

    setNombre(usuario.name);
    setCodigo(usuario.codigo_de_usuario);
    setEmpresa(usuario.empresa || '');
    setCentroCostos(usuario.centro_costos || '');
    setUsuarioRed(usuario.network_username || 'reliteltda\\scaner');
    setCarpeta(usuario.smb_path || '');

    // Cargar permisos base/maestros
    setPermisosBase({
      func_copier: usuario.func_copier || false,
      func_copier_color: usuario.func_copier_color || false,
      func_printer: usuario.func_printer || false,
      func_printer_color: usuario.func_printer_color || false,
      func_document_server: usuario.func_document_server || false,
      func_fax: usuario.func_fax || false,
      func_scanner: usuario.func_scanner || false,
      func_browser: usuario.func_browser || false,
    });

    // Si viene de impresora, ya tiene el array poblado
    if (usuario.impresoras && usuario.impresoras.length > 0) {
      setImpresorasAsignadas(usuario.impresoras);
      setEquipoIds(usuario.impresoras.map(p => p.printer_id));
      // Seleccionar la primera por defecto para ver sus permisos
      setImpresoraSeleccionada(usuario.impresoras[0]);
    }

    // Si tiene ID numérico, cargar datos extendidos de DB
    if (!isNaN(Number(userId)) && userId.toString().trim() !== '' && !userId.toString().startsWith('printer_')) {
      try {
        setCargandoDatos(true);
        const dataConEquipos = await obtenerUsuarioConEquipos(Number(userId));
        if (dataConEquipos.equipos) {
          const mappedImpresoras: ImpresoraUsuario[] = dataConEquipos.equipos.map((eq: any) => ({
            id: eq.id,
            printer_id: eq.printer_id,
            printer_name: eq.printer_name,
            printer_ip: eq.printer_ip,
            printer_location: eq.printer_location || '',
            entry_index: eq.entry_index,
            permisos: eq.permisos
          }));
          setImpresorasAsignadas(mappedImpresoras);
          setEquipoIds(mappedImpresoras.map(p => p.printer_id));
          if (mappedImpresoras.length > 0) {
            setImpresoraSeleccionada(mappedImpresoras[0]);
          }
          if (idLocal !== userId) {
            setPermisosYaCargados(new Set());
          }
        }
      } catch (e) {
        console.error("Error cargando equipos extendidos:", e);
      } finally {
        setCargandoDatos(false);
      }
    }
    setTieneCambiosSinGuardar(false);
  };


  const cargarEquiposYPermisos = async (userId = idLocal) => {
    const finalId = userId ? (typeof userId === 'number' ? userId : Number(userId)) : null;
    if (!finalId || isNaN(finalId)) return;

    try {
      setCargandoDatos(true);
      const dataConEquipos = await obtenerUsuarioConEquipos(finalId);
      if (dataConEquipos.equipos) {
        const mappedImpresoras: ImpresoraUsuario[] = dataConEquipos.equipos.map((eq: any) => ({
          id: eq.id,
          printer_id: eq.printer_id,
          printer_name: eq.printer_name,
          printer_ip: eq.printer_ip,
          printer_location: eq.printer_location || '',
          entry_index: eq.entry_index,
          permisos: eq.permisos
        }));
        setImpresorasAsignadas(mappedImpresoras);
        setEquipoIds(mappedImpresoras.map(p => p.printer_id));
        
        // Mantener seleccionada la impresora actual si sigue asignada, de lo contrario la primera
        if (impresoraSeleccionada && mappedImpresoras.some(p => p.printer_id === impresoraSeleccionada.printer_id)) {
          const updatedSelected = mappedImpresoras.find(p => p.printer_id === impresoraSeleccionada.printer_id);
          if (updatedSelected) setImpresoraSeleccionada(updatedSelected);
        } else if (mappedImpresoras.length > 0) {
          setImpresoraSeleccionada(mappedImpresoras[0]);
        } else {
          setImpresoraSeleccionada(null);
        }
      }
    } catch (e) {
      console.error("Error recargando equipos y permisos:", e);
    } finally {
      setCargandoDatos(false);
    }
  };

  const cargarDetallesTodasImpresoras = async () => {
    if (impresorasAsignadas.length === 0) return;

    if (tieneCambiosSinGuardar) {
      const confirmar = window.confirm("Tienes cambios sin guardar en el modal. Al consultar en vivo se sobrescribirán los datos locales con el estado real de las impresoras. ¿Deseas continuar?");
      if (!confirmar) return;
    }

    try {
      setCargandoPermisos(true);
      setError(null);
      
      const printerIds = impresorasAsignadas.map(p => p.printer_id);
      setCargandoPermisoIds(prev => new Set([...prev, ...printerIds]));

      const promesas = impresorasAsignadas.map(async (imp) => {
        try {
          // console.log('🔍 Cargando permisos en vivo para:', imp.printer_ip, imp.entry_index);
          const res = await obtenerDetallesUsuarioImpresora(imp.printer_ip, imp.entry_index || '');
          
          if (res.success && res.permisos) {
            // Actualizar la carpeta si viene alguna
            if (res.carpeta && res.carpeta.trim() !== '') {
              setCarpeta(res.carpeta);
            }
            
            // Actualizar la impresora individualmente usando actualización funcional
            setImpresorasAsignadas(prev => prev.map(p =>
              p.printer_id === imp.printer_id
                ? {
                  ...p,
                  permisos: {
                    copiadora: res.permisos.copiadora,
                    copiadora_color: res.permisos.copiadora_color || false,
                    impresora: res.permisos.impresora,
                    impresora_color: res.permisos.impresora_color || false,
                    document_server: res.permisos.document_server,
                    fax: res.permisos.fax,
                    escaner: res.permisos.escaner,
                    navegador: res.permisos.navegador
                  },
                  lazy: false
                }
                : p
            ));

            setPermisosYaCargados(prev => new Set([...prev, imp.printer_id]));
            
            // Si esta es la impresora actualmente seleccionada, actualizar también el estado del editor
            if (impresoraSeleccionada && imp.printer_id === impresoraSeleccionada.printer_id) {
              setPermisos({
                func_copier: res.permisos.copiadora,
                func_copier_color: res.permisos.copiadora_color || false,
                func_printer: res.permisos.impresora,
                func_printer_color: res.permisos.impresora_color || false,
                func_document_server: res.permisos.document_server,
                func_fax: res.permisos.fax,
                func_scanner: res.permisos.escaner,
                func_browser: res.permisos.navegador,
              });
            }
          }
        } catch (err) {
          console.error(`❌ Error consultando en vivo impresora ${imp.printer_ip}:`, err);
        } finally {
          setCargandoPermisoIds(prev => {
            const next = new Set(prev);
            next.delete(imp.printer_id);
            return next;
          });
        }
      });

      await Promise.all(promesas);
      setTieneCambiosSinGuardar(false);
      onUsuarioGuardado?.();
    } catch (e: any) {
      console.error("❌ Error en consulta en vivo simultánea:", e);
      setError("Hubo un error al realizar la consulta en vivo de los equipos.");
    } finally {
      setCargandoPermisos(false);
    }
  };

  // Al cambiar de impresora seleccionada, actualizar los permisos del editor desde local
  useEffect(() => {
    // console.log('🔄 useEffect disparado - impresoraSeleccionada ID:', impresoraSeleccionada?.id || impresoraSeleccionada?.printer_id);
    
    if (impresoraSeleccionada) {
      // Buscar la versión actualizada de la impresora en el array usando el id de asignación (o fallback a printer_id si no hay id)
      const impresoraActualizada = impresorasAsignadas.find(
        p => (p.id && p.id === impresoraSeleccionada.id) || (!p.id && p.printer_id === impresoraSeleccionada.printer_id)
      );
      
      // console.log('🔍 Impresora actualizada encontrada:', impresoraActualizada);
      
      if (impresoraActualizada && impresoraActualizada.permisos) {
        const nuevosPermisos = {
          func_copier: impresoraActualizada.permisos.copiadora,
          func_copier_color: impresoraActualizada.permisos.copiadora_color || false,
          func_printer: impresoraActualizada.permisos.impresora,
          func_printer_color: impresoraActualizada.permisos.impresora_color || false,
          func_document_server: impresoraActualizada.permisos.document_server,
          func_fax: impresoraActualizada.permisos.fax,
          func_scanner: impresoraActualizada.permisos.escaner,
          func_browser: impresoraActualizada.permisos.navegador,
        };
        // console.log('✅ Actualizando permisos en el editor:', nuevosPermisos);
        setPermisos(nuevosPermisos);
      }
    }
  }, [impresoraSeleccionada?.id, impresoraSeleccionada?.printer_id]);

  const handleCambioPermisos = (nuevosPermisos: any) => {
    setPermisos(nuevosPermisos);
    setTieneCambiosSinGuardar(true);

    if (impresoraSeleccionada) {
      setImpresorasAsignadas(prev => prev.map(p =>
        ((p.id && p.id === impresoraSeleccionada.id) || (!p.id && p.printer_id === impresoraSeleccionada.printer_id))
          ? {
              ...p,
              permisos: {
                copiadora: nuevosPermisos.func_copier,
                copiadora_color: nuevosPermisos.func_copier_color,
                impresora: nuevosPermisos.func_printer,
                impresora_color: nuevosPermisos.func_printer_color,
                document_server: nuevosPermisos.func_document_server,
                fax: nuevosPermisos.func_fax,
                escaner: nuevosPermisos.func_scanner,
                navegador: nuevosPermisos.func_browser
              },
              lazy: false
            }
          : p
      ));
    }
  };

  const handleCambioPermisosBase = (nuevosPermisos: any) => {
    setPermisosBase(nuevosPermisos);
    setTieneCambiosSinGuardar(true);
  };

  const handleCerrar = () => {
    if (tieneCambiosSinGuardar) {
      const confirmar = window.confirm("Tienes cambios sin guardar. ¿Estás seguro de que deseas cerrar y perder las modificaciones?");
      if (!confirmar) return;
    }
    onCerrar();
  };

  const handleQuitarEquipo = async () => {
    if (!usuario || !impresoraSeleccionada) return;
    
    const verificado = window.confirm(
      `¿Estás seguro de que deseas quitar al usuario "${nombre}" de la impresora "${impresoraSeleccionada.printer_location || impresoraSeleccionada.printer_name}"? Se deshabilitarán todas sus funciones y se eliminará el registro en la impresora.`
    );
    if (!verificado) return;

    try {
      setGuardando(true);
      setError(null);
      
      const finalId = typeof idLocal === 'number' ? idLocal : Number(idLocal);
      if (!isNaN(finalId)) {
        await desasignarEquipos(finalId, [impresoraSeleccionada.printer_id]);
        setExito(true);
        setTieneCambiosSinGuardar(false);
        setTimeout(() => setExito(false), 3000);
        
        // Recargar asignaciones y restablecer selección
        await cargarEquiposYPermisos(finalId);
      }
      onUsuarioGuardado?.();
    } catch (e: any) {
      console.error("❌ Error al quitar de equipo:", e);
      setError(e.message || "No se pudo quitar al usuario del equipo físico.");
    } finally {
      setGuardando(false);
    }
  };

  const handleGuardarTerminal = async () => {
    try {
      setGuardando(true);
      setError(null);

      // 1. Manejo especial para usuarios que vienen de SINCRO (aún no en DB)
      // Si el ID empieza con 'printer_', primero debemos IMPORTARLO a la DB
      let finalUsuarioId: number | null = null;
      if (typeof idLocal === 'number') {
        finalUsuarioId = idLocal;
      } else if (typeof idLocal === 'string' && !isNaN(Number(idLocal))) {
        finalUsuarioId = Number(idLocal);
      }

      let esImportado = false;

      if (!finalUsuarioId && idLocal?.toString().startsWith('printer_')) {
        // console.log("📥 Auto-importando usuario detectado en impresora:", codigo);
        const nuevoUsuario = await crearUsuario({
          name: nombre,
          codigo_de_usuario: codigo,
          empresa: empresa || undefined,
          centro_costos: centroCostos || undefined,
          network_credentials: {
            username: usuarioRed || "reliteltda\\scaner",
            password: ""
          },
          smb_config: {
            server: "192.168.91.5",
            port: 21,
            path: carpeta || "\\\\ALMACEN\\SCANS"
          },
          available_functions: {
            copier: permisosBase.func_copier,
            copier_color: (permisosBase as any).func_copier_color || false,
            printer: permisosBase.func_printer,
            printer_color: (permisosBase as any).func_printer_color || false,
            document_server: permisosBase.func_document_server,
            fax: permisosBase.func_fax,
            scanner: permisosBase.func_scanner,
            browser: permisosBase.func_browser
          }
        });
        finalUsuarioId = typeof nuevoUsuario.id === 'string' ? Number(nuevoUsuario.id) : nuevoUsuario.id;
        setIdLocal(finalUsuarioId); // Actualizar el estado local con el ID numérico real
        esImportado = true;
      }

      // 1.5 Si se acaba de importar, crear asignaciones en DB para los otros equipos que tenga asociados
      if (esImportado && finalUsuarioId) {
        // console.log("🔗 Creando asignaciones en DB para impresoras del usuario importado...");
        for (const imp of impresorasAsignadas) {
          if (impresoraSeleccionada && imp.printer_id === impresoraSeleccionada.printer_id) {
            continue; // Evitamos duplicar llamada con el paso 2
          }
          try {
            await actualizarPermisosAsignacion(
              finalUsuarioId,
              imp.printer_id,
              {
                copiadora: imp.permisos?.copiadora || false,
                copiadora_color: imp.permisos?.copiadora_color || false,
                impresora: imp.permisos?.impresora || false,
                impresora_color: imp.permisos?.impresora_color || false,
                document_server: imp.permisos?.document_server || false,
                fax: imp.permisos?.fax || false,
                escaner: imp.permisos?.escaner || false,
                navegador: imp.permisos?.navegador || false,
              },
              imp.entry_index
            );
          } catch (errAssign) {
            console.error(`⚠️ No se pudo pre-crear asignación en DB para impresora ${imp.printer_id}:`, errAssign);
          }
        }
      }

      // 2. Si hay una impresora seleccionada, enviamos los ajustes específicos al equipo
      if (impresoraSeleccionada && finalUsuarioId) {
        await actualizarPermisosAsignacion(
          finalUsuarioId,
          impresoraSeleccionada.printer_id,
          {
            copiadora: permisos.func_copier,
            copiadora_color: permisos.func_copier_color,
            impresora: permisos.func_printer,
            impresora_color: permisos.func_printer_color,
            document_server: permisos.func_document_server,
            fax: permisos.func_fax,
            escaner: permisos.func_scanner,
            navegador: permisos.func_browser,
          },
          impresoraSeleccionada.entry_index
        );
      }

      // 3. Guardar cambios en el perfil general (solo si estamos en la pestaña de 'info')
      if (finalUsuarioId && tabActiva === 'info') {
        if (!esImportado) {
          await actualizarUsuario(finalUsuarioId, {
            name: nombre,
            codigo_de_usuario: codigo,
            empresa: empresa || undefined,
            centro_costos: centroCostos || undefined,
            network_username: usuarioRed || undefined,
            smb_path: carpeta || undefined,
            ...permisosBase
          });
        }

        // 4. Sincronizar a TODAS las impresoras asignadas
        if (impresorasAsignadas.length > 0) {
          // console.log("🔄 Sincronizando cambios de perfil a todas las impresoras...");
          setSincronizandoImpresoras(true);
          try {
            // Extraer las IPs de todas las impresoras asignadas
            const printerIps = impresorasAsignadas.map(imp => imp.printer_ip);
            const syncResult = await sincronizarUsuarioTodasImpresoras(finalUsuarioId, printerIps, sincronizarPermisosBase);
            // console.log("✅ Resultado de sincronización:", syncResult.message);
          } catch (syncError: any) {
            console.error("⚠️ Error en sincronización a impresoras:", syncError);
            // No fallar la operación completa si la sincronización falla
            setError(`Datos guardados en DB, pero hubo problemas sincronizando con algunas impresoras: ${syncError.message}`);
          } finally {
            setSincronizandoImpresoras(false);
          }
        }
      }

      setExito(true);
      setTieneCambiosSinGuardar(false);
      if (finalUsuarioId) {
        await cargarEquiposYPermisos(finalUsuarioId);
      }
      // Notificar al padre para recargar la tabla general de usuarios al instante
      onUsuarioGuardado?.();
      // No cerrar el modal automáticamente para permitir editar otras impresoras
      setTimeout(() => setExito(false), 3000); // Ocultar mensaje de éxito después de 3 segundos
    } catch (e: any) {
      console.error("Error en handleGuardarTerminal:", e);
      setError(e.message || "No se pudo completar la sincronización con el equipo");
    } finally {
      setGuardando(false);
    }
  };

  return createPortal(
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-50 p-2 sm:p-4">
      <div className="bg-white rounded-2xl shadow-2xl modal-content w-full h-[95vh] md:h-[85vh] flex flex-col md:flex-row overflow-hidden border border-white/20 animate-in zoom-in-95 duration-200">

        {/* Sidebar de Navegación */}
        <div className="w-full md:w-56 lg:w-64 bg-slate-900 flex flex-col border-b md:border-b-0 md:border-r border-slate-800 flex-shrink-0">
          <div className="p-4 md:p-5 lg:p-6 hidden md:block">
            <h2 className="text-white font-black text-responsive-base tracking-tighter flex items-center gap-2">
              <span className="bg-ricoh-red p-1 rounded text-xs sm:text-sm">R</span> 
              <span className="hidden sm:inline">RICOH EQUIPMENT</span>
              <span className="sm:hidden">RICOH</span>
            </h2>
            <p className="text-slate-500 text-responsive-xs font-bold uppercase tracking-widest mt-1">Gestión de Perfil</p>
          </div>

          <nav className="flex-row md:flex-col flex-1 px-4 py-3 md:py-0 space-x-2 md:space-x-0 space-y-0 md:space-y-1 overflow-x-auto md:overflow-x-visible md:overflow-y-auto flex items-center md:items-stretch scrollbar-none">
            <button
              onClick={() => { setTabActiva('info'); setImpresoraSeleccionada(null); }}
              className={`flex-shrink-0 w-auto md:w-full flex items-center gap-2 md:gap-3 px-4 py-2.5 md:py-3 rounded-xl text-xs md:text-sm font-bold transition-all ${tabActiva === 'info' ? 'bg-ricoh-red text-white shadow-lg shadow-red-500/20' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
            >
              <Settings size={18} /> Perfil y SMB
            </button>

            <div className="pt-4 pb-2 hidden md:flex items-center justify-between px-4">
              <p className="text-slate-500 text-[9px] font-black uppercase tracking-[0.2em]">Equipos Asignados</p>
            </div>

            <div className="flex flex-row md:flex-col space-x-2 md:space-x-0 space-y-0 md:space-y-1 max-h-none md:max-h-none overflow-x-auto md:overflow-x-visible md:overflow-y-visible px-1 flex-1 md:flex-none scrollbar-none">
              {impresorasAsignadas.map((p, index) => {
                const estaCargandoEsta = cargandoPermisoIds.has(p.printer_id);
                const yaFueCargada = permisosYaCargados.has(p.printer_id);
                const esSeleccionada = impresoraSeleccionada 
                  ? ((p.id && p.id === impresoraSeleccionada.id) || (!p.id && p.printer_id === impresoraSeleccionada.printer_id))
                  : false;
                return (
                <button
                  key={`${p.id || p.printer_id}-${p.entry_index || index}`}
                  onClick={() => { setImpresoraSeleccionada(p); setTabActiva('permisos'); }}
                  className={`flex-shrink-0 w-auto md:w-full flex flex-row md:flex-col items-center md:items-start px-3 md:px-4 py-2 md:py-3 rounded-xl transition-all group gap-2 md:gap-0 min-w-0 ${esSeleccionada ? 'bg-slate-800 border border-slate-700' : 'hover:bg-white/5'}`}
                >
                  <div className="flex items-center gap-2 w-full min-w-0">
                    <Printer size={14} className={esSeleccionada ? 'text-red-400' : 'text-slate-500'} />
                    <span className={`text-xs font-black truncate text-left ${esSeleccionada ? 'text-white' : 'text-slate-400'}`}>
                      {p.printer_location || p.printer_name}
                    </span>
                    {/* Indicador de estado de carga */}
                    {estaCargandoEsta && (
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse flex-shrink-0" title="Leyendo permisos..." />
                    )}
                    {yaFueCargada && !estaCargandoEsta && (
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" title="Permisos cargados" />
                    )}
                  </div>
                  <span className="text-[9px] md:text-[10px] text-slate-400 font-bold bg-white/10 px-1.5 py-0.5 rounded md:mt-1 flex-shrink-0">{p.printer_ip}</span>
                </button>
                );
              })}

              <button
                onClick={() => setTabActiva('equipos')}
                className={`flex-shrink-0 w-auto md:w-full flex items-center gap-2 px-3 md:px-4 py-2 md:py-3 rounded-xl text-[10px] md:text-[11px] font-black uppercase tracking-wider transition-all border border-dashed ${tabActiva === 'equipos' ? 'bg-ricoh-red/20 text-ricoh-red border-ricoh-red/50' : 'text-slate-500 border-slate-700 hover:border-slate-500 hover:text-slate-300'}`}
              >
                <Plus size={14} /> <span className="hidden md:inline">Agregar/Quitar</span> <span className="inline md:hidden">Equipos</span>
              </button>
            </div>
          </nav>

          <div className="p-6 mt-auto border-t border-slate-800 hidden md:block">
            <div className="flex items-center gap-3 bg-slate-800/50 p-3 rounded-xl">
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-white">
                {nombre.substring(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[11px] font-bold text-white truncate">{nombre || 'Nuevo Usuario'}</p>
                <p className="text-[10px] text-slate-500 font-mono">#{codigo || '----'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Área de Contenido */}
        <div className="flex-1 flex flex-col bg-slate-50 relative">

          {/* Header del contenido */}
          <div className="container-padding py-4 sm:py-5 border-b border-slate-200 flex items-center justify-between bg-white">
            <div>
              <h3 className="text-slate-900 font-black text-responsive-base tracking-tight">
                {tabActiva === 'info' ? 'Datos del Usuario' :
                  tabActiva === 'permisos' ? `Ajustes en ${impresoraSeleccionada?.printer_location || impresoraSeleccionada?.printer_name}` :
                    'Equipos Disponibles'}
              </h3>
              <p className="text-slate-500 text-responsive-xs font-medium">
                {tabActiva === 'info' ? 'Ajustes maestros del usuario' :
                  tabActiva === 'permisos' ? `Definiendo qué puede hacer en: ${impresoraSeleccionada?.printer_ip}` :
                    'Elige dónde puede imprimir este usuario'}
              </p>
            </div>
            <button onClick={handleCerrar} className="text-slate-400 hover:text-slate-900 p-2 rounded-full hover:bg-slate-100 transition-all">
              <X size={22} />
            </button>
          </div>

          {/* Cuerpo con Scroll */}
          <div className="flex-1 overflow-y-auto p-8">

            {error && (
              <Alert variant="error" onClose={() => setError(null)} className="mb-6">
                {error}
              </Alert>
            )}

            {exito && (
              <Alert variant="success" className="mb-6">
                Cambios aplicados correctamente
              </Alert>
            )}

            {sincronizandoImpresoras && (
              <Alert variant="info" className="mb-6">
                <div>
                  <p className="text-sm font-bold">Sincronizando con todas las impresoras...</p>
                  <p className="text-xs mt-1">Actualizando nombre, código, carpeta y credenciales en {impresorasAsignadas.length} equipos</p>
                  <p className="text-[10px] mt-0.5 italic">Nota: Empresa y Centro de costos solo se guardan en la base de datos</p>
                </div>
              </Alert>
            )}

            {tabActiva === 'info' && (
              <div className="space-y-8 max-w-3xl">
                <section className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Nombre Completo</label>
                      <Input
                        value={nombre}
                        onChange={(e) => { setNombre(e.target.value); setTieneCambiosSinGuardar(true); }}
                        className="font-bold"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Código de Usuario</label>
                      <Input
                        value={codigo}
                        onChange={(e) => { setCodigo(e.target.value); setTieneCambiosSinGuardar(true); }}
                        maxLength={8}
                        className="font-mono font-bold"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                    <div className="space-y-2">
                      <EmpresaAutocomplete
                        label="Empresa"
                        value={empresa}
                        onChange={(val) => { setEmpresa(val); setTieneCambiosSinGuardar(true); }}
                        placeholder="Buscar o seleccionar empresa..."
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Centro de costos</label>
                      <CentroCostosAutocomplete
                        value={centroCostos}
                        onChange={(val) => { setCentroCostos(val); setTieneCambiosSinGuardar(true); }}
                        empresaName={empresa}
                      />
                    </div>
                  </div>
                </section>

                <hr className="border-slate-200" />

                <section className="space-y-6">
                  <div className="flex items-center gap-2">
                    <Globe size={16} className="text-blue-500" />
                    <h4 className="text-sm font-black text-slate-800 uppercase tracking-wide">Configuración de Escaneo (SMB)</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Usuario Autenticación Red</label>
                      <Input
                        value={usuarioRed}
                        readOnly
                        className="bg-slate-100 font-mono text-slate-600"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Ruta de Carpeta Compartida</label>
                      <Input
                        placeholder="\\servidor\carpeta"
                        value={carpeta}
                        onChange={(e) => { setCarpeta(e.target.value); setTieneCambiosSinGuardar(true); }}
                        className="font-mono font-bold"
                      />
                    </div>
                  </div>
                </section>

                <hr className="border-slate-200" />

                <section className="space-y-6">
                  <div className="flex items-center gap-2">
                    <ShieldCheck size={16} className="text-red-500" />
                    <h4 className="text-sm font-black text-slate-800 uppercase tracking-wide">Permisos Predeterminados (Base)</h4>
                  </div>
                  <p className="text-xs text-slate-500">Estos permisos se utilizarán por defecto al asignar al usuario a nuevos equipos.</p>
                  <EditorPermisos
                    permisos={permisosBase}
                    onChange={handleCambioPermisosBase}
                  />
                  {impresorasAsignadas.length > 0 && (
                    <div className="flex items-center gap-3 bg-red-50 border border-red-100/80 rounded-2xl p-4 mt-4 animate-in fade-in duration-300">
                      <input
                        type="checkbox"
                        id="syncPermissionsToAll"
                        checked={sincronizarPermisosBase}
                        onChange={(e) => setSincronizarPermisosBase(e.target.checked)}
                        className="w-4 h-4 text-ricoh-red border-slate-300 rounded focus:ring-ricoh-red cursor-pointer"
                      />
                      <label htmlFor="syncPermissionsToAll" className="text-xs font-black text-slate-700 cursor-pointer select-none">
                        Sincronizar estos permisos base a todas las impresoras asignadas al guardar
                      </label>
                    </div>
                  )}
                </section>
              </div>
            )}

            {tabActiva === 'permisos' && (
              <div className="animate-in fade-in duration-300 relative">
                <div className="bg-slate-100/80 backdrop-blur-sm border border-slate-200/50 rounded-2xl p-5 mb-8 flex items-start justify-between gap-4 shadow-sm flex-wrap sm:flex-nowrap">
                  <div className="flex items-start gap-4 min-w-0">
                    <div className="bg-slate-800 p-2 rounded-xl text-white shadow-md flex-shrink-0">
                      <ShieldCheck size={20} />
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-sm font-bold text-slate-900 tracking-tight truncate">Estás enviando cambios a la impresora</h4>
                      <p className="text-xs text-slate-600 mt-1 break-words">Lo que elijas aquí se aplicará directamente en <b>{impresoraSeleccionada?.printer_location || impresoraSeleccionada?.printer_name}</b> al terminar.</p>
                    </div>
                  </div>
                  <div className="flex gap-2 flex-wrap sm:flex-nowrap mt-3 sm:mt-0 w-full sm:w-auto">
                    {impresorasAsignadas.length > 0 && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={cargarDetallesTodasImpresoras}
                        disabled={cargandoPermisos}
                        icon={<RefreshCw size={14} className={cargandoPermisos ? 'animate-spin' : ''} />}
                        className="text-xs font-bold text-slate-600 border-slate-300 hover:border-slate-400 bg-white shadow-sm flex-shrink-0"
                      >
                        {cargandoPermisos ? 'Consultando...' : 'CONSULTAR PERMISOS'}
                      </Button>
                    )}
                  </div>
                </div>

                {cargandoPermisos && (
                  <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center rounded-2xl">
                    <Spinner size="lg" text="Leyendo permisos..." className="text-ricoh-red" />
                    <p className="text-[10px] text-slate-500 font-bold mt-1 italic">Conectando con Ricoh @ {impresoraSeleccionada?.printer_ip}</p>
                  </div>
                )}

                {impresoraSeleccionada && !permisosYaCargados.has(impresoraSeleccionada.printer_id) && (
                  <div className="bg-amber-50 border border-amber-200/50 rounded-2xl p-4 mb-6 flex items-start gap-3 text-amber-800 animate-in fade-in duration-300">
                    <span className="text-lg">⚠️</span>
                    <div className="text-xs">
                      <p className="font-bold text-amber-900">Valores de Base de Datos (Sin verificar en vivo)</p>
                      <p className="mt-0.5 text-amber-700 leading-relaxed">
                        Los permisos que ve abajo provienen de la base de datos local. Para evitar sobrescribir o eliminar permisos que el usuario ya posea físicamente en esta impresora, le recomendamos encarecidamente pulsar <b>"CONSULTAR PERMISOS"</b> antes de guardar cualquier ajuste.
                      </p>
                    </div>
                  </div>
                )}

                <EditorPermisos
                  permisos={permisos}
                  onChange={handleCambioPermisos}
                />
              </div>
            )}

            {tabActiva === 'equipos' && (
              <div className="animate-in fade-in duration-300">
                <GestorEquipos
                  usuarioId={Number(idLocal)}
                  equiposAsignados={equipoIds}
                  onCambio={(ids) => {
                    setEquipoIds(ids);
                    cargarEquiposYPermisos(Number(idLocal)); // Recargar de la API para actualizar la barra lateral al instante
                  }}
                />
              </div>
            )}
          </div>

          {/* Footer de Acciones */}
          <div className="px-8 py-5 border-t border-slate-200 bg-white flex items-center justify-between">
            <div>
              {tabActiva === 'permisos' && (
                <Button
                  variant="ghost"
                  icon={<Trash2 size={16} />}
                  className="text-red-600 hover:bg-red-50"
                  onClick={handleQuitarEquipo}
                  loading={guardando}
                >
                  Quitar de este equipo
                </Button>
              )}
            </div>

            <div className="flex gap-3">
              <Button
                variant="ghost"
                onClick={handleCerrar}
              >
                Cerrar
              </Button>
              <Button
                onClick={handleGuardarTerminal}
                loading={guardando || cargandoDatos}
                icon={<Save size={16} />}
                className="bg-ricoh-red hover:bg-red-700 shadow-xl shadow-red-500/20"
              >
                {tabActiva === 'permisos' ? 'Aplicar en Impresora' : 'Guardar Ajustes'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};
