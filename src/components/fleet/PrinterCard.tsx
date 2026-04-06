import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui";
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
      "group overflow-hidden border transition-all duration-300 shadow-sm cursor-pointer hover:shadow-xl hover:-translate-y-1 rounded-2xl",
      isSelected ? "border-ricoh-red ring-2 ring-red-500/10 bg-white" : "border-slate-200 hover:border-slate-400 bg-white"
    )}>
      <div 
        className={cn(
          "p-4 border-b flex justify-between items-center transition-colors",
          isSelected ? "bg-red-50/50" : "bg-slate-50/50"
        )}
        onClick={() => togglePrinter(id)}
      >
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center">
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => togglePrinter(id)}
              className="w-5 h-5 text-ricoh-red border-slate-300 rounded-lg focus:ring-ricoh-red transition-all cursor-pointer"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
          <div>
            <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest">{name}</h3>
            <p className="text-sm font-bold text-slate-900 font-mono mt-0.5 tracking-tight">{ip}</p>
            {location && (
              <div className="flex items-center gap-1 mt-1 text-[10px] font-bold text-ricoh-red uppercase tracking-wider bg-red-50 w-fit px-2 py-0.5 rounded-full">
                <span className="w-1 h-1 rounded-full bg-ricoh-red animate-pulse"></span>
                {location}
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1">
          {onRefresh && (
            <Button
              variant="ghost"
              size="sm"
              icon={<RefreshCw size={14} />}
              onClick={(e) => {
                e.stopPropagation();
                onRefresh();
              }}
              className="text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full w-8 h-8 flex items-center justify-center p-0"
              title="Actualizar datos SNMP"
            />
          )}
          {onEdit && (
            <Button
              variant="ghost"
              size="sm"
              icon={<Edit2 size={14} />}
              onClick={(e) => {
                e.stopPropagation();
                onEdit();
              }}
              className="text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full w-8 h-8 flex items-center justify-center p-0"
              title="Editar impresora"
            />
          )}
          <div className={cn(
            "h-2.5 w-2.5 rounded-full border-2 border-white shadow-sm ml-1",
            isOnline ? "bg-emerald-500 animate-pulse ring-4 ring-emerald-500/10" : "bg-slate-300"
          )} />
        </div>
      </div>
      
      <CardContent className="p-3 space-y-4" onClick={() => togglePrinter(id)}>
        {/* Toner Visualizer */}
        {(toner.c > 0 || toner.m > 0 || toner.y > 0 || toner.k > 0) && (
          <div className="space-y-2">
            <div className="flex justify-between text-[10px] font-black text-slate-400 uppercase tracking-widest">
              <span>Suministros</span>
              <span className="text-slate-500">{Math.min(toner.c, toner.m, toner.y, toner.k)}% min</span>
            </div>
            <div className="grid grid-cols-4 gap-1.5 h-1">
              <div className="bg-slate-100 rounded-full overflow-hidden h-full relative">
                <div className="bg-[#00FFFF] absolute left-0 top-0 h-full transition-all duration-500" style={{ width: `${toner.c}%` }} />
              </div>
              <div className="bg-slate-100 rounded-full overflow-hidden h-full relative">
                <div className="bg-[#FF00FF] absolute left-0 top-0 h-full transition-all duration-500" style={{ width: `${toner.m}%` }} />
              </div>
              <div className="bg-slate-100 rounded-full overflow-hidden h-full relative">
                <div className="bg-[#FFFF00] absolute left-0 top-0 h-full transition-all duration-500" style={{ width: `${toner.y}%` }} />
              </div>
              <div className="bg-slate-100 rounded-full overflow-hidden h-full relative">
                <div className="bg-slate-900 absolute left-0 top-0 h-full transition-all duration-500" style={{ width: `${toner.k}%` }} />
              </div>
            </div>
          </div>
        )}

        {/* Labels CMYK */}
        <div className="grid grid-cols-4 gap-1.5 text-[8px] font-black text-center text-slate-400 uppercase tracking-tighter">
          <span>C</span><span>M</span><span>Y</span><span>K</span>
        </div>

        {/* Governance Toggles */}
        <div className="flex justify-between items-center pt-3 border-t border-slate-100">
          <div className="flex gap-4">
            <div className="group/icon relative">
              <Printer size={15} className="text-ricoh-red drop-shadow-[0_0_8px_rgba(206,17,38,0.3)]" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-500 rounded-full border-2 border-white"></div>
            </div>
            <Scan size={15} className="text-slate-300 group-hover:text-slate-500 transition-colors" />
            <Pipette size={15} className="text-slate-300 group-hover:text-slate-500 transition-colors" />
          </div>
          <div className="flex items-center gap-1.5">
            <div className="text-[10px] font-black text-emerald-600 uppercase tracking-widest px-2 py-0.5 bg-emerald-50 rounded-full">En Línea</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};