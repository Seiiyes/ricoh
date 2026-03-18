import { useEffect, useState } from 'react';
import { useUsuarioStore } from '@/store/useUsuarioStore';
import { obtenerUsuarios } from '@/services/servicioUsuarios';
import { TablaUsuarios } from './TablaUsuarios';
import { ModificarUsuario } from './ModificarUsuario';
import { Users, Search, RefreshCw } from 'lucide-react';
import { Button, Input, Spinner } from '@/components/ui';
import type { Usuario } from '@/types/usuario';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const AdministracionUsuarios = () => {
  const {
    usuarios,
    cargando,
    busqueda,
    filtroEstado,
    setUsuarios,
    setCargando,
    setBusqueda,
    setFiltroEstado,
    obtenerUsuariosFiltrados,
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

  // Cargar usuarios al montar el componente
  useEffect(() => {
    cargarUsuarios();
  }, [filtroEstado]);

  const cargarUsuarios = async () => {
    try {
      setCargando(true);
      const soloActivos = filtroEstado === 'activos';
      const resultado = await obtenerUsuarios(0, 100, soloActivos);
      setUsuarios(resultado);
    } catch (error) {
      console.error('Error al cargar usuarios:', error);
    } finally {
      setCargando(false);
    }
  };

  const handleSincronizar = async () => {
    try {
      setSincronizando(true);

      // Construir URL con parámetros
      let url = `${API_URL}/discovery/sync-users-from-printers`;
      const params = new URLSearchParams();
      
      if (modoSincronizacion === 'especifico' && codigoUsuarioBuscar.trim()) {
        params.append('user_code', codigoUsuarioBuscar.trim());
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        throw new Error('Error al sincronizar usuarios');
      }

      const data = await response.json();

      if (data.success) {
        setUsuariosImpresora(data.users || []);

        // Debug: ver estructura de datos
        console.log('📊 Total usuarios recibidos:', data.users?.length);
        console.log('📊 Primeros 3 usuarios:', data.users?.slice(0, 3));
        console.log('📊 Primer usuario completo:', data.users?.[0]);
        console.log('📊 Impresoras del primer usuario:', data.users?.[0]?.impresoras);

        // Verificar cuántos usuarios tienen impresoras
        const usuariosConImpresoras = data.users?.filter((u: any) => u.impresoras && u.impresoras.length > 0) || [];
        console.log('📊 Usuarios con impresoras:', usuariosConImpresoras.length);
        console.log('📊 Ejemplo usuario con impresoras:', usuariosConImpresoras[0]);

        // Estadísticas de distribución de impresoras
        const distribucion = data.users?.reduce((acc: any, u: any) => {
          const numImpresoras = u.impresoras?.length || 0;
          acc[numImpresoras] = (acc[numImpresoras] || 0) + 1;
          return acc;
        }, {});
        console.log('📊 Distribución de impresoras por usuario:', distribucion);

        // Buscar usuarios en múltiples impresoras
        const usuariosMultiples = data.users?.filter((u: any) => u.impresoras && u.impresoras.length > 1) || [];
        console.log('📊 Usuarios en múltiples impresoras:', usuariosMultiples.length);
        if (usuariosMultiples.length > 0) {
          console.log('📊 Ejemplo usuario en múltiples impresoras:', usuariosMultiples[0]);
        }

        // Mostrar resumen detallado
        let mensaje = `✅ ${data.message}\n\n`;
        mensaje += `📊 Resumen:\n`;
        mensaje += `• Total usuarios únicos: ${data.total_usuarios_unicos}\n`;
        mensaje += `• En base de datos: ${data.usuarios_en_db}\n`;
        mensaje += `• Solo en impresoras: ${data.usuarios_solo_impresoras}\n\n`;

        if (data.printers_scanned && data.printers_scanned.length > 0) {
          mensaje += `🖨️ Impresoras escaneadas:\n`;
          data.printers_scanned.forEach((p: any) => {
            if (p.error) {
              mensaje += `• ${p.hostname} (${p.ip}): ❌ Error\n`;
            } else if (p.skipped) {
              mensaje += `• ${p.hostname} (${p.ip}): ⏭️ Omitida (${p.reason})\n`;
            } else {
              mensaje += `• ${p.hostname} (${p.ip}): ${p.users_count} usuarios\n`;
            }
          });
        }

        if (data.errors && data.errors.length > 0) {
          mensaje += `\n⚠️ Errores:\n`;
          data.errors.forEach((err: string) => {
            mensaje += `• ${err}\n`;
          });
        }

        alert(mensaje);
      } else {
        alert(`⚠️ ${data.message}`);
      }

    } catch (error: any) {
      console.error('Error sincronizando usuarios:', error);
      
      // Mensaje de error más descriptivo
      let errorMsg = '❌ Error al sincronizar usuarios desde las impresoras\n\n';
      
      if (error.message) {
        errorMsg += `Detalle: ${error.message}\n`;
      }
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMsg += '\n⚠️ Posible causa: El servidor backend no está corriendo.\n';
        errorMsg += 'Verifica que el backend esté activo en http://localhost:8000';
      }
      
      alert(errorMsg);
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
          en_db: true
        };
      }

      return {
        ...usuarioDB,
        en_db: true
      };
    });

    // Convertir usuarios de impresora al formato de Usuario (solo los que NO están en DB)
    const usuariosSoloImpresora = usuariosImpresora
      .filter(u => !u.en_db)
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
  
  // Calcular paginación
  const totalUsuarios = usuariosMostrar.length;
  const totalPaginas = Math.ceil(totalUsuarios / usuariosPorPagina);
  const indiceInicio = (paginaActual - 1) * usuariosPorPagina;
  const indiceFin = indiceInicio + usuariosPorPagina;
  const usuariosPaginados = usuariosMostrar.slice(indiceInicio, indiceFin);
  
  // Resetear a página 1 cuando cambie el filtro
  useEffect(() => {
    setPaginaActual(1);
  }, [busqueda, filtroEstado, mostrarOrigen]);

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      {/* Encabezado */}
      <div className="bg-white border-b shadow-sm">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Users className="text-ricoh-red" size={24} />
              <h1 className="text-xl font-bold text-industrial-gray uppercase tracking-tight">
                Administración de Usuarios
              </h1>
            </div>

            <div className="flex gap-2 items-center">
              {/* Selector de modo de sincronización */}
              <div className="flex items-center gap-2 bg-slate-100 rounded-lg p-1">
                <button
                  onClick={() => setModoSincronizacion('todos')}
                  className={`px-3 py-1 text-xs font-bold uppercase tracking-wide rounded transition-colors ${
                    modoSincronizacion === 'todos'
                      ? 'bg-white text-slate-700 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  Todos
                </button>
                <button
                  onClick={() => setModoSincronizacion('especifico')}
                  className={`px-3 py-1 text-xs font-bold uppercase tracking-wide rounded transition-colors ${
                    modoSincronizacion === 'especifico'
                      ? 'bg-white text-slate-700 shadow-sm'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  Usuario Específico
                </button>
              </div>

              {/* Campo de código de usuario (solo visible en modo específico) */}
              {modoSincronizacion === 'especifico' && (
                <input
                  type="text"
                  placeholder="Código de usuario (ej: 1234)"
                  value={codigoUsuarioBuscar}
                  onChange={(e) => setCodigoUsuarioBuscar(e.target.value)}
                  className="px-3 py-2 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              )}

              <Button
                variant="primary"
                size="sm"
                icon={<RefreshCw size={14} className={sincronizando ? 'animate-spin' : ''} />}
                onClick={handleSincronizar}
                disabled={sincronizando || (modoSincronizacion === 'especifico' && !codigoUsuarioBuscar.trim())}
                className="rounded-full"
              >
                {sincronizando ? 'Sincronizando...' : modoSincronizacion === 'especifico' ? 'Buscar Usuario' : 'Sincronizar'}
              </Button>
            </div>
          </div>

          {/* Barra de búsqueda y filtros */}
          <div className="mt-4 flex gap-4 items-center">
            {/* Búsqueda */}
            <div className="flex-1">
              <Input
                type="search"
                placeholder="Buscar por nombre, código, empresa o centro de costos..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                icon={<Search size={18} />}
              />
            </div>

            {/* Filtro de estado */}
            <div className="flex gap-2">
              <button
                onClick={() => setFiltroEstado('todos')}
                className={`px-4 py-2 text-xs font-bold uppercase tracking-wide rounded-lg transition-colors ${filtroEstado === 'todos'
                    ? 'bg-industrial-gray text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                Todos
              </button>
              <button
                onClick={() => setFiltroEstado('activos')}
                className={`px-4 py-2 text-xs font-bold uppercase tracking-wide rounded-lg transition-colors ${filtroEstado === 'activos'
                    ? 'bg-industrial-gray text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                Activos
              </button>
              <button
                onClick={() => setFiltroEstado('inactivos')}
                className={`px-4 py-2 text-xs font-bold uppercase tracking-wide rounded-lg transition-colors ${filtroEstado === 'inactivos'
                    ? 'bg-industrial-gray text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                Inactivos
              </button>
            </div>
          </div>

          {/* Filtro de origen (solo visible si hay usuarios sincronizados) */}
          {usuariosImpresora.length > 0 && (
            <div className="mt-3 flex gap-2 items-center">
              <span className="text-xs text-slate-600 font-semibold">Mostrar:</span>
              <button
                onClick={() => setMostrarOrigen('todos')}
                className={`px-3 py-1 text-xs font-bold uppercase tracking-wide rounded-lg transition-colors ${mostrarOrigen === 'todos'
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                Todos
              </button>
              <button
                onClick={() => setMostrarOrigen('db')}
                className={`px-3 py-1 text-xs font-bold uppercase tracking-wide rounded-lg transition-colors ${mostrarOrigen === 'db'
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                💾 Base de Datos
              </button>
              <button
                onClick={() => setMostrarOrigen('impresora')}
                className={`px-3 py-1 text-xs font-bold uppercase tracking-wide rounded-lg transition-colors ${mostrarOrigen === 'impresora'
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
              >
                🖨️ Solo Impresoras
              </button>
            </div>
          )}
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
                  ? 'Sincroniza con las impresoras para ver usuarios'
                  : 'No hay usuarios disponibles'}
            </p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-slate-200">
            <TablaUsuarios
              usuarios={usuariosPaginados}
              onEditar={handleEditarUsuario}
            />
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
        />
      )}
    </div>
  );
};
