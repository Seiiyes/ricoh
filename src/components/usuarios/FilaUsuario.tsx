import { useState, useEffect } from 'react';
import { Edit2, ChevronDown, ChevronRight, Loader2 } from 'lucide-react';
import { obtenerIconosPermisos, contarPermisosActivos } from '@/services/servicioUsuarios';
import { obtenerUsuarioConEquipos } from '@/services/servicioUsuarios';
import type { Usuario } from '@/types/usuario';
import type { EquipoAsignado } from '@/types/usuario';

interface FilaUsuarioProps {
  usuario: Usuario;
  expandido: boolean;
  onToggleExpandir: () => void;
  onEditar: () => void;
}

export const FilaUsuario = ({
  usuario,
  expandido,
  onToggleExpandir,
  onEditar,
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
      console.log('⏭️ Saltando carga de equipos para usuario de impresora:', usuario.id);
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
      <tr className="hover:bg-slate-50 transition-colors">
        {/* Origen */}
        <td className="px-4 py-3 text-center">
          {usuario.en_db === false ? (
            <span className="inline-flex items-center gap-1 text-xs font-bold text-blue-700" title="Solo en impresoras">
              🖨️
            </span>
          ) : usuario.impresoras && usuario.impresoras.length > 0 ? (
            <span className="inline-flex items-center gap-1 text-xs font-bold text-purple-700" title="En DB y en impresoras">
              💾🖨️
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-xs font-bold text-green-700" title="Solo en Base de Datos">
              💾
            </span>
          )}
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
            <div className="flex items-center justify-center gap-1">
              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 text-xs font-bold">
                {usuario.impresoras.length}
              </span>
              <span className="text-xs text-slate-500">🖨️</span>
            </div>
          ) : usuario.origen === 'db' ? (
            <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-700 text-xs font-bold">
              {equipos.length}
            </span>
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

        {/* Estado */}
        <td className="px-4 py-3 text-center">
          {usuario.is_active ? (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700">
              Activo
            </span>
          ) : (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700">
              Inactivo
            </span>
          )}
        </td>

        {/* Acciones */}
        <td className="px-4 py-3 text-center">
          <button
            onClick={onEditar}
            className="inline-flex items-center gap-1 px-3 py-1 text-xs font-bold text-ricoh-red hover:bg-red-50 rounded transition-colors"
          >
            <Edit2 size={14} />
            Editar
          </button>
        </td>
      </tr>

      {/* Fila expandida - Mostrar impresoras si existen */}
      {expandido && usuario.impresoras && usuario.impresoras.length > 0 && (
        <tr className="bg-blue-50">
          <td colSpan={9} className="px-4 py-4">
            <div className="ml-8">
              <h4 className="text-xs font-bold text-slate-600 uppercase mb-3">
                🖨️ Impresoras donde está registrado este usuario
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {usuario.impresoras.map((impresora, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 bg-white border border-blue-200 rounded-lg p-3"
                  >
                    <span className="text-2xl">🖨️</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold text-slate-900 truncate">
                        {impresora.printer_name}
                      </p>
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
              
              <div className="mt-3 p-3 bg-blue-100 border border-blue-200 rounded-lg">
                <p className="text-xs text-blue-800">
                  💡 Este usuario está registrado en <span className="font-bold">{usuario.impresoras.length}</span> impresora(s).
                  {!usuario.en_db && ' Al editar, se guardará en la base de datos.'}
                </p>
              </div>
            </div>
          </td>
        </tr>
      )}
      
      {/* Fila expandida - Equipos asignados (solo para usuarios de DB sin impresoras) */}
      {expandido && usuario.origen !== 'impresora' && (!usuario.impresoras || usuario.impresoras.length === 0) && (
        <tr className="bg-slate-50">
          <td colSpan={9} className="px-4 py-4">
            <div className="ml-8">
              <h4 className="text-xs font-bold text-slate-600 uppercase mb-2">
                Equipos Asignados
              </h4>
              
              {cargandoEquipos ? (
                <div className="flex items-center gap-2 text-slate-400 text-sm py-2">
                  <Loader2 size={16} className="animate-spin" />
                  Cargando equipos...
                </div>
              ) : equipos.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                  {equipos.map((equipo) => (
                    <div
                      key={equipo.id}
                      className="flex items-center gap-2 bg-white border border-slate-200 rounded px-3 py-2"
                    >
                      <div
                        className={`w-2 h-2 rounded-full ${
                          equipo.status === 'online'
                            ? 'bg-green-500'
                            : 'bg-red-500'
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900 truncate">
                          {equipo.hostname}
                        </p>
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
