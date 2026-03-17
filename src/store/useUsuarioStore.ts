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
    
    let filtrados = usuarios;
    
    // Filtrar por estado
    if (filtroEstado === 'activos') {
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
          (u.centro_costos && u.centro_costos.toLowerCase().includes(busquedaLower)) ||
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
