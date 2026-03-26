/**
 * Servicio de usuarios admin
 * Maneja operaciones CRUD de usuarios administradores (solo superadmin)
 */
import apiClient from './apiClient';
import { AdminUser } from './authService';

export interface AdminUserCreate {
  username: string;
  password: string;
  nombre_completo: string;
  email: string;
  rol: 'superadmin' | 'admin' | 'viewer' | 'operator';
  empresa_id: number | null;
}

export interface AdminUserUpdate {
  nombre_completo?: string;
  email?: string;
  rol?: 'superadmin' | 'admin' | 'viewer' | 'operator';
  empresa_id?: number | null;
}

export interface AdminUserListResponse {
  items: AdminUser[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface GetAllParams {
  page?: number;
  page_size?: number;
  search?: string;
  rol?: string;
  empresa_id?: number;
}

class AdminUserService {
  /**
   * Obtener todos los usuarios admin con paginación, búsqueda y filtros
   */
  async getAll(params?: GetAllParams): Promise<AdminUserListResponse> {
    const response = await apiClient.get<AdminUserListResponse>('/admin-users', { params });
    return response.data;
  }
  
  /**
   * Obtener usuario admin por ID
   */
  async getById(id: number): Promise<AdminUser> {
    const response = await apiClient.get<AdminUser>(`/admin-users/${id}`);
    return response.data;
  }
  
  /**
   * Crear nuevo usuario admin
   */
  async create(data: AdminUserCreate): Promise<AdminUser> {
    const response = await apiClient.post<AdminUser>('/admin-users', data);
    return response.data;
  }
  
  /**
   * Actualizar usuario admin
   */
  async update(id: number, data: AdminUserUpdate): Promise<AdminUser> {
    const response = await apiClient.put<AdminUser>(`/admin-users/${id}`, data);
    return response.data;
  }
  
  /**
   * Desactivar usuario admin (soft delete)
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/admin-users/${id}`);
  }
}

export default new AdminUserService();
