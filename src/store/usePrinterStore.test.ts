import { describe, it, expect, beforeEach } from 'vitest';
import * as fc from 'fast-check';
import { usePrinterStore } from './usePrinterStore';
import type { PrinterDevice } from '@/types';

// Arbitrary generator for PrinterDevice
const printerDeviceArbitrary = fc.record({
  id: fc.string({ minLength: 1 }),
  hostname: fc.string({ minLength: 1 }),
  ip_address: fc.ipV4(),
  status: fc.constantFrom('online' as const, 'offline' as const),
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
});

describe('usePrinterStore - Unit Tests', () => {
  beforeEach(() => {
    // Reset store state before each test
    const store = usePrinterStore.getState();
    store.clearPrinters();
    store.setLoading(false);
    store.clearSelection();
  });

  // **Validates: Requirements 7.5**
  it('should toggle printer selection when printer ID comes from store', () => {
    const store = usePrinterStore.getState();
    
    // Set up printers in the store
    const testPrinters: PrinterDevice[] = [
      {
        id: 'printer-1',
        hostname: 'RICOH-MP-C3004',
        ip_address: '192.168.1.100',
        status: 'online',
        toner_levels: { cyan: 75, magenta: 60, yellow: 85, black: 90 },
        capabilities: { color: true, scanner: true },
      },
      {
        id: 'printer-2',
        hostname: 'RICOH-SP-4510DN',
        ip_address: '192.168.1.101',
        status: 'offline',
        toner_levels: { cyan: 0, magenta: 0, yellow: 0, black: 45 },
        capabilities: { color: false, scanner: false },
      },
    ];
    
    store.setPrinters(testPrinters);
    
    // Verify printers are in the store
    expect(usePrinterStore.getState().printers).toEqual(testPrinters);
    
    // Initially, no printers should be selected
    expect(usePrinterStore.getState().selectedPrinters).toEqual([]);
    
    // Toggle first printer - should add it to selection
    store.togglePrinter('printer-1');
    expect(usePrinterStore.getState().selectedPrinters).toEqual(['printer-1']);
    
    // Toggle second printer - should add it to selection
    store.togglePrinter('printer-2');
    expect(usePrinterStore.getState().selectedPrinters).toEqual(['printer-1', 'printer-2']);
    
    // Toggle first printer again - should remove it from selection
    store.togglePrinter('printer-1');
    expect(usePrinterStore.getState().selectedPrinters).toEqual(['printer-2']);
    
    // Toggle second printer again - should remove it from selection
    store.togglePrinter('printer-2');
    expect(usePrinterStore.getState().selectedPrinters).toEqual([]);
  });

  // **Validates: Requirements 7.5**
  it('should persist selected state correctly across multiple operations', () => {
    const store = usePrinterStore.getState();
    
    // Set up printers in the store
    const testPrinters: PrinterDevice[] = [
      {
        id: 'printer-a',
        hostname: 'Printer-A',
        ip_address: '10.0.0.1',
        status: 'online',
        toner_levels: { cyan: 100, magenta: 100, yellow: 100, black: 100 },
        capabilities: { color: true, scanner: true },
      },
      {
        id: 'printer-b',
        hostname: 'Printer-B',
        ip_address: '10.0.0.2',
        status: 'online',
        toner_levels: { cyan: 50, magenta: 50, yellow: 50, black: 50 },
        capabilities: { color: true, scanner: false },
      },
      {
        id: 'printer-c',
        hostname: 'Printer-C',
        ip_address: '10.0.0.3',
        status: 'offline',
        toner_levels: { cyan: 25, magenta: 25, yellow: 25, black: 25 },
        capabilities: { color: false, scanner: false },
      },
    ];
    
    store.setPrinters(testPrinters);
    
    // Select multiple printers
    store.togglePrinter('printer-a');
    store.togglePrinter('printer-b');
    store.togglePrinter('printer-c');
    
    // Verify all are selected
    expect(usePrinterStore.getState().selectedPrinters).toEqual(['printer-a', 'printer-b', 'printer-c']);
    
    // Deselect one in the middle
    store.togglePrinter('printer-b');
    expect(usePrinterStore.getState().selectedPrinters).toEqual(['printer-a', 'printer-c']);
    
    // Re-select it
    store.togglePrinter('printer-b');
    expect(usePrinterStore.getState().selectedPrinters).toEqual(['printer-a', 'printer-c', 'printer-b']);
    
    // Verify printers data is still intact
    expect(usePrinterStore.getState().printers).toEqual(testPrinters);
  });

  // **Validates: Requirements 7.5**
  it('should handle toggling non-existent printer ID gracefully', () => {
    const store = usePrinterStore.getState();
    
    // Set up printers in the store
    const testPrinters: PrinterDevice[] = [
      {
        id: 'printer-1',
        hostname: 'Test-Printer',
        ip_address: '192.168.1.1',
        status: 'online',
        toner_levels: { cyan: 80, magenta: 80, yellow: 80, black: 80 },
        capabilities: { color: true, scanner: true },
      },
    ];
    
    store.setPrinters(testPrinters);
    
    // Toggle a printer ID that doesn't exist in the store
    // This should not throw an error, just add it to selection
    store.togglePrinter('non-existent-printer');
    
    // The selection should include the non-existent ID
    // (The store doesn't validate IDs against the printers array)
    expect(usePrinterStore.getState().selectedPrinters).toEqual(['non-existent-printer']);
    
    // Toggle it again to remove it
    store.togglePrinter('non-existent-printer');
    expect(usePrinterStore.getState().selectedPrinters).toEqual([]);
  });
});

