import { fetchPrinters, fetchPrinterJobs } from './printerService';
import type { PrinterDevice } from '@/types';

describe('printerService', () => {
  describe('fetchPrinters', () => {
    it('should return an empty array', async () => {
      const result = await fetchPrinters();
      
      expect(result).toEqual([]);
      expect(result.length).toBe(0);
    });

    it('should return a value that matches PrinterDevice[] type', async () => {
      const result = await fetchPrinters();
      
      // Verify the result is an array
      expect(Array.isArray(result)).toBe(true);
      
      // Type assertion to verify TypeScript type compatibility
      const typedResult: PrinterDevice[] = result;
      expect(typedResult).toBeDefined();
    });
  });

  describe('fetchPrinterJobs', () => {
    it('should throw an error when not authenticated or invalid printer', async () => {
      await expect(fetchPrinterJobs(9999)).rejects.toThrow();
    });
  });
});

