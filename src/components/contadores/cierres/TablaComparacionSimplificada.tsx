import React from 'react';

interface Usuario {
  codigo_usuario: string;
  nombre_usuario: string;
  consumo_cierre1: number;
  consumo_cierre2: number;
  diferencia: number;
  diferencia_bn: number;
  diferencia_color: number;
  
  // Período 1 - Desglose completo
  total_paginas_cierre1: number;
  copiadora_bn_cierre1: number;
  copiadora_color_cierre1: number;
  impresora_bn_cierre1: number;
  impresora_color_cierre1: number;
  escaner_bn_cierre1: number;
  escaner_color_cierre1: number;
  
  // Período 2 - Desglose completo
  total_paginas_cierre2: number;
  copiadora_bn_cierre2: number;
  copiadora_color_cierre2: number;
  impresora_bn_cierre2: number;
  impresora_color_cierre2: number;
  escaner_bn_cierre2: number;
  escaner_color_cierre2: number;
  
  // Diferencias calculadas
  difCopia: number;
  difImpre: number;
  difEscan: number;
  difCopiaBN: number;
  difCopiaColor: number;
  difImpreBN: number;
  difImpreColor: number;
  difEscanBN: number;
  difEscanColor: number;
}

interface Props {
  usuarios: Usuario[];
  onSort: (key: string) => void;
  sortKey: string;
  sortDir: 'asc' | 'desc';
  hasColor: boolean;
}

