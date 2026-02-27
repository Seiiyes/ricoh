import { useState } from 'react';
import { FilaUsuario } from './FilaUsuario';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import type { Usuario } from '@/types/usuario';

interface TablaUsuariosProps {
  usuarios: Usuario[];
  onEditar: (usuario: Usuario) => void;
}

type CampoOrden = 'origen' | 'nombre' | 'codigo' | 'empresa' | 'centro_costos' | 'impresoras' | 'estado';
type DireccionOrden = 'asc' | 'desc' | null;

export const TablaUsuarios = ({ usuarios, onEditar }: TablaUsuariosProps) => {
  const [usuarioExpandido, setUsuarioExpandido] = useState<number | string | null>(null);
  const [campoOrden, setCampoOrden] = useState<CampoOrden | null>(null);
  const [direccionOrden, setDireccionOrden] = useState<DireccionOrden>(null);

  const toggleExpandir = (id: number | string) => {
    setUsuarioExpandido(usuarioExpandido === id ? null : id);
  };

  const handleOrdenar = (campo: CampoOrden) => {
    if (campoOrden === campo) {
      // Ciclar: asc -> desc -> null
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
      case 'estado':
        return usuario.is_active ? 1 : 0;
      default:
        return '';
    }
  };

  const usuariosOrdenados = [...usuarios].sort((a, b) => {
    if (!campoOrden || !direccionOrden) return 0;

    const valorA = obtenerValorOrden(a, campoOrden);
    const valorB = obtenerValorOrden(b, campoOrden);

    if (valorA < valorB) return direccionOrden === 'asc' ? -1 : 1;
    if (valorA > valorB) return direccionOrden === 'asc' ? 1 : -1;
    return 0;
  });

  const IconoOrden = ({ campo }: { campo: CampoOrden }) => {
    if (campoOrden !== campo) {
      return <ArrowUpDown size={14} className="opacity-40" />;
    }
    if (direccionOrden === 'asc') {
      return <ArrowUp size={14} className="text-ricoh-red" />;
    }
    if (direccionOrden === 'desc') {
      return <ArrowDown size={14} className="text-ricoh-red" />;
    }
    return <ArrowUpDown size={14} className="opacity-40" />;
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-slate-50 border-b border-slate-200">
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
              <button
                onClick={() => handleOrdenar('estado')}
                className="flex items-center gap-1 hover:text-ricoh-red transition-colors mx-auto"
              >
                Estado
                <IconoOrden campo="estado" />
              </button>
            </th>
            <th className="px-4 py-3 text-center text-xs font-bold text-slate-600 uppercase tracking-wider">
              Acciones
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {usuariosOrdenados.map((usuario) => (
            <FilaUsuario
              key={usuario.id}
              usuario={usuario}
              expandido={usuarioExpandido === usuario.id}
              onToggleExpandir={() => toggleExpandir(usuario.id)}
              onEditar={() => onEditar(usuario)}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};
