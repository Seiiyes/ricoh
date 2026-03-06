import { Printer } from 'lucide-react';
import type { PrinterDevice } from '@/types';
import type { TotalCounter } from '@/types/counter';

interface PrinterIdentificationProps {
  printer: PrinterDevice;
  counter: TotalCounter;
}

export const PrinterIdentification: React.FC<PrinterIdentificationProps> = ({
  printer,
  counter,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="flex items-start gap-4">
        <div className="bg-slate-100 p-3 rounded-lg">
          <Printer className="text-ricoh-red" size={32} />
        </div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-slate-900 mb-2">{printer.hostname}</h2>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
            <div>
              <span className="text-slate-500">Dirección IP:</span>
              <span className="ml-2 font-semibold text-slate-900">{printer.ip_address}</span>
            </div>
            {printer.location && (
              <div>
                <span className="text-slate-500">Ubicación:</span>
                <span className="ml-2 font-semibold text-slate-900">{printer.location}</span>
              </div>
            )}
            <div>
              <span className="text-slate-500">Estado:</span>
              <span className={`ml-2 font-semibold ${
                printer.status === 'online' ? 'text-green-600' : 'text-slate-400'
              }`}>
                {printer.status === 'online' ? 'En línea' : 'Fuera de línea'}
              </span>
            </div>
            <div>
              <span className="text-slate-500">Última lectura:</span>
              <span className="ml-2 font-semibold text-slate-900">
                {new Date(counter.fecha_lectura).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
