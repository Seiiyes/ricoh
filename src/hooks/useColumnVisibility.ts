/**
 * useColumnVisibility Hook
 * 
 * Hook for managing column visibility based on printer capabilities
 */

import { useMemo } from 'react';
import type { 
  PrinterCapabilities, 
  ColumnVisibilityConfig,
  ColumnGroup 
} from '../types/printer';
import { 
  calculateColumnVisibility, 
  shouldShowColumn,
  shouldShowGroupHeader,
  DEFAULT_CAPABILITIES 
} from '../types/printer';

/**
 * Hook return type
 */
export interface UseColumnVisibilityReturn {
  /** Column visibility configuration */
  visibility: ColumnVisibilityConfig;
  
  /** Check if a column should be visible */
  isColumnVisible: (group: ColumnGroup) => boolean;
  
  /** Check if a group header should be visible */
  isGroupHeaderVisible: (group: ColumnGroup) => boolean;
  
  /** Whether capabilities are loaded */
  hasCapabilities: boolean;
}

/**
 * Hook for managing column visibility based on printer capabilities
 * 
 * @param capabilities - Printer capabilities (undefined = show all for backward compatibility)
 * @returns Column visibility utilities
 * 
 * @example
 * ```tsx
 * function UserCounterTable({ printer }) {
 *   const { visibility, isColumnVisible } = useColumnVisibility(printer.capabilities);
 *   
 *   return (
 *     <table>
 *       <thead>
 *         <tr>
 *           <th>Usuario</th>
 *           {isColumnVisible('color') && <th>Color</th>}
 *           {isColumnVisible('hojas_2_caras') && <th>Dúplex</th>}
 *         </tr>
 *       </thead>
 *     </table>
 *   );
 * }
 * ```
 */
export function useColumnVisibility(
  capabilities?: PrinterCapabilities
): UseColumnVisibilityReturn {
  // Calculate visibility configuration
  const visibility = useMemo(() => {
    return calculateColumnVisibility(capabilities);
  }, [capabilities]);
  
  // Check if capabilities are loaded
  const hasCapabilities = capabilities !== undefined;
  
  // Memoized function to check column visibility
  const isColumnVisible = useMemo(() => {
    return (group: ColumnGroup) => shouldShowColumn(group, visibility);
  }, [visibility]);
  
  // Memoized function to check group header visibility
  const isGroupHeaderVisible = useMemo(() => {
    return (group: ColumnGroup) => shouldShowGroupHeader(group, visibility);
  }, [visibility]);
  
  return {
    visibility,
    isColumnVisible,
    isGroupHeaderVisible,
    hasCapabilities,
  };
}

/**
 * Hook variant that accepts a Printer object directly
 * 
 * @param printer - Printer object with capabilities
 * @returns Column visibility utilities
 * 
 * @example
 * ```tsx
 * function UserCounterTable({ printer }) {
 *   const { isColumnVisible } = useColumnVisibilityForPrinter(printer);
 *   
 *   return (
 *     <table>
 *       {isColumnVisible('color') && <th>Color</th>}
 *     </table>
 *   );
 * }
 * ```
 */
export function useColumnVisibilityForPrinter(
  printer?: { capabilities?: PrinterCapabilities }
): UseColumnVisibilityReturn {
  return useColumnVisibility(printer?.capabilities);
}

export default useColumnVisibility;
