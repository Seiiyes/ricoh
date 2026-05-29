import React from 'react';
import { Download } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ChartCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  onExport?: () => void;
  className?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  title,
  description,
  children,
  onExport,
  className,
}) => {
  return (
    <div className={cn("bg-white rounded-xl shadow-sm border border-slate-100 p-5 flex flex-col h-full", className)}>
      <div className="flex justify-between items-center mb-4 gap-3">
        <div className="min-w-0">
          <h3 className="text-sm font-bold text-slate-800">{title}</h3>
          {description ? (
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">{description}</p>
          ) : null}
        </div>
        {onExport && (
          <button 
            onClick={onExport}
            className="p-1.5 text-slate-400 hover:text-ricoh-red hover:bg-red-50 rounded-md transition-colors"
            title="Exportar Gráfico"
          >
            <Download size={16} />
          </button>
        )}
      </div>
      <div className="flex-1 min-h-0 relative">
        {children}
      </div>
    </div>
  );
};
