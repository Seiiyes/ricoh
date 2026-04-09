/**
 * Table Component
 * 
 * Componente de tabla reutilizable con sorting, paginación y búsqueda.
 * 
 * @created 2026-03-18
 * @author Kiro AI
 */

import React, { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown, Search } from 'lucide-react';

export interface Column<T> {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

export interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string | number;
  sortable?: boolean;
  searchable?: boolean;
  searchPlaceholder?: string;
  pagination?: boolean;
  pageSize?: number;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  className?: string;
}

type SortDirection = 'asc' | 'desc' | null;

export function Table<T extends Record<string, any>>({
  columns,
  data,
  keyExtractor,
  sortable = true,
  searchable = false,
  searchPlaceholder = 'Buscar...',
  pagination = false,
  pageSize = 10,
  onRowClick,
  emptyMessage = 'No hay datos disponibles',
  className = '',
}: TableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  // Filtrar datos por búsqueda
  const filteredData = useMemo(() => {
    if (!searchable || !searchTerm.trim()) return data;

    const searchLower = searchTerm.toLowerCase();
    return data.filter((row) =>
      columns.some((col) => {
        const value = row[col.key];
        return value?.toString().toLowerCase().includes(searchLower);
      })
    );
  }, [data, searchTerm, searchable, columns]);

  // Ordenar datos
  const sortedData = useMemo(() => {
    if (!sortKey || !sortDirection) return filteredData;

    return [...filteredData].sort((a, b) => {
      const aValue = a[sortKey];
      const bValue = b[sortKey];

      if (aValue === bValue) return 0;

      const comparison = aValue < bValue ? -1 : 1;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [filteredData, sortKey, sortDirection]);

  // Paginar datos
  const paginatedData = useMemo(() => {
    if (!pagination) return sortedData;

    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return sortedData.slice(startIndex, endIndex);
  }, [sortedData, pagination, currentPage, pageSize]);

  const totalPages = Math.ceil(sortedData.length / pageSize);

  // Manejar click en header para ordenar
  const handleSort = (key: string) => {
    if (!sortable) return;

    if (sortKey === key) {
      // Ciclo: asc -> desc -> null
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortKey(null);
        setSortDirection(null);
      }
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  // Resetear página cuando cambia la búsqueda
  React.useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Búsqueda */}
      {searchable && (
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder={searchPlaceholder}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50/50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent text-sm transition-all shadow-sm hover:bg-white"
          />
        </div>
      )}

      {/* Tabla */}
      <div className="overflow-x-auto overflow-y-auto max-h-[70vh] bg-white rounded-2xl shadow-xl border border-slate-100 transition-shadow hover:shadow-2xl duration-300">
        <table className="w-full relative">
          <thead className="sticky top-0 z-10 bg-slate-50/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider ${
                    column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                  } ${sortable && column.sortable !== false ? 'cursor-pointer hover:bg-slate-100/50 transition-colors' : ''}`}
                  style={{ width: column.width }}
                  onClick={() => column.sortable !== false && handleSort(column.key)}
                >
                  <div className="flex items-center gap-2">
                    <span>{column.label}</span>
                    {sortable && column.sortable !== false && (
                      <span className="text-slate-400">
                        {sortKey === column.key ? (
                          sortDirection === 'asc' ? (
                            <ChevronUp size={16} />
                          ) : (
                            <ChevronDown size={16} />
                          )
                        ) : (
                          <ChevronsUpDown size={16} />
                        )}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-100">
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-8 text-center text-slate-500">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((row) => (
                <tr
                  key={keyExtractor(row)}
                  className={`${onRowClick ? 'cursor-pointer hover:bg-blue-50/50 active:bg-blue-100/50' : 'hover:bg-slate-50/70'} transition-all duration-200 group`}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={`px-6 py-4 text-sm text-slate-800 font-medium group-hover:text-slate-900 transition-colors ${
                        column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                      }`}
                    >
                      {column.render ? column.render(row[column.key], row) : row[column.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      {pagination && totalPages > 1 && (
        <div className="flex items-center justify-between px-2 pt-2">
          <div className="text-sm text-slate-500 font-medium">
            Mostrando {(currentPage - 1) * pageSize + 1}-{Math.min(currentPage * pageSize, sortedData.length)} de {sortedData.length}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 text-sm font-semibold rounded-xl border border-slate-200 bg-white shadow-sm hover:bg-slate-50 hover:text-ricoh-red disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
            >
              ← Anterior
            </button>
            <span className="text-sm font-semibold text-slate-700 px-2">
              Página <span className="text-ricoh-red">{currentPage}</span> de {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 text-sm font-semibold rounded-xl border border-slate-200 bg-white shadow-sm hover:bg-slate-50 hover:text-ricoh-red disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
            >
              Siguiente →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
