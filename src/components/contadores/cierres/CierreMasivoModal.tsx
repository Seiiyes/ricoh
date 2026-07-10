import { useState, useEffect } from 'react';
import { Modal, Button, Alert } from '@/components/ui';
import { Printer, CheckCircle, XCircle, FileText, Calendar, Clock, Trash2, List, PlusCircle, Check } from 'lucide-react';
import closeService, { type ScheduledClosure } from '@/services/closeService';
import { parseApiError } from '@/utils/errorHandler';
import { useAuth } from '@/contexts/AuthContext';

interface CierreMasivoModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

interface CierreResult {
  printer_id: number;
  printer_name: string;
  success: boolean;
  cierre_id?: number;
  total_paginas: number;
  usuarios_count: number;
  error?: string;
}

export const CierreMasivoModal: React.FC<CierreMasivoModalProps> = ({ onClose, onSuccess }) => {
  const { user } = useAuth();
  
  // Tabs: 'immediate' | 'schedule' | 'list'
  const [activeTab, setActiveTab] = useState<'immediate' | 'schedule' | 'list'>('immediate');
  
  // Loading & Error States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Tab 1: Cierre Inmediato States
  const [results, setResults] = useState<CierreResult[] | null>(null);
  const [summary, setSummary] = useState<{ successful: number; failed: number; total: number } | null>(null);
  const [notas, setNotas] = useState('');

  // Tab 2: Programar Cierre Form States
  const [frequency, setFrequency] = useState<string>('daily');
  const [scheduledTime, setScheduledTime] = useState<string>('18:00');
  const [specificDate, setSpecificDate] = useState<string>('');
  const [dayOfWeek, setDayOfWeek] = useState<number>(0);
  const [dayOfMonth, setDayOfMonth] = useState<number>(1);
  const [scheduleNotas, setScheduleNotas] = useState<string>('');

  // Tab 3: List of schedules
  const [schedules, setSchedules] = useState<ScheduledClosure[]>([]);
  const [loadingSchedules, setLoadingSchedules] = useState(false);

  // Fecha actual local en formato YYYY-MM-DD
  const getLocalDateString = () => {
    const d = new Date();
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  const fechaActual = getLocalDateString();

  // Helper para formatear fechas YYYY-MM-DD de forma segura sin desplazamiento de zona horaria
  const formatLocalDateString = (dateStr: string | undefined | null) => {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      const [year, month, day] = parts;
      return `${parseInt(day)}/${parseInt(month)}/${year}`;
    }
    return dateStr;
  };

  // Helper para formatear fecha larga local
  const formatLocalDateLong = (dateStr: string) => {
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      const [year, month, day] = parts.map(Number);
      const dateObj = new Date(year, month - 1, day);
      return dateObj.toLocaleDateString('es-ES', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
    return dateStr;
  };

  const nombreUsuario = user?.nombre_completo || user?.username || 'Usuario';

  // Load schedules when switching to list tab
  useEffect(() => {
    if (activeTab === 'list') {
      fetchSchedules();
    }
  }, [activeTab]);

  const fetchSchedules = async () => {
    setLoadingSchedules(true);
    setError(null);
    try {
      const data = await closeService.getSchedules();
      setSchedules(data);
    } catch (err: any) {
      console.error('Error al cargar programaciones:', err);
      setError(parseApiError(err, 'Error al cargar las programaciones'));
    } finally {
      setLoadingSchedules(false);
    }
  };

  const handleImmediateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);
    setSummary(null);

    try {
      const response = await closeService.createCloseAllPrinters({
        fecha_inicio: fechaActual,
        fecha_fin: fechaActual,
        cerrado_por: nombreUsuario,
        notas: notas || undefined
      });

      setResults(response.results);
      setSummary({
        successful: response.successful,
        failed: response.failed,
        total: response.total
      });

      if (response.successful > 0) {
        onSuccess();
      }
    } catch (err: any) {
      console.error('Error al crear cierres masivos:', err);
      setError(parseApiError(err, 'Error al crear cierres masivos'));
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await closeService.createSchedule({
        frequency,
        scheduled_time: scheduledTime,
        specific_date: frequency === 'once' ? (specificDate || undefined) : undefined,
        day_of_week: frequency === 'weekly' ? dayOfWeek : undefined,
        day_of_month: frequency === 'monthly' ? dayOfMonth : undefined,
        notas: scheduleNotas || undefined
      });

      setSuccessMessage('¡La programación del cierre masivo se ha creado correctamente!');
      setFrequency('daily');
      setScheduledTime('18:00');
      setSpecificDate('');
      setDayOfWeek(0);
      setDayOfMonth(1);
      setScheduleNotas('');
      
      // Auto-switching to list after 1.5s
      setTimeout(() => {
        setSuccessMessage(null);
        setActiveTab('list');
      }, 1500);
    } catch (err: any) {
      console.error('Error al programar cierre:', err);
      setError(parseApiError(err, 'Error al crear la programación'));
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSchedule = async (schedule: ScheduledClosure) => {
    setError(null);
    try {
      await closeService.updateSchedule(schedule.id, {
        is_active: !schedule.is_active
      });
      fetchSchedules();
    } catch (err: any) {
      console.error('Error al alternar estado de programación:', err);
      setError(parseApiError(err, 'Error al actualizar la programación'));
    }
  };

  const handleDeleteSchedule = async (id: number) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta programación de cierre automático?')) {
      return;
    }
    setError(null);
    try {
      await closeService.deleteSchedule(id);
      fetchSchedules();
    } catch (err: any) {
      console.error('Error al eliminar programación:', err);
      setError(parseApiError(err, 'Error al eliminar la programación'));
    }
  };

  const getFrequencyText = (schedule: ScheduledClosure) => {
    switch (schedule.frequency) {
      case 'once':
        return `Una vez (${formatLocalDateString(schedule.specific_date)})`;
      case 'daily':
        return 'Todos los días';
      case 'weekly':
        const days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
        return `Semanal (${days[schedule.day_of_week ?? 0]})`;
      case 'monthly':
        return `Mensual (Día ${schedule.day_of_month})`;
      default:
        return schedule.frequency;
    }
  };

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Gestión de Cierre Masivo y Programación"
      size="xl"
    >
      <div className="space-y-6">
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-200">
          <button
            type="button"
            className={`py-2.5 px-4 font-semibold text-sm border-b-2 transition-all ${
              activeTab === 'immediate'
                ? 'border-red-600 text-red-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
            onClick={() => {
              setActiveTab('immediate');
              setError(null);
              setSuccessMessage(null);
            }}
          >
            Cierre Inmediato
          </button>
          <button
            type="button"
            className={`py-2.5 px-4 font-semibold text-sm border-b-2 transition-all ${
              activeTab === 'schedule'
                ? 'border-red-600 text-red-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
            onClick={() => {
              setActiveTab('schedule');
              setError(null);
              setSuccessMessage(null);
            }}
          >
            Programar Cierre
          </button>
          <button
            type="button"
            className={`py-2.5 px-4 font-semibold text-sm border-b-2 transition-all ${
              activeTab === 'list'
                ? 'border-red-600 text-red-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
            }`}
            onClick={() => {
              setActiveTab('list');
              setError(null);
              setSuccessMessage(null);
            }}
          >
            Lista de Programaciones
          </button>
        </div>

        {error && (
          <Alert variant="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {successMessage && (
          <Alert variant="success" onClose={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        )}

        {/* Tab 1: Cierre Inmediato */}
        {activeTab === 'immediate' && (
          <form onSubmit={handleImmediateSubmit} className="space-y-6">
            {!results ? (
              <>
                <div className="bg-slate-50 rounded-lg p-6 space-y-4">
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Fecha del Cierre
                      </label>
                      <div className="px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-900 font-bold">
                        {formatLocalDateLong(fechaActual)}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Realizado Por
                      </label>
                      <div className="px-4 py-3 bg-white border border-slate-200 rounded-lg text-slate-900 font-bold">
                        {nombreUsuario}
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    <FileText className="inline mr-2" size={16} />
                    Notas (Opcional)
                  </label>
                  <textarea
                    value={notas}
                    onChange={(e) => setNotas(e.target.value)}
                    placeholder="Notas adicionales sobre este cierre..."
                    rows={3}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent"
                    maxLength={1000}
                  />
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    <strong>⚠️ Advertencia:</strong> Esta acción creará un cierre diario en TODAS las impresoras activas a las que tienes acceso.
                    Los contadores se leerán automáticamente antes de crear los cierres.
                  </p>
                  <p className="text-sm text-yellow-800 mt-2">
                    <strong>Nota:</strong> Si ya existe un cierre diario para hoy en alguna impresora, esa impresora será omitida.
                  </p>
                </div>

                <div className="flex justify-end gap-3">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={onClose}
                    disabled={loading}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    variant="primary"
                    loading={loading}
                    icon={<Printer size={18} />}
                  >
                    Crear Cierres en Todas las Impresoras
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div className="space-y-4">
                  {summary && (
                    <div className="bg-slate-50 rounded-lg p-6">
                      <h3 className="text-lg font-bold text-slate-900 mb-4">Resumen de Operación</h3>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center">
                          <div className="text-3xl font-bold text-slate-900">{summary.total}</div>
                          <div className="text-sm text-slate-600">Total</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-green-600">{summary.successful}</div>
                          <div className="text-sm text-slate-600">Exitosos</div>
                        </div>
                        <div className="text-center">
                          <div className="text-3xl font-bold text-red-600">{summary.failed}</div>
                          <div className="text-sm text-slate-600">Fallidos</div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="max-h-96 overflow-y-auto space-y-2">
                    {results.map((result, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg border ${
                          result.success
                            ? 'bg-green-50 border-green-200'
                            : 'bg-red-50 border-red-200'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            {result.success ? (
                              <CheckCircle className="text-green-600 mt-1" size={20} />
                            ) : (
                              <XCircle className="text-red-600 mt-1" size={20} />
                            )}
                            <div>
                              <div className="font-bold text-slate-900">{result.printer_name}</div>
                              <div className="text-sm text-slate-600">ID: {result.printer_id}</div>
                              {result.success && (
                                <div className="text-sm text-slate-600 mt-1">
                                  {result.total_paginas.toLocaleString()} páginas • {result.usuarios_count} usuarios
                                </div>
                              )}
                              {result.error && (
                                <div className="text-sm text-red-600 mt-1">{result.error}</div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button
                    type="button"
                    variant="primary"
                    onClick={onClose}
                  >
                    Cerrar
                  </Button>
                </div>
              </>
            )}
          </form>
        )}

        {/* Tab 2: Programar Cierre Form */}
        {activeTab === 'schedule' && (
          <form onSubmit={handleScheduleSubmit} className="space-y-6">
            <div className="bg-slate-50 rounded-lg p-6 space-y-4">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Frecuencia de Ejecución
                  </label>
                  <select
                    value={frequency}
                    onChange={(e) => setFrequency(e.target.value)}
                    className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent"
                  >
                    <option value="once">Una vez (Fecha específica)</option>
                    <option value="daily">Todos los días</option>
                    <option value="weekly">Semanal (Día específico)</option>
                    <option value="monthly">Mensual (Día del mes)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-1.5">
                    <Clock size={16} /> Hora de Ejecución (24h)
                  </label>
                  <input
                    type="time"
                    value={scheduledTime}
                    onChange={(e) => setScheduledTime(e.target.value)}
                    required
                    className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Conditional Inputs Based on Frequency */}
              {frequency === 'once' && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-1.5">
                    <Calendar size={16} /> Seleccionar Fecha
                  </label>
                  <input
                    type="date"
                    value={specificDate}
                    onChange={(e) => setSpecificDate(e.target.value)}
                    required
                    min={fechaActual}
                    className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent"
                  />
                </div>
              )}

              {frequency === 'weekly' && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Seleccionar Día de la Semana
                  </label>
                  <select
                    value={dayOfWeek}
                    onChange={(e) => setDayOfWeek(parseInt(e.target.value))}
                    className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent"
                  >
                    <option value={0}>Lunes</option>
                    <option value={1}>Martes</option>
                    <option value={2}>Miércoles</option>
                    <option value={3}>Jueves</option>
                    <option value={4}>Viernes</option>
                    <option value={5}>Sábado</option>
                    <option value={6}>Domingo</option>
                  </select>
                </div>
              )}

              {frequency === 'monthly' && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Día del Mes (1 al 31)
                  </label>
                  <input
                    type="number"
                    value={dayOfMonth}
                    onChange={(e) => setDayOfMonth(Math.max(1, Math.min(31, parseInt(e.target.value) || 1)))}
                    required
                    min={1}
                    max={31}
                    className="w-full px-4 py-2 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Nota: Si un mes tiene menos días (ej: febrero), se ejecutará el último día de ese mes.
                  </p>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                <FileText className="inline mr-2" size={16} />
                Notas para los Cierres Automáticos (Opcional)
              </label>
              <textarea
                value={scheduleNotas}
                onChange={(e) => setScheduleNotas(e.target.value)}
                placeholder="Notas que se aplicarán automáticamente a cada cierre generado..."
                rows={3}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-600 focus:border-transparent"
                maxLength={1000}
              />
            </div>

            <div className="flex justify-end gap-3">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                variant="primary"
                loading={loading}
                icon={<PlusCircle size={18} />}
              >
                Guardar Programación
              </Button>
            </div>
          </form>
        )}

        {/* Tab 3: Lista de Programaciones */}
        {activeTab === 'list' && (
          <div className="space-y-4">
            {loadingSchedules ? (
              <div className="text-center py-12 text-slate-500">
                Cargando programaciones activas...
              </div>
            ) : schedules.length === 0 ? (
              <div className="text-center py-12 text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200">
                No hay cierres programados actualmente.
              </div>
            ) : (
              <div className="overflow-hidden border border-slate-200 rounded-lg bg-white">
                <table className="min-w-full divide-y divide-slate-200">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Frecuencia</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Hora</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Siguiente Ejecución</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Último Cierre</th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-slate-600 uppercase tracking-wider">Estado</th>
                      <th className="px-6 py-3 text-center text-xs font-semibold text-slate-600 uppercase tracking-wider">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {schedules.map((schedule) => (
                      <tr key={schedule.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                          {getFrequencyText(schedule)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                          {schedule.scheduled_time}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600 font-semibold">
                          {schedule.next_run ? new Date(schedule.next_run).toLocaleString('es-ES') : '—'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                          {schedule.last_run ? new Date(schedule.last_run).toLocaleString('es-ES') : '—'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <button
                            type="button"
                            onClick={() => handleToggleSchedule(schedule)}
                            className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold transition-colors ${
                              schedule.is_active
                                ? 'bg-green-100 text-green-800 hover:bg-green-200'
                                : 'bg-slate-100 text-slate-800 hover:bg-slate-200'
                            }`}
                          >
                            {schedule.is_active ? (
                              <>
                                <Check size={12} /> Activo
                              </>
                            ) : (
                              'Inactivo'
                            )}
                          </button>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                          <button
                            type="button"
                            onClick={() => handleDeleteSchedule(schedule.id)}
                            className="text-red-600 hover:text-red-900 transition-colors p-1"
                            title="Eliminar programación"
                          >
                            <Trash2 size={18} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="flex justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
              >
                Cerrar
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};
