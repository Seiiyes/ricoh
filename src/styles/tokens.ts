/**
 * Design Tokens - Sistema de diseño unificado
 * Estos tokens garantizan consistencia visual en toda la aplicación
 */

export const colors = {
  // Colores de marca
  brand: {
    primary: '#E30613',      // Ricoh Red
    secondary: '#1F2937',    // Industrial Gray
  },
  
  // Colores semánticos
  semantic: {
    success: '#10B981',      // Verde
    warning: '#F59E0B',      // Amarillo
    error: '#EF4444',        // Rojo
    info: '#3B82F6',         // Azul
  },
  
  // Escala de grises
  neutral: {
    50: '#F8FAFC',
    100: '#F1F5F9',
    200: '#E2E8F0',
    300: '#CBD5E1',
    400: '#94A3B8',
    500: '#64748B',
    600: '#475569',
    700: '#334155',
    800: '#1E293B',
    900: '#0F172A',
  },
};

export const spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
};

export const borderRadius = {
  none: '0',
  sm: '0.125rem',  // 2px
  md: '0.375rem',  // 6px
  lg: '0.5rem',    // 8px
  xl: '0.75rem',   // 12px
  full: '9999px',
};

export const typography = {
  // Headings
  h1: 'text-2xl font-bold',
  h2: 'text-xl font-bold',
  h3: 'text-lg font-bold',
  h4: 'text-base font-bold',
  
  // Body
  body: 'text-sm',
  bodyLarge: 'text-base',
  bodySmall: 'text-xs',
  
  // Special
  caption: 'text-xs text-gray-500',
  label: 'text-xs font-bold uppercase text-gray-600',
  code: 'font-mono text-sm',
};

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
};

export const transitions = {
  fast: '150ms ease-in-out',
  normal: '200ms ease-in-out',
  slow: '300ms ease-in-out',
};
