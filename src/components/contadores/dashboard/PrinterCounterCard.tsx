import { Printer } from 'lucide-react';
import type { PrinterDevice } from '@/types';
import type { TotalCounter } from '@/types/counter';

interface PrinterCounterCardProps {
  printer: PrinterDevice;
  counter?: TotalCounter;
  onClick: () => void;
}

export const PrinterCounterCard: React.FC<PrinterCounterCardProps> = ({
  printer,
  counter,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow-sm border border-slate-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
      data-testid="printer-card"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-bold text-slate-900">{printer.hostname}</h3>
          <p className="text-xs text-slate-500">{printer.ip_address}</p>
          {printer.location && (
            <p className="text-xs text-slate-500">{printer.location}</p>
          )}
        </div>
        <Printer className="text-slate-400" size={20} />
      </div>
      
      {counter ? (
        <div className="space-y-2">
          <div className="flex justify-between items-baseline">
            <span className="text-sm text-slate-600">Total:</span>
            <span className="text-lg font-bold text-slate-900">
              {counter.total.toLocaleString()}
            </span>
          </div>
          <div className="text-xs text-slate-400">
            Última lectura: {new Date(counter.fecha_lectura).toLocaleString()}
          </div>
        </div>
      ) : (
        <div className="text-sm text-slate-400">Sin contadores registrados</div>
      )}
    </div>
  );
};
