/// <reference types="@testing-library/jest-dom/vitest" />
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import * as fc from 'fast-check';
import { PrinterCard } from './PrinterCard';
import { printerDeviceToCardProps } from '@/utils/printerTransform';
import { usePrinterStore } from '@/store/usePrinterStore';
import type { PrinterDevice } from '@/types';

describe('PrinterCard - Unit Tests', () => {
  beforeEach(() => {
    // Reset store state before each test
    const store = usePrinterStore.getState();
    store.clearPrinters();
    store.setLoading(false);
  });

  // **Validates: Requirements 7.1**
  it('should render all required fields from transformed data', () => {
    // Create a sample PrinterDevice
    const printerDevice: PrinterDevice = {
      id: 'printer-1',
      hostname: 'RICOH-MP-C3004',
      ip_address: '192.168.1.100',
      status: 'online',
      toner_levels: {
        cyan: 75,
        magenta: 60,
        yellow: 85,
        black: 90,
      },
      capabilities: {
        color: true,
        scanner: true,
      },
    };

    // Transform the device to card props
    const cardProps = printerDeviceToCardProps(printerDevice);

    // Render the PrinterCard with transformed props
    render(<PrinterCard {...cardProps} />);

    // Assert that printer name (hostname) is displayed
    expect(screen.getByText('RICOH-MP-C3004')).toBeInTheDocument();

    // Assert that IP address is displayed
    expect(screen.getByText('192.168.1.100')).toBeInTheDocument();

    // Assert that status indicator is present (online status shows as pulsing dot)
    const statusIndicator = screen.getByText('RICOH-MP-C3004')
      .closest('div')
      ?.parentElement
      ?.querySelector('.bg-success');
    expect(statusIndicator).toBeInTheDocument();

    // Assert that toner levels are rendered (minimum toner level should be displayed)
    expect(screen.getByText('60% min')).toBeInTheDocument();
  });

  // **Validates: Requirements 7.1**
  it('should handle offline status correctly', () => {
    const printerDevice: PrinterDevice = {
      id: 'printer-2',
      hostname: 'RICOH-SP-4510DN',
      ip_address: '192.168.1.101',
      status: 'offline',
      toner_levels: {
        cyan: 0,
        magenta: 0,
        yellow: 0,
        black: 45,
      },
      capabilities: {
        color: false,
        scanner: false,
      },
    };

    const cardProps = printerDeviceToCardProps(printerDevice);
    render(<PrinterCard {...cardProps} />);

    // Assert that printer name is displayed
    expect(screen.getByText('RICOH-SP-4510DN')).toBeInTheDocument();

    // Assert that offline status indicator is present (gray dot)
    const statusIndicator = screen.getByText('RICOH-SP-4510DN')
      .closest('div')
      ?.parentElement
      ?.querySelector('.bg-slate-300');
    expect(statusIndicator).toBeInTheDocument();
  });

  // **Validates: Requirements 7.1**
  it('should work with empty printers array from store', () => {
    // Ensure store has empty printers array
    const store = usePrinterStore.getState();
    store.clearPrinters();

    // Verify store is empty
    expect(store.printers).toEqual([]);

    // This test verifies that the component can handle the case where
    // no printers are available from the store. The actual rendering
    // of empty state is handled by ProvisioningPanel, but PrinterCard
    // should be able to work with any valid transformed data when printers
    // are eventually added to the store.

    // Create a minimal printer device
    const printerDevice: PrinterDevice = {
      id: 'printer-3',
      hostname: 'Test-Printer',
      ip_address: '10.0.0.1',
      status: 'online',
      toner_levels: {
        cyan: 100,
        magenta: 100,
        yellow: 100,
        black: 100,
      },
      capabilities: {
        color: true,
        scanner: true,
      },
    };

    const cardProps = printerDeviceToCardProps(printerDevice);
    render(<PrinterCard {...cardProps} />);

    // Assert that the card renders correctly even when store is empty
    expect(screen.getByText('Test-Printer')).toBeInTheDocument();
    expect(screen.getByText('10.0.0.1')).toBeInTheDocument();
  });

  // **Validates: Requirements 7.1**
  it('should handle transformation with missing optional fields', () => {
    // Create a printer device with missing optional fields
    const partialDevice = {
      id: 'printer-4',
      hostname: 'Partial-Printer',
      ip_address: '172.16.0.1',
      // status is missing - should default to 'offline'
      // toner_levels is missing - should default to all zeros
    };

    const cardProps = printerDeviceToCardProps(partialDevice);
    render(<PrinterCard {...cardProps} />);

    // Assert that printer renders with defaults
    expect(screen.getByText('Partial-Printer')).toBeInTheDocument();
    expect(screen.getByText('172.16.0.1')).toBeInTheDocument();

    // Assert that offline status is used as default
    const statusIndicator = screen.getByText('Partial-Printer')
      .closest('div')
      ?.parentElement
      ?.querySelector('.bg-slate-300');
    expect(statusIndicator).toBeInTheDocument();

    // Assert that minimum toner level is 0% (all defaults to 0)
    expect(screen.getByText('0% min')).toBeInTheDocument();
  });
});

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

