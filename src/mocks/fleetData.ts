export const mockFleetData = [
  {
    id: '1',
    modelo: 'IM C6010',
    ip: '192.168.1.50',
    ubicacion: 'Sede Principal - Piso 2',
    empresa: 'Corporación Ricoh',
    estado: 'online',
    toner: { c: 80, m: 75, y: 85, k: 40 },
    capacidades: ['print', 'scan', 'copy'],
    tieneUsuarios: true,
  },
  {
    id: '2',
    modelo: 'Pro C5300s',
    ip: '192.168.1.51',
    ubicacion: 'Sede Principal - Diseño',
    empresa: 'Corporación Ricoh',
    estado: 'online',
    toner: { c: 20, m: 15, y: 10, k: 5 }, // Toner bajo
    capacidades: ['print', 'copy'],
    tieneUsuarios: true,
  },
  {
    id: '3',
    modelo: 'IM 430F',
    ip: '192.168.2.10',
    ubicacion: 'Sede Norte - Recepción',
    empresa: 'Empresa Norte SA',
    estado: 'offline',
    toner: { c: 0, m: 0, y: 0, k: 90 }, // B/W
    capacidades: ['print', 'scan', 'copy', 'fax'],
    tieneUsuarios: false,
  },
  {
    id: '4',
    modelo: 'IM C4500',
    ip: '192.168.1.60',
    ubicacion: 'Sede Principal - Ventas',
    empresa: 'Corporación Ricoh',
    estado: 'maintenance',
    toner: { c: 50, m: 45, y: 60, k: 80 },
    capacidades: ['print', 'scan', 'copy'],
    tieneUsuarios: true,
  },
  {
    id: '5',
    modelo: 'P 502',
    ip: '192.168.3.15',
    ubicacion: 'Sede Sur - Logística',
    empresa: 'Logística Sur',
    estado: 'online',
    toner: { c: 0, m: 0, y: 0, k: 30 },
    capacidades: ['print'],
    tieneUsuarios: false,
  },
  // Generando más datos simulados para llenar el grid
  ...Array.from({ length: 15 }).map((_, i) => ({
    id: `mock-${i + 6}`,
    modelo: `IM C${Math.floor(Math.random() * 5000) + 1000}`,
    ip: `192.168.1.${100 + i}`,
    ubicacion: `Oficina ${i + 1}`,
    empresa: 'Corporación Ricoh',
    estado: Math.random() > 0.8 ? 'offline' : 'online',
    toner: { 
      c: Math.floor(Math.random() * 100), 
      m: Math.floor(Math.random() * 100), 
      y: Math.floor(Math.random() * 100), 
      k: Math.floor(Math.random() * 100) 
    },
    capacidades: ['print', 'scan', 'copy'],
    tieneUsuarios: Math.random() > 0.3,
  }))
];
