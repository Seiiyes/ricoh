import type { PrinterCapabilities } from './printer';

interface PrinterDevice {
  id: string;
  hostname: string;
  ip_address: string;
  status: 'online' | 'offline';
  location?: string;
  empresa?: string;
  serial_number?: string;
  toner_levels: { cyan: number; magenta: number; yellow: number; black: number };
  capabilities?: PrinterCapabilities;
  has_color?: boolean;
  has_scanner?: boolean;
}

export type { PrinterDevice };