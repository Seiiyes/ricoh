/**
 * Close Service
 * Servicio para operaciones de cierres mensuales de contadores
 */
import apiClient from './apiClient';

export interface CreateCloseRequest {
  printer_id: number;
  tipo_periodo: 'diario' | 'semanal' | 'mensual' | 'personalizado';
  fecha_inicio: string; // YYYY-MM-DD
  fecha_fin: string; // YYYY-MM-DD
  cerrado_por?: string;
  notas?: string;
}

export interface CreateCierreMasivoRequest {
  tipo_periodo: 'diario' | 'semanal' | 'mensual' | 'personalizado';
  fecha_inicio: string; // YYYY-MM-DD
  fecha_fin: string; // YYYY-MM-DD
  cerrado_por?: string;
  notas?: string;
}

export interface CierreMensual {
  id: number;
  printer_id: number;
  periodo: string;
  fecha_cierre: string;
  contador_total: number;
  contador_color: number;
  contador_bn: number;
  notas?: string;
  created_at: string;
}

export interface CierreDetalle {
  cierre: CierreMensual;
  usuarios: Array<{
    user_id: number;
    nombre: string;
    codigo_de_usuario: string;
    contador_total: number;
    contador_color: number;
    contador_bn: number;
  }>;
  total_pages: number;
  current_page: number;
}

export interface ComparacionCierres {
  cierre1: CierreMensual;
  cierre2: CierreMensual;
  diferencia_total: number;
  diferencia_color: number;
  diferencia_bn: number;
  usuarios_cierre1: any[];
  usuarios_cierre2: any[];
}

export interface CierreResult {
  printer_id: number;
  printer_name: string;
  success: boolean;
  cierre_id?: number;
  total_paginas: number;
  usuarios_count: number;
  error?: string;
}

export interface CloseAllPrintersResponse {
  success: boolean;
  message: string;
  successful: number;
  failed: number;
  total: number;
  results: CierreResult[];
}

export const closeService = {
  /**
   * Crear un nuevo cierre mensual
   */
  createClose: async (data: CreateCloseRequest): Promise<CierreMensual> => {
    const response = await apiClient.post<CierreMensual>('/api/counters/close', data);
    return response.data;
  },

  /**
   * Crear cierres en todas las impresoras simultáneamente
   */
  createCloseAllPrinters: async (data: CreateCierreMasivoRequest): Promise<CloseAllPrintersResponse> => {
    const response = await apiClient.post<CloseAllPrintersResponse>('/api/counters/close-all', data);
    return response.data;
  },

  /**
   * Obtener todos los cierres mensuales
   */
  getMonthlyCloses: async (): Promise<CierreMensual[]> => {
    const response = await apiClient.get<CierreMensual[]>('/api/counters/monthly');
    return response.data;
  },

  /**
   * Obtener cierres de una impresora específica
   */
  getClosesByPrinter: async (printerId: number): Promise<CierreMensual[]> => {
    const response = await apiClient.get<CierreMensual[]>(`/api/counters/monthly/${printerId}`);
    return response.data;
  },

  /**
   * Obtener detalle de un cierre con paginación
   */
  getCloseDetail: async (closeId: number, page: number = 1, pageSize: number = 50): Promise<CierreDetalle> => {
    const response = await apiClient.get<CierreDetalle>(
      `/api/counters/monthly/${closeId}/detail`,
      { params: { page, page_size: pageSize } }
    );
    return response.data;
  },

  /**
   * Comparar dos cierres mensuales
   */
  compareCloses: async (closeId1: number, closeId2: number): Promise<ComparacionCierres> => {
    const response = await apiClient.get<ComparacionCierres>(
      `/api/counters/monthly/compare/${closeId1}/${closeId2}`
    );
    return response.data;
  },

  /**
   * Obtener usuarios de un cierre
   */
  getCloseUsers: async (closeId: number) => {
    const response = await apiClient.get(`/api/counters/monthly/${closeId}/users`);
    return response.data;
  },

  /**
   * Obtener suma de usuarios vs contador total
   */
  getCloseSummary: async (closeId: number) => {
    const response = await apiClient.get(`/api/counters/monthly/${closeId}/suma-usuarios`);
    return response.data;
  }
};

export default closeService;
