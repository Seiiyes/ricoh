/**
 * Printer Capabilities Types
 * 
 * Types for printer capabilities detection and column visibility configuration
 */

/**
 * Printer capabilities detected automatically or configured manually
 */
export interface PrinterCapabilities {
  /** Counter format: 'estandar' (18+ cols), 'simplificado' (13 cols), 'ecologico' */
  formato_contadores: 'estandar' | 'simplificado' | 'ecologico';
  
  /** Supports color printing */
  has_color: boolean;
  
  /** Supports duplex printing (2-sided) */
  has_hojas_2_caras: boolean;
  
  /** Supports multiple pages per sheet */
  has_paginas_combinadas: boolean;
  
  /** Supports single color printing */
  has_mono_color: boolean;
  
  /** Supports two-color printing */
  has_dos_colores: boolean;
  
  /** ISO 8601 timestamp of when capabilities were detected */
  detected_at: string;
  
  /** Whether capabilities were manually configured (prevents auto-detection override) */
  manual_override: boolean;
}

/**
 * Column visibility configuration based on printer capabilities
 */
export interface ColumnVisibilityConfig {
  /** Show color-related columns */
  showColor: boolean;
  
  /** Show duplex (2-sided) columns */
  showHojas2Caras: boolean;
  
  /** Show combined pages columns */
  showPaginasCombinadas: boolean;
  
  /** Show single color columns */
  showMonoColor: boolean;
  
  /** Show two-color columns */
  showDosColores: boolean;
}

/**
 * Column group for organizing related columns
 */
export type ColumnGroup = 
  | 'color' 
  | 'hojas_2_caras' 
  | 'paginas_combinadas' 
  | 'mono_color' 
  | 'dos_colores'
  | 'basic';

/**
 * Column definition with visibility group
 */
export interface ColumnDefinition {
  /** Column key/identifier */
  key: string;
  
  /** Display label */
  label: string;
  
  /** Column group for visibility control */
  group: ColumnGroup;
  
  /** Whether column is always visible (regardless of capabilities) */
  alwaysVisible?: boolean;
}

/**
 * Printer with capabilities
 */
export interface Printer {
  id: number;
  hostname: string;
  ip_address: string;
  location?: string;
  empresa?: string;
  status: string;
  detected_model?: string;
  serial_number?: string;
  has_color: boolean;
  has_scanner: boolean;
  has_fax: boolean;
  toner_cyan: number;
  toner_magenta: number;
  toner_yellow: number;
  toner_black: number;
  last_seen?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
  
  /** Printer capabilities (may be undefined for printers without detection) */
  capabilities?: PrinterCapabilities;
}

/**
 * Default capabilities (show all columns for backward compatibility)
 */
export const DEFAULT_CAPABILITIES: PrinterCapabilities = {
  formato_contadores: 'estandar',
  has_color: true,
  has_hojas_2_caras: true,
  has_paginas_combinadas: true,
  has_mono_color: true,
  has_dos_colores: true,
  detected_at: new Date().toISOString(),
  manual_override: false,
};

/**
 * Calculate column visibility from printer capabilities
 */
export function calculateColumnVisibility(
  capabilities?: PrinterCapabilities
): ColumnVisibilityConfig {
  // Use default capabilities if none provided (backward compatibility)
  const caps = capabilities || DEFAULT_CAPABILITIES;
  
  return {
    showColor: caps.has_color,
    showHojas2Caras: caps.has_hojas_2_caras,
    showPaginasCombinadas: caps.has_paginas_combinadas,
    showMonoColor: caps.has_mono_color,
    showDosColores: caps.has_dos_colores,
  };
}

/**
 * Check if a column should be visible based on its group and capabilities
 */
export function shouldShowColumn(
  group: ColumnGroup,
  visibility: ColumnVisibilityConfig
): boolean {
  switch (group) {
    case 'color':
      return visibility.showColor;
    case 'hojas_2_caras':
      return visibility.showHojas2Caras;
    case 'paginas_combinadas':
      return visibility.showPaginasCombinadas;
    case 'mono_color':
      return visibility.showMonoColor;
    case 'dos_colores':
      return visibility.showDosColores;
    case 'basic':
      return true; // Basic columns always visible
    default:
      return true;
  }
}

/**
 * Check if a group header should be shown (at least one column in group is visible)
 */
export function shouldShowGroupHeader(
  group: ColumnGroup,
  visibility: ColumnVisibilityConfig
): boolean {
  return shouldShowColumn(group, visibility);
}
