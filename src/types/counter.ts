/**
 * Counter Type Definitions
 * 
 * TypeScript interfaces for counter data models matching backend API responses.
 */

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
  copiadora_hojas_2_caras: number;
  copiadora_paginas_combinadas: number;
  impresora_bn: number;
  impresora_mono_color: number;
  impresora_dos_colores: number;
  impresora_color: number;
  impresora_hojas_2_caras: number;
  impresora_paginas_combinadas: number;
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
 * Monthly close record
 */
export interface MonthlyClose {
  id: number;
  printer_id: number;
  anio: number;
  mes: number;
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
  fecha_cierre: string; // ISO 8601
  cerrado_por: string | null;
  notas: string | null;
  created_at: string; // ISO 8601
}

/**
 * Request to perform monthly close
 */
export interface MonthlyCloseRequest {
  printer_id: number;
  anio: number;
  mes: number;
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