describe('usePrinterStore - Property-Based Tests', () => {
  beforeEach(() => {
    // Reset store state before each test
    const store = usePrinterStore.getState();
    store.clearPrinters();
    store.setLoading(false);
    store.clearSelection();
  });

  // Feature: remove-static-data, Property 1: Store printer data round-trip
  // **Validates: Requirements 2.2, 2.3**
  it('Property 1: Store Printer Data Round-Trip - setPrinters and printers maintain data integrity', () => {
    fc.assert(
      fc.property(
        fc.array(printerDeviceArbitrary),
        (printers: PrinterDevice[]) => {
          const store = usePrinterStore.getState();
          
          // Set the printers in the store
          store.setPrinters(printers);
          
          // Retrieve the printers from the store
          const retrievedPrinters = usePrinterStore.getState().printers;
          
          // Assert that the retrieved printers match the original printers
          expect(retrievedPrinters).toEqual(printers);
          expect(retrievedPrinters.length).toBe(printers.length);
          
          // Verify each printer's data is intact
          printers.forEach((printer, index) => {
            expect(retrievedPrinters[index].id).toBe(printer.id);
            expect(retrievedPrinters[index].hostname).toBe(printer.hostname);
            expect(retrievedPrinters[index].ip_address).toBe(printer.ip_address);
            expect(retrievedPrinters[index].status).toBe(printer.status);
            expect(retrievedPrinters[index].toner_levels).toEqual(printer.toner_levels);
            expect(retrievedPrinters[index].capabilities).toEqual(printer.capabilities);
          });
        }
      ),
      { numRuns: 100 }
    );
  });

  // Feature: remove-static-data, Property 2: Clear Printers Results in Empty State
  // **Validates: Requirements 2.4**
  it('Property 2: Clear Printers Results in Empty State - clearPrinters always results in empty array', () => {
    fc.assert(
      fc.property(
        fc.array(printerDeviceArbitrary),
        (printers: PrinterDevice[]) => {
          const store = usePrinterStore.getState();
          
          // Set any initial printer collection in the store
          store.setPrinters(printers);
          
          // Verify printers were set (if array was non-empty)
          if (printers.length > 0) {
            expect(usePrinterStore.getState().printers.length).toBeGreaterThan(0);
          }
          
          // Call clearPrinters
          store.clearPrinters();
          
          // Assert that the printers array is now empty
          const clearedPrinters = usePrinterStore.getState().printers;
          expect(clearedPrinters).toEqual([]);
          expect(clearedPrinters.length).toBe(0);
        }
      ),
      { numRuns: 100 }
    );
  });

  // Feature: remove-static-data, Property 3: Loading State Updates Correctly
  // **Validates: Requirements 3.2**
  it('Property 3: Loading State Updates Correctly - setLoading updates isLoading state to match provided value', () => {
    fc.assert(
      fc.property(
        fc.boolean(),
        (loadingValue: boolean) => {
          const store = usePrinterStore.getState();
          
          // Call setLoading with the boolean value
          store.setLoading(loadingValue);
          
          // Assert that isLoading state matches the provided value
          const currentLoadingState = usePrinterStore.getState().isLoading;
          expect(currentLoadingState).toBe(loadingValue);
        }
      ),
      { numRuns: 100 }
    );
  });

  // Feature: remove-static-data, Property 5: Printer Selection Works With Dynamic Data
  // **Validates: Requirements 7.5**
  it('Property 5: Printer Selection Works With Dynamic Data - togglePrinter correctly adds/removes printer IDs', () => {
    fc.assert(
      fc.property(
        fc.array(printerDeviceArbitrary, { minLength: 1 }),
        fc.integer({ min: 0, max: 100 }),
        (printers: PrinterDevice[], randomIndex: number) => {
          const store = usePrinterStore.getState();
          
          // Reset state for this test iteration
          store.clearSelection();
          store.setPrinters(printers);
          
          // Select a printer ID from the current collection
          const printerIndex = randomIndex % printers.length;
          const printerId = printers[printerIndex].id;
          
          // Initially, the printer should not be selected
          const initialSelection = usePrinterStore.getState().selectedPrinters;
          const wasInitiallySelected = initialSelection.includes(printerId);
          
          // Toggle the printer
          store.togglePrinter(printerId);
          
          // Get the updated selection
          const afterFirstToggle = usePrinterStore.getState().selectedPrinters;
          
          // If it wasn't selected, it should now be selected
          // If it was selected, it should now be deselected
          if (!wasInitiallySelected) {
            expect(afterFirstToggle).toContain(printerId);
          } else {
            expect(afterFirstToggle).not.toContain(printerId);
          }
          
          // Toggle again to verify the opposite behavior
          store.togglePrinter(printerId);
          const afterSecondToggle = usePrinterStore.getState().selectedPrinters;
          
          // After toggling twice, we should be back to the initial state
          if (!wasInitiallySelected) {
            expect(afterSecondToggle).not.toContain(printerId);
          } else {
            expect(afterSecondToggle).toContain(printerId);
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
