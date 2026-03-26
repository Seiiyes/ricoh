import { useState, useEffect } from 'react';
import { X, Save, AlertCircle, Printer, ShieldCheck, Settings, Globe, Trash2, Plus } from 'lucide-react';
import { actualizarUsuario, obtenerUsuarioConEquipos, actualizarPermisosAsignacion, crearUsuario, obtenerDetallesUsuarioImpresora, sincronizarUsuarioTodasImpresoras } from '@/services/servicioUsuarios';
import { EditorPermisos } from './EditorPermisos';
import { GestorEquipos } from './GestorEquipos';
import { Button, Alert, Spinner, Input, EmpresaAutocomplete } from '@/components/ui';
import type { Usuario, ImpresoraUsuario } from '@/types/usuario';

interface ModificarUsuarioProps {
  usuario: Usuario | null;
  onCerrar: () => void;
}

export const ModificarUsuario = ({
  usuario,
  onCerrar,
}: ModificarUsuarioProps) => {
  const [cargandoDatos, setCargandoDatos] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [sincronizandoImpresoras, setSincronizandoImpresoras] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);

  // Tabs de navegación interna
  const [tabActiva, setTabActiva] = useState<'info' | 'permisos' | 'equipos'>('info');
  const [impresoraSeleccionada, setImpresoraSeleccionada] = useState<ImpresoraUsuario | null>(null);
  const [cargandoPermisos, setCargandoPermisos] = useState(false);
  const [permisosYaCargados, setPermisosYaCargados] = useState<Set<number>>(new Set());

  // Datos del formulario
  const [nombre, setNombre] = useState('');
  const [codigo, setCodigo] = useState('');
  const [empresa, setEmpresa] = useState('');
  const [centroCostos, setCentroCostos] = useState('');
  const [usuarioRed, setUsuarioRed] = useState('reliteltda\\scaner');
  const [carpeta, setCarpeta] = useState('');

  // Permisos (Base o por Impresora)
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

  // Equipos asignados (con sus metadatos)
  const [impresorasAsignadas, setImpresorasAsignadas] = useState<ImpresoraUsuario[]>([]);
  const [equipoIds, setEquipoIds] = useState<number[]>([]);

  // Cargar datos al abrir
  useEffect(() => {
    if (usuario) {
      cargarDatosIniciales();
    }
  }, [usuario]);

  const cargarDatosIniciales = async () => {
    if (!usuario) return;

    setNombre(usuario.name);
    setCodigo(usuario.codigo_de_usuario);
    setEmpresa(usuario.empresa || '');
    setCentroCostos(usuario.centro_costos || '');
    setUsuarioRed(usuario.network_username || 'reliteltda\\scaner');
    setCarpeta(usuario.smb_path || '');

    // Si viene de impresora, ya tiene el array poblado
    if (usuario.impresoras && usuario.impresoras.length > 0) {
      setImpresorasAsignadas(usuario.impresoras);
      setEquipoIds(usuario.impresoras.map(p => p.printer_id));
      // Seleccionar la primera por defecto para ver sus permisos
      setImpresoraSeleccionada(usuario.impresoras[0]);
    }

    // Si tiene ID numérico, cargar datos extendidos de DB
    if (!isNaN(Number(usuario.id))) {
      try {
        setCargandoDatos(true);
        const dataConEquipos = await obtenerUsuarioConEquipos(Number(usuario.id));
        if (dataConEquipos.equipos) {
          // Nota: Aquí el backend debe mapear PrinterDevice a ImpresoraUsuario
          // Por ahora usamos lo que viene en 'usuario' que está más enriquecido por el sync
        }
      } catch (e) {
        console.error("Error cargando equipos extendidos:", e);
      } finally {
        setCargandoDatos(false);
      }
    }
  };

  const cargarDetallesImpresora = async (imp: ImpresoraUsuario) => {
    try {
      setCargandoPermisos(true);
      setError(null);
      
      console.log('🔍 Cargando permisos para:', imp.printer_ip, imp.entry_index);
      const res = await obtenerDetallesUsuarioImpresora(imp.printer_ip, imp.entry_index || '');
      console.log('📦 Respuesta del backend:', res);

      if (res.success && res.permisos) {
        console.log('✅ Permisos recibidos:', res.permisos);
        
        // Marcar que ya cargamos los permisos de esta impresora
        setPermisosYaCargados(prev => new Set(prev).add(imp.printer_id));
        
        // Actualizar la impresora en el array local de asignadas
        const nuevasImpresoras = impresorasAsignadas.map(p =>
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
        );

        console.log('📝 Actualizando impresorasAsignadas:', nuevasImpresoras);
        setImpresorasAsignadas(nuevasImpresoras);
        // El useEffect se encargará de actualizar los permisos cuando cambie impresorasAsignadas
      }
    } catch (e: any) {
      console.error("❌ Error cargando detalles lazy:", e);
      setError("No se pudieron leer los permisos reales del equipo. Usando valores predeterminados.");
    } finally {
      setCargandoPermisos(false);
    }
  };

  // Al cambiar de impresora seleccionada, actualizar los permisos del editor
  useEffect(() => {
    console.log('🔄 useEffect disparado - impresoraSeleccionada:', impresoraSeleccionada?.printer_id);
    console.log('🔄 useEffect - cargandoPermisos:', cargandoPermisos);
    
    if (impresoraSeleccionada) {
      // Verificar si ya cargamos los permisos de esta impresora
      if (permisosYaCargados.has(impresoraSeleccionada.printer_id)) {
        console.log('⏭️ Permisos ya fueron cargados para esta impresora, saltando...');
        
        // Solo actualizar el estado de permisos sin recargar
        const impresoraActualizada = impresorasAsignadas.find(
          p => p.printer_id === impresoraSeleccionada.printer_id
        );
        
        if (impresoraActualizada?.permisos) {
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
          setPermisos(nuevosPermisos);
        }
        return;
      }
      
      // Buscar la versión actualizada de la impresora en el array
      const impresoraActualizada = impresorasAsignadas.find(
        p => p.printer_id === impresoraSeleccionada.printer_id
      );
      
      console.log('🔍 Impresora actualizada encontrada:', impresoraActualizada);
      
      if (impresoraActualizada) {
        // Solo recargar si NO tiene permisos cargados o si está marcada como lazy
        const necesitaCargar = !impresoraActualizada.permisos || 
                               Object.values(impresoraActualizada.permisos).every(v => v === false) ||
                               (impresoraActualizada as any).lazy === true;
        
        console.log('❓ Necesita cargar:', necesitaCargar);
        console.log('📋 Permisos actuales:', impresoraActualizada.permisos);
        
        if (necesitaCargar && !cargandoPermisos) {
          console.log('⏳ Iniciando carga de permisos...');
          cargarDetallesImpresora(impresoraActualizada);
          return; // Esperar a que se carguen los permisos
        }

        // Actualizar permisos con la versión actualizada
        if (impresoraActualizada.permisos) {
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
          console.log('✅ Actualizando permisos en el editor:', nuevosPermisos);
          setPermisos(nuevosPermisos);
        }
      }
    } else {
      // Permisos base si no hay impresora o no tiene específicos
      console.log('📋 Usando permisos base del usuario');
      setPermisos({
        func_copier: usuario?.func_copier || false,
        func_copier_color: usuario?.func_copier_color || false,
        func_printer: usuario?.func_printer || false,
        func_printer_color: usuario?.func_printer_color || false,
        func_document_server: usuario?.func_document_server || false,
        func_fax: usuario?.func_fax || false,
        func_scanner: usuario?.func_scanner || false,
        func_browser: usuario?.func_browser || false,
      });
    }
  }, [impresoraSeleccionada, impresorasAsignadas, cargandoPermisos]);

  const handleCambioPermisos = (nuevosPermisos: any) => {
    setPermisos(nuevosPermisos);
    // TODO: Si hay una impresora seleccionada, podríamos marcar que hubo cambios locales
  };

  const handleGuardarTerminal = async () => {
    try {
      setGuardando(true);
      setError(null);

      // 1. Manejo especial para usuarios que vienen de SINCRO (aún no en DB)
      // Si el ID empieza con 'printer_', primero debemos IMPORTARLO a la DB
      let finalUsuarioId: number | null = null;
      if (typeof usuario?.id === 'number') {
        finalUsuarioId = usuario.id;
      } else if (typeof usuario?.id === 'string' && !isNaN(Number(usuario.id))) {
        finalUsuarioId = Number(usuario.id);
      }

      let esImportado = false;

      if (!finalUsuarioId && usuario?.id?.toString().startsWith('printer_')) {
        console.log("📥 Auto-importando usuario detectado en impresora:", usuario.codigo_de_usuario);
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
            copier: permisos.func_copier,
            copier_color: (permisos as any).func_copier_color || false,
            printer: permisos.func_printer,
            printer_color: (permisos as any).func_printer_color || false,
            document_server: permisos.func_document_server,
            fax: permisos.func_fax,
            scanner: permisos.func_scanner,
            browser: permisos.func_browser
          }
        });
        finalUsuarioId = typeof nuevoUsuario.id === 'string' ? Number(nuevoUsuario.id) : nuevoUsuario.id;
        esImportado = true;
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

      // 3. Guardar cambios en el perfil general (solo si no se acaba de crear arriba)
      if (finalUsuarioId && !esImportado) {
        await actualizarUsuario(finalUsuarioId, {
          name: nombre,
          codigo_de_usuario: codigo,
          empresa: empresa || undefined,
          centro_costos: centroCostos || undefined,
          network_username: usuarioRed || undefined,
          smb_path: carpeta || undefined,
          ...permisos
        });

        // 4. Si estamos en la pestaña de "Perfil y SMB" (info), sincronizar a TODAS las impresoras
        if (tabActiva === 'info' && impresorasAsignadas.length > 0) {
          console.log("🔄 Sincronizando cambios de perfil a todas las impresoras...");
          setSincronizandoImpresoras(true);
          try {
            // Extraer las IPs de todas las impresoras asignadas
            const printerIps = impresorasAsignadas.map(imp => imp.printer_ip);
            const syncResult = await sincronizarUsuarioTodasImpresoras(finalUsuarioId, printerIps);
            console.log("✅ Resultado de sincronización:", syncResult.message);
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
      // No cerrar el modal automáticamente para permitir editar otras impresoras
      setTimeout(() => setExito(false), 3000); // Ocultar mensaje de éxito después de 3 segundos
    } catch (e: any) {
      console.error("Error en handleGuardarTerminal:", e);
      setError(e.message || "No se pudo completar la sincronización con el equipo");
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-5xl w-full h-[85vh] flex overflow-hidden border border-white/20 animate-in zoom-in-95 duration-200">

        {/* Sidebar de Navegación */}
        <div className="w-64 bg-slate-900 flex flex-col border-r border-slate-800">
          <div className="p-6">
            <h2 className="text-white font-black text-xl tracking-tighter flex items-center gap-2">
              <span className="bg-ricoh-red p-1 rounded">R</span> RICOH EQUIPMENT
            </h2>
            <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest mt-1">Gestión de Perfil</p>
          </div>

          <nav className="flex-1 px-4 space-y-1">
            <button
              onClick={() => { setTabActiva('info'); setImpresoraSeleccionada(null); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all ${tabActiva === 'info' ? 'bg-ricoh-red text-white shadow-lg shadow-red-500/20' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
            >
              <Settings size={18} /> Perfil y SMB
            </button>

            <div className="pt-4 pb-2">
              <p className="text-slate-500 text-[9px] font-black uppercase tracking-[0.2em] px-4">Equipos Asignados</p>
            </div>

            <div className="space-y-1 max-h-[300px] overflow-y-auto px-1">
              {impresorasAsignadas.map((p, index) => (
                <button
                  key={`${p.printer_id}-${p.entry_index || index}`}
                  onClick={() => { setImpresoraSeleccionada(p); setTabActiva('permisos'); }}
                  className={`w-full flex flex-col items-start px-4 py-3 rounded-xl transition-all group ${impresoraSeleccionada?.printer_id === p.printer_id ? 'bg-slate-800 border border-slate-700' : 'hover:bg-white/5'}`}
                >
                  <div className="flex items-center gap-2 w-full">
                    <Printer size={14} className={impresoraSeleccionada?.printer_id === p.printer_id ? 'text-blue-400' : 'text-slate-500'} />
                    <span className={`text-xs font-black truncate flex-1 text-left ${impresoraSeleccionada?.printer_id === p.printer_id ? 'text-white' : 'text-slate-400'}`}>
                      {p.printer_location || p.printer_name}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-900 font-bold ml-5 bg-blue-100/50 px-1 rounded">{p.printer_ip}</span>
                </button>
              ))}

              <button
                onClick={() => setTabActiva('equipos')}
                className={`w-full flex items-center gap-2 px-4 py-3 rounded-xl text-[11px] font-black uppercase tracking-wider transition-all border border-dashed ${tabActiva === 'equipos' ? 'bg-blue-600 text-white border-blue-400' : 'text-slate-500 border-slate-700 hover:border-slate-500 hover:text-slate-300'}`}
              >
                <Plus size={14} /> Agregar o Quitar Impresoras
              </button>
            </div>
          </nav>

          <div className="p-6 mt-auto border-t border-slate-800">
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
        <div className="flex-1 flex flex-col bg-[#F9FAFB]">

          {/* Header del contenido */}
          <div className="px-8 py-5 border-b border-slate-200 flex items-center justify-between bg-white">
            <div>
              <h3 className="text-slate-900 font-black text-lg tracking-tight">
                {tabActiva === 'info' ? 'Datos del Usuario' :
                  tabActiva === 'permisos' ? `Ajustes en ${impresoraSeleccionada?.printer_location || impresoraSeleccionada?.printer_name}` :
                    'Equipos Disponibles'}
              </h3>
              <p className="text-slate-500 text-xs font-medium">
                {tabActiva === 'info' ? 'Ajustes maestros del usuario' :
                  tabActiva === 'permisos' ? `Definiendo qué puede hacer en: ${impresoraSeleccionada?.printer_ip}` :
                    'Elige dónde puede imprimir este usuario'}
              </p>
            </div>
            <button onClick={onCerrar} className="text-slate-400 hover:text-slate-900 p-2 rounded-full hover:bg-slate-100 transition-all">
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
                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Nombre Completo</label>
                      <Input
                        value={nombre}
                        onChange={(e) => setNombre(e.target.value)}
                        className="font-bold"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Código de Usuario</label>
                      <Input
                        value={codigo}
                        onChange={(e) => setCodigo(e.target.value)}
                        maxLength={8}
                        className="font-mono font-bold"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <EmpresaAutocomplete
                        label="Empresa"
                        value={empresa}
                        onChange={setEmpresa}
                        placeholder="Buscar o seleccionar empresa..."
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Centro de costos</label>
                      <Input
                        value={centroCostos}
                        onChange={(e) => setCentroCostos(e.target.value)}
                        className="font-bold"
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
                  <div className="grid grid-cols-2 gap-6">
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
                        onChange={(e) => setCarpeta(e.target.value)}
                        className="font-mono font-bold"
                      />
                    </div>
                  </div>
                </section>
              </div>
            )}

            {tabActiva === 'permisos' && (
              <div className="animate-in fade-in duration-300 relative">
                <div className="bg-blue-50 border border-blue-100 rounded-2xl p-5 mb-8 flex items-start gap-4">
                  <div className="bg-blue-600 p-2 rounded-lg text-white">
                    <ShieldCheck size={20} />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-blue-900">Estás enviando cambios a la impresora</h4>
                    <p className="text-xs text-blue-700 mt-1">Lo que elijas aquí se aplicará directamente en <b>{impresoraSeleccionada?.printer_location || impresoraSeleccionada?.printer_name}</b> al terminar.</p>
                  </div>
                </div>

                {cargandoPermisos && (
                  <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-10 flex flex-col items-center justify-center rounded-2xl">
                    <Spinner size="lg" text="Leyendo permisos reales..." className="text-blue-600" />
                    <p className="text-[10px] text-slate-500 font-bold mt-1 italic">Conectando con Ricoh @ {impresoraSeleccionada?.printer_ip}</p>
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
                  usuarioId={Number(usuario?.id)}
                  equiposAsignados={equipoIds}
                  onCambio={(ids) => {
                    setEquipoIds(ids);
                    // TODO: Recargar lista de impresorasAsignadas para refrescar el sidebar
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
                >
                  Quitar de este equipo
                </Button>
              )}
            </div>

            <div className="flex gap-3">
              <Button
                variant="ghost"
                onClick={onCerrar}
              >
                Cerrar
              </Button>
              <Button
                onClick={handleGuardarTerminal}
                loading={guardando || cargandoDatos}
                icon={<Save size={16} />}
                className="bg-blue-600 hover:bg-blue-700 shadow-xl shadow-blue-500/20"
              >
                {tabActiva === 'permisos' ? 'Aplicar en Impresora' : 'Guardar Ajustes'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
