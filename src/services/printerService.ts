import type { PrinterDevice } from '@/types';
import apiClient from './apiClient';

/**
 * Printer Service
 * 
 * This module provides functions for interacting with the backend API.
 * Uses apiClient for authenticated requests.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ============================================================================
// Discovery API
// ============================================================================

/**
 * Scans network for Ricoh printers
 * 
 * @param ipRange - IP range in CIDR notation (e.g., "192.168.1.0/24")
 * @returns Promise resolving to an array of discovered devices
 */
export async function scanPrinters(ipRange: string = '192.168.1.0/24'): Promise<any[]> {
  try {
    const response = await apiClient.post('/discovery/scan', { ip_range: ipRange });
    return response.data.devices;
  } catch (error) {
    console.error('Failed to scan printers:', error);
    throw error;
  }
}

/**
 * Registers discovered printers to the database
 * 
 * @param devices - Array of discovered devices to register
 */
export async function registerDiscoveredPrinters(devices: any[]): Promise<void> {
  try {
    await apiClient.post('/discovery/register-discovered', devices);
  } catch (error) {
    console.error('Failed to register discovered printers:', error);
    throw error;
  }
}

// ============================================================================
// Printer Management API
// ============================================================================

/**
 * Fetches all registered printers from the database
 * 
 * @returns Promise resolving to an array of PrinterDevice objects
 */
export async function fetchPrinters(): Promise<PrinterDevice[]> {
  try {
    const response = await apiClient.get('/printers/');
    // Backend retorna PrinterListResponse con estructura { items: [...], total, page, ... }
    const printers = response.data.items || response.data;
    
    // Transform backend response to frontend format
    return printers.map((printer: any) => ({
      id: printer.id.toString(),
      hostname: printer.hostname,
      ip_address: printer.ip_address,
      status: printer.status,
      location: printer.location,
      empresa: printer.empresa,
      serial_number: printer.serial_number,
      toner_levels: {
        cyan: printer.toner_cyan,
        magenta: printer.toner_magenta,
        yellow: printer.toner_yellow,
        black: printer.toner_black,
      },
      has_color: printer.has_color,
      has_scanner: printer.has_scanner,
      capabilities: printer.capabilities, // Full capabilities from backend
    }));
  } catch (error) {
    console.error('Failed to fetch printers:', error);
    return [];
  }
}

/**
 * Creates a new printer manually
 * 
 * @param printer - Printer data to create
 */
export async function createPrinter(printer: any): Promise<any> {
  try {
    const response = await apiClient.post('/printers/', printer);
    return response.data;
  } catch (error) {
    console.error('Failed to create printer:', error);
    throw error;
  }
}

/**
 * Updates an existing printer
 * 
 * @param printerId - ID of the printer to update
 * @param updates - Fields to update
 */
export async function updatePrinter(printerId: number, updates: any): Promise<any> {
  try {
    const response = await apiClient.put(`/printers/${printerId}`, updates);
    return response.data;
  } catch (error) {
    console.error('Failed to update printer:', error);
    throw error;
  }
}

/**
 * Removes a printer from the database
 * 
 * @param printerId - ID of the printer to remove
 */
export async function removePrinter(printerId: number): Promise<void> {
  try {
    await apiClient.delete(`/printers/${printerId}`);
  } catch (error) {
    console.error('Failed to remove printer:', error);
    throw error;
  }
}

/**
 * Refresh printer information via SNMP
 * 
 * @param printerId - ID of the printer to refresh
 */
export async function refreshPrinterSNMP(printerId: number): Promise<any> {
  try {
    const response = await apiClient.post(`/discovery/refresh-snmp/${printerId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to refresh printer SNMP:', error);
    throw error;
  }
}

// ============================================================================
// User Management API
// ============================================================================

/**
 * Creates a new user
 * 
 * @param user - User data to create
 */
export async function createUser(user: {
  name: string;
  codigo_de_usuario: string;
  empresa?: string;
  centro_costos?: string;
  network_credentials?: {
    username: string;
    password?: string;
  };
  smb_config?: {
    server: string;
    port: number;
    path: string;
  };
  available_functions?: {
    copier?: boolean;
    copier_color?: boolean;
    printer?: boolean;
    printer_color?: boolean;
    document_server?: boolean;
    fax?: boolean;
    scanner?: boolean;
    browser?: boolean;
  };
}): Promise<any> {
  try {
    console.log('📤 Sending user creation request:', user);
    const response = await apiClient.post('/users/', user);
    console.log('✅ User created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to create user:', error);
    throw error;
  }
}

/**
 * Fetches all users
 */
export async function fetchUsers(): Promise<any[]> {
  try {
    const response = await apiClient.get('/users/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch users:', error);
    return [];
  }
}

// ============================================================================
// Provisioning API
// ============================================================================

/**
 * Provisions a user to multiple printers
 * 
 * @param userId - User ID to provision
 * @param printerIds - Array of printer IDs
 */
export async function provisionUser(userId: number, printerIds: number[]): Promise<any> {
  try {
    const response = await apiClient.post('/provisioning/provision', {
      user_id: userId,
      printer_ids: printerIds,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to provision user:', error);
    throw error;
  }
}

/**
 * Gets provisioning status for a user
 * 
 * @param userId - User ID
 */
export async function getUserProvisioningStatus(userId: number): Promise<any> {
  try {
    const response = await apiClient.get(`/provisioning/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get provisioning status:', error);
    throw error;
  }
}

// ============================================================================
// WebSocket Connection
// ============================================================================

/**
 * Connects to WebSocket for real-time log updates
 * 
 * @param onMessage - Callback for received messages
 * @returns WebSocket instance
 */
export function connectWebSocket(onMessage: (event: any) => void): WebSocket {
  const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/logs';
  const ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
}
