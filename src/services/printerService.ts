import type { PrinterDevice } from '@/types';

/**
 * Printer Service
 * 
 * This module provides functions for interacting with the backend API.
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
    const response = await fetch(`${API_BASE_URL}/discovery/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ip_range: ipRange }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Scan failed');
    }
    
    const data = await response.json();
    return data.devices;
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
    const response = await fetch(`${API_BASE_URL}/discovery/register-discovered`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(devices),
    });
    
    if (!response.ok) {
      throw new Error('Failed to register printers');
    }
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
    const response = await fetch(`${API_BASE_URL}/printers/`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch printers: ${response.statusText}`);
    }
    
    const printers = await response.json();
    
    // Transform backend response to frontend format
    return printers.map((printer: any) => ({
      id: printer.id.toString(),
      hostname: printer.hostname,
      ip_address: printer.ip_address,
      status: printer.status,
      location: printer.location,
      toner_levels: {
        cyan: printer.toner_cyan,
        magenta: printer.toner_magenta,
        yellow: printer.toner_yellow,
        black: printer.toner_black,
      },
      capabilities: {
        color: printer.has_color,
        scanner: printer.has_scanner,
      },
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
    const response = await fetch(`${API_BASE_URL}/printers/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(printer),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create printer');
    }
    
    return await response.json();
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
    const response = await fetch(`${API_BASE_URL}/printers/${printerId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update printer');
    }
    
    return await response.json();
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
    const response = await fetch(`${API_BASE_URL}/printers/${printerId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to remove printer: ${response.statusText}`);
    }
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
    const response = await fetch(`${API_BASE_URL}/discovery/refresh-snmp/${printerId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to refresh printer data');
    }
    
    return await response.json();
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
  pin: string;
  smb_path?: string;
  email?: string;
  department?: string;
}): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(user),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create user');
    }
    
    return await response.json();
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
    const response = await fetch(`${API_BASE_URL}/users/`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }
    
    return await response.json();
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
    const response = await fetch(`${API_BASE_URL}/provisioning/provision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        printer_ids: printerIds,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Provisioning failed');
    }
    
    return await response.json();
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
    const response = await fetch(`${API_BASE_URL}/provisioning/user/${userId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get provisioning status');
    }
    
    return await response.json();
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