describe('PrinterCard - Property-Based Tests', () => {
  beforeEach(() => {
    // Reset store state before each test
    const store = usePrinterStore.getState();
    store.clearPrinters();
    store.setLoading(false);
  });

  // Feature: remove-static-data, Property 4: PrinterCard Renders All Required Fields
  // **Validates: Requirements 7.1**
  it('Property 4: PrinterCard Renders All Required Fields - renders name, IP, status, and all toner levels', () => {
    fc.assert(
      fc.property(
        printerDeviceArbitrary,
        (printerDevice: PrinterDevice) => {
          // Transform the device to card props
          const cardProps = printerDeviceToCardProps(printerDevice);

          // Render the PrinterCard with transformed props
          const { container } = render(<PrinterCard {...cardProps} />);

          // Assert that printer name (hostname) is rendered
          // Use a flexible matcher that handles whitespace normalization
          const hostnameElement = container.querySelector('.text-xs.font-bold.text-industrial-gray');
          expect(hostnameElement).toBeInTheDocument();
          expect(hostnameElement?.textContent).toBe(printerDevice.hostname);

          // Assert that IP address is rendered
          const ipElement = container.querySelector('.text-\\[10px\\].text-slate-500.font-mono');
          expect(ipElement).toBeInTheDocument();
          expect(ipElement?.textContent).toBe(printerDevice.ip_address);

          // Assert that status indicator is present
          // Online status shows as .bg-success, offline shows as .bg-slate-300
          const expectedStatusClass = printerDevice.status === 'online' ? 'bg-success' : 'bg-slate-300';
          const statusIndicator = container.querySelector(`.${expectedStatusClass}`);
          expect(statusIndicator).toBeInTheDocument();

          // Assert that all four toner levels are rendered
          // The component displays the minimum toner level as "X% min"
          const minTonerLevel = Math.min(
            printerDevice.toner_levels.cyan,
            printerDevice.toner_levels.magenta,
            printerDevice.toner_levels.yellow,
            printerDevice.toner_levels.black
          );
          
          // Find the toner level display using a flexible text matcher
          const tonerDisplay = Array.from(container.querySelectorAll('span')).find(
            el => el.textContent?.includes('% min')
          );
          expect(tonerDisplay).toBeInTheDocument();
          expect(tonerDisplay?.textContent).toBe(`${minTonerLevel}% min`);

          // Verify that the toner visualization elements exist
          // The component renders 4 toner bars (cyan, magenta, yellow, black)
          const cyanBar = container.querySelector('.bg-cyan-400');
          const magentaBar = container.querySelector('.bg-magenta-400');
          const yellowBar = container.querySelector('.bg-yellow-400');
          const blackBar = container.querySelector('.bg-slate-900');
          
          expect(cyanBar).toBeInTheDocument();
          expect(magentaBar).toBeInTheDocument();
          expect(yellowBar).toBeInTheDocument();
          expect(blackBar).toBeInTheDocument();
        }
      ),
      { numRuns: 100 }
    );
  });
});
