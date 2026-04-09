import type { Usuario, ActualizarUsuario, UsuarioConEquipos } from '@/types/usuario';
import apiClient from './apiClient';

/**
 * Servicio de Usuarios
 * 
 * Funciones para interactuar con la API de usuarios
 * Usa apiClient para requests autenticados
 */

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
    // Convertir skip/limit a page/page_size requeridos por el backend
    const page = Math.floor(skip / limit) + 1;
    const page_size = limit;
    
    const response = await apiClient.get('/users/', {
      params: {
        page,
        page_size,
        active_only: soloActivos,
      },
    });
    // Backend retorna UserListResponse con estructura { items: [...], total, page, ... }
    return response.data.items || response.data;
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
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
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
    const response = await apiClient.get(`/provisioning/user/${id}`);
    const data = response.data;

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
    const response = await apiClient.get('/discovery/user-details', {
      params: {
        printer_ip: printerIp,
        entry_index: entryIndex,
      },
    });
    return response.data;
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
    const response = await apiClient.get(`/users/search/${encodeURIComponent(query)}`);
    return response.data;
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
    const response = await apiClient.post('/users/', datos);
    return response.data;
  } catch (error: any) {
    console.error('Error al crear usuario:', error);
    const detail = error.response?.data?.detail || error.message || 'Error al crear usuario';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
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
    const response = await apiClient.put(`/users/${id}`, datos);
    return response.data;
  } catch (error: any) {
    console.error('Error al actualizar usuario:', error);
    const detail = error.response?.data?.detail || error.message || 'Error al actualizar usuario';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
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
    // Enviar todo en el body (no en query params)
    const body = {
      user_id: usuarioId,
      printer_id: printerId,
      permissions: permisos,
      entry_index: entryIndex || null
    };

    const response = await apiClient.patch('/provisioning/update-assignment', body);
    return response.data;
  } catch (error: any) {
    console.error('Error al actualizar permisos de asignación:', error);
    const detail = error.response?.data?.detail || error.message || 'Error al actualizar permisos en el equipo';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
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
    const response = await apiClient.post('/provisioning/provision', {
      user_id: usuarioId,
      printer_ids: equipoIds,
    });
    return response.data;
  } catch (error: any) {
    console.error('Error al asignar equipos:', error);
    const detail = error.response?.data?.detail || error.message || 'Error al asignar equipos';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
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
    const response = await apiClient.delete('/provisioning/remove', {
      data: {
        user_id: usuarioId,
        printer_ids: equipoIds,
      },
    });
    return response.data;
  } catch (error: any) {
    console.error('Error al desasignar equipos:', error);
    const detail = error.response?.data?.detail || error.message || 'Error al desasignar equipos';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
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
    await apiClient.delete(`/users/${id}`);
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
    const response = await apiClient.put(`/provisioning/printers/${printerIp}/users/${userCode}/functions`, funciones);
    return response.data;
  } catch (error: any) {
    console.error('Error al actualizar funciones en impresora:', error);
    const detail = error.response?.data?.detail || error.message || 'Error al actualizar funciones en la impresora';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
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
    const response = await apiClient.post(`/provisioning/printers/${printerIp}/sync`);
    return response.data;
  } catch (error: any) {
    console.error('Error al sincronizar usuarios:', error);
    const detail = error.response?.data?.detail || error.message || 'Error al sincronizar usuarios de la impresora';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
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
    const response = await apiClient.put(`/provisioning/users/${usuarioId}/sync-to-all-printers`, {
      printer_ips: printerIps,
    });
    return response.data;
  } catch (error: any) {
    console.error('Error al sincronizar usuario a todas las impresoras:', error);
    const detail = error.response?.data?.detail || error.message || 'Error al sincronizar usuario a todas las impresoras';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
}
