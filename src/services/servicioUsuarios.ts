import type { Usuario, ActualizarUsuario, UsuarioConEquipos } from '@/types/usuario';

/**
 * Servicio de Usuarios
 * 
 * Funciones para interactuar con la API de usuarios
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================================================
// Obtener Usuarios
// ============================================================================

/**
 * Obtiene todos los usuarios del sistema
 */
export async function obtenerUsuarios(
  skip: number = 0,
  limit: number = 100,
  soloActivos: boolean = true
): Promise<Usuario[]> {
  try {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
      active_only: soloActivos.toString(),
    });

    const response = await fetch(`${API_BASE_URL}/users/?${params}`);

    if (!response.ok) {
      throw new Error('Error al obtener usuarios');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al obtener usuarios:', error);
    throw error;
  }
}

/**
 * Obtiene un usuario por ID
 */
export async function obtenerUsuarioPorId(id: number): Promise<Usuario> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${id}`);

    if (!response.ok) {
      throw new Error(`Usuario con ID ${id} no encontrado`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al obtener usuario:', error);
    throw error;
  }
}

/**
 * Obtiene el estado de aprovisionamiento de un usuario (con equipos asignados)
 */
export async function obtenerUsuarioConEquipos(id: number): Promise<UsuarioConEquipos> {
  try {
    const response = await fetch(`${API_BASE_URL}/provisioning/user/${id}`);

    if (!response.ok) {
      throw new Error(`Error al obtener equipos del usuario ${id}`);
    }

    const data = await response.json();

    // Transformar respuesta del backend al formato del frontend
    return {
      id: data.user_id,
      name: data.user_name,
      codigo_de_usuario: '',
      empresa: data.empresa,
      centro_costos: data.centro_costos || '',
      network_username: '',
      smb_server: '',
      smb_port: 21,
      smb_path: data.smb_path || '',
      func_copier: false,
      func_printer: false,
      func_document_server: false,
      func_fax: false,
      func_scanner: false,
      func_browser: false,
      is_active: true,
      created_at: '',
      equipos: (data.printers || []).map((p: any) => ({
        printer_id: p.id,
        printer_name: p.hostname,
        printer_ip: p.ip_address,
        printer_location: p.location,
        entry_index: p.entry_index,
        permisos: {
          copiadora: p.permisos?.copiadora || false,
          impresora: p.permisos?.impresora || false,
          document_server: p.permisos?.document_server || false,
          fax: p.permisos?.fax || false,
          escaner: p.permisos?.escaner || false,
          navegador: p.permisos?.navegador || false,
        }
      })),
      total_equipos: data.total_printers || 0,
    };
  } catch (error) {
    console.error('Error al obtener usuario con equipos:', error);
    throw error;
  }
}

/**
 * Obtiene los detalles (permisos reales) de un usuario en una impresora específica
 * Utilizado para Lazy Loading
 */
export async function obtenerDetallesUsuarioImpresora(
  printerIp: string,
  entryIndex: string
): Promise<any> {
  try {
    const params = new URLSearchParams({
      printer_ip: printerIp,
      entry_index: entryIndex,
    });

    const response = await fetch(`${API_BASE_URL}/discovery/user-details?${params}`);

    if (!response.ok) {
      throw new Error(`Error al obtener detalles del usuario en ${printerIp}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al obtener detalles del usuario:', error);
    throw error;
  }
}

/**
 * Busca usuarios por nombre o email
 */
