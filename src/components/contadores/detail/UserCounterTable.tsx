import { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import type { UserCounter } from '@/types/counter';
import type { PrinterDevice } from '@/types';
import { useColumnVisibility } from '@/hooks/useColumnVisibility';
import type { ColumnDefinition } from '@/types/printer';

interface UserCounterTableProps {
  userCounters: UserCounter[];
  printer?: PrinterDevice;
}

type SortField = 'codigo' | 'nombre' | 'total_paginas' | 'total_bn' | 'total_color' |
  'copiadora_bn' | 'copiadora_mono_color' | 'copiadora_dos_colores' | 'copiadora_todo_color' | 'copiadora_hojas_2_caras' | 'copiadora_paginas_combinadas' |
  'impresora_bn' | 'impresora_mono_color' | 'impresora_dos_colores' | 'impresora_color' | 'impresora_hojas_2_caras' | 'impresora_paginas_combinadas' |
  'escaner_bn' | 'escaner_todo_color';
type SortDirection = 'asc' | 'desc';

// Column definitions with groups for visibility control
const COLUMN_DEFINITIONS: ColumnDefinition[] = [
  // Basic columns (always visible)
  { key: 'codigo', label: 'Código', group: 'basic', alwaysVisible: true },
  { key: 'nombre', label: 'Nombre', group: 'basic', alwaysVisible: true },
  { key: 'total_paginas', label: 'Total', group: 'basic', alwaysVisible: true },
  { key: 'total_bn', label: 'B/N', group: 'basic', alwaysVisible: true },
  { key: 'total_color', label: 'Color', group: 'color' },
  
  // Copiadora columns
  { key: 'copiadora_bn', label: 'B/N', group: 'basic', alwaysVisible: true },
  { key: 'copiadora_mono_color', label: 'Mono', group: 'mono_color' },
  { key: 'copiadora_dos_colores', label: '2 Col', group: 'dos_colores' },
  { key: 'copiadora_todo_color', label: 'Todo', group: 'color' },
  { key: 'copiadora_hojas_2_caras', label: '2 Caras', group: 'hojas_2_caras' },
  { key: 'copiadora_paginas_combinadas', label: 'Comb', group: 'paginas_combinadas' },
  
  // Impresora columns
  { key: 'impresora_bn', label: 'B/N', group: 'basic', alwaysVisible: true },
  { key: 'impresora_mono_color', label: 'Mono', group: 'mono_color' },
  { key: 'impresora_dos_colores', label: '2 Col', group: 'dos_colores' },
  { key: 'impresora_color', label: 'Color', group: 'color' },
  { key: 'impresora_hojas_2_caras', label: '2 Caras', group: 'hojas_2_caras' },
  { key: 'impresora_paginas_combinadas', label: 'Comb', group: 'paginas_combinadas' },
  
  // Escáner columns
  { key: 'escaner_bn', label: 'B/N', group: 'basic', alwaysVisible: true },
  { key: 'escaner_todo_color', label: 'Color', group: 'color' },
];

export const UserCounterTable: React.FC<UserCounterTableProps> = ({ userCounters, printer }) => {
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<SortField>('total_paginas');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  // Get column visibility based on printer capabilities
  const { isColumnVisible, isGroupHeaderVisible } = useColumnVisibility(printer?.capabilities);
  
  // Determine if printer uses ecological format
  const isEcologicalFormat = printer?.capabilities?.formato_contadores === 'ecologico';

  // Helper to check if a column should be shown
  const shouldShowColumn = (key: string): boolean => {
    // For ecological format, only show basic columns
    if (isEcologicalFormat) {
      return ['codigo', 'nombre', 'total_paginas'].includes(key);
    }
    
    const col = COLUMN_DEFINITIONS.find(c => c.key === key);
    if (!col) return true;
    if (col.alwaysVisible) return true;
    return isColumnVisible(col.group);
  };

  // Calculate visible column counts for group headers
  const getGroupColSpan = (group: 'total' | 'copiadora' | 'impresora' | 'escaner'): number => {
    let count = 0;
    if (group === 'total') {
      if (shouldShowColumn('total_paginas')) count++;
      if (shouldShowColumn('total_bn')) count++;
      if (shouldShowColumn('total_color')) count++;
    } else if (group === 'copiadora') {
      if (shouldShowColumn('copiadora_bn')) count++;
      if (shouldShowColumn('copiadora_mono_color')) count++;
      if (shouldShowColumn('copiadora_dos_colores')) count++;
      if (shouldShowColumn('copiadora_todo_color')) count++;
      if (shouldShowColumn('copiadora_hojas_2_caras')) count++;
      if (shouldShowColumn('copiadora_paginas_combinadas')) count++;
    } else if (group === 'impresora') {
      if (shouldShowColumn('impresora_bn')) count++;
      if (shouldShowColumn('impresora_mono_color')) count++;
      if (shouldShowColumn('impresora_dos_colores')) count++;
      if (shouldShowColumn('impresora_color')) count++;
      if (shouldShowColumn('impresora_hojas_2_caras')) count++;
      if (shouldShowColumn('impresora_paginas_combinadas')) count++;
    } else if (group === 'escaner') {
      if (shouldShowColumn('escaner_bn')) count++;
      if (shouldShowColumn('escaner_todo_color')) count++;
    }
    return count;
  };

  // Filter
  const filtered = useMemo(() => {
    return userCounters.filter(user =>
      user.nombre_usuario.toLowerCase().includes(search.toLowerCase()) ||
      user.codigo_usuario.toLowerCase().includes(search.toLowerCase())
    );
  }, [userCounters, search]);

  // Sort
  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      let aVal: any, bVal: any;
      
      if (sortField === 'codigo') {
        aVal = a.codigo_usuario;
        bVal = b.codigo_usuario;
      } else if (sortField === 'nombre') {
        aVal = a.nombre_usuario;
        bVal = b.nombre_usuario;
      } else {
        // For numeric fields, access directly
        aVal = a[sortField];
        bVal = b[sortField];
      }
      
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filtered, sortField, sortDirection]);

  // Paginate
  const totalPages = Math.ceil(sorted.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginated = sorted.slice(startIndex, startIndex + itemsPerPage);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Reset to page 1 when search changes
  useMemo(() => {
    setCurrentPage(1);
  }, [search]);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200">
      {/* Header with search */}
      <div className="p-4 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-700">Contadores por Usuario</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={16} />
            <input
              type="text"
              placeholder="Buscar usuario..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red"
              aria-label="Buscar usuario por nombre o código"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      {paginated.length === 0 ? (
        <div className="p-8 text-center text-slate-400">
          No se encontraron usuarios
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                {/* Group headers */}
                <tr className="border-b border-slate-300">
                  <th rowSpan={2} className="px-3 py-2 text-left text-xs font-bold uppercase text-slate-600 border-r border-slate-300 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('codigo')}>
                    Código {sortField === 'codigo' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  <th rowSpan={2} className="px-3 py-2 text-left text-xs font-bold uppercase text-slate-600 border-r border-slate-300 cursor-pointer hover:bg-slate-100" onClick={() => handleSort('nombre')}>
                    Nombre {sortField === 'nombre' && (sortDirection === 'asc' ? '↑' : '↓')}
                  </th>
                  {getGroupColSpan('total') > 0 && (
                    <th colSpan={getGroupColSpan('total')} className="px-3 py-2 text-center text-xs font-bold uppercase text-slate-600 border-r border-slate-300 bg-slate-100">
                      Total
                    </th>
                  )}
                  {getGroupColSpan('copiadora') > 0 && (
                    <th colSpan={getGroupColSpan('copiadora')} className="px-3 py-2 text-center text-xs font-bold uppercase text-slate-600 border-r border-slate-300 bg-blue-50">
                      Copiadora
                    </th>
                  )}
                  {getGroupColSpan('impresora') > 0 && (
                    <th colSpan={getGroupColSpan('impresora')} className="px-3 py-2 text-center text-xs font-bold uppercase text-slate-600 border-r border-slate-300 bg-green-50">
                      Impresora
                    </th>
                  )}
                  {getGroupColSpan('escaner') > 0 && (
                    <th colSpan={getGroupColSpan('escaner')} className="px-3 py-2 text-center text-xs font-bold uppercase text-slate-600 bg-purple-50">
                      Escáner
                    </th>
                  )}
                </tr>
                {/* Sub-headers */}
                <tr className="border-b border-slate-200">
                  {shouldShowColumn('total_paginas') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-slate-100 cursor-pointer hover:bg-slate-200" onClick={() => handleSort('total_paginas')}>
                      Total {sortField === 'total_paginas' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('total_bn') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-slate-100 cursor-pointer hover:bg-slate-200" onClick={() => handleSort('total_bn')}>
                      B/N {sortField === 'total_bn' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('total_color') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-slate-100 border-r border-slate-300 cursor-pointer hover:bg-slate-200" onClick={() => handleSort('total_color')}>
                      Color {sortField === 'total_color' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('copiadora_bn') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-blue-50 cursor-pointer hover:bg-blue-100" onClick={() => handleSort('copiadora_bn')}>
                      B/N {sortField === 'copiadora_bn' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('copiadora_mono_color') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-blue-50 cursor-pointer hover:bg-blue-100" onClick={() => handleSort('copiadora_mono_color')}>
                      Mono {sortField === 'copiadora_mono_color' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('copiadora_dos_colores') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-blue-50 cursor-pointer hover:bg-blue-100" onClick={() => handleSort('copiadora_dos_colores')}>
                      2 Col {sortField === 'copiadora_dos_colores' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('copiadora_todo_color') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-blue-50 cursor-pointer hover:bg-blue-100" onClick={() => handleSort('copiadora_todo_color')}>
                      Todo {sortField === 'copiadora_todo_color' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('copiadora_hojas_2_caras') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-blue-50 cursor-pointer hover:bg-blue-100" onClick={() => handleSort('copiadora_hojas_2_caras')}>
                      2 Caras {sortField === 'copiadora_hojas_2_caras' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('copiadora_paginas_combinadas') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-blue-50 border-r border-slate-300 cursor-pointer hover:bg-blue-100" onClick={() => handleSort('copiadora_paginas_combinadas')}>
                      Comb {sortField === 'copiadora_paginas_combinadas' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('impresora_bn') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-green-50 cursor-pointer hover:bg-green-100" onClick={() => handleSort('impresora_bn')}>
                      B/N {sortField === 'impresora_bn' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('impresora_mono_color') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-green-50 cursor-pointer hover:bg-green-100" onClick={() => handleSort('impresora_mono_color')}>
                      Mono {sortField === 'impresora_mono_color' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('impresora_dos_colores') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-green-50 cursor-pointer hover:bg-green-100" onClick={() => handleSort('impresora_dos_colores')}>
                      2 Col {sortField === 'impresora_dos_colores' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('impresora_color') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-green-50 cursor-pointer hover:bg-green-100" onClick={() => handleSort('impresora_color')}>
                      Color {sortField === 'impresora_color' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('impresora_hojas_2_caras') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-green-50 cursor-pointer hover:bg-green-100" onClick={() => handleSort('impresora_hojas_2_caras')}>
                      2 Caras {sortField === 'impresora_hojas_2_caras' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('impresora_paginas_combinadas') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-green-50 border-r border-slate-300 cursor-pointer hover:bg-green-100" onClick={() => handleSort('impresora_paginas_combinadas')}>
                      Comb {sortField === 'impresora_paginas_combinadas' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('escaner_bn') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-purple-50 cursor-pointer hover:bg-purple-100" onClick={() => handleSort('escaner_bn')}>
                      B/N {sortField === 'escaner_bn' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                  {shouldShowColumn('escaner_todo_color') && (
                    <th className="px-2 py-2 text-right text-xs font-bold text-slate-600 bg-purple-50 cursor-pointer hover:bg-purple-100" onClick={() => handleSort('escaner_todo_color')}>
                      Color {sortField === 'escaner_todo_color' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                  )}
                </tr>
              </thead>
              <tbody>
                {paginated.map((user, index) => (
                  <tr key={user.id} className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50'}>
                    <td className="px-3 py-2 text-slate-900 border-r border-slate-200">{user.codigo_usuario}</td>
                    <td className="px-3 py-2 text-slate-900 border-r border-slate-200">{user.nombre_usuario}</td>
                    {shouldShowColumn('total_paginas') && (
                      <td className="px-2 py-2 text-slate-900 text-right font-semibold bg-slate-50">
                        {user.total_paginas.toLocaleString()}
                      </td>
                    )}
                    {shouldShowColumn('total_bn') && (
                      <td className="px-2 py-2 text-slate-600 text-right bg-slate-50">
                        {user.total_bn.toLocaleString()}
                      </td>
                    )}
                    {shouldShowColumn('total_color') && (
                      <td className="px-2 py-2 text-slate-600 text-right border-r border-slate-200 bg-slate-50">
                        {user.total_color.toLocaleString()}
                      </td>
                    )}
                    {shouldShowColumn('copiadora_bn') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.copiadora_bn.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('copiadora_mono_color') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.copiadora_mono_color.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('copiadora_dos_colores') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.copiadora_dos_colores.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('copiadora_todo_color') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.copiadora_todo_color.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('copiadora_hojas_2_caras') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.copiadora_hojas_2_caras.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('copiadora_paginas_combinadas') && (
                      <td className="px-2 py-2 text-slate-600 text-right border-r border-slate-200">{user.copiadora_paginas_combinadas.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('impresora_bn') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.impresora_bn.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('impresora_mono_color') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.impresora_mono_color.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('impresora_dos_colores') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.impresora_dos_colores.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('impresora_color') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.impresora_color.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('impresora_hojas_2_caras') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.impresora_hojas_2_caras.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('impresora_paginas_combinadas') && (
                      <td className="px-2 py-2 text-slate-600 text-right border-r border-slate-200">{user.impresora_paginas_combinadas.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('escaner_bn') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.escaner_bn.toLocaleString()}</td>
                    )}
                    {shouldShowColumn('escaner_todo_color') && (
                      <td className="px-2 py-2 text-slate-600 text-right">{user.escaner_todo_color.toLocaleString()}</td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="p-4 border-t border-slate-200 flex items-center justify-between">
              <div className="text-sm text-slate-500">
                Mostrando {startIndex + 1}-{Math.min(startIndex + itemsPerPage, sorted.length)} de {sorted.length}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 text-sm font-bold rounded-lg border border-slate-300 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Página anterior"
                >
                  ← Anterior
                </button>
                <span className="px-3 py-1 text-sm font-bold text-slate-700">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 text-sm font-bold rounded-lg border border-slate-300 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Página siguiente"
                >
                  Siguiente →
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
