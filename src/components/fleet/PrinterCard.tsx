import { Card, CardContent } from "@/components/ui/card";
import { Printer, Scan, Pipette, Edit2, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePrinterStore } from "@/store/usePrinterStore";

interface TonerLevels {
  c: number; m: number; y: number; k: number;
}

interface PrinterCardProps {
  id: string;
  name: string;
  ip: string;
  status: 'online' | 'offline';
  location?: string;
  toner: TonerLevels;
  onEdit?: () => void;
  onRefresh?: () => void;
}

export const PrinterCard = ({ id, name, ip, status, location, toner, onEdit, onRefresh }: PrinterCardProps) => {
  const isOnline = status === 'online';
  const { selectedPrinters, togglePrinter } = usePrinterStore();
  const isSelected = selectedPrinters.includes(id);

  return (
    <Card className={cn(
      "overflow-hidden border-2 transition-all shadow-sm cursor-pointer",
      isSelected ? "border-ricoh-red bg-red-50" : "border-slate-200 hover:border-slate-300"
    )}>
      <div 
        className="p-3 bg-slate-50 border-b flex justify-between items-center"
        onClick={() => togglePrinter(id)}
      >
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => togglePrinter(id)}
            className="w-4 h-4 text-ricoh-red border-slate-300 rounded focus:ring-ricoh-red"
            onClick={(e) => e.stopPropagation()}
          />
          <div>
            <h3 className="text-xs font-bold text-industrial-gray uppercase tracking-tight">{name}</h3>
            <p className="text-sm font-bold text-slate-700 font-mono mt-0.5">{ip}</p>
            {location && (
              <p className="text-xs font-semibold text-ricoh-red uppercase tracking-wide mt-1">{location}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {onRefresh && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onRefresh();
              }}
              className="p-1.5 hover:bg-slate-200 rounded transition-colors"
              title="Actualizar datos SNMP"
            >
              <RefreshCw size={14} className="text-slate-600" />
            </button>
          )}
          {onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
              className="p-1.5 hover:bg-slate-200 rounded transition-colors"
              title="Editar impresora"
            >
              <Edit2 size={14} className="text-slate-600" />
            </button>
          )}
          <div className={cn(
            "h-2 w-2 rounded-full",
            isOnline ? "bg-success animate-pulse-subtle shadow-[0_0_8px_rgba(16,185,129,0.6)]" : "bg-slate-300"
          )} />
        </div>
      </div>
      
      <CardContent className="p-3 space-y-4" onClick={() => togglePrinter(id)}>
        {/* Toner Visualizer - Only show if there's real data */}
        {(toner.c > 0 || toner.m > 0 || toner.y > 0 || toner.k > 0) && (
          <div className="space-y-1.5">
            <div className="flex justify-between text-[9px] font-bold text-slate-400 uppercase">
              <span>Estado de Consumibles</span>
              <span>{Math.min(toner.c, toner.m, toner.y, toner.k)}% mín</span>
            </div>
            <div className="grid grid-cols-4 gap-1 h-1.5">
              <div className="bg-cyan-400 rounded-full overflow-hidden"><div className="bg-slate-200 h-full w-full" style={{ transform: `translateX(${toner.c}%)` }} /></div>
              <div className="bg-magenta-400 rounded-full overflow-hidden"><div className="bg-slate-200 h-full w-full" style={{ transform: `translateX(${toner.m}%)` }} /></div>
              <div className="bg-yellow-400 rounded-full overflow-hidden"><div className="bg-slate-200 h-full w-full" style={{ transform: `translateX(${toner.y}%)` }} /></div>
              <div className="bg-slate-900 rounded-full overflow-hidden"><div className="bg-slate-200 h-full w-full" style={{ transform: `translateX(${toner.k}%)` }} /></div>
            </div>
          </div>
        )}

        {/* Governance Toggles */}
        <div className="flex justify-between items-center pt-2 border-t border-slate-100">
          <div className="flex gap-3 text-slate-400">
            <Printer size={14} className="text-ricoh-red" />
            <Scan size={14} />
            <Pipette size={14} />
          </div>
          <div className="text-[10px] font-mono text-slate-400 italic">Listo</div>
        </div>
      </CardContent>
    </Card>
  );
};