export async function buscarUsuarios(query: string): Promise<Usuario[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/search/${encodeURIComponent(query)}`);

    if (!response.ok) {
      throw new Error('Error al buscar usuarios');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al buscar usuarios:', error);
    return [];
  }
}

// ============================================================================
// Crear Usuario
// ============================================================================

/**
 * Crea un nuevo usuario en el sistema
 */
export async function crearUsuario(datos: any): Promise<Usuario> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datos),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error detallado del servidor:', errorData);

      const detail = typeof errorData.detail === 'string'
        ? errorData.detail
        : JSON.stringify(errorData.detail || errorData);

      throw new Error(detail || 'Error al crear usuario');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al crear usuario:', error);
    throw error;
  }
}

// ============================================================================
// Actualizar Usuario
// ============================================================================

/**
 * Actualiza la información de un usuario
 */
export async function actualizarUsuario(
  id: number,
  datos: ActualizarUsuario
): Promise<Usuario> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datos),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al actualizar usuario');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al actualizar usuario:', error);
    throw error;
  }
}

/**
 * Actualiza solo los permisos de un usuario
 */
export async function actualizarPermisos(
  id: number,
  permisos: {
    func_copier?: boolean;
    func_printer?: boolean;
    func_document_server?: boolean;
    func_fax?: boolean;
    func_scanner?: boolean;
    func_browser?: boolean;
  }
): Promise<Usuario> {
  return actualizarUsuario(id, permisos);
}

// ============================================================================
// Gestión de Equipos
// ============================================================================

/**
 * Actualiza los permisos de un usuario en un equipo específico
 */
export async function actualizarPermisosAsignacion(
  usuarioId: number,
  printerId: number,
  permisos: any,
  entryIndex?: string
): Promise<any> {
  try {
    const url = new URL(`${API_BASE_URL}/provisioning/update-assignment`);
    url.searchParams.append('user_id', usuarioId.toString());
    url.searchParams.append('printer_id', printerId.toString());
    if (entryIndex) url.searchParams.append('entry_index', entryIndex);

    const response = await fetch(url.toString(), {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(permisos),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al actualizar permisos en el equipo');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al actualizar permisos de asignación:', error);
    throw error;
  }
}

/**
 * Asigna equipos a un usuario
 */
export async function asignarEquipos(
  usuarioId: number,
  equipoIds: number[]
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/provisioning/provision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: usuarioId,
        printer_ids: equipoIds,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al asignar equipos');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al asignar equipos:', error);
    throw error;
  }
}

/**
 * Desasigna equipos de un usuario
 */
export async function desasignarEquipos(
  usuarioId: number,
  equipoIds: number[]
): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/provisioning/remove`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: usuarioId,
        printer_ids: equipoIds,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al desasignar equipos');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al desasignar equipos:', error);
    throw error;
  }
}

// ============================================================================
// Eliminar Usuario
// ============================================================================

/**
 * Elimina un usuario (soft delete)
 */
export async function eliminarUsuario(id: number): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Error al eliminar usuario');
    }
  } catch (error) {
    console.error('Error al eliminar usuario:', error);
    throw error;
  }
}

// ============================================================================
// Utilidades
// ============================================================================

/**
 * Obtiene iconos de permisos habilitados
 */
export function obtenerIconosPermisos(usuario: Usuario): string[] {
  const iconos: string[] = [];

  if (usuario.func_copier) {
    iconos.push(usuario.func_copier_color ? '📄🌈' : '📄');
  }
  if (usuario.func_printer) {
    iconos.push(usuario.func_printer_color ? '🖨️🌈' : '🖨️');
  }
  if (usuario.func_scanner) iconos.push('🔍');
  if (usuario.func_fax) iconos.push('📠');
  if (usuario.func_document_server) iconos.push('📁');
  if (usuario.func_browser) iconos.push('🌐');

  return iconos;
}

/**
 * Cuenta cuántos permisos tiene habilitados un usuario
 */
export function contarPermisosActivos(usuario: Usuario): number {
  let count = 0;
  if (usuario.func_copier) count++;
  if (usuario.func_printer) count++;
  if (usuario.func_scanner) count++;
  if (usuario.func_fax) count++;
  if (usuario.func_document_server) count++;
  if (usuario.func_browser) count++;
  return count;
}


// ============================================================================
// Actualizar Funciones en Impresora
// ============================================================================

/**
 * Actualiza las funciones de un usuario directamente en una impresora específica
 */
export async function actualizarFuncionesEnImpresora(
  printerIp: string,
  userCode: string,
  funciones: {
    copiadora: boolean;
    copiadora_color: boolean;
    impresora: boolean;
    impresora_color: boolean;
    escaner: boolean;
    document_server: boolean;
    fax: boolean;
    navegador: boolean;
  }
): Promise<{ success: boolean; message: string; user_code: string; printer_ip: string; functions_updated: any }> {
  try {
    const response = await fetch(`${API_BASE_URL}/provisioning/printers/${printerIp}/users/${userCode}/functions`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(funciones),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al actualizar funciones en la impresora');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al actualizar funciones en impresora:', error);
    throw error;
  }
}

/**
 * Sincroniza todos los usuarios de una impresora
 * Lee las funciones reales desde el hardware y actualiza la base de datos
 */
export async function sincronizarUsuariosImpresora(
  printerIp: string
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/provisioning/printers/${printerIp}/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al sincronizar usuarios de la impresora');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al sincronizar usuarios:', error);
    throw error;
  }
}

/**
 * Sincroniza los datos del usuario (carpeta, credenciales) a las impresoras especificadas
 */
export async function sincronizarUsuarioTodasImpresoras(
  usuarioId: number,
  printerIps: string[]
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/provisioning/users/${usuarioId}/sync-to-all-printers`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ printer_ips: printerIps }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error al sincronizar usuario a todas las impresoras');
    }

    return await response.json();
  } catch (error) {
    console.error('Error al sincronizar usuario a todas las impresoras:', error);
    throw error;
  }
}
