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
  filtroEstado: 'activos',
  
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
     * Un usuario se considera INACTIVO cuando:
     * - Tiene al menos una impresora asignada (impresoras.length > 0), Y
     * - En TODAS sus impresoras asignadas, TODOS los permisos están en false.
     * 
     * Si el usuario no tiene impresoras asignadas, se cae en el campo is_active de la BD.
     */
    const esInactivo = (u: Usuario): boolean => {
      const impresoras = u.impresoras;
      if (impresoras && impresoras.length > 0) {
        // Revisar si TODAS las impresoras tienen TODOS los permisos en false
        return impresoras.every((imp) => {
          const p = imp.permisos;
          if (!p) return true; // Sin permisos = todo desactivado
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
      // Sin impresoras: usar el campo is_active de BD como fallback
      return !u.is_active;
    };

    let filtrados = usuarios;
    
    // Filtrar por estado
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
    filtroEstado: 'activos',
  }),
}));
