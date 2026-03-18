import { useState, useEffect } from 'react';
import { Printer, Trash2, Plus } from 'lucide-react';
import { fetchPrinters } from '@/services/printerService';
import { asignarEquipos } from '@/services/servicioUsuarios';
import { Button, Spinner } from '@/components/ui';
import type { PrinterDevice } from '@/types';

interface GestorEquiposProps {
  usuarioId: number;
  equiposAsignados: number[];
  onCambio: (equipos: number[]) => void;
}

export const GestorEquipos = ({
  usuarioId,
  equiposAsignados,
  onCambio,
}: GestorEquiposProps) => {
  const [equiposDisponibles, setEquiposDisponibles] = useState<PrinterDevice[]>([]);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [equiposSeleccionados, setEquiposSeleccionados] = useState<number[]>(equiposAsignados);
  const [cambiosPendientes, setCambiosPendientes] = useState(false);

  useEffect(() => {
    cargarEquipos();
  }, []);

  useEffect(() => {
    setEquiposSeleccionados(equiposAsignados);
  }, [equiposAsignados]);

  useEffect(() => {
    // Detectar si hay cambios pendientes
    const hayDiferencias =
      equiposSeleccionados.length !== equiposAsignados.length ||
      equiposSeleccionados.some((id) => !equiposAsignados.includes(id));

    // Solo activamos cambios pendientes si no estamos cargando inicialmente
    if (!cargando) {
      setCambiosPendientes(hayDiferencias);
    }
  }, [equiposSeleccionados, equiposAsignados, cargando]);

  const cargarEquipos = async () => {
    try {
      setCargando(true);
      const equipos = await fetchPrinters();
      setEquiposDisponibles(equipos);
    } catch (error) {
      console.error('Error al cargar equipos:', error);
    } finally {
      setCargando(false);
    }
  };

  const handleToggleEquipo = (equipoId: number) => {
    setEquiposSeleccionados((prev) => {
      const isSelected = prev.includes(equipoId);
      if (isSelected) {
        return prev.filter((id) => id !== equipoId);
      } else {
        return [...prev, equipoId];
      }
    });
  };

  const handleGuardarCambios = async () => {
    try {
      setGuardando(true);
      await asignarEquipos(usuarioId, equiposSeleccionados);
      onCambio(equiposSeleccionados);
      setCambiosPendientes(false);
    } catch (error) {
      console.error('Error al guardar equipos:', error);
      alert('Error al guardar los cambios en los equipos');
    } finally {
      setGuardando(false);
    }
  };

  const handleCancelarCambios = () => {
    setEquiposSeleccionados(equiposAsignados);
    setCambiosPendientes(false);
  };

  const equiposAsignadosIds = new Set(equiposSeleccionados);
  const asignados = equiposDisponibles.filter(e => equiposAsignadosIds.has(parseInt(e.id)));
  const noAsignados = equiposDisponibles.filter(e => !equiposAsignadosIds.has(parseInt(e.id)));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <h3 className="text-sm font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
          <span className="text-blue-600">🏢</span> Gestión de Acceso
        </h3>
        <span className="bg-slate-100 text-slate-600 px-3 py-1 rounded-full text-[10px] font-black uppercase">
          {equiposSeleccionados.length} equipos activos
        </span>
      </div>

      {cargando ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white rounded-2xl border-2 border-dashed border-slate-100">
          <Spinner size="lg" text="Consultando equipos Ricoh..." className="text-ricoh-red" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Columna ASIGNADOS */}
          <div className="space-y-3">
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4">Equipos con Acceso</h4>
            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
              {asignados.length === 0 ? (
                <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                  <p className="text-[10px] font-bold text-slate-400 uppercase">Sin accesos configurados</p>
                </div>
              ) : (
                asignados.map(equipo => (
                  <div key={equipo.id} className="group relative bg-white border-2 border-blue-100 p-4 rounded-xl flex items-center gap-4 shadow-sm hover:border-blue-400 transition-all">
                    <div className="bg-blue-50 p-2 rounded-lg text-blue-600">
                      <Printer size={18} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-black text-slate-800 truncate">{equipo.hostname}</p>
                      <p className="text-[10px] font-mono text-slate-500">{equipo.ip_address}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleEquipo(parseInt(equipo.id))}
                      icon={<Trash2 size={16} />}
                      className="text-slate-300 hover:text-red-500 hover:bg-red-50"
                      title="Quitar acceso"
                    />
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Columna DISPONIBLES */}
          <div className="space-y-3">
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4">Equipos Disponibles</h4>
            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2">
              {noAsignados.map(equipo => (
                <div
                  key={equipo.id}
                  onClick={() => handleToggleEquipo(parseInt(equipo.id))}
                  className="bg-slate-50 border-2 border-transparent p-4 rounded-xl flex items-center gap-4 hover:bg-white hover:border-ricoh-red/20 hover:shadow-md cursor-pointer transition-all group"
                >
                  <div className="bg-white p-2 rounded-lg text-slate-400 group-hover:text-ricoh-red border border-slate-200 transition-all">
                    <Printer size={18} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-slate-600 truncate">{equipo.hostname}</p>
                    <p className="text-[10px] font-mono text-slate-400">{equipo.ip_address}</p>
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 bg-ricoh-red text-white p-1.5 rounded-lg transition-all">
                    <Plus size={14} />
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}

      {cambiosPendientes && (
        <div className="bg-slate-900 rounded-2xl p-4 flex items-center justify-between shadow-2xl animate-in fade-in slide-in-from-bottom-4">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
            <p className="text-xs font-bold text-white uppercase tracking-widest">Tienes cambios en los equipos</p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancelarCambios}
              className="text-slate-400 hover:text-white"
            >
              Descartar
            </Button>
            <Button
              onClick={handleGuardarCambios}
              loading={guardando}
              size="sm"
              className="bg-blue-600 hover:bg-blue-500"
            >
              {guardando ? 'Procesando...' : 'Aplicar Cambios'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
