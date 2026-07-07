import React from 'react';
import { cn } from '../../lib/utils';
import { chartColors } from '../../utils/chartColors';

interface KPICardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  trend?: number; // Porcentaje (positivo o negativo)
  trendLabel?: string;
  color?: string;
  className?: string;
  invertTrendColor?: boolean;
}

export const KPICard: React.FC<KPICardProps> = ({ 
  title, 
  value, 
  icon, 
  trend, 
  trendLabel,
  color = chartColors.primary, 
  className,
  invertTrendColor = false
}) => {
  const isPositive = trend !== undefined && trend > 0;
  const isNegative = trend !== undefined && trend < 0;

  // Lógica de colores de la tendencia (normal o invertida)
  let trendBgClass = "bg-slate-100 text-slate-700";
  if (trend !== undefined) {
    if (invertTrendColor) {
      trendBgClass = isPositive ? "bg-red-100 text-red-700" : isNegative ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-700";
    } else {
      trendBgClass = isPositive ? "bg-green-100 text-green-700" : isNegative ? "bg-red-100 text-red-700" : "bg-slate-100 text-slate-700";
    }
  }

  return (
    <div className={cn("bg-white rounded-xl shadow-sm border border-slate-100 p-5 flex flex-col relative overflow-hidden", className)}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">{title}</h3>
        {icon && (
          <div className="p-2 rounded-lg" style={{ backgroundColor: `${color}15`, color }}>
            {icon}
          </div>
        )}
      </div>
      <div className="mt-1 flex-1 flex flex-col justify-end">
        <div className="text-3xl font-black text-slate-800 tracking-tight">{value}</div>
        
        {trend !== undefined && (
          <div className="flex items-center gap-2 mt-2">
            <span className={cn(
              "text-xs font-bold px-1.5 py-0.5 rounded-md",
              trendBgClass
            )}>
              {isPositive ? '+' : ''}{trend}%
            </span>
            {trendLabel && <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{trendLabel}</span>}
          </div>
        )}
      </div>
      {/* Accent border bottom */}
      <div className="absolute bottom-0 left-0 w-full h-1" style={{ backgroundColor: color }} />
    </div>
  );
};
