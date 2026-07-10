/**
 * Close Service
 * Servicio para operaciones de cierres mensuales de contadores
 */
import apiClient from './apiClient';
import type { CierreMensual, ComparacionCierres, CierreMensualDetalle as CierreDetalle } from '../components/contadores/cierres/types';

export interface CreateCloseRequest {
  printer_id: number;
  fecha_inicio: string; // YYYY-MM-DD
  fecha_fin: string; // YYYY-MM-DD
  cerrado_por?: string;
  notas?: string;
}

export interface CreateCierreMasivoRequest {
  fecha_inicio: string; // YYYY-MM-DD
  fecha_fin: string; // YYYY-MM-DD
  cerrado_por?: string;
  notas?: string;
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
  },

  /**
   * Guardar una comparación mensual
   */
  saveComparacion: async (data: {
    titulo: string;
    descripcion?: string;
    cierre1_id: number;
    cierre2_id: number;
    snapshot_json: any;
  }): Promise<any> => {
    const response = await apiClient.post<any>('/api/counters/comparaciones', data);
    return response.data;
  },

  /**
   * Obtener comparaciones guardadas
   */
  getComparacionesGuardadas: async (params?: {
    cierre1_id?: number;
    cierre2_id?: number;
    empresa_id?: number;
  }): Promise<any[]> => {
    const response = await apiClient.get<any[]>('/api/counters/comparaciones', { params });
    return response.data;
  },

  /**
   * Eliminar una comparación guardada
   */
  deleteComparacion: async (comparacionId: number): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/api/counters/comparaciones/${comparacionId}`);
    return response.data;
  },

  /**
   * Obtener todas las programaciones de cierres
   */
  getSchedules: async (): Promise<ScheduledClosure[]> => {
    const response = await apiClient.get<ScheduledClosure[]>('/api/counters/schedules');
    return response.data;
  },

  /**
   * Crear una programación de cierre masivo
   */
  createSchedule: async (data: CreateScheduledClosureRequest): Promise<ScheduledClosure> => {
    const response = await apiClient.post<ScheduledClosure>('/api/counters/schedules', data);
    return response.data;
  },

  /**
   * Actualizar una programación de cierre
   */
  updateSchedule: async (id: number, data: UpdateScheduledClosureRequest): Promise<ScheduledClosure> => {
    const response = await apiClient.put<ScheduledClosure>(`/api/counters/schedules/${id}`, data);
    return response.data;
  },

  /**
   * Eliminar una programación de cierre
   */
  deleteSchedule: async (id: number): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/api/counters/schedules/${id}`);
    return response.data;
  }
};

export interface ScheduledClosure {
  id: number;
  frequency: string;
  scheduled_time: string;
  specific_date?: string;
  day_of_week?: number;
  day_of_month?: number;
  empresa_id?: number;
  is_active: boolean;
  notas?: string;
  created_by: string;
  last_run?: string;
  next_run?: string;
  created_at: string;
  updated_at?: string;
}

export interface CreateScheduledClosureRequest {
  frequency: string;
  scheduled_time: string;
  specific_date?: string;
  day_of_week?: number;
  day_of_month?: number;
  empresa_id?: number;
  notas?: string;
}

export interface UpdateScheduledClosureRequest {
  is_active?: boolean;
  frequency?: string;
  scheduled_time?: string;
  specific_date?: string;
  day_of_week?: number;
  day_of_month?: number;
  empresa_id?: number;
  notas?: string;
}

export default closeService;

