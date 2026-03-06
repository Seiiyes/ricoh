/**
 * Counter Service
 * 
 * Service layer for counter API integration.
 * Encapsulates all HTTP calls to the backend counter endpoints.
 */

import type {
  TotalCounter,
  UserCounter,
  MonthlyClose,
  MonthlyCloseRequest,
  ReadResult,
  ReadAllResult,
} from '@/types/counter';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Fetches the latest total counter for a printer
 * 
 * @param printerId - ID of the printer
 * @returns Promise resolving to TotalCounter
 * @throws Error if request fails
 */
export async function fetchLatestCounter(printerId: number): Promise<TotalCounter> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/counters/printer/${printerId}`);
    
    if (!response.ok) {
      let errorMessage = `Failed to fetch counter: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error fetching counter');
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
    const params = new URLSearchParams();
    if (options?.startDate) params.append('start_date', options.startDate);
    if (options?.endDate) params.append('end_date', options.endDate);
    if (options?.limit) params.append('limit', options.limit.toString());
    
    const url = `${API_BASE_URL}/api/counters/printer/${printerId}/history${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      let errorMessage = `Failed to fetch history: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error fetching history');
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
    const response = await fetch(`${API_BASE_URL}/api/counters/users/${printerId}`);
    
    if (!response.ok) {
      let errorMessage = `Failed to fetch user counters: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error fetching user counters');
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
    const params = new URLSearchParams();
    if (options?.codigoUsuario) params.append('codigo_usuario', options.codigoUsuario);
    if (options?.startDate) params.append('start_date', options.startDate);
    if (options?.endDate) params.append('end_date', options.endDate);
    if (options?.limit) params.append('limit', options.limit.toString());
    
    const url = `${API_BASE_URL}/api/counters/users/${printerId}/history${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      let errorMessage = `Failed to fetch user history: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error fetching user history');
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
    const response = await fetch(`${API_BASE_URL}/api/counters/read/${printerId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      let errorMessage = `Failed to read counters: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error reading counters');
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
    const response = await fetch(`${API_BASE_URL}/api/counters/read-all`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      let errorMessage = `Failed to read all counters: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error reading all counters');
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
    const response = await fetch(`${API_BASE_URL}/api/counters/close-month`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      let errorMessage = 'Failed to perform monthly close';
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error performing monthly close');
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
    const url = year
      ? `${API_BASE_URL}/api/counters/monthly/${printerId}?year=${year}`
      : `${API_BASE_URL}/api/counters/monthly/${printerId}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      let errorMessage = `Failed to fetch monthly closes: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error fetching monthly closes');
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
    const response = await fetch(
      `${API_BASE_URL}/api/counters/monthly/${printerId}/${year}/${month}`
    );
    
    if (!response.ok) {
      let errorMessage = `Failed to fetch monthly close: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch {
        // Ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error fetching monthly close');
  }
}
