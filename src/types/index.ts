interface PrinterDevice {
  id: string;
  hostname: string;
  ip_address: string;
  status: 'online' | 'offline';
  location?: string;
  toner_levels: { cyan: number; magenta: number; yellow: number; black: number };
  capabilities: { color: boolean; scanner: boolean };
}

export type { PrinterDevice };