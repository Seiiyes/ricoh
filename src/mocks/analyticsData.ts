export const mockAnalyticsData = {
  kpis: {
    totalPaginas: 145230,
    promedioMes: 48410,
    costoEstimado: 2450.50,
    variacionAnterior: 5.2, // Porcentaje positivo
  },
  evolucionConsumo: [
    { name: 'Ene', paginas: 40000, periodoAnterior: 38000 },
    { name: 'Feb', paginas: 42000, periodoAnterior: 39500 },
    { name: 'Mar', paginas: 45000, periodoAnterior: 41000 },
    { name: 'Abr', paginas: 50000, periodoAnterior: 40000 },
    { name: 'May', paginas: 48000, periodoAnterior: 43000 },
    { name: 'Jun', paginas: 55000, periodoAnterior: 46000 },
    { name: 'Jul', paginas: 52000, periodoAnterior: 48000 },
    { name: 'Ago', paginas: 60000, periodoAnterior: 51000 },
    { name: 'Sep', paginas: 58000, periodoAnterior: 54000 },
    { name: 'Oct', paginas: 65000, periodoAnterior: 56000 },
    { name: 'Nov', paginas: 70000, periodoAnterior: 60000 },
    { name: 'Dic', paginas: 75000, periodoAnterior: 65000 },
  ],
  consumoPorFuncion: [
    { name: 'Impresora', value: 85000 },
    { name: 'Copiadora', value: 45000 },
    { name: 'Escáner', value: 12000 },
    { name: 'Fax', value: 3230 },
  ],
  topEquipos: [
    { name: 'IM C6010 (Ventas)', paginas: 25000 },
    { name: 'Pro C5300s (Diseño)', paginas: 20000 },
    { name: 'IM 430F (Recepción)', paginas: 15000 },
    { name: 'P 502 (Logística)', paginas: 12000 },
    { name: 'IM C4500 (RRHH)', paginas: 10000 },
    { name: 'M C250FWB (Gerencia)', paginas: 8000 },
    { name: 'SP 3710DN (Almacén)', paginas: 6000 },
    { name: 'IM C3000 (Marketing)', paginas: 5000 },
    { name: 'IM 550F (Finanzas)', paginas: 4000 },
    { name: 'SP 230DNw (Soporte)', paginas: 2000 },
  ],
  comparativa: [
    { id: '1', indicador: 'Total de Páginas', periodoA: 145230, periodoB: 138050, variacion: 5.2 },
    { id: '2', indicador: 'Páginas Color', periodoA: 45000, periodoB: 40000, variacion: 12.5 },
    { id: '3', indicador: 'Páginas B/N', periodoA: 100230, periodoB: 98050, variacion: 2.2 },
    { id: '4', indicador: 'Equipos Activos', periodoA: 42, periodoB: 40, variacion: 5.0 },
    { id: '5', indicador: 'Costo Promedio', periodoA: 2450.50, periodoB: 2500.00, variacion: -2.0 },
  ]
};
