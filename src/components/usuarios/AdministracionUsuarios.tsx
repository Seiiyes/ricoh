import { useEffect, useState } from 'react';
import { useUsuarioStore } from '@/store/useUsuarioStore';
import { obtenerUsuarios, eliminarUsuario } from '@/services/servicioUsuarios';
import { TablaUsuarios, CampoOrden, DireccionOrden } from './TablaUsuarios';
import { ModificarUsuario } from './ModificarUsuario';
import { Users, Search, RefreshCw } from 'lucide-react';
import { Button, Input, Spinner } from '@/components/ui';
import type { Usuario } from '@/types/usuario';
import discoveryService from '@/services/discoveryService';
import { parseApiError } from '@/utils/errorHandler';
import { useNotification } from '@/hooks/useNotification';

export const AdministracionUsuarios = () => {
  const notify = useNotification();
  const {
    usuarios,
    cargando,
    busqueda,
    setUsuarios,
    setCargando,
    setBusqueda,
    obtenerUsuariosFiltrados,
    filtroEstado,
    setFiltroEstado,
  } = useUsuarioStore();

  const [modalAbierto, setModalAbierto] = useState(false);
  const [usuarioEditar, setUsuarioEditar] = useState<Usuario | null>(null);
  const [sincronizando, setSincronizando] = useState(false);
  const [usuariosImpresora, setUsuariosImpresora] = useState<any[]>([]);
  const [mostrarOrigen, setMostrarOrigen] = useState<'todos' | 'db' | 'impresora'>('todos');
  const [modoSincronizacion, setModoSincronizacion] = useState<'todos' | 'especifico'>('todos');
  const [codigoUsuarioBuscar, setCodigoUsuarioBuscar] = useState('');

  // Paginación
  const [paginaActual, setPaginaActual] = useState(1);
  const usuariosPorPagina = 50;

  // Ordenamiento Global
  const [campoOrden, setCampoOrden] = useState<CampoOrden | null>(null);
  const [direccionOrden, setDireccionOrden] = useState<DireccionOrden>(null);

  const handleOrdenar = (campo: CampoOrden) => {
    if (campoOrden === campo) {
      if (direccionOrden === 'asc') {
        setDireccionOrden('desc');
      } else if (direccionOrden === 'desc') {
        setDireccionOrden(null);
        setCampoOrden(null);
      }
    } else {
      setCampoOrden(campo);
      setDireccionOrden('asc');
    }
  };

  const obtenerValorOrden = (usuario: any, campo: CampoOrden): any => {
    switch (campo) {
      case 'origen':
        return usuario.en_db === false ? 2 : usuario.impresoras && usuario.impresoras.length > 0 ? 1 : 0;
      case 'nombre':
        return usuario.name.toLowerCase();
      case 'codigo':
        return usuario.codigo_de_usuario;
      case 'empresa':
        return (usuario.empresa || '').toLowerCase();
      case 'centro_costos':
        return (usuario.centro_costos || '').toLowerCase();
      case 'impresoras':
        return usuario.impresoras?.length || 0;
      default:
        return '';
    }
  };

  // Cargar usuarios al montar el componente
  useEffect(() => {
    cargarUsuarios();
  }, []);

  const cargarUsuarios = async () => {
    try {
      setCargando(true);
      const resultado = await obtenerUsuarios(0, 5000, false); // Cargar todos los usuarios
      setUsuarios(resultado);

      // Actualizar reactivamente el usuarioEditar si coincide con el usuario recién guardado/actualizado
      if (usuarioEditar) {
        const usuarioActualizado = resultado.find(
          u => u.id === usuarioEditar.id || u.codigo_de_usuario === usuarioEditar.codigo_de_usuario
        );
        if (usuarioActualizado) {
          setUsuarioEditar(usuarioActualizado);
        }
      }
    } catch (error) {
      console.error('Error al cargar usuarios:', error);
    } finally {
      setCargando(false);
    }
  };

  const handleSincronizar = async () => {
    try {
      setSincronizando(true);

      // Determinar si se debe buscar un usuario específico
      const userCode = modoSincronizacion === 'especifico' && codigoUsuarioBuscar.trim()
        ? codigoUsuarioBuscar.trim()
        : undefined;

      

      const response = await discoveryService.syncUsersFromPrinters(userCode);

      // console.log('🔄 Respuesta de sincronización:', response);
      // console.log('📊 Usuarios sincronizados:', response.users?.length || 0);

      if (response.success) {
        notify.success('Usuarios actualizados', response.message);

        // Recargar usuarios de la base de datos
        await cargarUsuarios();

        // Actualizar usuarios de impresoras con la respuesta
        if (response.users && Array.isArray(response.users)) {
          // console.log('✅ Actualizando estado con usuarios de impresoras:', response.users.length);
          setUsuariosImpresora(response.users);
        } else {
          console.warn('⚠️ No se recibieron usuarios en la respuesta');
        }
      } else {
        notify.error('Error al actualizar', 'No se pudieron actualizar los usuarios desde los equipos');
      }
    } catch (error: any) {
      console.error('Error al actualizar:', error);
      notify.error('Error al actualizar', parseApiError(error, 'No se pudieron obtener los usuarios de las impresoras'));
    } finally {
      setSincronizando(false);
    }
  };

  const handleEditarUsuario = (usuario: Usuario) => {
    setUsuarioEditar(usuario);
    setModalAbierto(true);
  };

  const handleCerrarModal = () => {
    setModalAbierto(false);
    setUsuarioEditar(null);
  };

  const handleDesactivarUsuario = async (usuario: Usuario) => {
    if (!usuario) return;
    
    const id = usuario.id;
    if (typeof id !== 'number') {
      notify.error('Acción no permitida', 'Solo se pueden desactivar usuarios guardados en la base de datos.');
      return;
    }
    
    const verificado = window.confirm(`¿Estás seguro de que deseas desactivar al usuario "${usuario.name}"? Se desactivará en el sistema y se le deshabilitarán todos los permisos en las impresoras físicas asignadas.`);
    if (!verificado) return;
    
    try {
      setCargando(true);
      await eliminarUsuario(id);
      notify.success('Usuario desactivado', `El usuario "${usuario.name}" fue desactivado correctamente.`);
      await cargarUsuarios();
    } catch (error: any) {
      console.error('Error al desactivar usuario:', error);
      notify.error('Error al desactivar', parseApiError(error, 'No se pudo desactivar el usuario.'));
    } finally {
      setCargando(false);
    }
  };


  // Combinar usuarios de DB con usuarios de impresoras
  const todosLosUsuarios = () => {
    const usuariosDB = obtenerUsuariosFiltrados();

    // Enriquecer usuarios de DB con información de impresoras
    const usuariosDBEnriquecidos = usuariosDB.map(usuarioDB => {
      // Buscar si este usuario también está en impresoras
      const usuarioEnImpresoras = usuariosImpresora.find(
        u => u.codigo === usuarioDB.codigo_de_usuario
      );

      if (usuarioEnImpresoras && usuarioEnImpresoras.impresoras) {
        return {
          ...usuarioDB,
          impresoras: usuarioEnImpresoras.impresoras,
          en_db: true,
          origen: 'db' as const
        };
      }

      return {
        ...usuarioDB,
        en_db: true,
        origen: 'db' as const
      };
    });

    // Convertir usuarios de impresora al formato de Usuario (solo los que NO están en DB)
    const codigosEnDB = new Set(usuariosDB.map(u => u.codigo_de_usuario));
    const usuariosSoloImpresora = usuariosImpresora
      .filter(u => !codigosEnDB.has(u.codigo))
      .map(u => ({
        id: `printer_${u.codigo}`,
        name: u.nombre,
        codigo_de_usuario: u.codigo,
        // Hack fix: Si el email parece una ruta de red (empieza con \\), no lo mostramos como email
        email: (u.email && u.email.startsWith('\\\\')) ? '' : (u.email || ''),
        department: '',
        empresa: '',
        centro_costos: '',
        is_active: true,
        func_copier: u.permisos?.copiadora || false,
        func_scanner: u.permisos?.escaner || false,
        func_printer: u.permisos?.impresora || false,
        func_document_server: u.permisos?.document_server || false,
        func_fax: u.permisos?.fax || false,
        func_browser: u.permisos?.navegador || false,
        smb_path: u.carpeta || '',
        origen: 'impresora' as const,
        en_db: false,
        impresoras: u.impresoras || []
      }));

    // Aplicar filtro de búsqueda a usuarios solo de impresora
    let usuariosSoloImpresoraFiltrados = usuariosSoloImpresora;
    if (busqueda.trim()) {
      const busquedaLower = busqueda.toLowerCase().trim();
      usuariosSoloImpresoraFiltrados = usuariosSoloImpresora.filter(
        (u) =>
          u.name.toLowerCase().includes(busquedaLower) ||
          u.codigo_de_usuario.toLowerCase().includes(busquedaLower) ||
          (u.empresa && u.empresa.toLowerCase().includes(busquedaLower)) ||
          (u.centro_costos && u.centro_costos.toLowerCase().includes(busquedaLower))
      );
    }

    // Filtrar según selección de origen
    if (mostrarOrigen === 'db') {
      return usuariosDBEnriquecidos;
    } else if (mostrarOrigen === 'impresora') {
      return usuariosSoloImpresoraFiltrados;
    } else {
      return [...usuariosDBEnriquecidos, ...usuariosSoloImpresoraFiltrados];
    }
  };

  const usuariosMostrar = todosLosUsuarios();

  // Ordenar usuarios según el campo y dirección seleccionados globalmente
  const usuariosOrdenados = [...usuariosMostrar].sort((a, b) => {
    if (!campoOrden || !direccionOrden) return 0;

    const valorA = obtenerValorOrden(a, campoOrden);
    const valorB = obtenerValorOrden(b, campoOrden);
    const comparacion = valorA < valorB ? -1 : valorA > valorB ? 1 : 0;
    
    return direccionOrden === 'asc' ? comparacion : -comparacion;
  });

  // Calcular paginación
  const totalUsuarios = usuariosMostrar.length;
  const totalPaginas = Math.ceil(totalUsuarios / usuariosPorPagina);
  const indiceInicio = (paginaActual - 1) * usuariosPorPagina;
  const indiceFin = indiceInicio + usuariosPorPagina;
  const usuariosPaginados = usuariosOrdenados.slice(indiceInicio, indiceFin);

  // Resetear a página 1 cuando cambie el filtro
  useEffect(() => {
    setPaginaActual(1);
  }, [busqueda, mostrarOrigen, filtroEstado]);

  return (
    <div className="flex flex-col h-full bg-slate-50 relative">
      {/* Encabezado */}
      <div className="bg-white border-b border-slate-100 shadow-sm">
        <div className="px-6 py-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-red-50 text-ricoh-red rounded-xl">
                <Users size={22} />
              </div>
              <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
                Gestión de Usuarios
              </h1>
            </div>

            <div className="flex flex-wrap gap-3 items-center">
              {/* Selector de modo de sincronización */}
              <div className="flex items-center bg-slate-100/80 p-1.5 rounded-xl border border-slate-200/50 shadow-inner">
                <button
                  onClick={() => setModoSincronizacion('todos')}
                  className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 ${modoSincronizacion === 'todos'
                      ? 'bg-white text-slate-800 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700 hover:bg-white/50'
                    }`}
                >
                  Todos
                </button>
                <button
                  onClick={() => setModoSincronizacion('especifico')}
                  className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 ${modoSincronizacion === 'especifico'
                      ? 'bg-white text-slate-800 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700 hover:bg-white/50'
                    }`}
                >
                  Por código
                </button>
              </div>

              {/* Campo de código de usuario (solo visible en modo específico) */}
              {modoSincronizacion === 'especifico' && (
                <div className="animate-fade-in relative transition-all duration-300">
                  <input
                    type="text"
                    placeholder="Ej: 1234"
                    value={codigoUsuarioBuscar}
                    onChange={(e) => setCodigoUsuarioBuscar(e.target.value)}
                    className="w-32 px-4 py-2 border border-slate-200 rounded-xl text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red transition-all"
                  />
                </div>
              )}

              <Button
                variant="primary"
                size="md"
                icon={<RefreshCw size={16} className={sincronizando ? 'animate-spin' : ''} />}
                onClick={handleSincronizar}
                disabled={sincronizando || (modoSincronizacion === 'especifico' && !codigoUsuarioBuscar.trim())}
                className="font-semibold shadow-md hover:shadow-lg transition-all"
              >
                {sincronizando ? 'Actualizando...' : modoSincronizacion === 'especifico' ? 'Buscar' : 'Actualizar desde Equipos'}
              </Button>
            </div>
          </div>

          {/* Barra de búsqueda */}
          <div className="mt-4">
            <Input
              type="search"
              placeholder="Buscar por nombre, código, empresa o centro de costos..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              icon={<Search size={18} />}
            />
          </div>

          {/* Filtros de Origen y Estado DB */}
          <div className="mt-3 flex flex-wrap gap-6 items-center">
            {/* Filtro de origen (solo visible si hay usuarios sincronizados) */}
            {usuariosImpresora.length > 0 && (
              <div className="flex gap-2 items-center">
                <span className="text-xs text-slate-500 font-semibold">Origen:</span>
                <button
                  onClick={() => setMostrarOrigen('todos')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 ${mostrarOrigen === 'todos'
                    ? 'bg-slate-800 text-white shadow-md'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                >
                  Todos
                </button>
                <button
                  onClick={() => setMostrarOrigen('db')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 ${mostrarOrigen === 'db'
                    ? 'bg-slate-800 text-white shadow-md'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                >
                  💾 Base de Datos
                </button>
                <button
                  onClick={() => setMostrarOrigen('impresora')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 ${mostrarOrigen === 'impresora'
                    ? 'bg-slate-800 text-white shadow-md'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                    }`}
                >
                  🖨️ Solo Impresoras
                </button>
              </div>
            )}

            {/* Filtro de estado de base de datos */}
            <div className="flex gap-2 items-center">
              <span className="text-xs text-slate-500 font-semibold">Estado DB:</span>
              <button
                onClick={() => setFiltroEstado('activos')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 ${filtroEstado === 'activos'
                  ? 'bg-slate-800 text-white shadow-md'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                Activos
              </button>
              <button
                onClick={() => setFiltroEstado('inactivos')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 ${filtroEstado === 'inactivos'
                  ? 'bg-slate-800 text-white shadow-md'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                Inactivos
              </button>
              <button
                onClick={() => setFiltroEstado('todos')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all duration-300 ${filtroEstado === 'todos'
                  ? 'bg-slate-800 text-white shadow-md'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                Todos
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="flex-1 overflow-auto p-6">
        {cargando ? (
          <div className="flex flex-col items-center justify-center h-full">
            <Spinner size="xl" text="Cargando usuarios..." />
          </div>
        ) : usuariosMostrar.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-400">
            <Users size={64} className="mb-4 opacity-20" />
            <p className="text-lg font-bold mb-2">No se encontraron usuarios</p>
            <p className="text-sm">
              {busqueda
                ? 'Intenta con otra búsqueda'
                : usuariosImpresora.length === 0
                  ? 'Actualiza la lista para ver usuarios de los equipos'
                  : 'No hay usuarios disponibles'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Control de paginación superior */}
            <div className="flex items-center justify-between bg-white px-5 py-3 rounded-2xl border border-slate-100 shadow-sm">
              <div className="text-xs font-bold text-slate-500">
                Mostrando {indiceInicio + 1}-{Math.min(indiceFin, totalUsuarios)} de {totalUsuarios} usuario(s)
              </div>
              {totalPaginas > 1 && (
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPaginaActual(Math.max(1, paginaActual - 1))}
                    disabled={paginaActual === 1}
                    className="h-8 py-0 px-2.5 text-xs font-semibold"
                  >
                    ← Anterior
                  </Button>
                  <span className="text-xs font-bold text-slate-700 bg-slate-50/50 px-2.5 py-1.5 rounded-lg border border-slate-100">
                    Página {paginaActual} de {totalPaginas}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPaginaActual(Math.min(totalPaginas, paginaActual + 1))}
                    disabled={paginaActual === totalPaginas}
                    className="h-8 py-0 px-2.5 text-xs font-semibold"
                  >
                    Siguiente →
                  </Button>
                </div>
              )}
            </div>

            <div className="bg-white rounded-2xl shadow-xl border border-slate-100 animate-slide-up relative overflow-hidden">
              <TablaUsuarios
                usuarios={usuariosPaginados}
                onEditar={handleEditarUsuario}
                onDesactivar={handleDesactivarUsuario}
                campoOrden={campoOrden}
                direccionOrden={direccionOrden}
                onOrdenar={handleOrdenar}
              />
            </div>
          </div>
        )}

        {/* Contador de resultados y paginación */}
        {!cargando && usuariosMostrar.length > 0 && (
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-slate-500">
              Mostrando {indiceInicio + 1}-{Math.min(indiceFin, totalUsuarios)} de {totalUsuarios} usuario(s)
              {usuariosImpresora.length > 0 && (
                <span className="ml-2">
                  (💾 {usuarios.length} en DB, 🖨️ {usuariosImpresora.filter(u => !u.en_db).length} solo en impresoras)
                </span>
              )}
            </div>

            {/* Controles de paginación */}
            {totalPaginas > 1 && (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaginaActual(Math.max(1, paginaActual - 1))}
                  disabled={paginaActual === 1}
                >
                  ← Anterior
                </Button>

                <span className="text-sm font-bold text-slate-700">
                  Página {paginaActual} de {totalPaginas}
                </span>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaginaActual(Math.min(totalPaginas, paginaActual + 1))}
                  disabled={paginaActual === totalPaginas}
                >
                  Siguiente →
                </Button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modal de edición */}
      {modalAbierto && (
        <ModificarUsuario
          usuario={usuarioEditar}
          onCerrar={handleCerrarModal}
          onUsuarioGuardado={cargarUsuarios}
        />
      )}
    </div>
  );
};
