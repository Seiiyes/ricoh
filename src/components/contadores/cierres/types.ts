/**
 * Types for the unified close system
 */

export interface CierreMensual {
  id: number;
  printer_id: number;
  tipo_periodo: 'diario' | 'semanal' | 'mensual' | 'personalizado';
  fecha_inicio: string; // ISO date
  fecha_fin: string; // ISO date
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
  fecha_cierre: string; // ISO datetime
  cerrado_por: string | null;
  notas: string | null;
  hash_verificacion: string | null;
  created_at: string; // ISO datetime
}

export interface CierreMensualUsuario {
  id: number;
  cierre_mensual_id: number;
  codigo_usuario: string;
  nombre_usuario: string;
  total_paginas: number;
  total_bn: number;
  total_color: number;
  copiadora_bn: number;
  copiadora_color: number;
  impresora_bn: number;
  impresora_color: number;
  escaner_bn: number;
  escaner_color: number;
  fax_bn: number;
  consumo_total: number;
  consumo_copiadora: number;
  consumo_impresora: number;
  consumo_escaner: number;
  consumo_fax: number;
  created_at: string; // ISO datetime
}

export interface CierreMensualDetalle extends CierreMensual {
  usuarios: CierreMensualUsuario[];
}

export interface UsuarioComparacion {
  codigo_usuario: string;
  nombre_usuario: string;
  consumo_cierre1: number;
  consumo_cierre2: number;
  diferencia: number;
  porcentaje_cambio: number;
}

export interface ComparacionCierres {
  cierre1: CierreMensual;
  cierre2: CierreMensual;
  diferencia_total: number;
  diferencia_copiadora: number;
  diferencia_impresora: number;
  diferencia_escaner: number;
  diferencia_fax: number;
  dias_entre_cierres: number;
  top_usuarios_aumento: UsuarioComparacion[];
  top_usuarios_disminucion: UsuarioComparacion[];
  total_usuarios_activos: number;
  promedio_consumo_por_usuario: number;
}

export interface CierreRequest {
  printer_id: number;
  tipo_periodo: 'diario' | 'semanal' | 'mensual' | 'personalizado';
  fecha_inicio: string; // ISO date
  fecha_fin: string; // ISO date
  cerrado_por?: string;
  notas?: string;
}

export interface Printer {
  id: number;
  hostname: string;
  ip_address: string;
  location: string | null;
  empresa: string | null;
  status: string;
}

export type TipoPeriodo = 'diario' | 'semanal' | 'mensual' | 'personalizado';

export enum EstadoCierre {
  CERRADO = 'cerrado',
  PENDIENTE = 'pendiente',
  FUTURO = 'futuro',
  FALTA = 'falta'
}
