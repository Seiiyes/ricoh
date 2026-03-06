# Design Document: Frontend Contadores

## Overview

### Critical Design Updates

**IMPORTANT CHANGES FROM INITIAL DESIGN:**

1. **Daily Close (Not Monthly)**: The system implements DAILY close functionality with specific date selection, not monthly closes
   - Users select a specific date (e.g., March 2, 2026)
   - System compares with same day of previous month (e.g., February 2, 2026)
   - Differences calculated between these two specific dates

2. **Backend API Extension Required**: New endpoints needed for daily closes
   - POST /api/counters/close-day
   - GET /api/counters/closes/daily
   - GET /api/counters/closes/daily/{id}
   - See "Backend API Extension for Daily Closes" section for details

3. **User Counter Table Visibility**: UserCounterTable is visible in Printer Detail View
   - Fetches from existing endpoint: /api/counters/users/{printer_id}
   - Shows cumulative totals per user (not differences)

### Purpose

This design document specifies the frontend implementation for the counter management module (Contadores) of the Ricoh Equipment Manager system. The module provides a comprehensive interface for viewing, querying, and managing printer counters through a modern React-based web application.

### Scope

The frontend counter module includes:
- Dashboard view with counter summary for all printers
- Detailed printer counter view with breakdown by function
- Historical counter visualization with charts
- User counter tables with sorting and filtering (visible in Printer Detail View)
- Daily close operations with specific date selection and comparison
- Export functionality (Excel/PDF)
- Real-time counter reading triggers
- Comprehensive error handling and loading states

### Technology Stack

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom theme
- **Icons**: Lucide React
- **State Management**: Zustand (optional, for complex state)
- **Charts**: Recharts (lazy-loaded)
- **Export**: xlsx (Excel), jspdf (PDF)
- **HTTP Client**: Fetch API

### Design Principles

1. **Consistency**: Follow existing project patterns for navigation, styling, and component structure
2. **Performance**: Lazy-load heavy dependencies, implement pagination, optimize re-renders
3. **Accessibility**: ARIA labels, keyboard navigation, screen reader support
4. **Responsiveness**: Support desktop (1024px+) and tablet (768px+) viewports
5. **User Feedback**: Clear loading states, error messages, and success confirmations


## Architecture

### High-Level Architecture

The counter module follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  (React Components: Views, Tables, Charts, Modals)          │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  (counterService.ts, exportService.ts)                      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    State Management                          │
│  (Zustand Store - optional, for caching)                    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│  (9 existing + 3 new endpoints for daily closes)            │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
App.tsx
└── Navigation Menu
    └── Contadores Module
        ├── DashboardView (default)
        │   ├── PrinterCounterCard (multiple)
        │   │   ├── CounterSummary
        │   │   └── LastReadingInfo
        │   └── ReadAllButton
        │
        ├── PrinterDetailView
        │   ├── PrinterIdentification
        │   ├── CounterBreakdown
        │   │   ├── CopierCounters
        │   │   ├── PrinterCounters
        │   │   ├── ScannerCounters
        │   │   └── FaxCounters
        │   ├── ManualReadButton
        │   ├── HistoryChart
        │   │   ├── DateRangeFilter
        │   │   └── LineChart (recharts)
        │   └── UserCounterTable (fetches from /api/counters/users/{printer_id})
        │       ├── TableHeader (sortable)
        │       ├── TableBody
        │       ├── SearchFilter
        │       └── Pagination
        │
        └── DailyCloseView
            ├── CloseForm
            │   ├── PrinterSelect
            │   ├── DatePicker (specific date selection)
            │   └── NotesInput
            ├── CloseHistoryTable
            │   ├── DateRangeFilter
            │   ├── TableBody
            │   └── ExportButton (per row)
            └── SuccessMessage

Shared Components:
├── LoadingIndicator
├── ErrorHandler
└── RefreshButton
```

### Navigation Flow

The module uses state-based navigation matching the existing pattern:

```typescript
type CounterView = 'dashboard' | 'printer-detail' | 'daily-close';

interface CounterState {
  vistaActual: CounterView;
  selectedPrinterId?: number;
}
```

Navigation transitions:
- Dashboard → Printer Detail (click printer card)
- Printer Detail → Dashboard (back button)
- Dashboard → Daily Close (menu item)
- Daily Close → Dashboard (back button)


## Components and Interfaces

### Service Layer

#### counterService.ts

Encapsulates all API calls to the backend counter endpoints. Follows the pattern established in `printerService.ts`.

```typescript
// src/services/counterService.ts

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Fetches the latest total counter for a printer
 */
