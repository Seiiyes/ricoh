/**
 * Discovery Service
 * Servicio para operaciones de descubrimiento de impresoras
 */
import apiClient from './apiClient';

export interface CheckPrinterRequest {
  ip: string;
}

export interface CheckPrinterResponse {
  success: boolean;
  printer?: {
    ip: string;
    hostname: string;
    model: string;
    serial_number: string;
    has_color: boolean;
    has_scanner: boolean;
    has_fax: boolean;
  };
  message?: string;
}

export const discoveryService = {
  /**
   * Verificar una impresora por IP
   */
  checkPrinter: async (ip: string): Promise<CheckPrinterResponse> => {
    const response = await apiClient.post<CheckPrinterResponse>('/discovery/check-printer', { ip });
    return response.data;
  },

  /**
   * Sincronizar usuarios desde impresoras
   */
  syncUsersFromPrinters: async (userCode?: string): Promise<{ 
    success: boolean; 
    message: string;
    users?: any[];
    printers_scanned?: any[];
    total_usuarios_unicos?: number;
    usuarios_en_db?: number;
    usuarios_solo_impresoras?: number;
    search_mode?: string;
    user_code_searched?: string;
  }> => {
    const params = userCode ? { user_code: userCode } : {};
    const response = await apiClient.post('/discovery/sync-users-from-printers', null, { params });
    return response.data;
  },

  /**
   * Obtener detalles de usuario de impresora (lazy load)
   */
  getUserDetails: async (printerId: number, userId: number) => {
    const response = await apiClient.get(`/discovery/user-details`, {
      params: { printer_id: printerId, user_id: userId }
    });
    return response.data;
  }
};

export default discoveryService;
