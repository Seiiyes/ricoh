import { useState, useEffect } from 'react';
import { Edit2, ChevronDown, ChevronRight, Trash2, RefreshCw } from 'lucide-react';
import { obtenerIconosPermisos, contarPermisosActivos } from '@/services/servicioUsuarios';
import { obtenerUsuarioConEquipos } from '@/services/servicioUsuarios';
import { Button, Spinner } from '@/components/ui';
import type { Usuario } from '@/types/usuario';
import type { EquipoAsignado } from '@/types/usuario';

interface FilaUsuarioProps {
  usuario: Usuario;
  expandido: boolean;
  desactivando?: boolean;
  onToggleExpandir: () => void;
  onEditar: () => void;
  onDesactivar: (usuario: Usuario) => void;
}

export const FilaUsuario = ({
  usuario,
  expandido,
  desactivando = false,
  onToggleExpandir,
  onEditar,
  onDesactivar,
}: FilaUsuarioProps) => {
  const [equipos, setEquipos] = useState<EquipoAsignado[]>([]);
  const [cargandoEquipos, setCargandoEquipos] = useState(false);
  const [equiposCargados, setEquiposCargados] = useState(false);

  const iconosPermisos = obtenerIconosPermisos(usuario);
  const totalPermisos = contarPermisosActivos(usuario);

  // Cargar equipos cuando se expande
  useEffect(() => {
    // Solo cargar equipos si:
    // 1. Está expandido
    // 2. No se han cargado aún
    // 3. Es un usuario de DB (tiene ID numérico)
    // 4. NO tiene información de impresoras (si tiene impresoras, no necesitamos cargar equipos)
    if (expandido && !equiposCargados && typeof usuario.id === 'number' && (!usuario.impresoras || usuario.impresoras.length === 0)) {
      cargarEquipos();
    }
  }, [expandido]);

  const cargarEquipos = async () => {
    // Verificación adicional: solo cargar si el ID es numérico
    if (typeof usuario.id !== 'number') {
      // console.log('⏭️ Saltando carga de equipos para usuario de impresora:', usuario.id);
      setEquiposCargados(true);
      return;
    }
    
    try {
      setCargandoEquipos(true);
      const datos = await obtenerUsuarioConEquipos(usuario.id);
      setEquipos(datos.equipos || []);
      setEquiposCargados(true);
    } catch (error) {
      console.error('Error al cargar equipos:', error);
      setEquipos([]);
      setEquiposCargados(true); // Marcar como cargado para evitar reintentos
    } finally {
      setCargandoEquipos(false);
    }
  };

  return (
    <>
      <tr className="hover:bg-slate-50/80 transition-all duration-300 group">
        {/* Origen */}
        <td className="px-4 py-3 text-center">
          <div className="flex flex-col gap-1 items-center justify-center">
            {(usuario.is_active === false || totalPermisos === 0) && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-red-100 text-red-800 border border-red-200" title={usuario.is_active === false ? "Usuario desactivado en Base de Datos" : "Usuario sin permisos activos en equipos"}>
                Inactivo
              </span>
            )}
            {usuario.en_db === false ? (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-100" title="Solo en impresoras">
                Solo Impresora
              </span>
            ) : usuario.impresoras && usuario.impresoras.length > 0 ? (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-purple-50 text-purple-700 border border-purple-100" title="En DB y en impresoras">
                Sincronizado
              </span>
            ) : (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-100" title="Solo en Base de Datos">
                Base de Datos
              </span>
            )}
          </div>
        </td>

        {/* Nombre con botón de expandir */}
        <td className="px-4 py-3">
          <button
            onClick={onToggleExpandir}
            className="flex items-center gap-2 text-sm font-medium text-slate-900 hover:text-ricoh-red transition-colors"
          >
            {expandido ? (
              <ChevronDown size={16} className="text-slate-400" />
            ) : (
              <ChevronRight size={16} className="text-slate-400" />
            )}
            {usuario.name}
          </button>
        </td>

        {/* Código */}
        <td className="px-4 py-3">
          <span className="font-mono text-sm text-slate-700 bg-slate-100 px-2 py-1 rounded">
            {usuario.codigo_de_usuario}
          </span>
        </td>

        {/* Empresa */}
        <td className="px-4 py-3 text-sm text-slate-600">
          {usuario.empresa || (
            <span className="text-slate-400 italic">Sin empresa</span>
          )}
        </td>

        {/* Centro de costos */}
        <td className="px-4 py-3 text-sm text-slate-600">
          {usuario.centro_costos || (
            <span className="text-slate-400 italic">Sin centro de costos</span>
          )}
        </td>

        {/* Impresoras */}
        <td className="px-4 py-3 text-center">
          {usuario.impresoras && usuario.impresoras.length > 0 ? (
            (() => {
              const activas = usuario.is_active === false
                ? 0
                : usuario.impresoras.filter(p => p.is_active !== false).length;
              const inactivas = usuario.is_active === false
                ? usuario.impresoras.length
                : usuario.impresoras.filter(p => p.is_active === false).length;
              return (
                <div className="flex items-center justify-center gap-1.5" title={`${activas} activas, ${inactivas} desactivadas`}>
                  {activas > 0 ? (
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 text-xs font-bold shadow-sm">
                      {activas}
                    </span>
                  ) : inactivas > 0 ? (
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 text-slate-400 text-xs font-bold border border-slate-200" title="Asignaciones desactivadas">
                      0
                    </span>
                  ) : (
                    <span className="text-xs text-slate-400 italic">-</span>
                  )}
                  <span className="text-xs text-slate-500">🖨️</span>
                </div>
              );
            })()
          ) : usuario.origen === 'db' ? (
            (() => {
              // Si se cargaron equipos perezosamente, contar cuántos tienen permisos activos
              const activas = usuario.is_active === false
                ? 0
                : equipos.filter(eq => eq.permisos && Object.values(eq.permisos).some(v => v === true)).length;
              const inactivas = equipos.length - activas;
              return (
                <div className="flex items-center justify-center gap-1.5" title={`${activas} activas, ${inactivas} desactivadas`}>
                  {activas > 0 ? (
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 text-xs font-bold shadow-sm">
                      {activas}
                    </span>
                  ) : equipos.length > 0 ? (
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 text-slate-400 text-xs font-bold border border-slate-200" title="Asignaciones desactivadas">
                      0
                    </span>
                  ) : (
                    <span className="text-xs text-slate-400 italic">-</span>
                  )}
                  <span className="text-xs text-slate-500">🖨️</span>
                </div>
              );
            })()
          ) : (
            <span className="text-xs text-slate-400 italic">-</span>
          )}
        </td>

        {/* Permisos */}
        <td className="px-4 py-3">
          <div className="flex items-center justify-center gap-1">
            {iconosPermisos.length > 0 ? (
              <>
                {iconosPermisos.slice(0, 4).map((icono, idx) => (
                  <span key={idx} className="text-lg">
                    {icono}
                  </span>
                ))}
                {totalPermisos > 4 && (
                  <span className="text-xs text-slate-500 ml-1">
                    +{totalPermisos - 4}
                  </span>
                )}
              </>
            ) : (
              <span className="text-slate-400 text-xs italic">Sin permisos</span>
            )}
          </div>
        </td>

        {/* Acciones */}
        <td className="px-4 py-3 text-center">
          <div className="flex items-center justify-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              icon={<Edit2 size={14} />}
              onClick={onEditar}
              disabled={desactivando}
              className="text-ricoh-red hover:bg-red-50/80 opacity-60 hover:opacity-100 transition-all focus:opacity-100 disabled:opacity-30 disabled:pointer-events-none"
            >
              Editar
            </Button>
            {usuario.en_db !== false && typeof usuario.id === 'number' && usuario.is_active !== false && (
              desactivando ? (
                <button
                  disabled
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-black rounded-lg bg-red-400 text-white cursor-not-allowed shadow-sm select-none animate-pulse"
                >
                  <RefreshCw size={13} className="animate-spin" />
                  Desactivando...
                </button>
              ) : (
                <Button
                  variant="ghost"
                  size="sm"
                  icon={<Trash2 size={14} />}
                  onClick={() => onDesactivar(usuario)}
                  className="text-slate-400 hover:text-red-600 hover:bg-red-50/80 opacity-60 hover:opacity-100 transition-all focus:opacity-100"
                >
                  Desactivar
                </Button>
              )
            )}
          </div>
        </td>
      </tr>

      {/* Fila expandida - Mostrar impresoras si existen */}
      {expandido && usuario.impresoras && usuario.impresoras.length > 0 && (
        <tr className="bg-red-50/30 animate-fade-in shadow-inner">
          <td colSpan={9} className="px-4 py-6 border-l-4 border-ricoh-red bg-gradient-to-r from-red-50/50 to-transparent">
            <div className="ml-8">
              <h4 className="text-xs font-bold text-slate-800 uppercase mb-4 tracking-wider flex items-center gap-2">
                <span className="p-1.5 bg-white rounded shadow-sm">🖨️</span>
                Impresoras donde está registrado este usuario
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {usuario.impresoras.map((impresora, idx) => (
                  <div
                    key={idx}
                    className={`flex items-start gap-4 backdrop-blur-sm border rounded-xl p-4 shadow-sm hover:shadow-md transition-all duration-300 ${
                      (usuario.is_active === false || impresora.is_active === false)
                        ? 'bg-slate-100/70 border-slate-200 opacity-60'
                        : 'bg-white border-slate-200/60'
                    }`}
                  >
                    <span className="text-2xl">🖨️</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-bold text-slate-900 truncate">
                          {impresora.printer_name}
                        </p>
                        {(usuario.is_active === false || impresora.is_active === false) && (
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-red-100 text-red-800 border border-red-200">
                            Desactivado
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 font-mono">
                        {impresora.printer_ip}
                      </p>
                      {impresora.carpeta && (
                        <p className="text-xs text-slate-600 mt-1 truncate" title={impresora.carpeta}>
                          📁 {impresora.carpeta}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 p-4 bg-white border border-slate-200 rounded-xl shadow-sm">
                <p className="text-sm text-slate-600 flex items-center gap-2">
                  <span className="text-ricoh-red">💡</span>
                  <span>
                    Este usuario está registrado en <span className="font-bold text-slate-800">{usuario.impresoras.length}</span> impresora(s).
                    {!usuario.en_db && ' Al editar, se guardará en la base de datos.'}
                  </span>
                </p>
              </div>
            </div>
          </td>
        </tr>
      )}
      
      {/* Fila expandida - Equipos asignados (solo para usuarios de DB sin impresoras) */}
      {expandido && usuario.origen !== 'impresora' && (!usuario.impresoras || usuario.impresoras.length === 0) && (
        <tr className="bg-slate-50/50 animate-fade-in shadow-inner">
          <td colSpan={9} className="px-4 py-6 border-l-4 border-slate-300 bg-gradient-to-r from-slate-100/50 to-transparent">
            <div className="ml-8">
              <h4 className="text-xs font-bold text-slate-700 uppercase mb-4 tracking-wider">
                Equipos Asignados
              </h4>
              
              {cargandoEquipos ? (
                <Spinner size="sm" text="Cargando equipos..." className="text-ricoh-red" />
              ) : equipos.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {equipos.map((equipo) => (
                    <div
                      key={equipo.id}
                      className={`flex items-center gap-3 backdrop-blur-sm border rounded-xl p-3 shadow-sm hover:shadow-md transition-all duration-300 ${
                        usuario.is_active === false
                          ? 'bg-slate-100/70 border-slate-200 opacity-60'
                          : 'bg-white border-slate-200/60'
                      }`}
                    >
                      <div
                        className={`w-2 h-2 rounded-full ${
                          usuario.is_active === false
                            ? 'bg-slate-400'
                            : equipo.status === 'online'
                            ? 'bg-green-500'
                            : 'bg-red-500'
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium text-slate-900 truncate">
                            {equipo.hostname}
                          </p>
                          {usuario.is_active === false && (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[9px] font-black uppercase tracking-wider bg-red-100 text-red-800 border border-red-200">
                              Desactivado
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-500 font-mono">
                          {equipo.ip_address}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400 italic py-2">
                  Este usuario no tiene equipos asignados
                </p>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
};
