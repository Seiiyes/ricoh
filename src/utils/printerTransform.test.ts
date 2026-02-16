import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { printerDeviceToCardProps } from './printerTransform';
import type { PrinterDevice } from '@/types';

// Arbitrary generator for valid PrinterDevice
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

describe('printerTransform', () => {
  describe('printerDeviceToCardProps with missing fields', () => {
    it('provides default "offline" status when status is missing', () => {
      const deviceWithoutStatus = {
        id: 'printer-1',
        hostname: 'Test Printer',
        ip_address: '192.168.1.100',
        toner_levels: { cyan: 50, magenta: 60, yellow: 70, black: 80 },
      };

      const result = printerDeviceToCardProps(deviceWithoutStatus);

      expect(result.status).toBe('offline');
      expect(result.id).toBe('printer-1');
      expect(result.name).toBe('Test Printer');
      expect(result.ip).toBe('192.168.1.100');
    });

    it('provides default zero toner levels when toner_levels is missing', () => {
      const deviceWithoutToner = {
        id: 'printer-2',
        hostname: 'Test Printer 2',
        ip_address: '192.168.1.101',
        status: 'online' as const,
      };

      const result = printerDeviceToCardProps(deviceWithoutToner);

      expect(result.toner).toEqual({
        c: 0,
        m: 0,
        y: 0,
        k: 0,
      });
      expect(result.status).toBe('online');
    });

    it('provides defaults for both missing status and toner_levels', () => {
      const minimalDevice = {
        id: 'printer-3',
        hostname: 'Minimal Printer',
        ip_address: '192.168.1.102',
      };

      const result = printerDeviceToCardProps(minimalDevice);

      expect(result.status).toBe('offline');
      expect(result.toner).toEqual({
        c: 0,
        m: 0,
        y: 0,
        k: 0,
      });
    });

    it('uses provided values when all fields are present', () => {
      const completeDevice = {
        id: 'printer-4',
        hostname: 'Complete Printer',
        ip_address: '192.168.1.103',
        status: 'online' as const,
        toner_levels: { cyan: 90, magenta: 85, yellow: 80, black: 75 },
        capabilities: { color: true, scanner: true },
      };

      const result = printerDeviceToCardProps(completeDevice);

      expect(result.status).toBe('online');
      expect(result.toner).toEqual({
        c: 90,
        m: 85,
        y: 80,
        k: 75,
      });
    });
  });

  // Feature: remove-static-data, Property: Transformation preserves fields
  // **Validates: Requirements 6.3**
  describe('Property-Based Tests', () => {
    it('Property: Transformation preserves all valid PrinterDevice fields', () => {
      fc.assert(
        fc.property(
          printerDeviceArbitrary,
          (device: PrinterDevice) => {
            // Transform the device
            const result = printerDeviceToCardProps(device);
            
            // Assert that all fields are preserved correctly
            expect(result.id).toBe(device.id);
            expect(result.name).toBe(device.hostname);
            expect(result.ip).toBe(device.ip_address);
            expect(result.status).toBe(device.status);
            
            // Assert that toner levels are correctly mapped
            expect(result.toner.c).toBe(device.toner_levels.cyan);
            expect(result.toner.m).toBe(device.toner_levels.magenta);
            expect(result.toner.y).toBe(device.toner_levels.yellow);
            expect(result.toner.k).toBe(device.toner_levels.black);
          }
        ),
        { numRuns: 100 }
      );
    });
  });
});
