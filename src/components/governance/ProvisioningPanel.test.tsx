/// <reference types="@testing-library/jest-dom/vitest" />
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { ProvisioningPanel } from './ProvisioningPanel';
import { usePrinterStore } from '@/store/usePrinterStore';
import * as printerService from '@/services/printerService';

// Mock the printer service
vi.mock('@/services/printerService');

describe('ProvisioningPanel - Unit Tests', () => {
  beforeEach(() => {
    // Reset store state before each test
    const store = usePrinterStore.getState();
    store.clearPrinters();
    store.setLoading(false);
    store.clearSelection();
    
    // Mock fetchPrinters to return empty array by default
    vi.mocked(printerService.fetchPrinters).mockResolvedValue([]);
  });

  // **Validates: Requirements 3.3**
  it('should display loading indicator when isLoading is true', () => {
    // Set loading state to true
    const store = usePrinterStore.getState();
    store.setLoading(true);

    // Render the component
    render(<ProvisioningPanel />);

    // Assert that loading indicator is present
    expect(screen.getByText('Cargando impresoras...')).toBeInTheDocument();
    
    // Assert that the loading spinner is present (Loader2 icon with animate-spin class)
    const loader = screen.getByText('Cargando impresoras...').previousElementSibling;
    expect(loader).toBeInTheDocument();
  });

  // **Validates: Requirements 4.1, 4.2**
  it('should display empty state when printers array is empty and not loading', async () => {
    // Ensure printers array is empty and loading is false
    const store = usePrinterStore.getState();
    store.clearPrinters();
    store.setLoading(false);

    // Render the component
    render(<ProvisioningPanel />);

    // Wait for the useEffect to complete
    await waitFor(() => {
      expect(screen.queryByText('Cargando impresoras...')).not.toBeInTheDocument();
    });

    // Assert that empty state message is present
    expect(screen.getByText('No hay impresoras en la base de datos')).toBeInTheDocument();
  });

  // **Validates: Requirements 7.2**
  it('should render user provisioning form', () => {
    // Render the component
    render(<ProvisioningPanel />);

    // Assert that form title is present
    expect(screen.getByText('Crear Usuario en Impresoras')).toBeInTheDocument();
    
    // Assert that form fields are present
    expect(screen.getByPlaceholderText('Nombre del Usuario')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('1234')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('\\\\10.0.0.5\\scans\\')).toBeInTheDocument();
    
    // Assert that submit button is present
    expect(screen.getByText('Enviar Configuración')).toBeInTheDocument();
  });

  // **Validates: Requirements 7.3**
  it('should render live console', () => {
    // Render the component
    render(<ProvisioningPanel />);

    // Assert that console title is present
    expect(screen.getByText('Registro de Actividad')).toBeInTheDocument();
    
    // Assert that console placeholder message is present when no logs
    expect(screen.getByText('No hay actividad registrada. Esperando configuración...')).toBeInTheDocument();
  });
});

describe('ProvisioningPanel - Integration Tests', () => {
  beforeEach(() => {
    // Reset store state before each test
    const store = usePrinterStore.getState();
    store.clearPrinters();
    store.setLoading(false);
    store.clearSelection();
    
    // Clear all mocks
    vi.clearAllMocks();
  });

  // **Validates: Requirements 5.5**
  it('should call fetchPrinters and update store correctly on mount', async () => {
    // Mock fetchPrinters to return test data
    const mockPrinters = [
      {
        id: 'printer-1',
        hostname: 'RICOH-MP-C3004',
        ip_address: '192.168.1.100',
        status: 'online' as const,
        toner_levels: { cyan: 75, magenta: 60, yellow: 85, black: 90 },
        capabilities: { color: true, scanner: true },
      },
      {
        id: 'printer-2',
        hostname: 'RICOH-SP-4510DN',
        ip_address: '192.168.1.101',
        status: 'offline' as const,
        toner_levels: { cyan: 0, magenta: 0, yellow: 0, black: 45 },
        capabilities: { color: false, scanner: false },
      },
    ];
    
    vi.mocked(printerService.fetchPrinters).mockResolvedValue(mockPrinters);

    // Render the component
    render(<ProvisioningPanel />);

    // Verify that fetchPrinters was called
    expect(printerService.fetchPrinters).toHaveBeenCalledTimes(1);

    // Wait for the async operation to complete and verify store was updated
    await waitFor(() => {
      const store = usePrinterStore.getState();
      expect(store.printers).toEqual(mockPrinters);
    });

    // Verify that the printers are rendered
    expect(screen.getByText('RICOH-MP-C3004')).toBeInTheDocument();
    expect(screen.getByText('RICOH-SP-4510DN')).toBeInTheDocument();
  });

  // **Validates: Requirements 5.5**
  it('should transition loading state properly during fetch', async () => {
    // Mock fetchPrinters with a delay to observe loading state
    const mockPrinters = [
      {
        id: 'printer-1',
        hostname: 'Test-Printer',
        ip_address: '192.168.1.1',
        status: 'online' as const,
        toner_levels: { cyan: 80, magenta: 80, yellow: 80, black: 80 },
        capabilities: { color: true, scanner: true },
      },
    ];
    
    vi.mocked(printerService.fetchPrinters).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(mockPrinters), 50))
    );

    // Render the component
    render(<ProvisioningPanel />);

    // Initially, loading should be true
    await waitFor(() => {
      expect(screen.getByText('Cargando impresoras...')).toBeInTheDocument();
    });

    // After fetch completes, loading should be false and printers should be displayed
    await waitFor(() => {
      expect(screen.queryByText('Cargando impresoras...')).not.toBeInTheDocument();
      expect(screen.getByText('Test-Printer')).toBeInTheDocument();
    });

    // Verify final store state
    const store = usePrinterStore.getState();
    expect(store.isLoading).toBe(false);
    expect(store.printers).toEqual(mockPrinters);
  });

  // **Validates: Requirements 5.5**
  it('should handle fetch errors gracefully', async () => {
    // Mock fetchPrinters to reject with an error
    const mockError = new Error('Network error');
    vi.mocked(printerService.fetchPrinters).mockRejectedValue(mockError);

    // Spy on console.error to verify error logging
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Render the component
    render(<ProvisioningPanel />);

    // Wait for the async operation to complete
    await waitFor(() => {
      const store = usePrinterStore.getState();
      expect(store.isLoading).toBe(false);
    });

    // Verify that error was logged
    expect(consoleErrorSpy).toHaveBeenCalledWith('Error al cargar impresoras:', mockError);

    // Verify that store remains in a valid state (empty printers array)
    const store = usePrinterStore.getState();
    expect(store.printers).toEqual([]);

    // Verify that empty state is displayed
    expect(screen.getByText('No hay impresoras en la base de datos')).toBeInTheDocument();

    // Restore console.error
    consoleErrorSpy.mockRestore();
  });

  // **Validates: Requirements 5.5**
  it('should set loading to false even when fetch fails', async () => {
    // Mock fetchPrinters to reject
    vi.mocked(printerService.fetchPrinters).mockRejectedValue(new Error('API error'));

    // Spy on console.error to suppress error output
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Render the component
    render(<ProvisioningPanel />);

    // Wait for loading state to transition to false
    await waitFor(() => {
      const store = usePrinterStore.getState();
      expect(store.isLoading).toBe(false);
    });

    // Verify that loading indicator is not shown
    expect(screen.queryByText('Cargando impresoras...')).not.toBeInTheDocument();

    // Restore console.error
    consoleErrorSpy.mockRestore();
  });
});
