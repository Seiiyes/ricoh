/**
 * Counter Service
 * 
 * Service layer for counter API integration.
 * Encapsulates all HTTP calls to the backend counter endpoints.
 * Uses apiClient for authenticated requests.
 */

import type {
  TotalCounter,
  UserCounter,
  MonthlyClose,
  MonthlyCloseRequest,
  ReadResult,
  ReadAllResult,
} from '@/types/counter';
import apiClient from './apiClient';

/**
 * Fetches the latest total counter for a printer
 * 
 * @param printerId - ID of the printer
 * @returns Promise resolving to TotalCounter
 * @throws Error if request fails
 */
export async function fetchLatestCounter(printerId: number): Promise<TotalCounter> {
  try {
    const response = await apiClient.get(`/api/counters/printer/${printerId}`);
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch counter';
    throw new Error(errorMessage);
  }
}

/**
 * Fetches counter history with optional date filters
 * 
 * @param printerId - ID of the printer
 * @param options - Optional filters (startDate, endDate, limit)
 * @returns Promise resolving to array of TotalCounter
 * @throws Error if request fails
 */
export async function fetchCounterHistory(
  printerId: number,
  options?: {
    startDate?: string;
    endDate?: string;
    limit?: number;
  }
): Promise<TotalCounter[]> {
  try {
    const params: any = {};
    if (options?.startDate) params.start_date = options.startDate;
    if (options?.endDate) params.end_date = options.endDate;
    if (options?.limit) params.limit = options.limit;
    
    const response = await apiClient.get(`/api/counters/printer/${printerId}/history`, { params });
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch history';
    throw new Error(errorMessage);
  }
}

/**
 * Fetches user counters for a printer
 * 
 * @param printerId - ID of the printer
 * @returns Promise resolving to array of UserCounter
 * @throws Error if request fails
 */
export async function fetchUserCounters(printerId: number): Promise<UserCounter[]> {
  try {
    const response = await apiClient.get(`/api/counters/users/${printerId}`);
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch user counters';
    throw new Error(errorMessage);
  }
}

/**
 * Fetches user counter history with optional filters
 * 
 * @param printerId - ID of the printer
 * @param options - Optional filters (codigoUsuario, startDate, endDate, limit)
 * @returns Promise resolving to array of UserCounter
 * @throws Error if request fails
 */
export async function fetchUserCounterHistory(
  printerId: number,
  options?: {
    codigoUsuario?: string;
    startDate?: string;
    endDate?: string;
    limit?: number;
  }
): Promise<UserCounter[]> {
  try {
    const params: any = {};
    if (options?.codigoUsuario) params.codigo_usuario = options.codigoUsuario;
    if (options?.startDate) params.start_date = options.startDate;
    if (options?.endDate) params.end_date = options.endDate;
    if (options?.limit) params.limit = options.limit;
    
    const response = await apiClient.get(`/api/counters/users/${printerId}/history`, { params });
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch user history';
    throw new Error(errorMessage);
  }
}

/**
 * Triggers manual counter reading for a printer
 * 
 * @param printerId - ID of the printer
 * @returns Promise resolving to ReadResult
 * @throws Error if request fails
 */
export async function triggerManualRead(printerId: number): Promise<ReadResult> {
  try {
    const response = await apiClient.post(`/api/counters/read/${printerId}`);
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to read counters';
    throw new Error(errorMessage);
  }
}

/**
 * Triggers counter reading for all printers
 * 
 * @returns Promise resolving to ReadAllResult
 * @throws Error if request fails
 */
export async function triggerReadAll(): Promise<ReadAllResult> {
  try {
    const response = await apiClient.post('/api/counters/read-all');
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to read all counters';
    throw new Error(errorMessage);
  }
}

/**
 * Performs a monthly close
 * 
 * @param data - Monthly close request data
 * @returns Promise resolving to MonthlyClose
 * @throws Error if request fails
 */
export async function performMonthlyClose(data: MonthlyCloseRequest): Promise<MonthlyClose> {
  try {
    const response = await apiClient.post('/api/counters/close-month', data);
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to perform monthly close';
    throw new Error(errorMessage);
  }
}

/**
 * Fetches monthly closes with optional year filter
 * 
 * @param printerId - ID of the printer
 * @param year - Optional year filter
 * @returns Promise resolving to array of MonthlyClose
 * @throws Error if request fails
 */
export async function fetchMonthlyCloses(
  printerId: number,
  year?: number
): Promise<MonthlyClose[]> {
  try {
    const params = year ? { year } : {};
    const response = await apiClient.get(`/api/counters/monthly/${printerId}`, { params });
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch monthly closes';
    throw new Error(errorMessage);
  }
}

/**
 * Fetches a specific monthly close
 * 
 * @param printerId - ID of the printer
 * @param year - Year of the close
 * @param month - Month of the close (1-12)
 * @returns Promise resolving to MonthlyClose
 * @throws Error if request fails
 */
export async function fetchMonthlyClose(
  printerId: number,
  year: number,
  month: number
): Promise<MonthlyClose> {
  try {
    const response = await apiClient.get(`/api/counters/monthly/${printerId}/${year}/${month}`);
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch monthly close';
    throw new Error(errorMessage);
  }
}
