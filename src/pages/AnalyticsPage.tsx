import React, { useMemo, useState } from 'react';
import {
  Download,
  ChevronDown,
  FileText,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Layers,
  Loader2,
  Search,
  Edit2,
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { KPICard } from '../components/analytics/KPICard';
import { ChartCard } from '../components/analytics/ChartCard';
import { chartColors } from '../utils/chartColors';
import { exportReportToPDF, exportTableToExcel } from '../utils/exportUtils';
import apiClient from '../services/apiClient';
import { cn } from '../lib/utils';
import { EmpresaAutocomplete, CentroCostosAutocomplete } from '../components/ui';
import {
  useEvolucionConsumo,
  useComparativa,
  useGlobalUserConsumption,
  useUpdateUserConsumption,
  useTopUsers,
  useMonthlyCloses,
  GlobalCierreUsuario
} from '../hooks/useAnalyticsData';

const formatDate = (dateStr: string) => {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  return parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : dateStr;
};

const PERIOD_OPTIONS = [
  { id: 'may_2026', label: 'Mayo 2026', start: '2026-05-01', end: '2026-05-31' },
  { id: 'apr_2026', label: 'Abril 2026', start: '2026-04-01', end: '2026-04-30' },
  { id: 'mar_2026', label: 'Marzo 2026', start: '2026-03-01', end: '2026-03-31' },
  { id: 'q1_2026', label: 'Trimestre 1 2026', start: '2026-01-01', end: '2026-03-31' },
  { id: 'q4_2025', label: 'Trimestre 4 2025', start: '2025-10-01', end: '2025-12-31' },
];

const AnalyticsPage = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'users'>('overview');

  const [dateRangeA, setDateRangeA] = useState(PERIOD_OPTIONS[0]); // Mayo 2026
  const [dateRangeB, setDateRangeB] = useState(PERIOD_OPTIONS[1]); // Abril 2026

  // Global filters
  const [globalEmpresaId, setGlobalEmpresaId] = useState<number | undefined>(undefined);
  const [globalEmpresaName, setGlobalEmpresaName] = useState<string>('');

  // Tab 1: Overview hooks
  const { data: evolucionConsumo, isLoading: evoLoading } = useEvolucionConsumo(12);
  const { data: comparativa, isLoading: compLoading } = useComparativa(
    dateRangeA.start,
    dateRangeA.end,
    dateRangeB.start,
    dateRangeB.end
  );

  const { data: topUsers, isLoading: topUsersLoading } = useTopUsers({
    fechaInicio: dateRangeA.start,
    fechaFin: dateRangeA.end,
    limit: 5,
    empresaId: globalEmpresaId
  });

  const pieData = useMemo(() => {
    if (!comparativa) return [];
    const copias = comparativa.find((r: any) => r.indicador === 'Páginas Copiadas')?.periodoA || 0;
    const impresiones = comparativa.find((r: any) => r.indicador === 'Páginas Impresas')?.periodoA || 0;
    const escaner = comparativa.find((r: any) => r.indicador === 'Páginas Escaneadas')?.periodoA || 0;
    const fax = comparativa.find((r: any) => r.indicador === 'Páginas de Fax')?.periodoA || 0;

    const list = [];
    if (impresiones > 0) list.push({ name: 'Impresión', value: impresiones });
    if (copias > 0) list.push({ name: 'Copiado', value: copias });
    if (escaner > 0) list.push({ name: 'Escáner', value: escaner });
    if (fax > 0) list.push({ name: 'Fax', value: fax });

    if (list.length === 0) {
      return [
        { name: 'Impresión', value: 0 },
        { name: 'Copiado', value: 0 },
        { name: 'Escáner', value: 0 },
        { name: 'Fax', value: 0 }
      ];
    }
    return list;
  }, [comparativa]);

  const monthsCount = useMemo(() => {
    const start = new Date(dateRangeA.start);
    const end = new Date(dateRangeA.end);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 45 ? 3 : 1;
  }, [dateRangeA]);

  // Tab 2: User Consumption hooks and states
  const [userPage, setUserPage] = useState(1);
  const [userSearch, setUserSearch] = useState('');
  const [filterFechaInicio, setFilterFechaInicio] = useState('');
  const [filterFechaFin, setFilterFechaFin] = useState('');
  const [filterCentroCostos, setFilterCentroCostos] = useState('');

  const { data: closures } = useMonthlyCloses();

  const uniquePeriods = useMemo(() => {
    if (!closures) return [];
    const periodsMap = new Map<string, { start: string; end: string }>();
    closures.forEach((c: any) => {
      const key = `${c.fecha_inicio}_${c.fecha_fin}`;
      if (!periodsMap.has(key)) {
        periodsMap.set(key, {
          start: c.fecha_inicio,
          end: c.fecha_fin
        });
      }
    });
    return Array.from(periodsMap.values()).sort(
      (a, b) => new Date(b.end).getTime() - new Date(a.end).getTime()
    );
  }, [closures]);

  const [editingRecord, setEditingRecord] = useState<GlobalCierreUsuario | null>(null);
  const [editTotal, setEditTotal] = useState<number>(0);
  const [editConsumo, setEditConsumo] = useState<number>(0);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [saveErrorMsg, setSaveErrorMsg] = useState<string | null>(null);
  const [isExportingUsers, setIsExportingUsers] = useState(false);
  const [exportUsersErrorMsg, setExportUsersErrorMsg] = useState<string | null>(null);

  // New states for consolidated view
  const [viewMode, setViewMode] = useState<'printer' | 'user' | 'area'>('printer');
  const [userPageSize, setUserPageSize] = useState<number>(25);

  // Helper: label for the active period filter
  const activePeriodLabel = useMemo(() => {
    if (!filterFechaInicio || !filterFechaFin) return null;
    const fmt = (s: string) => { const [y, m, d] = s.split('-'); return `${d}/${m}/${y}`; };
    return filterFechaInicio === filterFechaFin
      ? `Cierre del ${fmt(filterFechaInicio)}`
      : `Período: ${fmt(filterFechaInicio)} al ${fmt(filterFechaFin)}`;
  }, [filterFechaInicio, filterFechaFin]);

  const { data: globalUserConsumptionData, isLoading: userLoading } = useGlobalUserConsumption({
    page: userPage,
    pageSize: userPageSize,
    search: userSearch || undefined,
    fechaInicio: filterFechaInicio || undefined,
    fechaFin: filterFechaFin || undefined,
    centroCostos: filterCentroCostos || undefined
  });
  const globalUserConsumption = globalUserConsumptionData as any;

  // Dedicated query for 'area' view — fetches ALL records (no pagination) so the tree totals are always complete
  const { data: areaConsumptionData, isLoading: areaLoading } = useGlobalUserConsumption({
    page: 1,
    pageSize: 1000,
    search: undefined,  // No search filter for consolidated view — shows everything
    fechaInicio: filterFechaInicio || undefined,
    fechaFin: filterFechaFin || undefined,
    centroCostos: filterCentroCostos || undefined
  });
  const areaConsumption = areaConsumptionData as any;

  const updateMutation = useUpdateUserConsumption();

  const groupedCierres = useMemo(() => {
    const items = globalUserConsumption?.items || [];
    const map = new Map<number, {
      cierre_mensual_id: number;
      printer_id: number;
      printer_hostname: string;
      printer_ip: string;
      printer_location: string;
      printer_serial?: string;
      fecha_inicio: string;
      fecha_fin: string;
      fecha_cierre: string;
      cerrado_por?: string;
      users: GlobalCierreUsuario[];
      total_consumo: number;
    }>();

    for (const r of items) {
      if (!map.has(r.cierre_mensual_id)) {
        map.set(r.cierre_mensual_id, {
          cierre_mensual_id: r.cierre_mensual_id,
          printer_id: r.printer_id,
          printer_hostname: r.printer_hostname,
          printer_ip: r.printer_ip,
          printer_location: r.printer_location,
          printer_serial: r.printer_serial,
          fecha_inicio: r.fecha_inicio,
          fecha_fin: r.fecha_fin,
          fecha_cierre: r.fecha_cierre,
          cerrado_por: r.cerrado_por,
          users: [],
          total_consumo: 0,
        });
      }
      const g = map.get(r.cierre_mensual_id)!;
      g.users.push(r);
      g.total_consumo += r.consumo_total || 0;
    }

    return Array.from(map.values()).sort(
      (a, b) => new Date(b.fecha_cierre).getTime() - new Date(a.fecha_cierre).getTime()
    );
  }, [globalUserConsumption?.items]);

  // Aggregation logic: consolidatedUsers (groups by user_id)
  const consolidatedUsers = useMemo(() => {
    const items = globalUserConsumption?.items || [];
    const map = new Map<number, {
      user_id: number;
      codigo_usuario: string;
      nombre_usuario: string;
      centro_costos: string | null;
      consumo_total: number;
      total_paginas: number;
      total_bn: number;
      total_color: number;
      consumo_copiadora: number;
      consumo_impresora: number;
      consumo_escaner: number;
      consumo_fax: number;
      printers: {
        id: number;
        cierre_mensual_id: number;
        printer_id: number;
        printer_hostname: string;
        printer_ip: string;
        printer_location: string;
        consumo_total: number;
        total_paginas: number;
        total_bn: number;
        total_color: number;
        consumo_copiadora: number;
        consumo_impresora: number;
        consumo_escaner: number;
        consumo_fax: number;
        fecha_inicio: string;
        fecha_fin: string;
        fecha_cierre: string;
        cerrado_por?: string;
        printer_serial?: string;
        rawRecord: GlobalCierreUsuario;
      }[];
    }>();

    for (const r of items) {
      if (!map.has(r.user_id)) {
        map.set(r.user_id, {
          user_id: r.user_id,
          codigo_usuario: r.codigo_usuario,
          nombre_usuario: r.nombre_usuario,
          centro_costos: r.centro_costos || null,
          consumo_total: 0,
          total_paginas: 0,
          total_bn: 0,
          total_color: 0,
          consumo_copiadora: 0,
          consumo_impresora: 0,
          consumo_escaner: 0,
          consumo_fax: 0,
          printers: [],
        });
      }
      const u = map.get(r.user_id)!;
      u.consumo_total += r.consumo_total || 0;
      u.total_paginas += r.total_paginas || 0;
      u.total_bn += r.total_bn || 0;
      u.total_color += r.total_color || 0;
      u.consumo_copiadora += r.consumo_copiadora || 0;
      u.consumo_impresora += r.consumo_impresora || 0;
      u.consumo_escaner += r.consumo_escaner || 0;
      u.consumo_fax += r.consumo_fax || 0;

      u.printers.push({
        id: r.id,
        cierre_mensual_id: r.cierre_mensual_id,
        printer_id: r.printer_id,
        printer_hostname: r.printer_hostname,
        printer_ip: r.printer_ip,
        printer_location: r.printer_location,
        printer_serial: r.printer_serial,
        consumo_total: r.consumo_total,
        total_paginas: r.total_paginas,
        total_bn: r.total_bn,
        total_color: r.total_color,
        consumo_copiadora: r.consumo_copiadora,
        consumo_impresora: r.consumo_impresora,
        consumo_escaner: r.consumo_escaner,
        consumo_fax: r.consumo_fax,
        fecha_inicio: r.fecha_inicio,
        fecha_fin: r.fecha_fin,
        fecha_cierre: r.fecha_cierre,
        cerrado_por: r.cerrado_por,
        rawRecord: r
      });
    }

    return Array.from(map.values()).sort(
      (a, b) => b.consumo_total - a.consumo_total
    );
  }, [globalUserConsumption?.items]);

  const consolidatedHierarchy = useMemo(() => {
    // Use the dedicated area query (all records, no pagination) for correct totals
    const items = areaConsumption?.items || [];

    // Map to group by Company -> Area -> User -> Printer
    const companyMap = new Map<string, {
      companyName: string;
      total_bn: number;
      total_color: number;
      areas: Map<string, {
        areaName: string;
        total_bn: number;
        total_color: number;
        users: Map<number, {
          userId: number;
          userName: string;
          userCode: string;
          total_bn: number;
          total_color: number;
          printers: {
            printerId: number;
            hostname: string;
            ip: string;
            serial: string;
            location: string;
            total_bn: number;
            total_color: number;
            fecha_inicio: string;
            fecha_fin: string;
          }[];
        }>;
      }>;
    }>();

    for (const r of items) {
      const compKey = r.empresa_nombre || 'SIN EMPRESA';
      const areaKey = r.centro_costos || 'SIN CENTRO DE COSTOS';
      const userKey = r.user_id;

      // Ensure Company exists
      if (!companyMap.has(compKey)) {
        companyMap.set(compKey, {
          companyName: compKey,
          total_bn: 0,
          total_color: 0,
          areas: new Map()
        });
      }
      const company = companyMap.get(compKey)!;
      company.total_bn += r.consumo_bn || 0;
      company.total_color += r.consumo_color || 0;

      // Ensure Area exists
      if (!company.areas.has(areaKey)) {
        company.areas.set(areaKey, {
          areaName: areaKey,
          total_bn: 0,
          total_color: 0,
          users: new Map()
        });
      }
      const area = company.areas.get(areaKey)!;
      area.total_bn += r.consumo_bn || 0;
      area.total_color += r.consumo_color || 0;

      // Ensure User exists
      if (!area.users.has(userKey)) {
        area.users.set(userKey, {
          userId: userKey,
          userName: r.nombre_usuario,
          userCode: r.codigo_usuario,
          total_bn: 0,
          total_color: 0,
          printers: []
        });
      }
      const user = area.users.get(userKey)!;
      user.total_bn += r.consumo_bn || 0;
      user.total_color += r.consumo_color || 0;

      // Add Printer breakdown ONLY if user had real activity on this printer in this period.
      // A user may be registered on 5 printers but only used 1 — only that 1 should appear.
      const printerBN = r.consumo_bn || 0;
      const printerColor = r.consumo_color || 0;
      if (printerBN > 0 || printerColor > 0) {
        user.printers.push({
          printerId: r.printer_id,
          hostname: r.printer_hostname,
          ip: r.printer_ip,
          serial: r.printer_serial || '',
          location: r.printer_location,
          total_bn: printerBN,
          total_color: printerColor,
          fecha_inicio: r.fecha_inicio,
          fecha_fin: r.fecha_fin
        });
      }
    }

    // Convert Map structure to sorted arrays.
    // Filter out zero-activity entries at every level so the tree only shows
    // users/areas/companies that had at least 1 page of real consumption.
    return Array.from(companyMap.values())
      .map(company => ({
        ...company,
        areas: Array.from(company.areas.values())
          .map(area => ({
            ...area,
            users: Array.from(area.users.values())
              // Only show users that printed/copied/scanned at least 1 page
              .filter(user => user.total_bn > 0 || user.total_color > 0)
              .map(user => ({
                ...user,
                printers: user.printers.sort((a, b) => b.total_bn - a.total_bn)
              }))
              .sort((a, b) => b.total_bn - a.total_bn)
          }))
          // Only show areas that have at least 1 active user
          .filter(area => area.total_bn > 0 || area.total_color > 0)
          .sort((a, b) => b.total_bn - a.total_bn)
      }))
      // Only show companies with real consumption
      .filter(company => company.total_bn > 0 || company.total_color > 0)
      .sort((a, b) => b.total_bn - a.total_bn);
  }, [areaConsumption?.items]);

  const [expandedCompanies, setExpandedCompanies] = useState<Record<string, boolean>>({
    'ELITE': true,
    'ELITE FACILITY MANAGMENT': true
  });
  const [expandedAreas, setExpandedAreas] = useState<Record<string, boolean>>({});
  const [expandedUsers, setExpandedUsers] = useState<Record<string, boolean>>({});

  const toggleCompany = (companyName: string) => {
    setExpandedCompanies(prev => ({ ...prev, [companyName]: !prev[companyName] }));
  };

  const toggleArea = (companyName: string, areaName: string) => {
    const key = `${companyName}_${areaName}`;
    setExpandedAreas(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const toggleUser = (companyName: string, areaName: string, userId: number) => {
    const key = `${companyName}_${areaName}_${userId}`;
    setExpandedUsers(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const [expandedCierres, setExpandedCierres] = useState<Record<number, boolean>>({});
  const toggleCierre = (cierreId: number) => {
    setExpandedCierres(prev => ({ ...prev, [cierreId]: !prev[cierreId] }));
  };

  const [expandedConsolidatedUsers, setExpandedConsolidatedUsers] = useState<Record<number, boolean>>({});
  const toggleConsolidatedUser = (userId: number) => {
    setExpandedConsolidatedUsers(prev => ({ ...prev, [userId]: !prev[userId] }));
  };

  const [expandedUserRows, setExpandedUserRows] = useState<Record<number, boolean>>({});
  const toggleUserRow = (recordId: number) => {
    setExpandedUserRows(prev => ({ ...prev, [recordId]: !prev[recordId] }));
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserSearch(e.target.value);
    setUserPage(1);
  };

  const handleOpenEdit = (record: GlobalCierreUsuario) => {
    setEditingRecord(record);
    setEditTotal(record.total_paginas);
    setEditConsumo(record.consumo_total);
    setSaveSuccessMsg(null);
    setSaveErrorMsg(null);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingRecord) return;

    try {
      await updateMutation.mutateAsync({
        id: editingRecord.id,
        total_paginas: editTotal,
        consumo_total: editConsumo,
      });
      setSaveSuccessMsg('Consumo de usuario actualizado correctamente.');
      setTimeout(() => {
        setEditingRecord(null);
        setSaveSuccessMsg(null);
      }, 1500);
    } catch (err: any) {
      setSaveErrorMsg(err.response?.data?.detail || 'Error al actualizar el consumo.');
    }
  };

  const handleExportPDF = () => {
    if (!comparativa) return;
    const columns = [
      { header: 'Indicador', dataKey: 'indicador' },
      { header: dateRangeA.label, dataKey: 'periodoA' },
      { header: dateRangeB.label, dataKey: 'periodoB' },
      { header: 'Variación (%)', dataKey: 'variacion' }
    ];
    exportReportToPDF(`Reporte Analítico - Ricoh Equipment Manager (${dateRangeA.label} vs ${dateRangeB.label})`, comparativa, columns, `comparativa_ricoh_${dateRangeA.label.replace(/\s+/g, '_')}_vs_${dateRangeB.label.replace(/\s+/g, '_')}`);
  };

  const handleExportExcel = () => {
    if (!comparativa) return;
    const excelData = comparativa.map((row: any) => ({
      'Indicador': row.indicador,
      [dateRangeA.label]: row.periodoA,
      [dateRangeB.label]: row.periodoB,
      'Variación (%)': `${row.variacion}%`
    }));
    exportTableToExcel(excelData, `comparativa_ricoh_${dateRangeA.label.replace(/\s+/g, '_')}_vs_${dateRangeB.label.replace(/\s+/g, '_')}`);
  };

  const handleExportUsersExcel = async () => {
    setExportUsersErrorMsg(null);

    // Exportar TODOS los registros del filtro actual (no solo la página visible).
    const pageSize = 500;
    const baseParams = new URLSearchParams();
    baseParams.append('page_size', pageSize.toString());
    if (userSearch) baseParams.append('search', userSearch);

    const fetchPage = async (page: number) => {
      const params = new URLSearchParams(baseParams);
      params.set('page', page.toString());
      const { data } = await apiClient.get(`/api/counters/monthly/users/all?${params.toString()}`);
      return data as { items: GlobalCierreUsuario[]; pages: number };
    };

    try {
      setIsExportingUsers(true);
      const first = await fetchPage(1);
      let allItems: GlobalCierreUsuario[] = [...(first.items || [])];

      for (let p = 2; p <= (first.pages || 1); p++) {
        const next = await fetchPage(p);
        allItems = allItems.concat(next.items || []);
      }

      if (allItems.length === 0) return;

      const cleanDataForExport = allItems.map(item => ({
        'Usuario': item.nombre_usuario,
        'Código Usuario': item.codigo_usuario,
        'Impresora Hostname': item.printer_hostname,
        'Impresora IP': item.printer_ip,
        'Ubicación': item.printer_location,
        'Consumo del Período (págs)': item.consumo_total,
        'Total Acumulado (págs)': item.total_paginas,
        'Fecha Cierre': new Date(item.fecha_cierre).toLocaleDateString(),
        'Periodo': `${item.fecha_inicio} a ${item.fecha_fin}`,
        'Cerrado Por': item.cerrado_por || 'Sistema'
      }));

      exportTableToExcel(cleanDataForExport, `consumo_usuarios_cierre_${new Date().toISOString().slice(0, 10)}`);
    } catch (err: any) {
      console.error('Error al exportar consumo de usuarios:', err);
      setExportUsersErrorMsg(err?.response?.data?.detail || 'No se pudo exportar el Excel.');
    } finally {
      setIsExportingUsers(false);
    }
  };

  const [isExportingFacturacion, setIsExportingFacturacion] = useState(false);

  const handleExportFacturacion = async () => {
    if (!globalEmpresaId) {
      alert("Por favor seleccione una Empresa primero para generar su reporte de facturación.");
      return;
    }

    // Use current tab's date filter or default to something sensible
    const start = filterFechaInicio || dateRangeA.start;
    const end = filterFechaFin || dateRangeA.end;

    if (!start || !end) {
      alert("Por favor defina Fecha Inicio y Fecha Fin en los filtros.");
      return;
    }

    try {
      setIsExportingFacturacion(true);
      const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/export/facturacion/${globalEmpresaId}?fecha_inicio=${start}&fecha_fin=${end}`;

      const token = localStorage.getItem('token');
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Error al exportar');
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `Reporte_Facturacion_${globalEmpresaName}.xlsx`;
      if (contentDisposition && contentDisposition.includes('filename=')) {
        filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
      }
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err: any) {
      alert(`Error al exportar facturación: ${err.message}`);
    } finally {
      setIsExportingFacturacion(false);
    }
  };

  if (activeTab === 'overview' && (evoLoading || compLoading)) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-10 w-10 animate-spin text-ricoh-red mx-auto mb-4" />
          <p className="font-bold text-slate-500 uppercase tracking-widest text-sm">Analizando Datos...</p>
        </div>
      </div>
    );
  }

  // KPIs
  // Nota: la comparativa actual retorna 1 fila; evitar depender del texto del indicador
  // (puede venir con problemas de encoding según configuración de DB).
  const kpiTotalPaginas = comparativa?.[0]?.periodoA || 0;
  const kpiVariacion = comparativa?.[0]?.variacion || 0;

  return (
    <div className="flex flex-col h-full animate-fade-in custom-scrollbar overflow-y-auto pb-10">
      {/* Title Header */}
      <div className="mb-responsive flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-responsive-xl font-black text-slate-800 tracking-tight">Reportes y Analíticas</h1>
          <p className="text-responsive-sm font-bold text-slate-500 uppercase tracking-widest mt-1">Inteligencia de Negocios</p>
        </div>
        {activeTab === 'overview' && (
          <div className="flex flex-col sm:flex-row gap-2">
            <button
              onClick={handleExportFacturacion}
              disabled={isExportingFacturacion || !globalEmpresaId}
              className="bg-green-600 text-white btn-padding-sm rounded-xl font-bold shadow-lg shadow-green-600/20 hover:bg-green-700 disabled:opacity-50 transition-all flex items-center gap-2 text-responsive-sm"
              title={!globalEmpresaId ? "Seleccione una empresa primero" : "Exportar Facturación Jerárquica"}
            >
              {isExportingFacturacion ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
              <span className="hidden sm:inline">Exportar Facturación</span>
              <span className="sm:hidden">Excel</span>
            </button>
            <button
              onClick={handleExportPDF}
              className="bg-ricoh-red text-white btn-padding-sm rounded-xl font-bold shadow-lg shadow-red-500/20 hover:bg-red-700 transition-all flex items-center gap-2 text-responsive-sm"
            >
              <Download size={16} />
              <span className="hidden sm:inline">Exportar PDF</span>
              <span className="sm:hidden">PDF</span>
            </button>
          </div>
        )}
      </div>

      {/* Tabs Selector */}
      <div className="flex border-b border-slate-200 mb-responsive gap-6">
        <button
          onClick={() => setActiveTab('overview')}
          className={cn(
            "pb-3 font-bold text-sm uppercase tracking-wider border-b-2 transition-all",
            activeTab === 'overview'
              ? "border-ricoh-red text-slate-800"
              : "border-transparent text-slate-400 hover:text-slate-600"
          )}
        >
          Resumen General
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={cn(
            "pb-3 font-bold text-sm uppercase tracking-wider border-b-2 transition-all",
            activeTab === 'users'
              ? "border-ricoh-red text-slate-800"
              : "border-transparent text-slate-400 hover:text-slate-600"
          )}
        >
          Consumo de Usuarios
        </button>
      </div>

      {/* Overview Tab Content */}
      {activeTab === 'overview' && (
        <>
          {/* Dynamic Date Filters */}
          <div className="flex flex-wrap gap-responsive-sm mb-responsive items-center bg-slate-50/50 p-4 rounded-2xl border border-slate-100/80">
            <div className="w-full max-w-sm">
              <EmpresaAutocomplete
                value={globalEmpresaName}
                onChange={(name, id) => {
                  setGlobalEmpresaName(name);
                  setGlobalEmpresaId(id);
                }}
                placeholder="Filtrar por Empresa..."
              />
            </div>

            {/* Selector de Período Principal (A) */}
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest whitespace-nowrap">Período Principal:</span>
              <select
                value={PERIOD_OPTIONS.findIndex(p => p.start === dateRangeA.start && p.end === dateRangeA.end)}
                onChange={(e) => {
                  const idx = parseInt(e.target.value);
                  setDateRangeA(PERIOD_OPTIONS[idx]);
                }}
                className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold text-slate-700 focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red cursor-pointer transition-all shadow-sm"
              >
                {PERIOD_OPTIONS.map((p, idx) => (
                  <option key={p.id} value={idx}>{p.label}</option>
                ))}
              </select>
            </div>

            {/* Selector de Período Comparativo (B) */}
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest whitespace-nowrap">Comparar con:</span>
              <select
                value={PERIOD_OPTIONS.findIndex(p => p.start === dateRangeB.start && p.end === dateRangeB.end)}
                onChange={(e) => {
                  const idx = parseInt(e.target.value);
                  setDateRangeB(PERIOD_OPTIONS[idx]);
                }}
                className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold text-slate-700 focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red cursor-pointer transition-all shadow-sm"
              >
                {PERIOD_OPTIONS.map((p, idx) => (
                  <option key={p.id} value={idx}>{p.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* KPIs Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-responsive mb-responsive">
            <KPICard
              title="Total Páginas"
              value={kpiTotalPaginas.toLocaleString()}
              icon={<Layers size={20} />}
              color={chartColors.primary}
            />
            <KPICard
              title="Promedio / Mes"
              value={(kpiTotalPaginas / monthsCount).toLocaleString(undefined, { maximumFractionDigits: 0 })}
              icon={<TrendingUp size={20} />}
              color={chartColors.info}
            />
            <KPICard
              title="Costo Estimado"
              value={`$${(kpiTotalPaginas * 0.05).toLocaleString(undefined, { maximumFractionDigits: 2 })}`}
              icon={<DollarSign size={20} />}
              color={chartColors.warning}
            />
            <KPICard
              title="Variación"
              value={""}
              trend={kpiVariacion}
              trendLabel={`vs ${dateRangeB.label}`}
              icon={<TrendingUp size={20} />}
              color={chartColors.success}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-responsive mb-responsive">
            {/* Line Chart */}
            <div className="lg:col-span-2 h-[350px] lg:h-[400px]">
              <ChartCard title="Evolución de Consumo" onExport={() => { }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={evolucionConsumo} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      formatter={(value: any) => value?.toLocaleString() || ''}
                    />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                    <Line
                      type="monotone"
                      dataKey="paginas"
                      name="Páginas Impresas"
                      stroke={chartColors.primary}
                      strokeWidth={3}
                      dot={{ r: 4, strokeWidth: 2 }}
                      activeDot={{ r: 6, strokeWidth: 0 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            {/* Pie Chart */}
            <div className="lg:col-span-1 h-[350px] lg:h-[400px]">
              <ChartCard title="Distribución por Función" onExport={() => { }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={80}
                      outerRadius={110}
                      paddingAngle={5}
                      dataKey="value"
                      stroke="none"
                    >
                      {pieData.map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={chartColors.categorical[index % chartColors.categorical.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value: any) => value?.toLocaleString() || ''}
                      contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend iconType="circle" layout="horizontal" verticalAlign="bottom" wrapperStyle={{ fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-responsive mb-responsive">
            {/* Comparative Table */}
            <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-100 card-padding-sm flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-bold text-slate-800">Comparativa Detallada ({dateRangeA.label} vs {dateRangeB.label})</h3>
                <button
                  onClick={handleExportExcel}
                  className="text-xs font-bold text-slate-500 hover:text-ricoh-red uppercase tracking-widest transition-colors flex items-center gap-1"
                >
                  <Download size={14} /> Excel
                </button>
              </div>

              <div className="overflow-x-auto rounded-lg border border-slate-100">
                <table className="w-full text-sm text-left">
                  <thead className="bg-slate-50 text-[10px] uppercase font-black tracking-widest text-slate-500">
                    <tr>
                      <th className="px-4 py-3">Indicador</th>
                      <th className="px-4 py-3 text-right">Consumo {dateRangeA.label}</th>
                      <th className="px-4 py-3 text-right">Consumo {dateRangeB.label}</th>
                      <th className="px-4 py-3 text-right">Variación</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {comparativa?.map((row: any, index: number) => {
                      const isPositive = row.variacion > 0;
                      const isNegative = row.variacion < 0;
                      return (
                        <tr key={index} className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-4 py-3 font-bold text-slate-700">{row.indicador}</td>
                          <td className="px-4 py-3 text-right text-slate-600">{row.periodoA.toLocaleString()}</td>
                          <td className="px-4 py-3 text-right text-slate-600">{row.periodoB.toLocaleString()}</td>
                          <td className="px-4 py-3 text-right">
                            <span className={cn(
                              "inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold",
                              isPositive ? "bg-green-100 text-green-700" :
                                isNegative ? "bg-red-100 text-red-700" :
                                  "bg-slate-100 text-slate-600"
                            )}>
                              {isPositive ? <TrendingUp size={12} /> : isNegative ? <TrendingDown size={12} /> : null}
                              {isPositive ? '+' : ''}{row.variacion}%
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Top 5 Consumers */}
            <div className="lg:col-span-1 bg-white rounded-xl shadow-sm border border-slate-100 card-padding-sm flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-sm font-bold text-slate-800">Top 5 Consumidores</h3>
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Rango Activo</span>
                </div>

                {topUsersLoading ? (
                  <div className="flex flex-1 items-center justify-center py-10">
                    <Loader2 className="h-6 w-6 animate-spin text-ricoh-red" />
                  </div>
                ) : !topUsers || topUsers.length === 0 ? (
                  <div className="flex flex-1 items-center justify-center py-10 text-center">
                    <p className="text-xs text-slate-400 font-bold">No hay consumos registrados en este período.</p>
                  </div>
                ) : (
                  <div className="flex flex-col gap-4">
                    {topUsers.map((user, idx) => {
                      const maxVal = topUsers[0]?.total_consumo_paginas || 1;
                      const percentage = Math.round((user.total_consumo_paginas / maxVal) * 100);
                      return (
                        <div key={user.user_id} className="flex flex-col gap-1">
                          <div className="flex justify-between items-center text-xs">
                            <span className="font-bold text-slate-700 truncate max-w-[150px]">
                              {idx + 1}. {user.nombre}
                            </span>
                            <span className="font-black text-slate-600 shrink-0">
                              {user.total_consumo_paginas.toLocaleString()} págs
                            </span>
                          </div>

                          <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-red-500 to-ricoh-red rounded-full transition-all duration-500"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>

                          <div className="flex justify-between items-center text-[8px] text-slate-400 font-semibold uppercase tracking-wider">
                            <span>{user.centro_costos || 'Sin Centro de Costos'}</span>
                            <span>{user.cierres_count} {user.cierres_count === 1 ? 'cierre' : 'cierres'}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {/* User Consumption Tab Content */}
      {activeTab === 'users' && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 flex flex-col gap-6">
          {/* Controls Bar */}
          <div className="flex flex-col lg:flex-row justify-between items-stretch lg:items-center gap-4">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 flex-1">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Buscar por usuario, código, IP o ubicación..."
                  value={userSearch}
                  onChange={handleSearchChange}
                  className="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red transition-all"
                />
              </div>

              {/* View Switcher Toggle */}
              <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-inner shrink-0 self-center sm:self-auto">
                <button
                  type="button"
                  onClick={() => { setViewMode('printer'); setUserPage(1); }}
                  className={cn(
                    "px-4 py-2 rounded-lg text-xs font-black transition-all flex items-center gap-1.5",
                    viewMode === 'printer'
                      ? "bg-white text-slate-800 shadow-sm"
                      : "text-slate-500 hover:text-slate-700"
                  )}
                >
                  <Layers size={14} />
                  Por Impresora
                </button>
                <button
                  type="button"
                  onClick={() => { setViewMode('user'); setUserPage(1); }}
                  className={cn(
                    "px-4 py-2 rounded-lg text-xs font-black transition-all flex items-center gap-1.5",
                    viewMode === 'user'
                      ? "bg-white text-slate-800 shadow-sm"
                      : "text-slate-500 hover:text-slate-700"
                  )}
                >
                  <Search size={14} />
                  Por Usuario
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setViewMode('area');
                    setUserPage(1);
                    // Auto-select the most recent period if none is active
                    if (!filterFechaInicio && !filterFechaFin && uniquePeriods.length > 0) {
                      setFilterFechaInicio(uniquePeriods[0].start);
                      setFilterFechaFin(uniquePeriods[0].end);
                    }
                  }}
                  className={cn(
                    "px-4 py-2 rounded-lg text-xs font-black transition-all flex items-center gap-1.5",
                    viewMode === 'area'
                      ? "bg-white text-slate-800 shadow-sm"
                      : "text-slate-500 hover:text-slate-700"
                  )}
                >
                  <Layers size={14} />
                  Consolidado por Área
                </button>
              </div>
            </div>

            <div className="flex items-center gap-3 justify-end shrink-0">
              {/* Page Size Selector */}
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest whitespace-nowrap">Mostrar</span>
                <select
                  value={userPageSize}
                  onChange={(e) => { setUserPageSize(parseInt(e.target.value)); setUserPage(1); }}
                  className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold text-slate-700 focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red cursor-pointer transition-all"
                >
                  <option value={15}>15 registros</option>
                  <option value={25}>25 registros</option>
                  <option value={50}>50 registros</option>
                  <option value={100}>100 registros</option>
                </select>
              </div>

              <button
                onClick={() => void handleExportUsersExcel()}
                disabled={isExportingUsers || !globalUserConsumption?.items || globalUserConsumption.items.length === 0}
                className="bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed font-bold text-xs uppercase tracking-widest px-4 py-2.5 rounded-xl transition-all flex items-center justify-center gap-2"
              >
                {isExportingUsers ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download size={14} />}
                Exportar Excel
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <div className="flex flex-col gap-1.5 col-span-1 sm:col-span-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Período de Cierre</label>
              <select
                value={filterFechaInicio && filterFechaFin ? `${filterFechaInicio}_${filterFechaFin}` : ''}
                onChange={(e) => {
                  const val = e.target.value;
                  if (val) {
                    const [start, end] = val.split('_');
                    setFilterFechaInicio(start);
                    setFilterFechaFin(end);
                  } else {
                    setFilterFechaInicio('');
                    setFilterFechaFin('');
                  }
                  setUserPage(1);
                }}
                className="w-full px-4 py-2.5 text-sm bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red font-semibold text-slate-700 transition-all shadow-sm cursor-pointer"
              >
                <option value="">Todos los períodos (sin filtro de fecha)</option>
                {uniquePeriods.map((p) => {
                  const formatDate = (dateStr: string) => {
                    const [y, m, d] = dateStr.split('-');
                    return `${d}/${m}/${y}`;
                  };
                  const label = p.start === p.end
                    ? `Cierre del ${formatDate(p.start)}`
                    : `Período del ${formatDate(p.start)} al ${formatDate(p.end)}`;
                  return (
                    <option key={`${p.start}_${p.end}`} value={`${p.start}_${p.end}`}>
                      {label}
                    </option>
                  );
                })}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Centro de Costos</label>
              <CentroCostosAutocomplete
                label=""
                value={filterCentroCostos}
                onChange={(val) => { setFilterCentroCostos(val); setUserPage(1); }}
                placeholder="Ej: Contabilidad, Ventas..."
                empresaName={globalEmpresaName}
                allowGlobal={true}
              />
            </div>
          </div>

          {exportUsersErrorMsg && (
            <div className="text-xs font-bold text-red-600 bg-red-50 border border-red-100 rounded-xl p-3">
              {exportUsersErrorMsg}
            </div>
          )}

          {/* Guía rápida explicativa de consumo */}
          <div className="bg-slate-50 border border-slate-150 rounded-2xl p-4 flex gap-3 items-start text-xs text-slate-600">
            <div className="bg-blue-50 text-blue-600 p-1.5 rounded-lg shrink-0 mt-0.5">
              <FileText size={14} />
            </div>
            <div>
              <p className="font-bold text-slate-800 mb-1">Guía de Lectura de Consumos</p>
              <ul className="list-disc list-inside space-y-1 text-slate-500">
                <li>
                  <strong className="text-slate-700">Consumo del Período:</strong> Páginas impresas, copiadas o escaneadas por el usuario **dentro de las fechas del cierre seleccionado** (calculado como la diferencia entre la lectura actual y la lectura anterior).
                </li>
                <li>
                  <strong className="text-slate-700">Total Acumulado:</strong> Contador histórico de páginas registradas en la impresora para el usuario desde su registro inicial en el equipo.
                </li>
              </ul>
            </div>
          </div>

          {/* Period context banner */}
          {activePeriodLabel ? (
            <div className="flex items-center gap-3 px-4 py-3 bg-emerald-50 border border-emerald-200 rounded-xl">
              <div className="flex-shrink-0 w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <div className="flex-1 min-w-0">
                <span className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">Período activo</span>
                <p className="text-sm font-black text-emerald-800">{activePeriodLabel}</p>
              </div>
              <span className="text-[10px] text-emerald-600 font-semibold hidden sm:block">
                Los consumos B/N y Color mostrados corresponden exclusivamente a este período de cierre
              </span>
            </div>
          ) : (
            <div className="flex items-start gap-3 px-4 py-3 bg-amber-50 border border-amber-200 rounded-xl">
              <div className="flex-shrink-0 mt-0.5">
                <svg className="w-4 h-4 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" /></svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-black text-amber-700">Sin filtro de período activo</p>
                <p className="text-[11px] text-amber-600 font-medium mt-0.5">
                  Estás viendo datos de <strong>todos los cierres registrados mezclados</strong>. Para un análisis correcto, selecciona un período de cierre en el selector de arriba.
                </p>
              </div>
              {uniquePeriods.length > 0 && (
                <button
                  type="button"
                  onClick={() => { setFilterFechaInicio(uniquePeriods[0].start); setFilterFechaFin(uniquePeriods[0].end); setUserPage(1); }}
                  className="shrink-0 text-[10px] font-black uppercase tracking-wider text-amber-700 bg-amber-100 hover:bg-amber-200 border border-amber-300 px-3 py-1.5 rounded-lg transition-all"
                >
                  Ver período más reciente
                </button>
              )}
            </div>
          )}

          {/* Grouped content (por cierre) */}
          {userLoading && (!globalUserConsumption?.items || globalUserConsumption.items.length === 0) ? (
            <div className="flex justify-center items-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-ricoh-red" />
            </div>
          ) : !globalUserConsumption?.items || globalUserConsumption.items.length === 0 ? (
            <div className="text-center py-20 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
              <p className="text-slate-400 font-bold text-sm">No se encontraron registros de consumo de usuario.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {viewMode === 'user' ? (
                consolidatedUsers.map((u) => {
                  const expanded = expandedConsolidatedUsers[u.user_id] ?? false;
                  return (
                    <div key={u.user_id} className="rounded-xl border border-slate-100 overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                      {/* Accordion Header */}
                      <button
                        type="button"
                        onClick={() => toggleConsolidatedUser(u.user_id)}
                        className="w-full bg-slate-50/70 px-5 py-4 flex items-start sm:items-center justify-between gap-4 text-left hover:bg-slate-100/70 transition-colors"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-black text-slate-800 text-sm truncate">{u.nombre_usuario}</span>
                            <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 bg-slate-200/50 px-2 py-0.5 rounded-md">
                              {u.codigo_usuario}
                            </span>
                            {u.centro_costos && (
                              <span className="text-[10px] font-black uppercase tracking-widest text-ricoh-red bg-red-50 px-2 py-0.5 rounded-md truncate max-w-[150px]">
                                {u.centro_costos}
                              </span>
                            )}
                          </div>

                          <div className="text-[11px] text-slate-500 font-semibold mt-1 flex flex-wrap gap-x-3 gap-y-1">
                            <span>Consumo consolidado: <strong className="text-slate-700">{u.consumo_total.toLocaleString()} págs</strong></span>
                            <span>·</span>
                            <span>Equipos utilizados: <strong className="text-slate-700">{u.printers.length} {u.printers.length === 1 ? 'impresora' : 'impresoras'}</strong></span>
                            <span>·</span>
                            <span className="text-slate-400 font-medium">B/N: {u.total_bn.toLocaleString()} | Color: {u.total_color.toLocaleString()}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-[10px] font-black uppercase tracking-widest text-slate-500 hidden sm:inline">
                            {expanded ? 'Ocultar' : 'Ver'} desglose
                          </span>
                          <ChevronDown
                            size={18}
                            className={cn('text-slate-400 transition-transform', expanded ? 'rotate-180' : 'rotate-0')}
                          />
                        </div>
                      </button>

                      {expanded && (
                        <div className="p-5 bg-white border-t border-slate-100 flex flex-col gap-6 animate-scale-in">
                          {/* KPI summary cards for consolidated functions */}
                          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            {/* Copiadora */}
                            <div className="flex flex-col gap-1 p-4 bg-slate-50/50 rounded-2xl border border-slate-100 hover:bg-slate-50 transition-colors">
                              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Total Copiadora</span>
                              <strong className="text-lg font-black text-slate-800">{u.consumo_copiadora.toLocaleString()} <span className="text-xs text-slate-400 font-medium">págs</span></strong>
                              <div className="w-full h-1 bg-slate-100 rounded-full mt-1 overflow-hidden">
                                <div className="h-full bg-ricoh-red rounded-full" style={{ width: `${u.consumo_total > 0 ? (u.consumo_copiadora / u.consumo_total) * 100 : 0}%` }} />
                              </div>
                              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mt-1">
                                {u.consumo_total > 0 ? Math.round((u.consumo_copiadora / u.consumo_total) * 100) : 0}% del total
                              </span>
                            </div>

                            {/* Impresora */}
                            <div className="flex flex-col gap-1 p-4 bg-slate-50/50 rounded-2xl border border-slate-100 hover:bg-slate-50 transition-colors">
                              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Total Impresora</span>
                              <strong className="text-lg font-black text-slate-800">{u.consumo_impresora.toLocaleString()} <span className="text-xs text-slate-400 font-medium">págs</span></strong>
                              <div className="w-full h-1 bg-slate-100 rounded-full mt-1 overflow-hidden">
                                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${u.consumo_total > 0 ? (u.consumo_impresora / u.consumo_total) * 100 : 0}%` }} />
                              </div>
                              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mt-1">
                                {u.consumo_total > 0 ? Math.round((u.consumo_impresora / u.consumo_total) * 100) : 0}% del total
                              </span>
                            </div>

                            {/* Escáner */}
                            <div className="flex flex-col gap-1 p-4 bg-slate-50/50 rounded-2xl border border-slate-100 hover:bg-slate-50 transition-colors">
                              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Total Escáner</span>
                              <strong className="text-lg font-black text-slate-800">{u.consumo_escaner.toLocaleString()} <span className="text-xs text-slate-400 font-medium">págs</span></strong>
                              <div className="w-full h-1 bg-slate-100 rounded-full mt-1 overflow-hidden">
                                <div className="h-full bg-green-500 rounded-full" style={{ width: `${u.consumo_total > 0 ? (u.consumo_escaner / u.consumo_total) * 100 : 0}%` }} />
                              </div>
                              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mt-1">
                                {u.consumo_total > 0 ? Math.round((u.consumo_escaner / u.consumo_total) * 100) : 0}% del total
                              </span>
                            </div>

                            {/* B/N vs Color Ratio */}
                            <div className="flex flex-col gap-1 p-4 bg-slate-50/50 rounded-2xl border border-slate-100 hover:bg-slate-50 transition-colors">
                              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Distribución Color</span>
                              <strong className="text-lg font-black text-slate-800">
                                {u.total_color.toLocaleString()} <span className="text-xs text-slate-400 font-medium">Color</span>{' '}
                                <span className="text-xs text-slate-300 font-normal">/</span>{' '}
                                <span className="text-sm font-bold text-slate-600">{u.total_bn.toLocaleString()} <span className="text-[10px] text-slate-400 font-normal">B/N</span></span>
                              </strong>
                              <div className="w-full h-1 bg-slate-100 rounded-full mt-1 overflow-hidden flex">
                                <div className="h-full bg-slate-400" style={{ width: `${u.consumo_total > 0 ? (u.total_bn / u.consumo_total) * 100 : 50}%` }} />
                                <div className="h-full bg-gradient-to-r from-pink-500 to-violet-500" style={{ width: `${u.consumo_total > 0 ? (u.total_color / u.consumo_total) * 100 : 50}%` }} />
                              </div>
                              <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mt-1 flex justify-between">
                                <span>B/N: {u.consumo_total > 0 ? Math.round((u.total_bn / u.consumo_total) * 100) : 0}%</span>
                                <span>Color: {u.consumo_total > 0 ? Math.round((u.total_color / u.consumo_total) * 100) : 0}%</span>
                              </span>
                            </div>
                          </div>

                          {/* Nested Sub-table of Printer Breakdown */}
                          <div className="flex flex-col gap-2">
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Detalle de Consumos por Impresora</span>

                            <div className="overflow-x-auto rounded-xl border border-slate-100">
                              <table className="w-full text-xs text-left">
                                <thead className="bg-slate-50 text-[9px] uppercase font-black tracking-widest text-slate-500 border-b border-slate-100">
                                  <tr>
                                    <th className="px-4 py-3">Impresora / Ubicación</th>
                                    <th className="px-4 py-3 text-center">Consumo del Período</th>
                                    <th className="px-4 py-3 text-center">Total Acumulado</th>
                                    <th className="px-4 py-3 text-center">B/N vs Color (Acumulado)</th>
                                    <th className="px-4 py-3 text-center">Funciones (Cop/Imp/Esc)</th>
                                    <th className="px-4 py-3 text-right">Acciones</th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                  {u.printers.map((pRecord) => (
                                    <tr key={pRecord.id} className="hover:bg-slate-50/40 transition-colors">
                                      <td className="px-4 py-3">
                                        <div className="font-bold text-slate-700">
                                          {pRecord.printer_serial && <span className="text-ricoh-red font-extrabold mr-1.5">{pRecord.printer_serial}</span>}
                                          {pRecord.printer_hostname}
                                        </div>
                                        <div className="text-[10px] text-slate-400 font-semibold">{pRecord.printer_ip} {pRecord.printer_location ? `· ${pRecord.printer_location}` : ''}</div>
                                        <div className="text-[10px] text-slate-400 font-medium mt-0.5">
                                          {pRecord.fecha_inicio === pRecord.fecha_fin
                                            ? `Cierre del ${formatDate(pRecord.fecha_fin)}`
                                            : `Período: ${formatDate(pRecord.fecha_inicio)} al ${formatDate(pRecord.fecha_fin)}`}
                                        </div>
                                      </td>
                                      <td className="px-4 py-3 text-center">
                                        <span className="inline-flex items-center px-2 py-0.5 rounded-full font-bold bg-red-50 text-ricoh-red">
                                          {pRecord.consumo_total.toLocaleString()} págs
                                        </span>
                                      </td>
                                      <td className="px-4 py-3 text-center font-bold text-slate-600">
                                        {pRecord.total_paginas.toLocaleString()} págs
                                      </td>
                                      <td className="px-4 py-3 text-center text-slate-500 font-semibold">
                                        <span>B/N: {pRecord.total_bn.toLocaleString()}</span>
                                        <span className="mx-1 text-slate-200">|</span>
                                        <span className="text-pink-600 font-bold">Col: {pRecord.total_color.toLocaleString()}</span>
                                      </td>
                                      <td className="px-4 py-3 text-center">
                                        <div className="flex justify-center gap-1.5 flex-wrap">
                                          <span className="px-1.5 py-0.5 rounded bg-slate-100 text-[9px] font-bold text-slate-500">Cop: {pRecord.consumo_copiadora}</span>
                                          <span className="px-1.5 py-0.5 rounded bg-slate-100 text-[9px] font-bold text-slate-500">Imp: {pRecord.consumo_impresora}</span>
                                          <span className="px-1.5 py-0.5 rounded bg-slate-100 text-[9px] font-bold text-slate-500">Esc: {pRecord.consumo_escaner}</span>
                                        </div>
                                      </td>
                                      <td className="px-4 py-3 text-right">
                                        <button
                                          type="button"
                                          onClick={() => handleOpenEdit(pRecord.rawRecord)}
                                          className="p-1.5 text-slate-400 hover:text-ricoh-red hover:bg-slate-50 rounded-lg transition-all"
                                          title="Editar consumo de este equipo"
                                        >
                                          <Edit2 size={14} />
                                        </button>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })
              ) : viewMode === 'area' ? (
                (() => {
                  const formatBN = (val: number) => {
                    return val.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                  };

                  const formatColor = (val: number) => {
                    return val.toLocaleString('es-CO', { maximumFractionDigits: 0 });
                  };

                  // Show loading state while dedicated area query loads
                  if (areaLoading && !areaConsumption?.items?.length) {
                    return (
                      <div className="flex flex-col items-center justify-center py-20 gap-3">
                        <Loader2 className="h-8 w-8 animate-spin text-ricoh-red" />
                        <p className="text-sm font-bold text-slate-500">Cargando consolidado completo...</p>
                        <p className="text-xs text-slate-400">Obteniendo todos los registros del período seleccionado</p>
                      </div>
                    );
                  }

                  return (
                    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
                      <table className="w-full border-collapse text-sm text-left">
                        <thead>
                          <tr className="bg-slate-800 text-white font-bold text-xs uppercase border-b border-slate-200">
                            <th className="px-6 py-3 border-r border-slate-700 text-left font-black tracking-wider w-[55%]">Etiquetas de fila</th>
                            <th className="px-6 py-3 border-r border-slate-700 text-left font-black tracking-wider w-[15%]">AREA</th>
                            <th className="px-6 py-3 border-r border-slate-700 text-right font-black tracking-wider w-[15%]">Suma de B/N</th>
                            <th className="px-6 py-3 text-right font-black tracking-wider w-[15%]">Suma de COLOR</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 font-sans text-slate-800">
                          {consolidatedHierarchy.map((company) => {
                            const isCompanyExpanded = expandedCompanies[company.companyName] ?? false;

                            // Render Company Row (Level 0)
                            const companyRow = (
                              <tr key={`company_${company.companyName}`} className="bg-slate-100/80 font-extrabold border-b border-slate-200">
                                <td className="px-4 py-3 border-r border-slate-200 text-left font-sans">
                                  <div className="flex items-center gap-1">
                                    <button
                                      type="button"
                                      onClick={() => toggleCompany(company.companyName)}
                                      className="p-1 hover:bg-slate-200 rounded text-slate-700 font-mono text-xs focus:outline-none"
                                    >
                                      {isCompanyExpanded ? '[-] ' : '[+] '}
                                    </button>
                                    <span className="uppercase tracking-wider text-slate-900">{company.companyName}</span>
                                  </div>
                                </td>
                                <td className="px-4 py-3 border-r border-slate-200"></td>
                                <td className="px-4 py-3 border-r border-slate-200 text-right font-mono text-slate-900 font-black">{formatBN(company.total_bn)}</td>
                                <td className="px-4 py-3 text-right font-mono text-slate-900 font-black">{formatColor(company.total_color)}</td>
                              </tr>
                            );

                            // If company is expanded, render Areas
                            const areaRows = isCompanyExpanded ? company.areas.map((area) => {
                              const areaKey = `${company.companyName}_${area.areaName}`;
                              const isAreaExpanded = expandedAreas[areaKey] ?? false;

                              // Render Area Row (Level 1)
                              const areaRow = (
                                <tr key={`area_${areaKey}`} className="hover:bg-slate-50/50 font-bold border-b border-slate-200">
                                  <td className="px-4 py-3 border-r border-slate-200"></td>
                                  <td className="px-4 py-3 border-r border-slate-200 text-left font-sans">
                                    <div className="flex items-center gap-1">
                                      <button
                                        type="button"
                                        onClick={() => toggleArea(company.companyName, area.areaName)}
                                        className="p-1 hover:bg-slate-200 rounded text-slate-700 font-mono text-xs focus:outline-none"
                                      >
                                        {isAreaExpanded ? '[-] ' : '[+] '}
                                      </button>
                                      <span className="uppercase text-slate-800">{area.areaName}</span>
                                    </div>
                                  </td>
                                  <td className="px-4 py-3 border-r border-slate-200 text-right font-mono text-slate-800">{formatBN(area.total_bn)}</td>
                                  <td className="px-4 py-3 text-right font-mono text-slate-800">{formatColor(area.total_color)}</td>
                                </tr>
                              );

                              // If area is expanded, render Users
                              const userRows = isAreaExpanded ? area.users.map((user) => {
                                const userKey = `${company.companyName}_${area.areaName}_${user.userId}`;
                                const isUserExpanded = expandedUsers[userKey] ?? false;

                                // Render User Row (Level 2) - Indented
                                const userRow = (
                                  <tr key={`user_${userKey}`} className="hover:bg-slate-50/30 border-b border-slate-200 text-xs">
                                    <td className="px-4 py-2.5 border-r border-slate-200"></td>
                                    <td className="px-4 py-2.5 border-r border-slate-200 text-left pl-6 font-sans">
                                      <div className="flex items-center gap-1">
                                        <button
                                          type="button"
                                          onClick={() => toggleUser(company.companyName, area.areaName, user.userId)}
                                          className="p-1 hover:bg-slate-200 rounded text-slate-600 font-mono text-xs focus:outline-none"
                                        >
                                          {isUserExpanded ? '[-] ' : '[+] '}
                                        </button>
                                        <span className="text-slate-700 font-bold">[{user.userName}]</span>
                                      </div>
                                    </td>
                                    <td className="px-4 py-2.5 border-r border-slate-200 text-right font-mono text-slate-700 font-semibold">{formatBN(user.total_bn)}</td>
                                    <td className="px-4 py-2.5 text-right font-mono text-slate-700 font-semibold">{formatColor(user.total_color)}</td>
                                  </tr>
                                );

                                // If user is expanded, render Printers
                                const printerRows = isUserExpanded ? user.printers.map((printer, idx) => {
                                  // Render Printer Row (Level 3) - Indented pl-12
                                  return (
                                    <tr key={`printer_${userKey}_${printer.printerId}_${idx}`} className="bg-slate-50/10 hover:bg-slate-100/20 border-b border-slate-100 text-[11px] text-slate-600">
                                      <td className="px-4 py-2 border-r border-slate-200"></td>
                                      <td className="px-4 py-2 border-r border-slate-200 text-left pl-12 font-sans">
                                        <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                                          {printer.serial && (
                                            <span className="text-ricoh-red font-black px-1.5 py-0.5 bg-red-50 rounded border border-red-100 text-[10px]">
                                              {printer.serial}
                                            </span>
                                          )}
                                          <span className="font-bold text-slate-700">{printer.hostname}</span>
                                          <span className="text-slate-400">({printer.ip}{printer.location ? ` - ${printer.location}` : ''})</span>
                                          <span className="text-[10px] text-slate-400 italic font-medium ml-auto">
                                            [{printer.fecha_inicio === printer.fecha_fin
                                              ? formatDate(printer.fecha_fin)
                                              : `${formatDate(printer.fecha_inicio)} al ${formatDate(printer.fecha_fin)}`}]
                                          </span>
                                        </div>
                                      </td>
                                      <td className="px-4 py-2 border-r border-slate-200 text-right font-mono text-slate-500">{formatBN(printer.total_bn)}</td>
                                      <td className="px-4 py-2 text-right font-mono text-slate-500">{formatColor(printer.total_color)}</td>
                                    </tr>
                                  );
                                }) : [];

                                return [userRow, ...printerRows];
                              }).flat() : [];

                              return [areaRow, ...userRows];
                            }).flat() : [];

                            return [companyRow, ...areaRows];
                          })}
                        </tbody>
                        {/* Grand Total Row */}
                        {consolidatedHierarchy.length > 0 && (() => {
                          const grandTotalBN = consolidatedHierarchy.reduce((s, c) => s + c.total_bn, 0);
                          const grandTotalColor = consolidatedHierarchy.reduce((s, c) => s + c.total_color, 0);
                          return (
                            <tfoot>
                              <tr className="bg-slate-900 text-white font-black text-sm border-t-2 border-slate-700">
                                <td className="px-6 py-4 border-r border-slate-700 tracking-wider uppercase">Total general</td>
                                <td className="px-4 py-4 border-r border-slate-700"></td>
                                <td className="px-4 py-4 border-r border-slate-700 text-right font-mono text-lg">{formatBN(grandTotalBN)}</td>
                                <td className="px-4 py-4 text-right font-mono text-lg">{formatColor(grandTotalColor)}</td>
                              </tr>
                            </tfoot>
                          );
                        })()}
                      </table>
                      {/* Data completeness badge */}
                      <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
                        {areaLoading ? (
                          <div className="flex items-center gap-2 text-xs text-slate-500">
                            <Loader2 className="h-3 w-3 animate-spin" />
                            <span>Actualizando datos...</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2 text-[10px] text-slate-400 font-semibold">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            <span>
                              {areaConsumption?.total
                                ? `Consolidando ${areaConsumption.total.toLocaleString()} registro${areaConsumption.total !== 1 ? 's' : ''} completos del período`
                                : 'Datos consolidados'}
                              {areaConsumption?.total > 1000 && (
                                <span className="text-amber-500 ml-2 font-bold">· Mostrando primeros 1.000 registros</span>
                              )}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })()
              ) : (
                groupedCierres.map((g) => {
                  const expanded = expandedCierres[g.cierre_mensual_id] ?? true;
                  return (
                    <div key={g.cierre_mensual_id} className="rounded-xl border border-slate-100 overflow-hidden">
                      <button
                        type="button"
                        onClick={() => toggleCierre(g.cierre_mensual_id)}
                        className="w-full bg-slate-50 px-5 py-4 flex items-start sm:items-center justify-between gap-4 text-left hover:bg-slate-100 transition-colors"
                      >
                        <div className="min-w-0">
                          <div className="font-black text-slate-800 truncate">
                            {g.printer_serial && <span className="text-ricoh-red font-extrabold mr-1.5">{g.printer_serial}</span>}
                            {g.printer_hostname} <span className="text-slate-400 font-bold">·</span>{' '}
                            <span className="text-slate-600 font-semibold text-xs bg-slate-100 px-2 py-0.5 rounded">{g.printer_ip}</span>
                          </div>
                          <div className="text-xs text-slate-500 font-semibold truncate">
                            {g.printer_location || 'Ubicación no definida'} · {g.fecha_inicio === g.fecha_fin ? `Cierre del ${formatDate(g.fecha_fin)}` : `Período del ${formatDate(g.fecha_inicio)} al ${formatDate(g.fecha_fin)}`}
                          </div>
                          <div className="text-[11px] text-slate-400 mt-1">
                            Cierre: {new Date(g.fecha_cierre).toLocaleDateString()} · Usuarios: {g.users.length} · Consumo total:{' '}
                            <span className="font-bold text-slate-600">{g.total_consumo.toLocaleString()} págs</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-[10px] font-black uppercase tracking-widest text-slate-500 hidden sm:inline">
                            {expanded ? 'Ocultar' : 'Ver'} usuarios
                          </span>
                          <ChevronDown
                            size={18}
                            className={cn('text-slate-400 transition-transform', expanded ? 'rotate-180' : 'rotate-0')}
                          />
                        </div>
                      </button>

                      {expanded && (
                        <div className="overflow-x-auto bg-white">
                          <table className="w-full text-sm text-left">
                            <thead className="bg-white text-[10px] uppercase font-black tracking-widest text-slate-500 border-t border-slate-100">
                              <tr>
                                <th className="px-5 py-4">Usuario</th>
                                <th className="px-5 py-4 text-center">Consumo Período</th>
                                <th className="px-5 py-4 text-center">Total Acumulado</th>
                                <th className="px-5 py-4 text-center hidden md:table-cell">B/N Acumulado</th>
                                <th className="px-5 py-4 text-center hidden md:table-cell">Color Acumulado</th>
                                <th className="px-5 py-4 text-right">Acciones</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {g.users.map((record) => (
                                <React.Fragment key={record.id}>
                                  <tr
                                    onClick={() => toggleUserRow(record.id)}
                                    className="hover:bg-slate-50/30 transition-colors cursor-pointer"
                                  >
                                    <td className="px-5 py-4">
                                      <div className="flex items-center gap-2">
                                        <ChevronDown
                                          size={16}
                                          className={cn("text-slate-400 transition-transform shrink-0", expandedUserRows[record.id] ? "rotate-180" : "rotate-0")}
                                        />
                                        <div>
                                          <div className="flex items-center gap-2">
                                            <span className="font-bold text-slate-800">{record.nombre_usuario}</span>
                                            {record.centro_costos && (
                                              <span className="text-[9px] font-black uppercase tracking-widest text-ricoh-red bg-red-50 px-2 py-0.5 rounded-md truncate max-w-[150px]" title={record.centro_costos}>
                                                {record.centro_costos}
                                              </span>
                                            )}
                                          </div>
                                          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{record.codigo_usuario}</div>
                                        </div>
                                      </div>
                                    </td>
                                    <td className="px-5 py-4 text-center">
                                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700">
                                        {record.consumo_total.toLocaleString()} págs
                                      </span>
                                    </td>
                                    <td className="px-5 py-4 text-center font-semibold text-slate-600">
                                      {record.total_paginas.toLocaleString()} págs
                                    </td>
                                    <td className="px-5 py-4 text-center hidden md:table-cell text-slate-600 font-semibold">
                                      {record.total_bn.toLocaleString()}
                                    </td>
                                    <td className="px-5 py-4 text-center hidden md:table-cell text-slate-600 font-semibold">
                                      {record.total_color.toLocaleString()}
                                    </td>
                                    <td className="px-5 py-4 text-right" onClick={(e) => e.stopPropagation()}>
                                      <button
                                        onClick={() => handleOpenEdit(record)}
                                        className="p-2 text-slate-400 hover:text-ricoh-red hover:bg-slate-50 rounded-lg transition-all"
                                        title="Editar consumo"
                                      >
                                        <Edit2 size={16} />
                                      </button>
                                    </td>
                                  </tr>
                                  {expandedUserRows[record.id] && (
                                    <tr className="bg-slate-50/40">
                                      <td colSpan={6} className="px-5 py-4 border-t border-slate-100">
                                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-white/70 backdrop-blur-md rounded-2xl border border-slate-100 shadow-sm animate-scale-in">

                                          {/* Copiadora */}
                                          <div className="flex flex-col gap-1 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Copiadora</div>
                                            <div className="text-sm font-black text-slate-700">{(record.consumo_copiadora || 0).toLocaleString()} págs</div>
                                            <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider flex justify-between mt-1">
                                              <span>B/N: {(record.copiadora_bn || 0).toLocaleString()}</span>
                                              <span>Color: {(record.copiadora_color || 0).toLocaleString()}</span>
                                            </div>
                                          </div>

                                          {/* Impresora */}
                                          <div className="flex flex-col gap-1 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Impresora</div>
                                            <div className="text-sm font-black text-slate-700">{(record.consumo_impresora || 0).toLocaleString()} págs</div>
                                            <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider flex justify-between mt-1">
                                              <span>B/N: {(record.impresora_bn || 0).toLocaleString()}</span>
                                              <span>Color: {(record.impresora_color || 0).toLocaleString()}</span>
                                            </div>
                                          </div>

                                          {/* Escáner */}
                                          <div className="flex flex-col gap-1 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Escáner</div>
                                            <div className="text-sm font-black text-slate-700">{(record.consumo_escaner || 0).toLocaleString()} págs</div>
                                            <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider flex justify-between mt-1">
                                              <span>B/N: {(record.escaner_bn || 0).toLocaleString()}</span>
                                              <span>Color: {(record.escaner_color || 0).toLocaleString()}</span>
                                            </div>
                                          </div>

                                          {/* Fax & Totales */}
                                          <div className="flex flex-col gap-1 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Fax</div>
                                            <div className="text-sm font-black text-slate-700">{(record.consumo_fax || 0).toLocaleString()} págs</div>
                                            <div className="text-[9px] text-slate-400 font-bold uppercase tracking-wider flex justify-between mt-1">
                                              <span>B/N: {(record.fax_bn || 0).toLocaleString()}</span>
                                              <span>Color: 0</span>
                                            </div>
                                          </div>

                                        </div>
                                      </td>
                                    </tr>
                                  )}
                                </React.Fragment>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* Pagination */}
          {globalUserConsumption && globalUserConsumption.pages > 1 && (
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-slate-100">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Página {userPage} de {globalUserConsumption.pages} ({globalUserConsumption.total} registros)
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setUserPage((prev) => Math.max(prev - 1, 1))}
                  disabled={userPage === 1}
                  className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-transparent transition-all"
                >
                  <ChevronLeft size={16} />
                </button>
                <button
                  onClick={() => setUserPage((prev) => Math.min(prev + 1, globalUserConsumption.pages))}
                  disabled={userPage === globalUserConsumption.pages}
                  className="p-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:hover:bg-transparent transition-all"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Editing Modal */}
      {editingRecord && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-100 max-w-md w-full p-6 relative animate-scale-in">
            {/* Close Button */}
            <button
              onClick={() => setEditingRecord(null)}
              className="absolute right-4 top-4 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X size={18} />
            </button>

            <h3 className="text-base font-black text-slate-800 mb-2">Modificar Consumo de Cierre</h3>

            {/* Info Card */}
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100 mb-6 text-xs text-slate-600 flex flex-col gap-1.5">
              <div>
                <span className="font-bold text-slate-800">Usuario: </span>
                {editingRecord.nombre_usuario} ({editingRecord.codigo_usuario})
              </div>
              <div>
                <span className="font-bold text-slate-800">Impresora: </span>
                {editingRecord.printer_hostname}
              </div>
              {editingRecord.printer_ip && (
                <div>
                  <span className="font-bold text-slate-800">Dirección IP: </span>
                  {editingRecord.printer_ip}
                </div>
              )}
              {editingRecord.printer_location && (
                <div>
                  <span className="font-bold text-slate-800">Ubicación: </span>
                  {editingRecord.printer_location}
                </div>
              )}
              <div className="mt-1 pt-1.5 border-t border-slate-200 text-slate-400 font-semibold uppercase tracking-wider text-[9px]">
                Período: {editingRecord.fecha_inicio} al {editingRecord.fecha_fin}
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSaveEdit} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1">
                <label className="text-xs font-black text-slate-600 uppercase tracking-widest">
                  Consumo del Período (Páginas)
                </label>
                <input
                  type="number"
                  min="0"
                  required
                  value={editConsumo}
                  onChange={(e) => setEditConsumo(parseInt(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red font-semibold text-slate-700"
                />
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs font-black text-slate-600 uppercase tracking-widest">
                  Total Acumulado al Cierre (Páginas)
                </label>
                <input
                  type="number"
                  min="0"
                  required
                  value={editTotal}
                  onChange={(e) => setEditTotal(parseInt(e.target.value) || 0)}
                  className="w-full px-4 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red/20 focus:border-ricoh-red font-semibold text-slate-700"
                />
              </div>

              {saveErrorMsg && (
                <div className="text-xs font-bold text-red-600 bg-red-50 border border-red-100 rounded-xl p-3">
                  {saveErrorMsg}
                </div>
              )}

              {saveSuccessMsg && (
                <div className="text-xs font-bold text-green-600 bg-green-50 border border-green-100 rounded-xl p-3">
                  {saveSuccessMsg}
                </div>
              )}

              <div className="flex gap-3 justify-end mt-4">
                <button
                  type="button"
                  onClick={() => setEditingRecord(null)}
                  className="px-4 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={updateMutation.isPending || !!saveSuccessMsg}
                  className="bg-ricoh-red hover:bg-red-700 text-white disabled:bg-slate-300 font-bold text-xs uppercase tracking-widest px-4 py-2.5 rounded-xl transition-all flex items-center justify-center gap-2"
                >
                  {updateMutation.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  Guardar Cambios
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsPage;
