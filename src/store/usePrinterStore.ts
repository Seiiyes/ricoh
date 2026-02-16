import { create } from 'zustand';
import type { PrinterDevice } from '@/types';

interface Log {
  id: string;
  timestamp: string;
  message: string;
  type: 'info' | 'error' | 'success';
}

interface PrinterStore {
  selectedPrinters: string[];
  logs: Log[];
  printers: PrinterDevice[];
  isLoading: boolean;
  togglePrinter: (id: string) => void;
  addLog: (message: string, type?: Log['type']) => void;
  clearSelection: () => void;
  setPrinters: (printers: PrinterDevice[]) => void;
  clearPrinters: () => void;
  setLoading: (loading: boolean) => void;
}

export const usePrinterStore = create<PrinterStore>((set) => ({
  selectedPrinters: [],
  logs: [],
  printers: [],
  isLoading: false,
  togglePrinter: (id) => set((state) => ({
    selectedPrinters: state.selectedPrinters.includes(id)
      ? state.selectedPrinters.filter(pId => pId !== id)
      : [...state.selectedPrinters, id]
  })),
  addLog: (message, type = 'info') => set((state) => ({
    logs: [...state.logs, {
      id: Math.random().toString(36),
      timestamp: new Date().toLocaleTimeString(),
      message,
      type
    }].slice(-50)  // Keep last 50, oldest first
  })),
  clearSelection: () => set({ selectedPrinters: [] }),
  setPrinters: (printers) => set({ printers }),
  clearPrinters: () => set({ printers: [] }),
  setLoading: (loading) => set({ isLoading: loading }),
}));