import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/apiClient';

/** Respuesta de GET /api/v1/dashboard/kpis (función get_dashboard_kpis) */
export interface DashboardKPIs {
  total_equipos: number;
  equipos_online: number;
  equipos_offline: number;
  usuarios_provisionados: number;
  cierres_pendientes: number;
}

export interface TopImpresoraMes {
  printer_id: number;
  hostname: string;
  modelo: string;
  ubicacion: string | null;
  total_paginas: number;
}

/** Usuarios Ricoh con mayor suma de consumo_total en cierres del mes (GET .../top-usuarios-consumo) */
export interface TopUsuarioConsumoMes {
  user_id: number;
  nombre: string;
  codigo_usuario: string;
  total_consumo_paginas: number;
  cierres_count: number;
}

export interface ActividadAuditoria {
  id: string;
  fecha: string;
  tipo: string;
  descripcion: string;
  usuario: string;
  status: string;
}

const queryDefaults = {
  retry: 1,
  refetchOnWindowFocus: true,
} as const;

export const useDashboardKPIs = () => {
  return useQuery({
    queryKey: ['dashboard', 'kpis'],
    queryFn: async () => {
      const { data } = await apiClient.get<DashboardKPIs>('/api/v1/dashboard/kpis');
      return data;
    },
    staleTime: 5 * 60 * 1000,
    ...queryDefaults,
  });
};

export const useTopImpresoras = (limit: number = 5) => {
  return useQuery({
    queryKey: ['dashboard', 'top-impresoras', limit],
    queryFn: async () => {
      const { data } = await apiClient.get<TopImpresoraMes[]>(
        `/api/v1/dashboard/top-impresoras?limit=${limit}`
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
    ...queryDefaults,
  });
};

export const useActividadReciente = (limit: number = 6) => {
  return useQuery({
    queryKey: ['dashboard', 'actividad-reciente', limit],
    queryFn: async () => {
      const { data } = await apiClient.get<ActividadAuditoria[]>(
        `/api/v1/dashboard/actividad-reciente?limit=${limit}`
      );
      return data;
    },
    staleTime: 1 * 60 * 1000,
    ...queryDefaults,
  });
};

export const useTopUsuariosConsumo = (limit: number = 5) => {
  return useQuery({
    queryKey: ['dashboard', 'top-usuarios-consumo', limit],
    queryFn: async () => {
      const { data } = await apiClient.get<TopUsuarioConsumoMes[]>(
        `/api/v1/dashboard/top-usuarios-consumo?limit=${limit}`
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
    ...queryDefaults,
  });
};

export interface ConsumoResumen {
  total_paginas: number;
  copiadora: number;
  impresora: number;
  escaner: number;
  fax: number;
  mes_nombre: string;
}

export interface TonerAlerta {
  printer_id: number;
  hostname: string;
  modelo: string;
  ubicacion: string;
  is_color: boolean;
  toner_black: number;
  toner_cyan: number;
  toner_magenta: number;
  toner_yellow: number;
  alerta: boolean;
  alerta_mensaje: string;
}

export const useConsumoResumen = () => {
  return useQuery({
    queryKey: ['dashboard', 'consumo-resumen'],
    queryFn: async () => {
      const { data } = await apiClient.get<ConsumoResumen>('/api/v1/dashboard/consumo-resumen');
      return data;
    },
    staleTime: 5 * 60 * 1000,
    ...queryDefaults,
  });
};

export const useTonerAlertas = () => {
  return useQuery({
    queryKey: ['dashboard', 'toner-alertas'],
    queryFn: async () => {
      const { data } = await apiClient.get<TonerAlerta[]>('/api/v1/dashboard/toner-alertas');
      return data;
    },
    staleTime: 1 * 60 * 1000,
    ...queryDefaults,
  });
};

/** Un punto de datos de evolución de consumo mensual (GET /api/v1/analytics/evolution) */
export interface EvolutionItem {
  name: string;      // Nombre del mes (ej: "Enero")
  paginas: number;   // Total de páginas consumidas
  anio: number;      // Año del dato
  mes: number;       // Número del mes (1-12)
}

export const useEvolutionData = (meses: number = 6) => {
  return useQuery({
    queryKey: ['analytics', 'evolution', meses],
    queryFn: async () => {
      const { data } = await apiClient.get<EvolutionItem[]>(
        `/api/v1/analytics/evolution?meses=${meses}`
      );
      return data;
    },
    staleTime: 60 * 60 * 1000, // 1 hora (igual que TTL del backend con Redis)
    ...queryDefaults,
  });
};
