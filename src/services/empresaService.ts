/**
 * Servicio de empresas
 * Maneja operaciones CRUD de empresas (solo superadmin)
 */
import apiClient from './apiClient';

export interface Empresa {
  id: number;
  razon_social: string;
  nombre_comercial: string;
  nit: string | null;
  direccion: string | null;
  telefono: string | null;
  email: string | null;
  contacto_nombre: string | null;
  contacto_cargo: string | null;
  logo_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmpresaCreate {
  razon_social: string;
  nombre_comercial: string;
  nit?: string;
  direccion?: string;
  telefono?: string;
  email?: string;
  contacto_nombre?: string;
  contacto_cargo?: string;
  logo_url?: string;
}

export interface EmpresaUpdate {
  razon_social?: string;
  nombre_comercial: string;
  nit?: string;
  direccion?: string;
  telefono?: string;
  email?: string;
  contacto_nombre?: string;
  contacto_cargo?: string;
  logo_url?: string;
}

export interface EmpresaListResponse {
  items: Empresa[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface GetAllParams {
  page?: number;
  page_size?: number;
  search?: string;
}

export interface CentroCosto {
  id: number;
  nombre: string;
  is_active: boolean;
}

export interface CentroCostosSugerenciasResponse {
  propios: CentroCosto[];
  sugerencias_globales: string[];
}

class EmpresaService {
  /**
   * Obtener todas las empresas con paginación y búsqueda
   */
  async getAll(params?: GetAllParams): Promise<EmpresaListResponse> {
    const response = await apiClient.get<EmpresaListResponse>('/empresas', { params });
    return response.data;
  }
  
  /**
   * Obtener empresa por ID
   */
  async getById(id: number): Promise<Empresa> {
    const response = await apiClient.get<Empresa>(`/empresas/${id}`);
    return response.data;
  }
  
  /**
   * Crear nueva empresa
   */
  async create(data: EmpresaCreate): Promise<Empresa> {
    const response = await apiClient.post<Empresa>('/empresas', data);
    return response.data;
  }
  
  /**
   * Actualizar empresa
   */
  async update(id: number, data: EmpresaUpdate): Promise<Empresa> {
    const response = await apiClient.put<Empresa>(`/empresas/${id}`, data);
    return response.data;
  }
  
  /**
   * Desactivar empresa (soft delete)
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/empresas/${id}`);
  }
  /**
   * Obtener centros de costos de una empresa y sugerencias globales
   */
  async getCentroCostos(empresaName: string): Promise<CentroCostosSugerenciasResponse> {
    const response = await apiClient.get<CentroCostosSugerenciasResponse>(`/empresas/by-name/${encodeURIComponent(empresaName)}/centro-costos`);
    return response.data;
  }
}

export default new EmpresaService();
