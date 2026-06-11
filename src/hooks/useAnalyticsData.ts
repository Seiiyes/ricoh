import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../services/apiClient';

export const useEvolucionConsumo = (meses: number = 12) => {
  return useQuery({
    queryKey: ['analytics', 'evolution', meses],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/analytics/evolution?meses=${meses}`);
      return data;
    },
    staleTime: 60 * 60 * 1000, // 1 hora
  });
};

export const useComparativa = (
  fechaInicioA: string,
  fechaFinA: string,
  fechaInicioB: string,
  fechaFinB: string
) => {
  return useQuery({
    queryKey: ['analytics', 'comparison', fechaInicioA, fechaFinA, fechaInicioB, fechaFinB],
    queryFn: async () => {
      const { data } = await apiClient.get(
        `/api/v1/analytics/comparison?fecha_inicio_a=${fechaInicioA}&fecha_fin_a=${fechaFinA}&fecha_inicio_b=${fechaInicioB}&fecha_fin_b=${fechaFinB}`
      );
      return data;
    },
    staleTime: 60 * 60 * 1000, // 1 hora
    enabled: !!(fechaInicioA && fechaFinA && fechaInicioB && fechaFinB),
  });
};

export interface GlobalUserConsumptionFilter {
  page?: number;
  pageSize?: number;
  search?: string;
  printerId?: number;
  userId?: number;
  fechaInicio?: string;
  fechaFin?: string;
  centroCostos?: string;
}

export interface GlobalCierreUsuario {
  id: number;
  cierre_mensual_id: number;
  user_id: number;
  codigo_usuario: string;
  nombre_usuario: string;
  empresa_nombre?: string;
  consumo_bn?: number;
  consumo_color?: number;
  
  // Contadores al cierre
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
  
  // Consumo del mes
  consumo_total: number;
  consumo_copiadora: number;
  consumo_impresora: number;
  consumo_escaner: number;
  consumo_fax: number;
  
  created_at: string;
  printer_id: number;
  printer_hostname: string;
  printer_ip: string;
  printer_location: string;
  printer_serial?: string;
  fecha_inicio: string;
  fecha_fin: string;
  fecha_cierre: string;
  cerrado_por?: string;
  centro_costos?: string | null;
}

export interface PaginatedGlobalUserConsumption {
  items: GlobalCierreUsuario[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export const useGlobalUserConsumption = (filters: GlobalUserConsumptionFilter) => {
  return useQuery<PaginatedGlobalUserConsumption>({
    queryKey: ['analytics', 'global-user-consumption', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.pageSize) params.append('page_size', filters.pageSize.toString());
      if (filters.search) params.append('search', filters.search);
      if (filters.printerId) params.append('printer_id', filters.printerId.toString());
      if (filters.userId) params.append('user_id', filters.userId.toString());
      if (filters.fechaInicio) params.append('fecha_inicio', filters.fechaInicio);
      if (filters.fechaFin) params.append('fecha_fin', filters.fechaFin);
      if (filters.centroCostos) params.append('centro_costos', filters.centroCostos);

      const { data } = await apiClient.get(`/api/counters/monthly/users/all?${params.toString()}`);
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
    placeholderData: (prev) => prev,
  });
};

export const useUpdateUserConsumption = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({
      id,
      total_paginas,
      consumo_total,
    }: {
      id: number;
      total_paginas: number;
      consumo_total: number;
    }) => {
      const { data } = await apiClient.put(`/api/counters/monthly/users/${id}`, {
        total_paginas,
        consumo_total,
      });
      return data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['analytics', 'global-user-consumption'] });
      void queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
};

export interface TopUserFilter {
  fechaInicio: string;
  fechaFin: string;
  limit?: number;
  empresaId?: number;
}

export interface TopUserConsumption {
  user_id: number;
  nombre: string;
  codigo_usuario: string;
  centro_costos: string | null;
  total_consumo_paginas: number;
  total_copiadora: number;
  total_impresora: number;
  total_escaner: number;
  total_fax: number;
  cierres_count: number;
}

export const useTopUsers = (filters: TopUserFilter) => {
  return useQuery<TopUserConsumption[]>({
    queryKey: ['analytics', 'top-users', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append('fecha_inicio', filters.fechaInicio);
      params.append('fecha_fin', filters.fechaFin);
      if (filters.limit) params.append('limit', filters.limit.toString());
      if (filters.empresaId) params.append('empresa_id', filters.empresaId.toString());

      const { data } = await apiClient.get(`/api/v1/analytics/top-users?${params.toString()}`);
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
    enabled: !!(filters.fechaInicio && filters.fechaFin),
  });
};

export const useMonthlyCloses = () => {
  return useQuery<any[]>({
    queryKey: ['analytics', 'monthly-closes'],
    queryFn: async () => {
      const { data } = await apiClient.get('/api/counters/monthly');
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
};

