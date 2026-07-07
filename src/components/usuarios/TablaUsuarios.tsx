import { useState } from 'react';
import { FilaUsuario } from './FilaUsuario';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import type { Usuario } from '@/types/usuario';

interface TablaUsuariosProps {
  usuarios: Usuario[];
  onEditar: (usuario: Usuario) => void;
  onDesactivar: (usuario: Usuario) => void;
  desactivandoUsuarioId: number | null;
  campoOrden: CampoOrden | null;
  direccionOrden: DireccionOrden;
  onOrdenar: (campo: CampoOrden) => void;
}

export type CampoOrden = 'origen' | 'nombre' | 'codigo' | 'empresa' | 'centro_costos' | 'impresoras';
export type DireccionOrden = 'asc' | 'desc' | null;

export const TablaUsuarios = ({ 
  usuarios, 
  onEditar, 
  onDesactivar,
  desactivandoUsuarioId,
  campoOrden,
  direccionOrden,
  onOrdenar
}: TablaUsuariosProps) => {
  const [usuarioExpandido, setUsuarioExpandido] = useState<number | string | null>(null);

  const toggleExpandir = (id: number | string) => {
    setUsuarioExpandido(usuarioExpandido === id ? null : id);
  };

  const handleOrdenar = (campo: CampoOrden) => {
    onOrdenar(campo);
  };

  const obtenerValorOrden = (usuario: Usuario, campo: CampoOrden): any => {
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

  // Ordenar usuarios según el campo y dirección seleccionados
  const usuariosOrdenados = [...usuarios].sort((a, b) => {
    if (!campoOrden || !direccionOrden) return 0;

    const valorA = obtenerValorOrden(a, campoOrden);
    const valorB = obtenerValorOrden(b, campoOrden);
    const comparacion = valorA < valorB ? -1 : valorA > valorB ? 1 : 0;
    
    return direccionOrden === 'asc' ? comparacion : -comparacion;
  });

  // Componente para mostrar el icono de ordenamiento
  const IconoOrden = ({ campo }: { campo: CampoOrden }) => {
    const esActivo = campoOrden === campo;
    const icono = !esActivo || !direccionOrden ? ArrowUpDown :
                  direccionOrden === 'asc' ? ArrowUp : ArrowDown;
    const Icon = icono;
    
    return (
      <Icon 
        size={14} 
        className={esActivo ? "text-ricoh-red" : "opacity-40"} 
      />
    );
  };

  return (
    <div className="overflow-x-auto rounded-2xl">
      <table className="w-full text-left border-collapse relative">
        <thead className="sticky top-0 z-10 bg-slate-50/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
              <button
                onClick={() => handleOrdenar('origen')}
                className="flex items-center gap-1 hover:text-ricoh-red transition-colors"
              >
                Origen
                <IconoOrden campo="origen" />
              </button>
            </th>
            <th className="px-4 py-3 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
              <button
                onClick={() => handleOrdenar('nombre')}
                className="flex items-center gap-1 hover:text-ricoh-red transition-colors"
              >
                Nombre
                <IconoOrden campo="nombre" />
              </button>
            </th>
            <th className="px-4 py-3 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
              <button
                onClick={() => handleOrdenar('codigo')}
                className="flex items-center gap-1 hover:text-ricoh-red transition-colors"
              >
                Código
                <IconoOrden campo="codigo" />
              </button>
            </th>
            <th className="px-4 py-3 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
              <button
                onClick={() => handleOrdenar('empresa')}
                className="flex items-center gap-1 hover:text-ricoh-red transition-colors"
              >
                Empresa
                <IconoOrden campo="empresa" />
              </button>
            </th>
            <th className="px-4 py-3 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">
              <button
                onClick={() => handleOrdenar('centro_costos')}
                className="flex items-center gap-1 hover:text-ricoh-red transition-colors"
              >
                Centro de costos
                <IconoOrden campo="centro_costos" />
              </button>
            </th>
            <th className="px-4 py-3 text-center text-xs font-bold text-slate-600 uppercase tracking-wider">
              <button
                onClick={() => handleOrdenar('impresoras')}
                className="flex items-center gap-1 hover:text-ricoh-red transition-colors mx-auto"
              >
                Impresoras
                <IconoOrden campo="impresoras" />
              </button>
            </th>
            <th className="px-4 py-3 text-center text-xs font-bold text-slate-600 uppercase tracking-wider">
              Permisos
            </th>
            <th className="px-4 py-3 text-center text-xs font-bold text-slate-600 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100/50">
          {usuariosOrdenados.map((usuario) => (
            <FilaUsuario
              key={usuario.id}
              usuario={usuario}
              expandido={usuarioExpandido === usuario.id}
              desactivando={typeof usuario.id === 'number' && desactivandoUsuarioId === usuario.id}
              onToggleExpandir={() => toggleExpandir(usuario.id)}
              onEditar={() => onEditar(usuario)}
              onDesactivar={onDesactivar}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};
