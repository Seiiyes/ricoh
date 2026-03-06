import { CierreMensual, Printer, TipoPeriodo } from './types';

interface ListaCierresProps {
  printer: Printer;
  year: number;
  tipoPeriodo: TipoPeriodo;
  cierres: CierreMensual[];
  onCreateCierre: (fechaInicio: string, fechaFin: string) => void;
  onViewDetalle: (cierre: CierreMensual) => void;
}

export const ListaCierres: React.FC<ListaCierresProps> = ({
  printer,
  year,
  tipoPeriodo,
  cierres,
  onCreateCierre,
  onViewDetalle
}) => {
  const formatNumber = (num: number) => num.toLocaleString('es-ES');
  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString('es-ES');

  console.log('ListaCierres rendered with:', { printer, year, tipoPeriodo, cierresCount: cierres.length });

  const handleCreateClick = (cierre: CierreMensual) => {
    onCreateCierre(cierre.fecha_inicio, cierre.fecha_fin);
  };

  if (cierres.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
        <svg className="w-16 h-16 text-yellow-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          No hay cierres {tipoPeriodo}s para {year}
        </h3>
        <p className="text-gray-600 mb-4">
          No se encontraron cierres {tipoPeriodo}s para la impresora {printer.hostname} en el año {year}
        </p>
        <button
          onClick={() => {
            // Crear cierre del mes actual
            const now = new Date();
            const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
            const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
            onCreateCierre(
              firstDay.toISOString().split('T')[0],
              lastDay.toISOString().split('T')[0]
            );
          }}
          className="px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
        >
          Crear Primer Cierre
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {printer.hostname}
            </h2>
            <p className="text-sm text-gray-600">
              {printer.ip_address} • {printer.location || 'Sin ubicación'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Cierres {tipoPeriodo}s</p>
            <p className="text-2xl font-bold text-gray-900">{cierres.length}</p>
          </div>
        </div>
      </div>

      {/* Lista de cierres */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cierres.map((cierre) => (
          <div
            key={cierre.id}
            className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => onViewDetalle(cierre)}
          >
            <div className="p-4">
              {/* Header del cierre */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${
                    cierre.diferencia_total > 0 ? 'bg-green-500' : 'bg-gray-400'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-700 capitalize">
                    {cierre.tipo_periodo}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  ID: {cierre.id}
                </span>
              </div>

              {/* Período */}
              <div className="mb-3">
                <p className="text-lg font-semibold text-gray-900">
                  {formatDate(cierre.fecha_inicio)}
                  {cierre.fecha_inicio !== cierre.fecha_fin && (
                    <> - {formatDate(cierre.fecha_fin)}</>
                  )}
                </p>
                <p className="text-xs text-gray-500">
                  Cerrado: {formatDate(cierre.fecha_cierre)}
                </p>
              </div>

              {/* Totales */}
              <div className="space-y-2 mb-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total páginas:</span>
                  <span className="font-semibold text-gray-900">
                    {formatNumber(cierre.total_paginas)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Consumo período:</span>
                  <span className={`font-semibold ${
                    cierre.diferencia_total > 0 ? 'text-green-600' : 'text-gray-400'
                  }`}>
                    {cierre.diferencia_total > 0 ? '+' : ''}{formatNumber(cierre.diferencia_total)}
                  </span>
                </div>
              </div>

              {/* Desglose */}
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-3">
                <div>
                  <span className="block">Copiadora:</span>
                  <span className="font-medium text-gray-900">
                    {formatNumber(cierre.diferencia_copiadora)}
                  </span>
                </div>
                <div>
                  <span className="block">Impresora:</span>
                  <span className="font-medium text-gray-900">
                    {formatNumber(cierre.diferencia_impresora)}
                  </span>
                </div>
                <div>
                  <span className="block">Escáner:</span>
                  <span className="font-medium text-gray-900">
                    {formatNumber(cierre.diferencia_escaner)}
                  </span>
                </div>
                <div>
                  <span className="block">Fax:</span>
                  <span className="font-medium text-gray-900">
                    {formatNumber(cierre.diferencia_fax)}
                  </span>
                </div>
              </div>

              {/* Footer */}
              <div className="pt-3 border-t border-gray-200 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {cierre.cerrado_por || 'Sistema'}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onViewDetalle(cierre);
                  }}
                  className="text-xs text-red-600 hover:text-red-700 font-medium"
                >
                  Ver detalle →
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Botón para crear nuevo cierre */}
      <div className="bg-white rounded-lg shadow p-4">
        <button
          onClick={() => {
            // Calcular siguiente período basado en el último cierre
            const ultimoCierre = cierres[0]; // Asumiendo que están ordenados
            const fechaFin = new Date(ultimoCierre.fecha_fin);
            fechaFin.setDate(fechaFin.getDate() + 1);
            
            let nuevaFechaInicio: Date;
            let nuevaFechaFin: Date;

            if (tipoPeriodo === 'diario') {
              nuevaFechaInicio = fechaFin;
              nuevaFechaFin = fechaFin;
            } else if (tipoPeriodo === 'semanal') {
              nuevaFechaInicio = fechaFin;
              nuevaFechaFin = new Date(fechaFin);
              nuevaFechaFin.setDate(nuevaFechaFin.getDate() + 6);
            } else if (tipoPeriodo === 'mensual') {
              nuevaFechaInicio = new Date(fechaFin.getFullYear(), fechaFin.getMonth(), 1);
              nuevaFechaFin = new Date(fechaFin.getFullYear(), fechaFin.getMonth() + 1, 0);
            } else {
              nuevaFechaInicio = fechaFin;
              nuevaFechaFin = new Date(fechaFin);
              nuevaFechaFin.setDate(nuevaFechaFin.getDate() + 7);
            }

            onCreateCierre(
              nuevaFechaInicio.toISOString().split('T')[0],
              nuevaFechaFin.toISOString().split('T')[0]
            );
          }}
          className="w-full px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Crear Nuevo Cierre {tipoPeriodo.charAt(0).toUpperCase() + tipoPeriodo.slice(1)}
        </button>
      </div>
    </div>
  );
};