export async function fetchLatestCounter(printerId: number): Promise<TotalCounter> {
  const response = await fetch(`${API_BASE_URL}/api/counters/printer/${printerId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch counter: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Fetches counter history with optional date filters
 */
export async function fetchCounterHistory(
  printerId: number,
  options?: {
    startDate?: string;
    endDate?: string;
    limit?: number;
  }
): Promise<TotalCounter[]> {
  const params = new URLSearchParams();
  if (options?.startDate) params.append('start_date', options.startDate);
  if (options?.endDate) params.append('end_date', options.endDate);
  if (options?.limit) params.append('limit', options.limit.toString());
  
  const url = `${API_BASE_URL}/api/counters/printer/${printerId}/history?${params}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Fetches user counters for a printer
 */
export async function fetchUserCounters(printerId: number): Promise<UserCounter[]> {
  const response = await fetch(`${API_BASE_URL}/api/counters/users/${printerId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user counters: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Triggers manual counter reading for a printer
 */
export async function triggerManualRead(printerId: number): Promise<ReadResult> {
  const response = await fetch(`${API_BASE_URL}/api/counters/read/${printerId}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to read counters: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Triggers counter reading for all printers
 */
export async function triggerReadAll(): Promise<ReadAllResult> {
  const response = await fetch(`${API_BASE_URL}/api/counters/read-all`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to read all counters: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Performs a daily close for a specific date
 */
export async function performDailyClose(data: DailyCloseRequest): Promise<DailyClose> {
  const response = await fetch(`${API_BASE_URL}/api/counters/close-day`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to perform daily close');
  }
  return await response.json();
}

/**
 * Fetches daily closes with optional date range filter
 */
export async function fetchDailyCloses(
  printerId: number,
  options?: {
    startDate?: string;
    endDate?: string;
  }
): Promise<DailyClose[]> {
  const params = new URLSearchParams();
  if (options?.startDate) params.append('start_date', options.startDate);
  if (options?.endDate) params.append('end_date', options.endDate);
  
  const url = `${API_BASE_URL}/api/counters/closes/daily?printer_id=${printerId}&${params}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch daily closes: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Fetches a specific daily close
 */
export async function fetchDailyClose(closeId: number): Promise<DailyClose> {
  const response = await fetch(
    `${API_BASE_URL}/api/counters/closes/daily/${closeId}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch daily close: ${response.statusText}`);
  }
  return await response.json();
}
```

#### exportService.ts

Handles export functionality for Excel and PDF reports.

```typescript
// src/services/exportService.ts

import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

/**
 * Exports counter data to Excel
 */
export function exportToExcel(
  printerName: string,
  totalCounter: TotalCounter,
  userCounters: UserCounter[]
): void {
  const workbook = XLSX.utils.book_new();
  
  // Sheet 1: Total Counters
  const totalData = [
    ['Campo', 'Valor'],
    ['Total', totalCounter.total],
    ['Copiadora B/N', totalCounter.copiadora_bn],
    ['Copiadora Color', totalCounter.copiadora_color],
    ['Impresora B/N', totalCounter.impresora_bn],
    ['Impresora Color', totalCounter.impresora_color],
    ['Escáner B/N', totalCounter.envio_escaner_bn],
    ['Escáner Color', totalCounter.envio_escaner_color],
    ['Fax B/N', totalCounter.fax_bn],
    ['Fecha Lectura', new Date(totalCounter.fecha_lectura).toLocaleString()],
  ];
  const totalSheet = XLSX.utils.aoa_to_sheet(totalData);
  XLSX.utils.book_append_sheet(workbook, totalSheet, 'Contadores Totales');
  
  // Sheet 2: User Counters
  const userData = [
    ['Código', 'Nombre', 'Total', 'B/N', 'Color', 'Copiadora', 'Impresora', 'Escáner', 'Fax'],
    ...userCounters.map(u => [
      u.codigo_usuario,
      u.nombre_usuario,
      u.total_paginas,
      u.total_bn,
      u.total_color,
      u.copiadora_bn,
      u.impresora_bn,
      u.escaner_bn,
      u.fax_bn,
    ]),
  ];
  const userSheet = XLSX.utils.aoa_to_sheet(userData);
  XLSX.utils.book_append_sheet(workbook, userSheet, 'Contadores por Usuario');
  
  // Generate filename and download
  const date = new Date().toISOString().split('T')[0];
  const filename = `counters_${printerName}_${date}.xlsx`;
  XLSX.writeFile(workbook, filename);
}

/**
 * Exports daily close to PDF
 */
export function exportDailyCloseToPDF(
  printerName: string,
  close: DailyClose
): void {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(18);
  doc.text('Cierre Diario de Contadores', 14, 20);
  
  // Printer info
  doc.setFontSize(12);
  doc.text(`Impresora: ${printerName}`, 14, 35);
  doc.text(`Fecha de Cierre: ${new Date(close.close_date).toLocaleDateString()}`, 14, 42);
  doc.text(`Fecha de Comparación: ${new Date(close.comparison_date).toLocaleDateString()}`, 14, 49);
  doc.text(`Cerrado por: ${close.cerrado_por || 'N/A'}`, 14, 56);
  doc.text(`Fecha: ${new Date(close.fecha_cierre).toLocaleString()}`, 14, 63);
  
  // Counter table
  const tableData = [
    ['Función', 'Total', 'Diferencia'],
    ['Total Páginas', close.total_paginas.toString(), close.diferencia_total.toString()],
    ['Copiadora', close.total_copiadora.toString(), close.diferencia_copiadora.toString()],
    ['Impresora', close.total_impresora.toString(), close.diferencia_impresora.toString()],
    ['Escáner', close.total_escaner.toString(), close.diferencia_escaner.toString()],
    ['Fax', close.total_fax.toString(), close.diferencia_fax.toString()],
  ];
  
  doc.autoTable({
    startY: 72,
    head: [tableData[0]],
    body: tableData.slice(1),
  });
  
  // Notes
  if (close.notas) {
    const finalY = (doc as any).lastAutoTable.finalY || 72;
    doc.text('Notas:', 14, finalY + 10);
    doc.setFontSize(10);
    doc.text(close.notas, 14, finalY + 17);
  }
  
  // Generate filename and download
  const dateStr = new Date(close.close_date).toISOString().split('T')[0];
  const filename = `close_${printerName}_${dateStr}.pdf`;
  doc.save(filename);
}
```


### View Components

#### DashboardView.tsx

Main dashboard displaying counter summary for all printers.

```typescript
// src/components/contadores/DashboardView.tsx

interface DashboardViewProps {
  onNavigateToPrinter: (printerId: number) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onNavigateToPrinter }) => {
  const [printers, setPrinters] = useState<PrinterDevice[]>([]);
  const [counters, setCounters] = useState<Map<number, TotalCounter>>(new Map());
  const [loading, setLoading] = useState(true);
  const [readingAll, setReadingAll] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load printers and their latest counters
  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 60000); // Refresh every 60s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const printerList = await fetchPrinters();
      setPrinters(printerList);
      
      // Fetch latest counter for each printer
      const counterMap = new Map<number, TotalCounter>();
      await Promise.all(
        printerList.map(async (printer) => {
          try {
            const counter = await fetchLatestCounter(Number(printer.id));
            counterMap.set(Number(printer.id), counter);
          } catch (err) {
            console.error(`Failed to fetch counter for printer ${printer.id}:`, err);
          }
        })
      );
      setCounters(counterMap);
    } catch (err) {
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleReadAll = async () => {
    try {
      setReadingAll(true);
      const result = await triggerReadAll();
      alert(`✅ Lectura completada\nExitosas: ${result.successful}\nFallidas: ${result.failed}`);
      await loadDashboardData(); // Refresh data
    } catch (err) {
      setError('Failed to read all printers');
    } finally {
      setReadingAll(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      {/* Header */}
      <div className="bg-white border-b shadow-sm px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-industrial-gray uppercase tracking-tight">
            Dashboard de Contadores
          </h1>
          <button
            onClick={handleReadAll}
            disabled={readingAll}
            className="flex items-center gap-2 bg-ricoh-red text-white px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide hover:bg-red-700 transition-colors disabled:opacity-50"
          >
            {readingAll ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Leyendo...
              </>
            ) : (
              <>
                <RefreshCw size={14} />
                Leer Todas
              </>
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {loading ? (
          <LoadingIndicator message="Cargando contadores..." />
        ) : error ? (
          <ErrorHandler message={error} onDismiss={() => setError(null)} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {printers.map((printer) => (
              <PrinterCounterCard
                key={printer.id}
                printer={printer}
                counter={counters.get(Number(printer.id))}
                onClick={() => onNavigateToPrinter(Number(printer.id))}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
```

#### PrinterDetailView.tsx

Detailed view of a single printer's counters with history and user breakdown.

**IMPORTANT**: This view includes the UserCounterTable component which fetches and displays user counter data from `/api/counters/users/{printer_id}`.

```typescript
// src/components/contadores/PrinterDetailView.tsx

interface PrinterDetailViewProps {
  printerId: number;
  onNavigateBack: () => void;
}

export const PrinterDetailView: React.FC<PrinterDetailViewProps> = ({
  printerId,
  onNavigateBack,
}) => {
  const [printer, setPrinter] = useState<PrinterDevice | null>(null);
  const [counter, setCounter] = useState<TotalCounter | null>(null);
  const [history, setHistory] = useState<TotalCounter[]>([]);
  const [userCounters, setUserCounters] = useState<UserCounter[]>([]);
  const [loading, setLoading] = useState(true);
  const [reading, setReading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPrinterData();
    const interval = setInterval(loadPrinterData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [printerId]);

  const loadPrinterData = async () => {
    try {
      setLoading(true);
      const [printerList, latestCounter, counterHistory, users] = await Promise.all([
        fetchPrinters(),
        fetchLatestCounter(printerId),
        fetchCounterHistory(printerId, { limit: 100 }),
        fetchUserCounters(printerId), // Fetches from /api/counters/users/{printer_id}
      ]);
      
      const printerData = printerList.find(p => Number(p.id) === printerId);
      setPrinter(printerData || null);
      setCounter(latestCounter);
      setHistory(counterHistory);
      setUserCounters(users);
    } catch (err) {
      setError('Failed to load printer data');
    } finally {
      setLoading(false);
    }
  };

  const handleManualRead = async () => {
    try {
      setReading(true);
      await triggerManualRead(printerId);
      await loadPrinterData(); // Refresh data
      alert('✅ Lectura completada exitosamente');
    } catch (err) {
      setError('Failed to read counters');
    } finally {
      setReading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      {/* Header */}
      <div className="bg-white border-b shadow-sm px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onNavigateBack}
              className="text-slate-600 hover:text-slate-900"
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="text-xl font-bold text-industrial-gray uppercase tracking-tight">
              {printer?.hostname || 'Cargando...'}
            </h1>
          </div>
          <button
            onClick={handleManualRead}
            disabled={reading}
            className="flex items-center gap-2 bg-ricoh-red text-white px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide hover:bg-red-700 transition-colors disabled:opacity-50"
          >
            {reading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Leyendo...
              </>
            ) : (
              <>
                <RefreshCw size={14} />
                Lectura Manual
              </>
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 space-y-6">
        {loading ? (
          <LoadingIndicator message="Cargando datos de la impresora..." />
        ) : error ? (
          <ErrorHandler message={error} onDismiss={() => setError(null)} />
        ) : (
          <>
            {/* Printer Identification */}
            <PrinterIdentification printer={printer!} counter={counter!} />
            
            {/* Counter Breakdown */}
            <CounterBreakdown counter={counter!} />
            
            {/* History Chart */}
            <HistoryChart printerId={printerId} history={history} />
            
            {/* User Counter Table - VISIBLE HERE */}
            <UserCounterTable userCounters={userCounters} />
          </>
        )}
      </div>
    </div>
  );
};
```

#### DailyCloseView.tsx

View for performing and viewing daily closes.

```typescript
// src/components/contadores/DailyCloseView.tsx

export const DailyCloseView: React.FC = () => {
  const [printers, setPrinters] = useState<PrinterDevice[]>([]);
  const [selectedPrinterId, setSelectedPrinterId] = useState<number | null>(null);
  const [closeDate, setCloseDate] = useState(new Date().toISOString().split('T')[0]);
  const [closedBy, setClosedBy] = useState('');
  const [notes, setNotes] = useState('');
  const [closes, setCloses] = useState<DailyClose[]>([]);
  const [dateRangeStart, setDateRangeStart] = useState<string | undefined>(undefined);
  const [dateRangeEnd, setDateRangeEnd] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPrinters();
  }, []);

  useEffect(() => {
    if (selectedPrinterId) {
      loadCloses();
    }
  }, [selectedPrinterId, dateRangeStart, dateRangeEnd]);

  const loadPrinters = async () => {
    const printerList = await fetchPrinters();
    setPrinters(printerList);
  };

  const loadCloses = async () => {
    if (!selectedPrinterId) return;
    try {
      const closeList = await fetchDailyCloses(selectedPrinterId, {
        startDate: dateRangeStart,
        endDate: dateRangeEnd,
      });
      setCloses(closeList);
    } catch (err) {
      console.error('Failed to load closes:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!selectedPrinterId) {
      setError('Seleccione una impresora');
      return;
    }
    
    const selectedDate = new Date(closeDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (selectedDate > today) {
      setError('La fecha no puede ser mayor a la fecha actual');
      return;
    }

    try {
      setLoading(true);
      const result = await performDailyClose({
        printer_id: selectedPrinterId,
        close_date: closeDate,
        cerrado_por: closedBy || undefined,
        notas: notes || undefined,
      });
      
      const comparisonDate = new Date(result.comparison_date).toLocaleDateString();
      alert(`✅ Cierre realizado exitosamente\nComparado con: ${comparisonDate}\nDiferencia total: ${result.diferencia_total} páginas`);
      
      // Reset form and reload closes
      setNotes('');
      await loadCloses();
    } catch (err: any) {
      if (err.message.includes('already exists')) {
        setError('Ya existe un cierre para esta fecha');
      } else if (err.message.includes('No counters')) {
        setError('No hay contadores disponibles para esta fecha');
      } else {
        setError('Error al realizar el cierre diario');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#F8FAFC]">
      {/* Header */}
      <div className="bg-white border-b shadow-sm px-6 py-4">
        <h1 className="text-xl font-bold text-industrial-gray uppercase tracking-tight">
          Cierres Diarios
        </h1>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Close Form */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-bold text-slate-700 mb-4">Realizar Cierre Diario</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">
                Impresora
              </label>
              <select
                value={selectedPrinterId || ''}
                onChange={(e) => setSelectedPrinterId(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ricoh-red"
                required
              >
                <option value="">Seleccione una impresora</option>
                {printers.map((printer) => (
                  <option key={printer.id} value={printer.id}>
                    {printer.hostname} - {printer.location}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">
                Fecha de Cierre
              </label>
              <input
                type="date"
                value={closeDate}
                onChange={(e) => setCloseDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ricoh-red"
                required
              />
              <p className="text-xs text-slate-500 mt-1">
                Se comparará con el mismo día del mes anterior
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">
                Cerrado por (opcional)
              </label>
              <input
                type="text"
                value={closedBy}
                onChange={(e) => setClosedBy(e.target.value)}
                placeholder="Nombre del responsable"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ricoh-red"
              />
            </div>
            
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-2">
                Notas (opcional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Observaciones adicionales"
                rows={3}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ricoh-red"
              />
            </div>
            
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
                {error}
              </div>
            )}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-industrial-gray text-white px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wide hover:bg-slate-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Procesando...' : 'Realizar Cierre'}
            </button>
          </form>
        </div>

        {/* Close History Table */}
        {selectedPrinterId && (
          <CloseHistoryTable
            closes={closes}
            dateRangeStart={dateRangeStart}
            dateRangeEnd={dateRangeEnd}
            onDateRangeChange={(start, end) => {
              setDateRangeStart(start);
              setDateRangeEnd(end);
            }}
            printerName={printers.find(p => Number(p.id) === selectedPrinterId)?.hostname || ''}
          />
        )}
      </div>
    </div>
  );
};
```


### Shared Components

#### LoadingIndicator.tsx

```typescript
// src/components/contadores/shared/LoadingIndicator.tsx

interface LoadingIndicatorProps {
  message?: string;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ 
  message = 'Cargando...' 
}) => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-slate-400">
      <Loader2 className="animate-spin mb-3" size={48} />
      <p className="text-sm">{message}</p>
    </div>
  );
};
```

#### ErrorHandler.tsx

```typescript
// src/components/contadores/shared/ErrorHandler.tsx

interface ErrorHandlerProps {
  message: string;
  onDismiss: () => void;
  critical?: boolean;
}

export const ErrorHandler: React.FC<ErrorHandlerProps> = ({ 
  message, 
  onDismiss,
  critical = false 
}) => {
  useEffect(() => {
    if (!critical) {
      const timer = setTimeout(onDismiss, 10000);
      return () => clearTimeout(timer);
    }
  }, [critical, onDismiss]);

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
      <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
      <div className="flex-1">
        <h3 className="font-bold text-red-900 text-sm">Error</h3>
        <p className="text-red-700 text-sm mt-1">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="text-xs font-bold uppercase text-red-600 hover:text-red-800"
      >
        Cerrar
      </button>
    </div>
  );
};
```

#### PrinterCounterCard.tsx

```typescript
// src/components/contadores/dashboard/PrinterCounterCard.tsx

interface PrinterCounterCardProps {
  printer: PrinterDevice;
  counter?: TotalCounter;
  onClick: () => void;
}

export const PrinterCounterCard: React.FC<PrinterCounterCardProps> = ({
  printer,
  counter,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-bold text-slate-900">{printer.hostname}</h3>
          <p className="text-xs text-slate-500">{printer.ip_address}</p>
          <p className="text-xs text-slate-500">{printer.location}</p>
        </div>
        <Printer className="text-slate-400" size={20} />
      </div>
      
      {counter ? (
        <div className="space-y-2">
          <div className="flex justify-between items-baseline">
            <span className="text-sm text-slate-600">Total:</span>
            <span className="text-lg font-bold text-slate-900">
              {counter.total.toLocaleString()}
            </span>
          </div>
          <div className="text-xs text-slate-400">
            Última lectura: {new Date(counter.fecha_lectura).toLocaleString()}
          </div>
        </div>
      ) : (
        <div className="text-sm text-slate-400">Sin contadores registrados</div>
      )}
    </div>
  );
};
```

#### HistoryChart.tsx

```typescript
// src/components/contadores/detail/HistoryChart.tsx

import { lazy, Suspense, useState } from 'react';

// Lazy load recharts
const LineChart = lazy(() => import('recharts').then(m => ({ default: m.LineChart })));
const Line = lazy(() => import('recharts').then(m => ({ default: m.Line })));
const XAxis = lazy(() => import('recharts').then(m => ({ default: m.XAxis })));
const YAxis = lazy(() => import('recharts').then(m => ({ default: m.YAxis })));
const CartesianGrid = lazy(() => import('recharts').then(m => ({ default: m.CartesianGrid })));
const Tooltip = lazy(() => import('recharts').then(m => ({ default: m.Tooltip })));
const Legend = lazy(() => import('recharts').then(m => ({ default: m.Legend })));

type DateRange = '7d' | '30d' | '90d' | 'all';

interface HistoryChartProps {
  printerId: number;
  history: TotalCounter[];
}

export const HistoryChart: React.FC<HistoryChartProps> = ({ printerId, history }) => {
  const [dateRange, setDateRange] = useState<DateRange>('30d');
  
  const filterByDateRange = (data: TotalCounter[]): TotalCounter[] => {
    if (dateRange === 'all') return data;
    
    const now = new Date();
    const days = dateRange === '7d' ? 7 : dateRange === '30d' ? 30 : 90;
    const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
    
    return data.filter(item => new Date(item.fecha_lectura) >= cutoff);
  };
  
  const chartData = filterByDateRange(history).map(item => ({
    date: new Date(item.fecha_lectura).toLocaleDateString(),
    total: item.total,
    copiadora: item.copiadora_bn + item.copiadora_color,
    impresora: item.impresora_bn + item.impresora_color,
    escaner: item.envio_escaner_bn + item.envio_escaner_color,
  }));

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-slate-700">Histórico de Contadores</h2>
        
        {/* Date Range Filter */}
        <div className="flex gap-2">
          {(['7d', '30d', '90d', 'all'] as DateRange[]).map(range => (
            <button
              key={range}
              onClick={() => setDateRange(range)}
              className={`px-3 py-1 text-xs font-bold uppercase tracking-wide rounded transition-colors ${
                dateRange === range
                  ? 'bg-industrial-gray text-white'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {range === 'all' ? 'Todo' : range}
            </button>
          ))}
        </div>
      </div>
      
      {chartData.length === 0 ? (
        <div className="text-center text-slate-400 py-8">
          No hay datos disponibles
        </div>
      ) : (
        <Suspense fallback={<LoadingIndicator message="Cargando gráfico..." />}>
          <LineChart width={800} height={300} data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="total" stroke="#E60012" name="Total" />
            <Line type="monotone" dataKey="copiadora" stroke="#3B82F6" name="Copiadora" />
            <Line type="monotone" dataKey="impresora" stroke="#10B981" name="Impresora" />
            <Line type="monotone" dataKey="escaner" stroke="#F59E0B" name="Escáner" />
          </LineChart>
        </Suspense>
      )}
    </div>
  );
};
```

#### UserCounterTable.tsx

```typescript
// src/components/contadores/detail/UserCounterTable.tsx

interface UserCounterTableProps {
  userCounters: UserCounter[];
}

type SortField = 'codigo' | 'nombre' | 'total' | 'bn' | 'color';
type SortDirection = 'asc' | 'desc';

export const UserCounterTable: React.FC<UserCounterTableProps> = ({ userCounters }) => {
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<SortField>('total');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  // Filter
  const filtered = userCounters.filter(user =>
    user.nombre_usuario.toLowerCase().includes(search.toLowerCase()) ||
    user.codigo_usuario.toLowerCase().includes(search.toLowerCase())
  );

  // Sort
  const sorted = [...filtered].sort((a, b) => {
    let aVal: any, bVal: any;
    
    switch (sortField) {
      case 'codigo':
        aVal = a.codigo_usuario;
        bVal = b.codigo_usuario;
        break;
      case 'nombre':
        aVal = a.nombre_usuario;
        bVal = b.nombre_usuario;
        break;
      case 'total':
        aVal = a.total_paginas;
        bVal = b.total_paginas;
        break;
      case 'bn':
        aVal = a.total_bn;
        bVal = b.total_bn;
        break;
      case 'color':
        aVal = a.total_color;
        bVal = b.total_color;
        break;
    }
    
    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  // Paginate
  const totalPages = Math.ceil(sorted.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginated = sorted.slice(startIndex, startIndex + itemsPerPage);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200">
      {/* Header with search */}
      <div className="p-4 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-700">Contadores por Usuario</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Buscar usuario..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-600 cursor-pointer hover:bg-slate-100"
                  onClick={() => handleSort('codigo')}>
                Código {sortField === 'codigo' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-4 py-3 text-left text-xs font-bold uppercase text-slate-600 cursor-pointer hover:bg-slate-100"
                  onClick={() => handleSort('nombre')}>
                Nombre {sortField === 'nombre' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-4 py-3 text-right text-xs font-bold uppercase text-slate-600 cursor-pointer hover:bg-slate-100"
                  onClick={() => handleSort('total')}>
                Total {sortField === 'total' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-4 py-3 text-right text-xs font-bold uppercase text-slate-600 cursor-pointer hover:bg-slate-100"
                  onClick={() => handleSort('bn')}>
                B/N {sortField === 'bn' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th className="px-4 py-3 text-right text-xs font-bold uppercase text-slate-600 cursor-pointer hover:bg-slate-100"
                  onClick={() => handleSort('color')}>
                Color {sortField === 'color' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
            </tr>
          </thead>
          <tbody>
            {paginated.map((user, index) => (
              <tr key={user.id} className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
                <td className="px-4 py-3 text-sm text-slate-900">{user.codigo_usuario}</td>
                <td className="px-4 py-3 text-sm text-slate-900">{user.nombre_usuario}</td>
                <td className="px-4 py-3 text-sm text-slate-900 text-right font-semibold">
                  {user.total_paginas.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-sm text-slate-600 text-right">
                  {user.total_bn.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-sm text-slate-600 text-right">
                  {user.total_color.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="p-4 border-t border-slate-200 flex items-center justify-between">
          <div className="text-sm text-slate-500">
            Mostrando {startIndex + 1}-{Math.min(startIndex + itemsPerPage, sorted.length)} de {sorted.length}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm font-bold rounded-lg border border-slate-300 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Anterior
            </button>
            <span className="px-3 py-1 text-sm font-bold text-slate-700">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm font-bold rounded-lg border border-slate-300 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Siguiente →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```


## Data Models

### Backend API Extension for Daily Closes

**CRITICAL**: The current backend only supports monthly closes. The daily close functionality requires new backend endpoints:

#### Required New Endpoints

**1. POST /api/counters/close-day**
- Purpose: Create a daily close for a specific date
- Request Body:
  ```json
  {
    "printer_id": 4,
    "close_date": "2026-03-02",
    "cerrado_por": "Admin",
    "notas": "Monthly accounting close"
  }
  ```
- Response: DailyClose object with comparison_date and differences
- Logic:
  - Read counters for close_date
  - Calculate comparison_date (same day of previous month: Feb 2)
  - Read counters for comparison_date
  - Calculate differences (close_date - comparison_date)
  - Store close record with both dates

**2. GET /api/counters/closes/daily**
- Purpose: List daily closes with optional filters
- Query Parameters:
  - `printer_id` (required): Filter by printer
  - `start_date` (optional): Filter closes from this date
  - `end_date` (optional): Filter closes until this date
- Response: Array of DailyClose objects

**3. GET /api/counters/closes/daily/{id}**
- Purpose: Get a specific daily close by ID
- Response: Single DailyClose object

#### Database Schema

New table required: `daily_closes`

```sql
CREATE TABLE daily_closes (
  id SERIAL PRIMARY KEY,
  printer_id INTEGER NOT NULL REFERENCES printers(id),
  close_date DATE NOT NULL,
  comparison_date DATE NOT NULL,
  total_paginas INTEGER NOT NULL,
  total_copiadora INTEGER NOT NULL,
  total_impresora INTEGER NOT NULL,
  total_escaner INTEGER NOT NULL,
  total_fax INTEGER NOT NULL,
  diferencia_total INTEGER NOT NULL,
  diferencia_copiadora INTEGER NOT NULL,
  diferencia_impresora INTEGER NOT NULL,
  diferencia_escaner INTEGER NOT NULL,
  diferencia_fax INTEGER NOT NULL,
  fecha_cierre TIMESTAMP NOT NULL DEFAULT NOW(),
  cerrado_por VARCHAR(100),
  notas TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(printer_id, close_date)
);
```

### TypeScript Interfaces

```typescript
// src/types/counter.ts

/**
 * Total counter for a printer
 */
export interface TotalCounter {
  id: number;
  printer_id: number;
  total: number;
  copiadora_bn: number;
  copiadora_color: number;
  copiadora_color_personalizado: number;
  copiadora_dos_colores: number;
  impresora_bn: number;
  impresora_color: number;
  impresora_color_personalizado: number;
  impresora_dos_colores: number;
  fax_bn: number;
  enviar_total_bn: number;
  enviar_total_color: number;
  transmision_fax_total: number;
  envio_escaner_bn: number;
  envio_escaner_color: number;
  otras_a3_dlt: number;
  otras_duplex: number;
  fecha_lectura: string; // ISO 8601
  created_at: string; // ISO 8601
}

/**
 * User counter for a printer
 */
export interface UserCounter {
  id: number;
  printer_id: number;
  codigo_usuario: string;
  nombre_usuario: string;
  total_paginas: number;
  total_bn: number;
  total_color: number;
  copiadora_bn: number;
  copiadora_mono_color: number;
  copiadora_dos_colores: number;
  copiadora_todo_color: number;
  impresora_bn: number;
  impresora_mono_color: number;
  impresora_dos_colores: number;
  impresora_color: number;
  escaner_bn: number;
  escaner_todo_color: number;
  fax_bn: number;
  fax_paginas_transmitidas: number;
  revelado_negro: number;
  revelado_color_ymc: number;
  eco_uso_2_caras: number | null;
  eco_uso_combinar: number | null;
  eco_reduccion_papel: number | null;
  tipo_contador: 'usuario' | 'ecologico';
  fecha_lectura: string; // ISO 8601
  created_at: string; // ISO 8601
}

/**
 * Daily close record
 */
export interface DailyClose {
  id: number;
  printer_id: number;
  close_date: string; // ISO 8601 date (e.g., "2026-03-02")
  comparison_date: string; // ISO 8601 date (e.g., "2026-02-02")
  total_paginas: number;
  total_copiadora: number;
  total_impresora: number;
  total_escaner: number;
  total_fax: number;
  diferencia_total: number;
  diferencia_copiadora: number;
  diferencia_impresora: number;
  diferencia_escaner: number;
  diferencia_fax: number;
  fecha_cierre: string; // ISO 8601 timestamp
  cerrado_por: string | null;
  notas: string | null;
  created_at: string; // ISO 8601 timestamp
}

/**
 * Request to perform daily close
 */
export interface DailyCloseRequest {
  printer_id: number;
  close_date: string; // ISO 8601 date (e.g., "2026-03-02")
  cerrado_por?: string;
  notas?: string;
}

/**
 * Result of manual counter reading
 */
export interface ReadResult {
  success: boolean;
  printer_id: number;
  contador_total: TotalCounter;
  usuarios_count: number;
  error: string | null;
}

/**
 * Result of reading all printers
 */
export interface ReadAllResult {
  success: boolean;
  total_printers: number;
  successful: number;
  failed: number;
  results: ReadResult[];
}

/**
 * Printer device (from existing types)
 */
export interface PrinterDevice {
  id: string;
  hostname: string;
  ip_address: string;
  status: string;
  location: string;
  toner_levels: {
    cyan: number;
    magenta: number;
    yellow: number;
    black: number;
  };
  capabilities: {
    color: boolean;
    scanner: boolean;
  };
}
```

### Data Flow Diagrams

#### Counter Reading Flow

```
User Action (Dashboard)
    ↓
[Click "Read All Printers"]
    ↓
DashboardView.handleReadAll()
    ↓
counterService.triggerReadAll()
    ↓
POST /api/counters/read-all
    ↓
Backend processes all printers (5-10 min)
    ↓
Response: { successful: 5, failed: 0, results: [...] }
    ↓
DashboardView.loadDashboardData()
    ↓
Fetch updated counters for all printers
    ↓
Update UI with new counter values
```

#### Daily Close Flow

```
User Action (Daily Close View)
    ↓
[Fill form: printer, date (e.g., March 2, 2026), notes]
    ↓
[Click "Realizar Cierre"]
    ↓
DailyCloseView.handleSubmit()
    ↓
Validate: date <= current date
    ↓
counterService.performDailyClose()
    ↓
POST /api/counters/close-day
    ↓
Backend:
  - Fetch counter for close_date (March 2, 2026)
  - Calculate comparison_date (February 2, 2026)
  - Fetch counter for comparison_date
  - Calculate differences
  - Save close record
    ↓
Response: DailyClose with differences and comparison_date
    ↓
Display success message with comparison date and differences
    ↓
Reload close history table
```

#### Export Flow

```
User Action (Close History Table)
    ↓
[Click "Export" button on close row]
    ↓
exportService.exportDailyCloseToPDF()
    ↓
Generate PDF with jsPDF:
  - Printer info
  - Close date and comparison date
  - Counter totals
  - Differences vs comparison date
  - Notes
    ↓
Trigger browser download
    ↓
File saved: close_printer_2026-03-02.pdf
```

### State Management

#### Option 1: Local Component State (Recommended for MVP)

Each view component manages its own state using React hooks:
- `useState` for data and UI state
- `useEffect` for data fetching and intervals
- Props for parent-child communication

Pros:
- Simple, no additional dependencies
- Easy to understand and maintain
- Sufficient for current requirements

Cons:
- No global state sharing
- Data refetched when navigating between views

#### Option 2: Zustand Store (Optional Enhancement)

Create a global store for counter data caching:

```typescript
// src/store/useCounterStore.ts

interface CounterStore {
  // Cache
  counters: Map<number, TotalCounter>;
  userCounters: Map<number, UserCounter[]>;
  history: Map<number, TotalCounter[]>;
  
  // Loading states
  loading: boolean;
  
  // Actions
  setCounter: (printerId: number, counter: TotalCounter) => void;
  setUserCounters: (printerId: number, users: UserCounter[]) => void;
  setHistory: (printerId: number, history: TotalCounter[]) => void;
  clearCache: () => void;
}

export const useCounterStore = create<CounterStore>((set) => ({
  counters: new Map(),
  userCounters: new Map(),
  history: new Map(),
  loading: false,
  
  setCounter: (printerId, counter) =>
    set((state) => ({
      counters: new Map(state.counters).set(printerId, counter),
    })),
  
  setUserCounters: (printerId, users) =>
    set((state) => ({
      userCounters: new Map(state.userCounters).set(printerId, users),
    })),
  
  setHistory: (printerId, history) =>
    set((state) => ({
      history: new Map(state.history).set(printerId, history),
    })),
  
  clearCache: () =>
    set({
      counters: new Map(),
      userCounters: new Map(),
      history: new Map(),
    }),
}));
```

Pros:
- Global state sharing across views
- Reduced API calls with caching
- Consistent with existing usuario module pattern

Cons:
- Additional complexity
- Need to manage cache invalidation

**Recommendation**: Start with Option 1 (local state) for MVP, migrate to Option 2 if performance issues arise.


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all 180+ acceptance criteria, I identified the following testable properties. Many criteria are specific examples or UI styling requirements that don't translate to universal properties. The key properties that emerged are:

**Identified Properties:**
1. API error handling (1.10) - For any failed API call, an error should be thrown
2. API type safety (1.12) - For any API function, valid input produces valid typed output
3. Printer card rendering (2.1, 2.3-2.5) - For any printer list, each printer gets a card with required fields
4. Card click navigation (2.6) - For any printer card, clicking navigates to detail view
5. Counter invariant (4.9) - For any counter, sum of function counters ≤ total
6. User counter invariant (5.10) - For any user counter, total_paginas = total_bn + total_color

**Redundancy Analysis:**
- Properties 3 and 4 can be combined into a single "printer card behavior" property
- Property 2 (type safety) is actually a meta-property about the service layer design, not a runtime property
- Properties 5 and 6 are both data invariants that should hold for all counter data

**Final Properties (after removing redundancy):**
1. API error handling across all service functions
2. Counter data invariants (both total and user counters)
3. Printer card rendering and interaction

### Property 1: API Error Handling

For any Counter Service API function, when the backend returns an error response (4xx or 5xx status code), the function shall throw an Error with a descriptive message that includes context about the failure.

**Validates: Requirements 1.10**

### Property 2: Total Counter Invariant

For any TotalCounter object, the sum of all function-specific counters (copiadora_bn + copiadora_color + impresora_bn + impresora_color + fax_bn + envio_escaner_bn + envio_escaner_color) shall be less than or equal to the total counter value.

**Validates: Requirements 4.9**

### Property 3: User Counter Invariant

For any UserCounter object, the total_paginas field shall equal the sum of total_bn and total_color.

**Validates: Requirements 5.10**

### Property 4: Printer Card Rendering

For any non-empty array of PrinterDevice objects passed to DashboardView, the rendered output shall contain exactly one PrinterCounterCard component for each printer, and each card shall display the printer's hostname, ip_address, and location fields.

**Validates: Requirements 2.1, 2.3, 2.4, 2.5**

### Property 5: Navigation on Card Click

For any PrinterCounterCard component, when the card's onClick handler is triggered with a valid printer ID, the application state shall transition to show the PrinterDetailView for that specific printer ID.

**Validates: Requirements 2.6**


## Error Handling

### Error Categories

The counter module handles four categories of errors:

1. **Network Errors**: Connection failures, timeouts
2. **API Errors**: 4xx/5xx responses from backend
3. **Validation Errors**: Client-side form validation failures
4. **Data Errors**: Invalid or inconsistent counter data

### Error Handling Strategy

#### Service Layer

All service functions follow a consistent error handling pattern:

```typescript
export async function fetchLatestCounter(printerId: number): Promise<TotalCounter> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/counters/printer/${printerId}`);
    
    if (!response.ok) {
      // Parse error details from backend
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
    // Re-throw with context
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown error fetching counter');
  }
}
```

#### Component Layer

Components catch errors from services and display them using ErrorHandler:

```typescript
const handleManualRead = async () => {
  try {
    setReading(true);
    setError(null);
    await triggerManualRead(printerId);
    await loadPrinterData();
    alert('✅ Lectura completada exitosamente');
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Error desconocido';
    setError(message);
  } finally {
    setReading(false);
  }
};
```

### Error Messages

Error messages follow a consistent format:

| Error Type | Message Format | Example |
|------------|---------------|---------|
| Network | "Connection error, check network" | When fetch fails |
| 404 | "Resource not found" | Printer or counter doesn't exist |
| 400 | Backend validation message | "Ya existe un cierre para ese mes" |
| 500 | "Server error, please try again" | Backend internal error |
| Validation | Specific field error | "El año no puede ser mayor al año actual" |

### Error Recovery

- **Auto-retry**: Not implemented (user must manually retry)
- **Fallback data**: Display cached data if available
- **Graceful degradation**: Show partial data if some requests fail
- **User guidance**: Error messages include actionable advice


## Testing Strategy

### Dual Testing Approach

The counter module requires both unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
- Specific user interactions (button clicks, form submissions)
- Edge cases (empty data, network failures)
- Integration points between components
- Error handling scenarios

**Property Tests**: Verify universal properties across all inputs
- Data invariants (counter totals, user counter sums)
- API error handling across all service functions
- Component rendering for any valid input data
- Navigation behavior for any printer ID

Together, these approaches provide comprehensive coverage: unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across the input space.

### Unit Testing

#### Test Framework

- **Framework**: Vitest (already configured in project)
- **React Testing**: @testing-library/react
- **Mocking**: vi.mock for service layer

#### Unit Test Coverage

**Service Layer Tests** (`counterService.test.ts`):
```typescript
describe('counterService', () => {
  describe('fetchLatestCounter', () => {
    it('should fetch counter for valid printer ID', async () => {
      // Mock successful response
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ id: 1, printer_id: 4, total: 372573, ... }),
      });
      
      const counter = await fetchLatestCounter(4);
      expect(counter.printer_id).toBe(4);
      expect(counter.total).toBe(372573);
    });
    
    it('should throw error for 404 response', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ detail: 'Printer not found' }),
      });
      
      await expect(fetchLatestCounter(999)).rejects.toThrow('Printer not found');
    });
    
    it('should handle network errors', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));
      
      await expect(fetchLatestCounter(4)).rejects.toThrow();
    });
  });
  
  // Similar tests for other service functions...
});
```

**Component Tests** (`DashboardView.test.tsx`):
```typescript
describe('DashboardView', () => {
  it('should render printer cards for all printers', async () => {
    const mockPrinters = [
      { id: '1', hostname: 'Printer1', ip_address: '192.168.1.10', ... },
      { id: '2', hostname: 'Printer2', ip_address: '192.168.1.11', ... },
    ];
    
    vi.mocked(fetchPrinters).mockResolvedValue(mockPrinters);
    
    render(<DashboardView onNavigateToPrinter={vi.fn()} />);
    
    await waitFor(() => {
      expect(screen.getByText('Printer1')).toBeInTheDocument();
      expect(screen.getByText('Printer2')).toBeInTheDocument();
    });
  });
  
  it('should show loading indicator while fetching', () => {
    vi.mocked(fetchPrinters).mockImplementation(() => new Promise(() => {}));
    
    render(<DashboardView onNavigateToPrinter={vi.fn()} />);
    
    expect(screen.getByText(/cargando/i)).toBeInTheDocument();
  });
  
  it('should handle empty printer list', async () => {
    vi.mocked(fetchPrinters).mockResolvedValue([]);
    
    render(<DashboardView onNavigateToPrinter={vi.fn()} />);
    
    await waitFor(() => {
      expect(screen.queryByRole('article')).not.toBeInTheDocument();
    });
  });
});
```

**Form Validation Tests** (`DailyCloseView.test.tsx`):
```typescript
describe('DailyCloseView validation', () => {
  it('should reject future date', async () => {
    render(<DailyCloseView />);
    
    const dateInput = screen.getByLabelText(/fecha de cierre/i);
    const submitButton = screen.getByText(/realizar cierre/i);
    
    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + 1);
    const futureDateStr = futureDate.toISOString().split('T')[0];
    
    fireEvent.change(dateInput, { target: { value: futureDateStr } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/fecha no puede ser mayor/i)).toBeInTheDocument();
    });
  });
  
  it('should accept valid past date', async () => {
    render(<DailyCloseView />);
    
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 5);
    const pastDateStr = pastDate.toISOString().split('T')[0];
    
    fireEvent.change(screen.getByLabelText(/fecha de cierre/i), { target: { value: pastDateStr } });
    fireEvent.click(screen.getByText(/realizar cierre/i));
    
    // Should not show validation error
    await waitFor(() => {
      expect(screen.queryByText(/fecha no puede ser mayor/i)).not.toBeInTheDocument();
    });
  });
});
```

### Property-Based Testing

#### Test Framework

- **Library**: fast-check (recommended for TypeScript)
- **Installation**: `npm install --save-dev fast-check`
- **Configuration**: Minimum 100 iterations per property test

#### Property Test Implementation

**Property 1: API Error Handling**
```typescript
import fc from 'fast-check';

describe('Property: API Error Handling', () => {
  it('should throw error for any failed API call', async () => {
    // Feature: frontend-contadores, Property 1: For any Counter Service API function, when the backend returns an error response, the function shall throw an Error
    
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 400, max: 599 }), // HTTP error status codes
        fc.string(), // Error message
        async (statusCode, errorMessage) => {
          global.fetch = vi.fn().mockResolvedValue({
            ok: false,
            status: statusCode,
            statusText: 'Error',
            json: async () => ({ detail: errorMessage }),
          });
          
          await expect(fetchLatestCounter(1)).rejects.toThrow();
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

**Property 2: Total Counter Invariant**
```typescript
describe('Property: Total Counter Invariant', () => {
  it('should maintain sum of function counters <= total', () => {
    // Feature: frontend-contadores, Property 2: For any TotalCounter object, the sum of all function-specific counters shall be <= total
    
    fc.assert(
      fc.property(
        fc.record({
          id: fc.integer({ min: 1 }),
          printer_id: fc.integer({ min: 1 }),
          total: fc.integer({ min: 0, max: 10000000 }),
          copiadora_bn: fc.integer({ min: 0, max: 1000000 }),
          copiadora_color: fc.integer({ min: 0, max: 1000000 }),
          impresora_bn: fc.integer({ min: 0, max: 1000000 }),
          impresora_color: fc.integer({ min: 0, max: 1000000 }),
          fax_bn: fc.integer({ min: 0, max: 100000 }),
          envio_escaner_bn: fc.integer({ min: 0, max: 1000000 }),
          envio_escaner_color: fc.integer({ min: 0, max: 1000000 }),
          // ... other fields
        }),
        (counter: TotalCounter) => {
          const sum = counter.copiadora_bn + counter.copiadora_color +
                      counter.impresora_bn + counter.impresora_color +
                      counter.fax_bn + counter.envio_escaner_bn +
                      counter.envio_escaner_color;
          
          return sum <= counter.total;
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

**Property 3: User Counter Invariant**
```typescript
describe('Property: User Counter Invariant', () => {
  it('should maintain total_paginas = total_bn + total_color', () => {
    // Feature: frontend-contadores, Property 3: For any UserCounter object, total_paginas shall equal total_bn + total_color
    
    fc.assert(
      fc.property(
        fc.record({
          id: fc.integer({ min: 1 }),
          printer_id: fc.integer({ min: 1 }),
          codigo_usuario: fc.string({ minLength: 1, maxLength: 10 }),
          nombre_usuario: fc.string({ minLength: 1, maxLength: 100 }),
          total_bn: fc.integer({ min: 0, max: 1000000 }),
          total_color: fc.integer({ min: 0, max: 1000000 }),
          // ... other fields
        }),
        (userCounter) => {
          const total_paginas = userCounter.total_bn + userCounter.total_color;
          return { ...userCounter, total_paginas };
        },
        (userCounter: UserCounter) => {
          return userCounter.total_paginas === (userCounter.total_bn + userCounter.total_color);
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

**Property 4: Printer Card Rendering**
```typescript
describe('Property: Printer Card Rendering', () => {
  it('should render one card per printer with required fields', () => {
    // Feature: frontend-contadores, Property 4: For any non-empty array of PrinterDevice objects, the rendered output shall contain exactly one card per printer
    
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            id: fc.integer({ min: 1 }).map(String),
            hostname: fc.string({ minLength: 1, maxLength: 50 }),
            ip_address: fc.ipV4(),
            location: fc.string({ minLength: 1, maxLength: 100 }),
            status: fc.constantFrom('online', 'offline', 'error'),
            toner_levels: fc.record({
              cyan: fc.integer({ min: 0, max: 100 }),
              magenta: fc.integer({ min: 0, max: 100 }),
              yellow: fc.integer({ min: 0, max: 100 }),
              black: fc.integer({ min: 0, max: 100 }),
            }),
            capabilities: fc.record({
              color: fc.boolean(),
              scanner: fc.boolean(),
            }),
          }),
          { minLength: 1, maxLength: 20 }
        ),
        (printers: PrinterDevice[]) => {
          const { container } = render(
            <DashboardView onNavigateToPrinter={vi.fn()} />
          );
          
          // Mock the fetch to return our generated printers
          vi.mocked(fetchPrinters).mockResolvedValue(printers);
          
          // Wait for render
          waitFor(() => {
            const cards = container.querySelectorAll('[data-testid="printer-card"]');
            expect(cards.length).toBe(printers.length);
            
            printers.forEach((printer) => {
              expect(screen.getByText(printer.hostname)).toBeInTheDocument();
              expect(screen.getByText(printer.ip_address)).toBeInTheDocument();
              expect(screen.getByText(printer.location)).toBeInTheDocument();
            });
          });
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Test Organization

```
src/
├── services/
│   ├── counterService.ts
│   ├── counterService.test.ts          # Unit tests
│   ├── counterService.property.test.ts # Property tests
│   ├── exportService.ts
│   └── exportService.test.ts
├── components/
│   └── contadores/
│       ├── DashboardView.tsx
│       ├── DashboardView.test.tsx
│       ├── DashboardView.property.test.ts
│       ├── PrinterDetailView.tsx
│       ├── PrinterDetailView.test.tsx
│       └── ...
└── types/
    └── counter.ts
```

### Test Execution

```bash
# Run all tests
npm test

# Run unit tests only
npm test -- --grep "^(?!.*Property:)"

# Run property tests only
npm test -- --grep "Property:"

# Run with coverage
npm test -- --coverage
```

### Coverage Goals

- **Service Layer**: 90%+ line coverage
- **Component Layer**: 80%+ line coverage
- **Property Tests**: All identified properties implemented
- **Critical Paths**: 100% coverage (counter reading, daily close, export)


## File Structure

### Directory Organization

```
src/
├── components/
│   └── contadores/                    # Counter module root
│       ├── ContadoresModule.tsx       # Main module component (navigation wrapper)
│       ├── dashboard/
│       │   ├── DashboardView.tsx      # Main dashboard view
│       │   ├── PrinterCounterCard.tsx # Individual printer card
│       │   └── CounterSummary.tsx     # Counter summary display
│       ├── detail/
│       │   ├── PrinterDetailView.tsx  # Printer detail view
│       │   ├── PrinterIdentification.tsx
│       │   ├── CounterBreakdown.tsx   # Counter breakdown by function
│       │   ├── HistoryChart.tsx       # Historical chart component
│       │   └── UserCounterTable.tsx   # User counter table (fetches from /api/counters/users/{printer_id})
│       ├── daily/
│       │   ├── DailyCloseView.tsx     # Daily close view
│       │   ├── CloseForm.tsx          # Close form component
│       │   └── CloseHistoryTable.tsx  # Close history table
│       └── shared/
│           ├── LoadingIndicator.tsx   # Loading spinner
│           ├── ErrorHandler.tsx       # Error display
│           └── RefreshButton.tsx      # Refresh button
├── services/
│   ├── counterService.ts              # Counter API service
│   └── exportService.ts               # Export service (Excel/PDF)
├── types/
│   └── counter.ts                     # Counter type definitions
└── store/                             # Optional
    └── useCounterStore.ts             # Zustand store (if needed)
```

### Integration with Existing App

#### App.tsx Modifications

Add counter module to navigation menu:

```typescript
// src/App.tsx

import { ContadoresModule } from './components/contadores/ContadoresModule';
import { BarChart3 } from 'lucide-react'; // Counter icon

function App() {
  const [vistaActual, setVistaActual] = useState<
    'descubrimiento' | 'aprovisionamiento' | 'administracion' | 'contadores'
  >('descubrimiento');

  return (
    <div className="flex h-screen">
      <nav className="w-64 bg-industrial-gray text-white shadow-lg flex flex-col">
        {/* ... existing menu items ... */}
        
        <button
          onClick={() => setVistaActual('contadores')}
          className={`w-full flex items-center gap-3 px-6 py-3 text-sm font-bold uppercase tracking-wide transition-colors ${
            vistaActual === 'contadores'
              ? 'bg-ricoh-red text-white border-l-4 border-white'
              : 'text-slate-300 hover:bg-slate-800'
          }`}
        >
          <BarChart3 size={18} />
          Contadores
        </button>
      </nav>

      <div className="flex-1 overflow-hidden">
        {vistaActual === 'contadores' ? (
          <ContadoresModule />
        ) : (
          // ... existing views ...
        )}
      </div>
    </div>
  );
}
```

#### ContadoresModule.tsx

Main module component managing internal navigation:

```typescript
// src/components/contadores/ContadoresModule.tsx

type CounterView = 'dashboard' | 'printer-detail' | 'daily-close';

export const ContadoresModule: React.FC = () => {
  const [currentView, setCurrentView] = useState<CounterView>('dashboard');
  const [selectedPrinterId, setSelectedPrinterId] = useState<number | null>(null);

  const handleNavigateToPrinter = (printerId: number) => {
    setSelectedPrinterId(printerId);
    setCurrentView('printer-detail');
  };

  const handleNavigateBack = () => {
    setCurrentView('dashboard');
    setSelectedPrinterId(null);
  };

  const handleNavigateToDailyClose = () => {
    setCurrentView('daily-close');
  };

  return (
    <>
      {currentView === 'dashboard' && (
        <DashboardView
          onNavigateToPrinter={handleNavigateToPrinter}
          onNavigateToDailyClose={handleNavigateToDailyClose}
        />
      )}
      
      {currentView === 'printer-detail' && selectedPrinterId && (
        <PrinterDetailView
          printerId={selectedPrinterId}
          onNavigateBack={handleNavigateBack}
        />
      )}
      
      {currentView === 'daily-close' && (
        <DailyCloseView onNavigateBack={handleNavigateBack} />
      )}
    </>
  );
};
```

### Dependencies to Install

```json
{
  "dependencies": {
    "recharts": "^2.10.0",
    "xlsx": "^0.18.5",
    "jspdf": "^2.5.1",
    "jspdf-autotable": "^3.8.0"
  },
  "devDependencies": {
    "fast-check": "^3.15.0",
    "@types/jspdf": "^2.0.0"
  }
}
```

Installation command:
```bash
npm install recharts xlsx jspdf jspdf-autotable
npm install --save-dev fast-check @types/jspdf
```

### Environment Variables

No new environment variables required. The module uses the existing `VITE_API_URL`:

```env
VITE_API_URL=http://localhost:8000
```

### Build Configuration

No changes required to Vite configuration. The module uses existing build setup.


## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal**: Set up basic infrastructure and service layer

Tasks:
1. Create directory structure
2. Define TypeScript types (`counter.ts`)
3. Implement `counterService.ts` with all 9 API functions
4. Write unit tests for service layer
5. Implement shared components (LoadingIndicator, ErrorHandler)

Deliverables:
- Complete service layer with tests
- Type definitions
- Shared components

### Phase 2: Dashboard View (Week 2)

**Goal**: Implement main dashboard with printer cards

Tasks:
1. Implement `DashboardView.tsx`
2. Implement `PrinterCounterCard.tsx`
3. Implement "Read All" functionality
4. Add auto-refresh (60s interval)
5. Write component tests
6. Integrate with App.tsx navigation

Deliverables:
- Working dashboard view
- Printer card display
- Manual and auto-refresh
- Navigation integration

### Phase 3: Printer Detail View (Week 3)

**Goal**: Implement detailed printer view with history and user counters

Tasks:
1. Implement `PrinterDetailView.tsx`
2. Implement `CounterBreakdown.tsx`
3. Implement `HistoryChart.tsx` with recharts (lazy-loaded)
4. Implement `UserCounterTable.tsx` with sorting, filtering, pagination
5. Add manual read functionality
6. Write component tests

Deliverables:
- Complete printer detail view
- Historical chart with date filters
- User counter table with full functionality
- Manual counter reading

### Phase 4: Daily Close (Week 4)

**Goal**: Implement daily close operations

Tasks:
1. Implement `DailyCloseView.tsx`
2. Implement `CloseForm.tsx` with date picker and validation
3. Implement `CloseHistoryTable.tsx` with date range filtering
4. Add comparison date display
5. Write form validation tests
6. Write component tests

Deliverables:
- Daily close form with date picker and validation
- Close history display with comparison dates
- Date range filtering

### Phase 5: Export Functionality (Week 5)

**Goal**: Add export capabilities

Tasks:
1. Implement `exportService.ts`
2. Add Excel export for counter data
3. Add PDF export for daily closes
4. Integrate export buttons in UI
5. Write export tests

Deliverables:
- Excel export functionality
- PDF export functionality for daily closes
- Export buttons in UI

### Phase 6: Polish and Testing (Week 6)

**Goal**: Finalize implementation with comprehensive testing

Tasks:
1. Implement property-based tests
2. Add accessibility features (ARIA labels, keyboard nav)
3. Optimize performance (React.memo, lazy loading)
4. Add responsive design refinements
5. Conduct end-to-end testing
6. Fix bugs and polish UI

Deliverables:
- Complete property test suite
- Accessibility compliance
- Performance optimizations
- Bug-free, polished UI

### Optional Enhancements (Future)

**State Management**:
- Implement Zustand store for caching
- Add optimistic updates
- Implement background sync

**Advanced Features**:
- Real-time updates via WebSocket
- Advanced filtering and search
- Custom date range selection
- Bulk operations
- Counter comparison between printers
- Trend analysis and predictions

**Performance**:
- Virtual scrolling for large tables
- Service worker for offline support
- Progressive Web App (PWA) features


## Design Decisions and Rationale

### 1. State-Based Navigation vs React Router

**Decision**: Use state-based navigation matching existing pattern

**Rationale**:
- Consistency with existing codebase (App.tsx uses `vistaActual` state)
- Simpler implementation for small number of views (3 views)
- No additional dependencies
- Easier to integrate with existing navigation menu

**Trade-offs**:
- No URL-based routing (can't bookmark specific views)
- No browser back/forward navigation
- Acceptable for internal admin tool

### 2. Local State vs Zustand Store

**Decision**: Start with local component state, optionally migrate to Zustand

**Rationale**:
- Simpler implementation for MVP
- Sufficient for current requirements
- Zustand already used in usuario module (familiar pattern)
- Easy to migrate later if needed

**Trade-offs**:
- Data refetched when navigating between views
- No global cache
- Acceptable with auto-refresh intervals

### 3. Recharts for Charting

**Decision**: Use Recharts library for historical charts

**Rationale**:
- React-native, declarative API
- Good TypeScript support
- Responsive by default
- Reasonable bundle size (~100KB)
- Active maintenance

**Alternatives considered**:
- Chart.js: More features but imperative API
- Victory: Larger bundle size
- D3.js: Too low-level, steep learning curve

### 4. Lazy Loading for Charts

**Decision**: Lazy-load Recharts library

**Rationale**:
- Charts only needed in detail view
- Reduces initial bundle size
- Improves dashboard load time
- React.lazy + Suspense built-in support

**Implementation**:
```typescript
const LineChart = lazy(() => import('recharts').then(m => ({ default: m.LineChart })));
```

### 5. Pagination at 50 Items

**Decision**: Use 50 items per page for user counter table

**Rationale**:
- Matches existing pattern in AdministracionUsuarios
- Good balance between data visibility and performance
- Typical printer has 200-300 users (4-6 pages)
- Acceptable scroll length

### 6. Auto-Refresh Intervals

**Decision**: 60s for dashboard, 30s for detail view

**Rationale**:
- Dashboard: Less critical, more expensive (multiple printers)
- Detail view: More critical, single printer
- Balance between freshness and server load
- User can manually refresh anytime

### 7. Error Handling Strategy

**Decision**: Display errors inline with auto-dismiss for non-critical errors

**Rationale**:
- Non-intrusive for transient errors
- Persistent for critical errors requiring user action
- Consistent with modern web app patterns
- Better UX than alert() dialogs

### 8. Export Libraries

**Decision**: Use xlsx for Excel, jsPDF for PDF

**Rationale**:
- xlsx: Industry standard, excellent Excel compatibility
- jsPDF: Mature, good TypeScript support, autotable plugin
- Both have reasonable bundle sizes
- Active maintenance and community support

**Alternatives considered**:
- ExcelJS: More features but larger bundle
- pdfmake: Different API style, less familiar

### 9. TypeScript Strict Mode

**Decision**: Use strict TypeScript types throughout

**Rationale**:
- Catch errors at compile time
- Better IDE support and autocomplete
- Self-documenting code
- Matches existing project standards

**Implementation**:
- All API responses typed
- No `any` types (use `unknown` if needed)
- Strict null checks enabled

### 10. Accessibility First

**Decision**: Build accessibility features from the start

**Rationale**:
- Easier to build in than retrofit
- Required for enterprise software
- Improves usability for all users
- Keyboard navigation essential for power users

**Features**:
- ARIA labels on all interactive elements
- Keyboard navigation (Tab, Enter, Escape)
- Focus indicators
- Screen reader announcements
- Semantic HTML


## Security Considerations

### 1. API Security

**Authentication**: Not implemented in current design (future enhancement)
- Backend API currently has no authentication
- Frontend makes direct API calls without tokens
- Acceptable for internal network deployment
- Future: Add JWT or session-based auth

**HTTPS**: Recommended for production
- Use HTTPS in production environment
- Configure VITE_API_URL with https:// prefix
- Prevents man-in-the-middle attacks

### 2. Input Validation

**Client-Side Validation**:
- Form inputs validated before submission
- Year range: 2020-2100
- Month range: 1-12
- Future dates rejected
- Prevents invalid API calls

**Server-Side Validation**:
- Backend performs authoritative validation
- Client validation is UX enhancement only
- Never trust client-side validation alone

### 3. XSS Prevention

**React Built-In Protection**:
- React escapes all rendered content by default
- No `dangerouslySetInnerHTML` used
- User input never executed as code

**Content Security Policy** (recommended):
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';">
```

### 4. Data Exposure

**Sensitive Data**:
- Counter data is not sensitive (business metrics)
- User codes and names are semi-public (internal users)
- No passwords or personal data displayed

**Network Exposure**:
- API calls visible in browser DevTools
- Acceptable for internal admin tool
- Future: Add request encryption for sensitive operations

### 5. Dependency Security

**Regular Updates**:
- Keep dependencies updated
- Monitor security advisories
- Use `npm audit` regularly

**Minimal Dependencies**:
- Only essential libraries included
- Avoid unnecessary third-party code
- Review dependencies before adding

### 6. Error Messages

**Information Disclosure**:
- Error messages user-friendly, not technical
- No stack traces exposed to users
- Backend error details logged, not displayed
- Prevents information leakage

**Example**:
```typescript
// Bad: Exposes internal details
throw new Error(`Database query failed: ${sqlError.message}`);

// Good: Generic user message
throw new Error('Failed to fetch counter data');
```

## Performance Optimization

### 1. Bundle Size Optimization

**Code Splitting**:
- Lazy-load Recharts library (~100KB)
- Lazy-load export libraries when needed
- Reduces initial bundle size by ~150KB

**Tree Shaking**:
- Import only needed Lucide icons
- Use named imports from libraries
- Vite automatically tree-shakes unused code

### 2. Rendering Optimization

**React.memo**:
- Memoize static components (PrinterCounterCard)
- Prevent unnecessary re-renders
- Especially important for lists

**useMemo and useCallback**:
- Memoize expensive computations (sorting, filtering)
- Memoize callback functions passed to children
- Reduces re-render cascades

**Example**:
```typescript
const PrinterCounterCard = React.memo<PrinterCounterCardProps>(({ printer, counter, onClick }) => {
  // Component implementation
});

const sortedUsers = useMemo(() => {
  return [...users].sort((a, b) => /* sorting logic */);
}, [users, sortField, sortDirection]);
```

### 3. Data Fetching Optimization

**Parallel Requests**:
- Fetch multiple printers in parallel (Promise.all)
- Reduces total load time
- Better user experience

**Request Debouncing**:
- Debounce search input (300ms)
- Prevents excessive API calls
- Improves performance and UX

**Caching** (optional with Zustand):
- Cache counter data in memory
- Reduce redundant API calls
- Invalidate on manual refresh

### 4. Table Optimization

**Pagination**:
- 50 items per page
- Reduces DOM nodes
- Faster rendering and scrolling

**Virtual Scrolling** (future enhancement):
- For tables with 1000+ rows
- Only render visible rows
- Libraries: react-window, react-virtual

### 5. Image and Asset Optimization

**Icons**:
- Use Lucide React (SVG icons)
- Tree-shakeable, small bundle size
- No image requests

**No Heavy Assets**:
- No images or videos in counter module
- Minimal CSS (Tailwind utilities)
- Fast initial load

### 6. Network Optimization

**Request Compression**:
- Backend should enable gzip/brotli
- Reduces payload size by 70-80%
- Configured at server level

**HTTP/2**:
- Use HTTP/2 if available
- Multiplexing reduces latency
- Configured at server level

### 7. Monitoring and Metrics

**Performance Metrics to Track**:
- Time to First Contentful Paint (FCP)
- Time to Interactive (TTI)
- Largest Contentful Paint (LCP)
- API response times

**Tools**:
- Chrome DevTools Performance tab
- Lighthouse audits
- React DevTools Profiler

**Target Metrics**:
- FCP < 1.5s
- TTI < 3s
- LCP < 2.5s
- API calls < 2s


## Appendix

### A. API Endpoint Reference

Quick reference for all counter API endpoints used by the frontend:

| Endpoint | Method | Purpose | Service Function |
|----------|--------|---------|------------------|
| `/api/counters/printer/{id}` | GET | Get latest counter | `fetchLatestCounter()` |
| `/api/counters/printer/{id}/history` | GET | Get counter history | `fetchCounterHistory()` |
| `/api/counters/users/{id}` | GET | Get user counters | `fetchUserCounters()` |
| `/api/counters/users/{id}/history` | GET | Get user history | `fetchUserCounterHistory()` |
| `/api/counters/read/{id}` | POST | Manual read | `triggerManualRead()` |
| `/api/counters/read-all` | POST | Read all printers | `triggerReadAll()` |
| `/api/counters/close-day` | POST | Perform daily close | `performDailyClose()` |
| `/api/counters/closes/daily` | GET | Get daily closes | `fetchDailyCloses()` |
| `/api/counters/closes/daily/{id}` | GET | Get specific close | `fetchDailyClose()` |

**Note**: The last 3 endpoints for daily closes are NEW and require backend implementation (see Requirement 8 in requirements.md).

### B. Color Palette Reference

Colors used in the counter module (from existing theme):

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| ricoh-red | #E60012 | Primary actions, active states, chart lines |
| industrial-gray | #1E293B | Navigation, secondary buttons, text |
| slate-50 | #F8FAFC | Background |
| slate-100 | #F1F5F9 | Hover states |
| slate-200 | #E2E8F0 | Borders |
| slate-400 | #94A3B8 | Placeholder text, icons |
| slate-600 | #475569 | Secondary text |
| slate-700 | #334155 | Headings |
| slate-900 | #0F172A | Primary text |
| white | #FFFFFF | Cards, tables |
| red-50 | #FEF2F2 | Error backgrounds |
| red-600 | #DC2626 | Error text, icons |
| green-600 | #16A34A | Success indicators |
| blue-600 | #2563EB | Info, links |

### C. Icon Reference

Lucide React icons used in the counter module:

| Icon | Component | Usage |
|------|-----------|-------|
| BarChart3 | `<BarChart3 />` | Counter module menu icon |
| Printer | `<Printer />` | Printer cards |
| RefreshCw | `<RefreshCw />` | Refresh buttons |
| Loader2 | `<Loader2 />` | Loading indicators |
| AlertCircle | `<AlertCircle />` | Error messages |
| Search | `<Search />` | Search inputs |
| ArrowLeft | `<ArrowLeft />` | Back navigation |
| Download | `<Download />` | Export buttons |
| Calendar | `<Calendar />` | Date filters |
| Users | `<Users />` | User counter table |

### D. Keyboard Shortcuts

Recommended keyboard shortcuts for power users:

| Shortcut | Action |
|----------|--------|
| Tab | Navigate between interactive elements |
| Enter | Activate button or submit form |
| Escape | Close modal or cancel action |
| Space | Toggle checkbox or select option |
| Arrow Keys | Navigate table rows or chart data |
| Ctrl/Cmd + R | Manual refresh (browser default) |

### E. Browser Compatibility

Minimum browser versions supported:

| Browser | Minimum Version |
|---------|----------------|
| Chrome | 90+ |
| Firefox | 88+ |
| Safari | 14+ |
| Edge | 90+ |

**Features requiring modern browsers**:
- ES2020 features (optional chaining, nullish coalescing)
- CSS Grid and Flexbox
- Fetch API
- Promises and async/await

**Polyfills**: Not required for target browsers

### F. Accessibility Checklist

Ensure the following accessibility features are implemented:

- [ ] All interactive elements have ARIA labels
- [ ] Keyboard navigation works for all features
- [ ] Focus indicators visible on all focusable elements
- [ ] Color contrast ratio ≥ 4.5:1 for text
- [ ] Loading states announced to screen readers
- [ ] Error messages announced with role="alert"
- [ ] Tables have proper header associations
- [ ] Forms have associated labels
- [ ] Buttons have descriptive text (not just icons)
- [ ] Charts have text alternatives

### G. Glossary

| Term | Definition |
|------|------------|
| Counter | A numeric value tracking printer usage (pages printed, copied, scanned, etc.) |
| Total Counter | Aggregate counter for all functions of a printer |
| User Counter | Counter tracking usage by individual user |
| Daily Close | Snapshot of counters for a specific date compared with same day of previous month |
| Comparison Date | The date used for comparison in daily close (same day of previous month) |
| Difference | Change in counter value between close date and comparison date |
| Manual Read | Triggered counter reading (vs automatic scheduled reading) |
| Function | Printer capability (copier, printer, scanner, fax) |
| B/N | Black and white (blanco y negro) |
| Color | Color printing |

### H. References

**External Documentation**:
- [React 19 Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Recharts Documentation](https://recharts.org/)
- [Lucide React Icons](https://lucide.dev/)
- [fast-check Documentation](https://fast-check.dev/)

**Internal Documentation**:
- Backend API: `docs/API_CONTADORES.md`
- Existing Frontend Patterns: `src/components/usuarios/`
- Service Pattern: `src/services/printerService.ts`

**Related Specifications**:
- Backend Counter Service (Fase 4)
- Frontend Requirements: `.kiro/specs/frontend-contadores/requirements.md`