export const TablaComparacionSimplificada: React.FC<Props> = ({ usuarios, onSort, sortKey, sortDir, hasColor }) => {
  const fmt = (n: number) => n.toLocaleString('es-ES');
  const fmtDiff = (n: number) => {
    if (n === 0) return '0';
    return `${n >= 0 ? '+' : ''}${fmt(n)}`;
  };
  const diffColor = (n: number) => 
    n > 0 ? 'text-emerald-600 font-semibold' : 
    n < 0 ? 'text-red-500 font-semibold' : 
    'text-gray-400';

  const SortIcon = ({ active, dir }: { active: boolean; dir: 'asc' | 'desc' }) => (
    <span className={`ml-1 inline-flex flex-col leading-none ${active ? 'text-current' : 'text-gray-300'}`}>
      <span style={{ fontSize: 8, lineHeight: '9px' }}>{!active || dir === 'asc' ? '▲' : ''}</span>
      <span style={{ fontSize: 8, lineHeight: '9px' }}>{!active || dir === 'desc' ? '▼' : ''}</span>
    </span>
  );

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse">
        <thead>
          {/* Fila 1: Secciones principales */}
          <tr className="border-b-2 border-gray-300">
            <th 
              rowSpan={3} 
              className="px-4 py-3 text-left text-sm font-bold text-gray-800 bg-white sticky left-0 z-20 border-r-2 border-gray-300 min-w-[200px] cursor-pointer hover:bg-gray-100"
              onClick={() => onSort('nombre')}
            >
              Usuario <SortIcon active={sortKey === 'nombre'} dir={sortDir} />
            </th>
            <th 
              rowSpan={3} 
              className="px-4 py-3 text-center text-sm font-bold text-gray-800 bg-white sticky left-[200px] z-20 border-r-2 border-gray-300 min-w-[100px] cursor-pointer hover:bg-gray-100"
              onClick={() => onSort('codigo')}
            >
              Código <SortIcon active={sortKey === 'codigo'} dir={sortDir} />
            </th>
            <th colSpan={hasColor ? 7 : 4} className="px-4 py-3 text-center text-sm font-bold text-blue-900 bg-blue-50 border-x border-gray-300">
              Período Base (Contadores Acumulados)
            </th>
            <th colSpan={hasColor ? 7 : 4} className="px-4 py-3 text-center text-sm font-bold text-purple-900 bg-purple-50 border-x border-gray-300">
              Período Comparado (Contadores Acumulados)
            </th>
            <th colSpan={hasColor ? 7 : 4} className="px-4 py-3 text-center text-sm font-bold text-emerald-900 bg-emerald-50 border-l-2 border-gray-400">
              Consumo del Período (Diferencias)
            </th>
          </tr>
          {/* Fila 2: Funciones */}
          <tr className="border-b border-gray-300">
            {/* Base */}
            <th 
              rowSpan={2}
              className="px-3 py-2 text-center text-xs font-semibold text-blue-800 bg-blue-50/50 border-l border-gray-300 cursor-pointer hover:bg-blue-100"
              onClick={() => onSort('total1')}
            >
              Total <SortIcon active={sortKey === 'total1'} dir={sortDir} />
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-blue-800 bg-blue-50/50 border-l border-gray-200">
              📋 Copiadora
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-blue-800 bg-blue-50/50 border-l border-gray-200">
              🖨️ Impresora
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-blue-800 bg-blue-50/50 border-l border-gray-200">
              📷 Escáner
            </th>
            
            {/* Comparado */}
            <th 
              rowSpan={2}
              className="px-3 py-2 text-center text-xs font-semibold text-purple-800 bg-purple-50/50 border-l border-gray-300 cursor-pointer hover:bg-purple-100"
              onClick={() => onSort('total2')}
            >
              Total <SortIcon active={sortKey === 'total2'} dir={sortDir} />
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-purple-800 bg-purple-50/50 border-l border-gray-200">
              📋 Copiadora
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-purple-800 bg-purple-50/50 border-l border-gray-200">
              🖨️ Impresora
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-purple-800 bg-purple-50/50 border-l border-gray-200 border-r border-gray-300">
              📷 Escáner
            </th>
            
            {/* Diferencias */}
            <th 
              rowSpan={2}
              className="px-3 py-2 text-center text-xs font-semibold text-emerald-900 bg-emerald-50/50 border-l-2 border-gray-400 cursor-pointer hover:bg-emerald-100"
              onClick={() => onSort('diferencia')}
            >
              Total <SortIcon active={sortKey === 'diferencia'} dir={sortDir} />
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-emerald-800 bg-emerald-50/50 border-l border-gray-200">
              📋 Copiadora
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-emerald-800 bg-emerald-50/50 border-l border-gray-200">
              🖨️ Impresora
            </th>
            <th colSpan={hasColor ? 2 : 1} className="px-3 py-2 text-center text-xs font-semibold text-emerald-800 bg-emerald-50/50 border-l border-gray-200">
              📷 Escáner
            </th>
          </tr>
          {/* Fila 3: B/N y Color */}
          <tr className="border-b-2 border-gray-300">
            {/* Base - Copiadora */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30 border-l border-gray-200">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30 border-l border-gray-200">B/N</th>
            )}
            {/* Base - Impresora */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30 border-l border-gray-200">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30 border-l border-gray-200">B/N</th>
            )}
            {/* Base - Escáner */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30 border-l border-gray-200">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30 border-r border-gray-300">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-blue-700 bg-blue-50/30 border-l border-gray-200 border-r border-gray-300">B/N</th>
            )}
            
            {/* Comparado - Copiadora */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30 border-l border-gray-200">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30 border-l border-gray-200">B/N</th>
            )}
            {/* Comparado - Impresora */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30 border-l border-gray-200">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30 border-l border-gray-200">B/N</th>
            )}
            {/* Comparado - Escáner */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30 border-l border-gray-200">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30 border-r border-gray-300">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-purple-700 bg-purple-50/30 border-l border-gray-200 border-r border-gray-300">B/N</th>
            )}
            
            {/* Diferencias - Copiadora */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30 border-l-2 border-gray-400">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30 border-l-2 border-gray-400">B/N</th>
            )}
            {/* Diferencias - Impresora */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30 border-l border-gray-200">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30 border-l border-gray-200">B/N</th>
            )}
            {/* Diferencias - Escáner */}
            {hasColor ? (
              <>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30 border-l border-gray-200">B/N</th>
                <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30">Color</th>
              </>
            ) : (
              <th className="px-2 py-1 text-center text-[10px] font-medium text-emerald-700 bg-emerald-50/30 border-l border-gray-200">B/N</th>
            )}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {usuarios.map((u, idx) => {
            const rowBg = idx % 2 === 0 ? 'bg-white' : 'bg-gray-50';
            return (
              <tr key={u.codigo_usuario} className={`${rowBg} hover:bg-indigo-50 transition-colors group`}>
                {/* Usuario */}
                <td className="px-4 py-3 text-sm font-medium text-gray-900 sticky left-0 z-10 bg-inherit group-hover:bg-indigo-50 border-r-2 border-gray-300">
                  {u.nombre_usuario}
                </td>
                {/* Código */}
                <td className="px-4 py-3 text-center sticky left-[200px] z-10 bg-inherit group-hover:bg-indigo-50 border-r-2 border-gray-300">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gray-200 text-gray-800">
                    {u.codigo_usuario}
                  </span>
                </td>
                
                {/* PERÍODO BASE */}
                <td className="px-3 py-3 text-center border-l border-gray-300 bg-blue-50/20">
                  <div className="text-sm font-bold text-blue-900">{fmt(u.consumo_cierre1 || 0)}</div>
                </td>
                {/* Copiadora */}
                <td className="px-2 py-3 text-center text-xs bg-blue-50/10 border-l border-gray-200">{fmt(u.copiadora_bn_cierre1 || 0)}</td>
                {hasColor && <td className="px-2 py-3 text-center text-xs bg-blue-50/10">{fmt(u.copiadora_color_cierre1 || 0)}</td>}
                {/* Impresora */}
                <td className="px-2 py-3 text-center text-xs bg-blue-50/10 border-l border-gray-200">{fmt(u.impresora_bn_cierre1 || 0)}</td>
                {hasColor && <td className="px-2 py-3 text-center text-xs bg-blue-50/10">{fmt(u.impresora_color_cierre1 || 0)}</td>}
                {/* Escáner */}
                <td className="px-2 py-3 text-center text-xs bg-blue-50/10 border-l border-gray-200">{fmt(u.escaner_bn_cierre1 || 0)}</td>
                {hasColor && <td className="px-2 py-3 text-center text-xs bg-blue-50/10 border-r border-gray-300">{fmt(u.escaner_color_cierre1 || 0)}</td>}
                {!hasColor && <td className="px-2 py-3 text-center text-xs bg-blue-50/10 border-r border-gray-300" style={{display: 'none'}}></td>}
                
                {/* PERÍODO COMPARADO */}
                <td className="px-3 py-3 text-center border-l border-gray-300 bg-purple-50/20">
                  <div className="text-sm font-bold text-purple-900">{fmt(u.consumo_cierre2 || 0)}</div>
                </td>
                {/* Copiadora */}
                <td className="px-2 py-3 text-center text-xs bg-purple-50/10 border-l border-gray-200">{fmt(u.copiadora_bn_cierre2 || 0)}</td>
                {hasColor && <td className="px-2 py-3 text-center text-xs bg-purple-50/10">{fmt(u.copiadora_color_cierre2 || 0)}</td>}
                {/* Impresora */}
                <td className="px-2 py-3 text-center text-xs bg-purple-50/10 border-l border-gray-200">{fmt(u.impresora_bn_cierre2 || 0)}</td>
                {hasColor && <td className="px-2 py-3 text-center text-xs bg-purple-50/10">{fmt(u.impresora_color_cierre2 || 0)}</td>}
                {/* Escáner */}
                <td className="px-2 py-3 text-center text-xs bg-purple-50/10 border-l border-gray-200">{fmt(u.escaner_bn_cierre2 || 0)}</td>
                {hasColor && <td className="px-2 py-3 text-center text-xs bg-purple-50/10 border-r border-gray-300">{fmt(u.escaner_color_cierre2 || 0)}</td>}
                {!hasColor && <td className="px-2 py-3 text-center text-xs bg-purple-50/10 border-r border-gray-300" style={{display: 'none'}}></td>}
                
                {/* DIFERENCIAS */}
                <td className={`px-3 py-3 text-center border-l-2 border-gray-400 bg-emerald-50/20 ${diffColor(u.diferencia)}`}>
                  <div className="text-sm font-bold">{fmtDiff(u.diferencia)}</div>
                </td>
                {/* Copiadora */}
                <td className={`px-2 py-3 text-center text-xs bg-emerald-50/10 border-l border-gray-200 ${diffColor(u.difCopiaBN || 0)}`}>
                  {fmtDiff(u.difCopiaBN || 0)}
                </td>
                {hasColor && (
                  <td className={`px-2 py-3 text-center text-xs bg-emerald-50/10 ${diffColor(u.difCopiaColor || 0)}`}>
                    {fmtDiff(u.difCopiaColor || 0)}
                  </td>
                )}
                {/* Impresora */}
                <td className={`px-2 py-3 text-center text-xs bg-emerald-50/10 border-l border-gray-200 ${diffColor(u.difImpreBN || 0)}`}>
                  {fmtDiff(u.difImpreBN || 0)}
                </td>
                {hasColor && (
                  <td className={`px-2 py-3 text-center text-xs bg-emerald-50/10 ${diffColor(u.difImpreColor || 0)}`}>
                    {fmtDiff(u.difImpreColor || 0)}
                  </td>
                )}
                {/* Escáner */}
                <td className={`px-2 py-3 text-center text-xs bg-emerald-50/10 border-l border-gray-200 ${diffColor(u.difEscanBN || 0)}`}>
                  {fmtDiff(u.difEscanBN || 0)}
                </td>
                {hasColor && (
                  <td className={`px-2 py-3 text-center text-xs bg-emerald-50/10 ${diffColor(u.difEscanColor || 0)}`}>
                    {fmtDiff(u.difEscanColor || 0)}
                  </td>
                )}
              </tr>
            );
          })}
          {usuarios.length === 0 && (
            <tr>
              <td colSpan={hasColor ? 23 : 14} className="text-center py-12">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">No se encontraron usuarios</p>
                    <p className="text-xs text-gray-500 mt-1">Intenta con otro término de búsqueda</p>
                  </div>
                </div>
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
