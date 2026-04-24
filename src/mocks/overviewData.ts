export const mockOverviewData = {
  kpis: {
    totalEquipos: 45,
    equiposOnline: 42,
    equiposOffline: 3,
    usuariosProvisionados: 128,
    cierresPendientes: 3
  },
  actividadReciente: [
    { id: '1', fecha: '2026-04-24T08:30:00Z', tipo: 'Aprovisionamiento', descripcion: 'Usuario asignado a Impresora Ventas', usuario: 'Alex Rivera', status: 'success' },
    { id: '2', fecha: '2026-04-23T15:45:00Z', tipo: 'Lectura de Contadores', descripcion: 'Lectura automática ejecutada en 42 equipos', usuario: 'Sistema', status: 'success' },
    { id: '3', fecha: '2026-04-23T10:15:00Z', tipo: 'Cierre Mensual', descripcion: 'Cierre automático ejecutado para Sede Principal', usuario: 'Sistema', status: 'success' },
    { id: '4', fecha: '2026-04-22T09:00:00Z', tipo: 'Error de Conexión', descripcion: 'Pérdida de ping en Escáner IT', usuario: 'Sistema', status: 'error' },
  ],
  topImpresoras: [
    { name: 'IM C6010 (Ventas)', value: 25000 },
    { name: 'Pro C5300s (Diseño)', value: 20000 },
    { name: 'IM 430F (Recepción)', value: 15000 },
    { name: 'P 502 (Logística)', value: 12000 },
    { name: 'IM C4500 (RRHH)', value: 10000 },
  ]
};
