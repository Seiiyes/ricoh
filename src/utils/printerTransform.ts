import type { PrinterDevice } from '@/types';

interface TonerLevels {
  c: number;
  m: number;
  y: number;
  k: number;
}

interface PrinterCardProps {
  id: string;
  name: string;
  ip: string;
  status: 'online' | 'offline';
  location?: string;
  toner: TonerLevels;
}

/**
 * Transforms a PrinterDevice object to PrinterCardProps format
 * Maps backend data structure to component props structure
 * Provides defaults for missing fields to handle incomplete API responses
 * 
 * @param device - The printer device from the backend/store
 * @returns PrinterCardProps formatted for the PrinterCard component
 */
export function printerDeviceToCardProps(device: Partial<PrinterDevice> & Pick<PrinterDevice, 'id' | 'hostname' | 'ip_address'>): PrinterCardProps {
  return {
    id: device.id,
    name: device.hostname,
    ip: device.ip_address,
    status: device.status ?? 'offline',
    location: device.location,
    toner: {
      c: device.toner_levels?.cyan ?? 0,
      m: device.toner_levels?.magenta ?? 0,
      y: device.toner_levels?.yellow ?? 0,
      k: device.toner_levels?.black ?? 0,
    },
  };
}
