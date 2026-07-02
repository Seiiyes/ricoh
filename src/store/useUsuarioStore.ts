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
     * Clasificación de estado del usuario:
     * - Activos   → is_active === true  en BD (fuente de verdad oficial)
     * - Inactivos → is_active === false en BD
     * Los dos grupos son mutuamente excluyentes: Activos + Inactivos = Total
     *
     * Nota: La función esInactivo (permisos) se mantiene disponible para uso futuro
     * (ej: badge visual "Sin permisos"), pero NO rige el filtro de estado.
     */
    const esInactivo = (u: Usuario): boolean => {
      const impresoras = u.impresoras;
      if (impresoras && impresoras.length > 0) {
        return impresoras.every((imp) => {
          const p = imp.permisos;
          if (!p) return true;
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
      return !u.is_active;
    };

    // Suprimir advertencia del compilador: esInactivo está disponible para uso futuro
    void esInactivo;

    let filtrados = usuarios;
    
    // Filtros mutuamente excluyentes — usan is_active de BD
    if (filtroEstado === 'activos' && !busqueda.trim()) {
      filtrados = filtrados.filter((u) => u.is_active);
    } else if (filtroEstado === 'inactivos') {
      filtrados = filtrados.filter((u) => !u.is_active);
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
