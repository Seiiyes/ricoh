// Editor de permisos de usuario
import { useState, useEffect } from 'react';
import { Save } from 'lucide-react';
import { actualizarFuncionesEnImpresora } from '@/services/servicioUsuarios';
import { Button, Alert } from '@/components/ui';
import { useNotification } from '@/hooks/useNotification';

interface Permisos {
  func_copier: boolean;
  func_copier_color?: boolean;
  func_printer: boolean;
  func_printer_color?: boolean;
  func_document_server: boolean;
  func_fax: boolean;
  func_scanner: boolean;
  func_browser: boolean;
}

interface EditorPermisosProps {
  permisos: Permisos;
  onChange: (permisos: Permisos) => void;
  // Modo impresora: si se proporciona, actualiza directamente en la impresora física
  modoImpresora?: {
    printerIp: string;
    printerName: string;
    userCode: string;
    userName: string;
    onSuccess?: () => void;
  };
}

export const EditorPermisos = ({ permisos, onChange, modoImpresora }: EditorPermisosProps) => {
  const notify = useNotification();
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [permisosLocales, setPermisosLocales] = useState(permisos);

  // Sincronizar estado local cuando cambien los permisos del padre
  useEffect(() => {
    console.log('🔄 EditorPermisos - Actualizando permisos locales:', permisos);
    setPermisosLocales(permisos);
  }, [permisos]);

  const handleToggle = (key: keyof Permisos) => {
    const nuevosPermisos = {
      ...permisosLocales,
      [key]: !permisosLocales[key],
    };
    setPermisosLocales(nuevosPermisos);
    
    // Si NO está en modo impresora, actualizar inmediatamente el padre
    if (!modoImpresora) {
      onChange(nuevosPermisos);
    }
  };

  const handleGuardarEnImpresora = async () => {
    if (!modoImpresora) return;

    try {
      setGuardando(true);
      setError(null);

      // Mapear de formato frontend a formato backend
      const funciones = {
        copiadora: permisosLocales.func_copier,
        copiadora_color: permisosLocales.func_copier_color || false,
        impresora: permisosLocales.func_printer,
        impresora_color: permisosLocales.func_printer_color || false,
        escaner: permisosLocales.func_scanner,
        document_server: permisosLocales.func_document_server,
        fax: permisosLocales.func_fax,
        navegador: permisosLocales.func_browser,
      };

      const resultado = await actualizarFuncionesEnImpresora(
        modoImpresora.printerIp,
        modoImpresora.userCode,
        funciones
      );

      if (resultado.success) {
        // Actualizar el padre con los nuevos permisos
        onChange(permisosLocales);
        
        // Mostrar mensaje de éxito
        notify.success('Permisos actualizados', `Los permisos se actualizaron correctamente en ${modoImpresora.printerName}`);
        
        if (modoImpresora.onSuccess) {
          modoImpresora.onSuccess();
        }
      } else {
        setError(resultado.message || 'Error al actualizar funciones');
      }
    } catch (err: any) {
      console.error('Error al guardar funciones:', err);
      setError(err.message || 'Error al actualizar funciones en la impresora');
    } finally {
      setGuardando(false);
    }
  };

  const permisosConfig = [
    {
      key: 'func_copier' as keyof Permisos,
      label: 'Copiadora',
      icon: '📄',
      descripcion: 'Permite el uso de las funciones de copiado.',
      colorKey: 'func_copier_color' as keyof Permisos,
    },
    {
      key: 'func_printer' as keyof Permisos,
      label: 'Impresora',
      icon: '🖨️',
      descripcion: 'Permite imprimir documentos desde el equipo.',
      colorKey: 'func_printer_color' as keyof Permisos,
    },
    {
      key: 'func_scanner' as keyof Permisos,
      label: 'Escaner',
      icon: '🔍',
      descripcion: 'Permite escanear y enviar documentos.',
    },
    {
      key: 'func_fax' as keyof Permisos,
      label: 'Fax',
      icon: '📠',
      descripcion: 'Permite el envío y recepción de faxes.',
    },
    {
      key: 'func_document_server' as keyof Permisos,
      label: 'Servidor de documentos',
      icon: '📁',
      descripcion: 'Permite almacenar archivos en el disco del equipo.',
    },
    {
      key: 'func_browser' as keyof Permisos,
      label: 'Navegador',
      icon: '🌐',
      descripcion: 'Permite navegar por internet desde el panel.',
    },
  ];

  const permisosActivos = Object.values(permisosLocales).filter(Boolean).length;
  const hayCambios = JSON.stringify(permisosLocales) !== JSON.stringify(permisos);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b pb-2">
        <div>
          <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
            ¿Qué puede hacer en este equipo?
          </h3>
          {modoImpresora && (
            <p className="text-[9px] text-slate-500 mt-1">
              📍 {modoImpresora.printerName} • {modoImpresora.printerIp}
            </p>
          )}
        </div>
        <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
          {permisosActivos} activas
        </span>
      </div>

      {/* Error */}
      {error && (
        <Alert variant="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Grid de permisos */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {permisosConfig.map((config) => (
          <div key={config.key} className="space-y-2">
            <label
              className={`flex items-start gap-3 p-4 border-2 rounded-xl cursor-pointer transition-all shadow-sm ${
                permisosLocales[config.key]
                  ? 'border-ricoh-red bg-red-50/30 ring-4 ring-red-500/5'
                  : 'border-slate-100 hover:border-slate-300 bg-white grayscale opacity-70 hover:grayscale-0 hover:opacity-100'
              }`}
            >
              <input
                type="checkbox"
                checked={permisosLocales[config.key]}
                onChange={() => handleToggle(config.key)}
                disabled={guardando}
                className="mt-1 w-5 h-5 text-ricoh-red focus:ring-ricoh-red rounded border-slate-300"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xl">{config.icon}</span>
                  <span
                    className={`text-[11px] font-black uppercase tracking-tight ${
                      permisosLocales[config.key] ? 'text-slate-900' : 'text-slate-700'
                    }`}
                  >
                    {config.label}
                  </span>
                </div>
                <p className="text-[10px] text-slate-500 font-bold leading-tight">
                  {config.descripcion}
                </p>
              </div>
            </label>

            {/* Sub-opción de COLOR */}
            {config.colorKey && permisosLocales[config.key] && (
              <div className="ml-6 animate-in slide-in-from-left-2 duration-200">
                <label
                  className={`flex items-center gap-2 p-2 rounded-lg border-2 cursor-pointer transition-all ${
                    permisosLocales[config.colorKey]
                      ? 'border-red-400 bg-red-50/50'
                      : 'border-slate-100 bg-slate-50 hover:bg-white'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={permisosLocales[config.colorKey]}
                    onChange={() => handleToggle(config.colorKey!)}
                    disabled={guardando}
                    className="w-4 h-4 text-ricoh-red focus:ring-ricoh-red rounded border-slate-300"
                  />
                  <span
                    className={`text-[10px] font-black uppercase tracking-wide ${
                      permisosLocales[config.colorKey] ? 'text-red-800' : 'text-slate-500'
                    }`}
                  >
                    Permitir Color
                  </span>
                </label>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Botón de guardar (solo en modo impresora) */}
      {modoImpresora && hayCambios && (
        <div className="pt-4 border-t">
          <Button
            onClick={handleGuardarEnImpresora}
            loading={guardando}
            icon={<Save size={18} />}
            className="w-full bg-ricoh-red hover:bg-red-700 shadow-xl shadow-red-500/20"
          >
            {guardando ? 'Guardando en impresora...' : `Guardar en ${modoImpresora.printerName}`}
          </Button>
        </div>
      )}
    </div>
  );
};
