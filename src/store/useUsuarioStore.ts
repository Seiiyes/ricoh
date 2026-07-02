import { create } from 'zustand';
import type { Usuario } from '@/types/usuario';

interface UsuarioStore {
  // Estado
  usuarios: Usuario[];
  usuarioSeleccionado: Usuario | null;
  cargando: boolean;
  busqueda: string;
  filtroEstado: 'todos' | 'activos' | 'inactivos';
  
  // Acciones
  setUsuarios: (usuarios: Usuario[]) => void;
  agregarUsuario: (usuario: Usuario) => void;
  actualizarUsuario: (id: number, datos: Partial<Usuario>) => void;
  eliminarUsuario: (id: number) => void;
  setUsuarioSeleccionado: (usuario: Usuario | null) => void;
  setCargando: (cargando: boolean) => void;
  setBusqueda: (busqueda: string) => void;
  setFiltroEstado: (estado: 'todos' | 'activos' | 'inactivos') => void;
  
  // Utilidades
  obtenerUsuariosFiltrados: () => Usuario[];
  limpiar: () => void;
}

export const useUsuarioStore = create<UsuarioStore>((set, get) => ({
  // Estado inicial
  usuarios: [],
  usuarioSeleccionado: null,
  cargando: false,
  busqueda: '',
  filtroEstado: 'todos',
  
  // Acciones
  setUsuarios: (usuarios) => set({ usuarios }),
  
  agregarUsuario: (usuario) => set((state) => ({
    usuarios: [...state.usuarios, usuario],
  })),
  
  actualizarUsuario: (id, datos) => set((state) => ({
    usuarios: state.usuarios.map((u) =>
      u.id === id ? { ...u, ...datos } : u
    ),
  })),
  
  eliminarUsuario: (id) => set((state) => ({
    usuarios: state.usuarios.filter((u) => u.id !== id),
  })),
  
  setUsuarioSeleccionado: (usuario) => set({ usuarioSeleccionado: usuario }),
  
  setCargando: (cargando) => set({ cargando }),
  
  setBusqueda: (busqueda) => set({ busqueda }),
  
  setFiltroEstado: (estado) => set({ filtroEstado: estado }),
  
  // Utilidades
  obtenerUsuariosFiltrados: () => {
    const { usuarios, busqueda, filtroEstado } = get();
    
    // Asegurar que usuarios es un array
    if (!Array.isArray(usuarios)) {
      console.error('usuarios no es un array:', usuarios);
      return [];
    }





    /**
     * Definición de negocio solicitada por el usuario:
     * - Activo:   Tiene al menos un permiso habilitado en alguna impresora asignada.
     * - Inactivo: No tiene ningún permiso habilitado en ninguna de sus impresoras asignadas
     *             (o no tiene impresoras asignadas).
     */
    const esInactivo = (u: Usuario): boolean => {
      const impresoras = u.impresoras;
      if (impresoras && impresoras.length > 0) {
        return impresoras.every((imp) => {
          const p = imp.permisos;
          if (!p) return true; // Sin permisos = inactivo
          return (
            !p.copiadora &&
            !p.copiadora_color &&
            !p.impresora &&
            !p.impresora_color &&
            !p.document_server &&
            !p.fax &&
            !p.escaner &&
            !p.navegador
          );
        });
      }
      // Sin impresoras asignadas = Inactivo
      return true;
    };

    let filtrados = usuarios;
    
    // Filtros basados puramente en la existencia de permisos en las impresoras
    if (filtroEstado === 'activos' && !busqueda.trim()) {
      filtrados = filtrados.filter((u) => !esInactivo(u));
    } else if (filtroEstado === 'inactivos') {
      filtrados = filtrados.filter((u) => esInactivo(u));
    }
    
    // Filtrar por búsqueda
    if (busqueda.trim()) {
      const busquedaLower = busqueda.toLowerCase().trim();
      filtrados = filtrados.filter(
        (u) =>
          u.name.toLowerCase().includes(busquedaLower) ||
          u.codigo_de_usuario.toLowerCase().includes(busquedaLower) ||
          (u.empresa && u.empresa.toLowerCase().includes(busquedaLower)) ||
          (u.centro_costos && u.centro_costos.toLowerCase().includes(busquedaLower))
      );
    }
    
    return filtrados;
  },
  
  limpiar: () => set({
    usuarios: [],
    usuarioSeleccionado: null,
    cargando: false,
    busqueda: '',
    filtroEstado: 'todos',
  }),
}));
