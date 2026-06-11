import { useState, useEffect, useRef } from 'react';
import { Briefcase, ChevronDown, X, Plus } from 'lucide-react';
import empresaService, { CentroCostosSugerenciasResponse } from '@/services/empresaService';

interface CentroCostosAutocompleteProps {
  label?: string;
  value: string;
  empresaName?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
  allowGlobal?: boolean;
}

export const CentroCostosAutocomplete = ({
  label = 'Centro de costos',
  value,
  empresaName,
  onChange,
  placeholder = 'Buscar o crear centro de costos...',
  disabled = false,
  required = false,
  error,
  allowGlobal = false,
}: CentroCostosAutocompleteProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<CentroCostosSugerenciasResponse | null>(null);
  const [inputValue, setInputValue] = useState(value || '');
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync prop to local state
  useEffect(() => {
    setInputValue(value || '');
  }, [value]);

  // Fetch options when empresaName changes
  useEffect(() => {
    if (empresaName) {
      loadData(empresaName);
    } else if (allowGlobal) {
      loadData('all');
    } else {
      setData(null);
    }
  }, [empresaName, allowGlobal]);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        // On blur, if they typed something but didn't select, we update the real value anyway (Creatable)
        if (inputValue !== value) {
          onChange(inputValue.trim().toUpperCase());
        }
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [inputValue, value, onChange]);

  const loadData = async (name: string) => {
    try {
      setLoading(true);
      const res = await empresaService.getCentroCostos(name);
      setData(res);
    } catch (err) {
      console.error('Error cargando centros de costos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (val: string) => {
    const finalVal = val.trim().toUpperCase();
    setInputValue(finalVal);
    onChange(finalVal);
    setIsOpen(false);
  };

  const handleClear = () => {
    setInputValue('');
    onChange('');
    inputRef.current?.focus();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value.toUpperCase(); // Force uppercase
    setInputValue(newValue);
    onChange(newValue);
    if (!isOpen && !disabled) setIsOpen(true);
  };

  const isInputDisabled = disabled || (!allowGlobal && !empresaName);
  const showPlaceholder = (!allowGlobal && !empresaName) ? 'Seleccione una empresa primero...' : placeholder;

  // Filter based on input
  const filterText = inputValue.toLowerCase().trim();
  const propiosFiltrados = data?.propios.filter(c => c.nombre.toLowerCase().includes(filterText)) || [];
  const sugerenciasFiltradas = data?.sugerencias_globales.filter(s => s.toLowerCase().includes(filterText)) || [];
  
  // Check if exactly matches
  const exactMatch = 
    propiosFiltrados.some(c => c.nombre.toLowerCase() === filterText) ||
    sugerenciasFiltradas.some(s => s.toLowerCase() === filterText);
    
  const showCreateOption = filterText.length > 0 && !exactMatch;

  return (
    <div className="relative" ref={dropdownRef}>
      {label && (
        <label className="block text-sm font-semibold text-slate-700 mb-1.5">
          {label}
          {required && <span className="text-red-500 ml-1 opacity-80">*</span>}
        </label>
      )}

      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <Briefcase size={18} />
        </div>

        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={() => { if (!isInputDisabled) setIsOpen(true); }}
          placeholder={showPlaceholder}
          disabled={isInputDisabled}
          className={`
            w-full pl-10 pr-20 py-2.5 border rounded-xl shadow-sm transition-all duration-300
            focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent bg-slate-50/50 hover:bg-white
            disabled:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-70 uppercase
            ${error ? 'border-red-400 focus:ring-red-500 hover:border-red-500' : 'border-slate-200 hover:border-slate-300'}
          `}
        />

        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {inputValue && !disabled && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600"
              title="Limpiar"
            >
              <X size={16} />
            </button>
          )}
          
          <button
            type="button"
            onClick={() => !isInputDisabled && setIsOpen(!isOpen)}
            className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600"
            disabled={isInputDisabled}
          >
            <ChevronDown size={16} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>

      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}

      {isOpen && !isInputDisabled && (
        <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-md border border-slate-100 rounded-2xl shadow-2xl overflow-hidden animate-slide-up">
          <div className="overflow-y-auto max-h-60">
            {loading ? (
              <div className="p-4 text-center text-gray-500 text-sm">
                Cargando...
              </div>
            ) : (
              <div className="py-2">
                {/* Crear Nueva Opción */}
                {showCreateOption && (
                  <button
                    type="button"
                    onClick={() => handleSelect(inputValue)}
                    className="w-full px-4 py-3 text-left hover:bg-red-50 transition-colors border-b border-slate-50 flex items-center gap-3 text-ricoh-red"
                  >
                    <Plus size={16} className="flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-sm">
                        Crear nuevo: <span className="font-bold">"{inputValue.toUpperCase()}"</span>
                      </p>
                      <p className="text-xs text-red-600/80 mt-0.5">Se asociará automáticamente a la empresa</p>
                    </div>
                  </button>
                )}

                {/* Lista Propios */}
                {propiosFiltrados.length > 0 && (
                  <div className="mb-2">
                    <div className="px-4 py-2 text-xs font-black text-slate-400 uppercase tracking-widest bg-slate-50/50">
                      De esta empresa
                    </div>
                    {propiosFiltrados.map((cc) => (
                      <button
                        key={`propio-${cc.id}`}
                        type="button"
                        onClick={() => handleSelect(cc.nombre)}
                        className={`
                          w-full px-4 py-2.5 text-left hover:bg-slate-50 transition-colors
                          ${inputValue === cc.nombre ? 'bg-red-50/60' : ''}
                        `}
                      >
                        <p className="font-semibold text-sm text-slate-800">{cc.nombre}</p>
                      </button>
                    ))}
                  </div>
                )}

                {/* Lista Sugerencias */}
                {sugerenciasFiltradas.length > 0 && (
                  <div>
                    <div className="px-4 py-2 text-xs font-black text-slate-400 uppercase tracking-widest bg-slate-50/50 border-t border-slate-100">
                      Sugerencias globales
                    </div>
                    {sugerenciasFiltradas.map((sug, idx) => (
                      <button
                        key={`sug-${idx}`}
                        type="button"
                        onClick={() => handleSelect(sug)}
                        className="w-full px-4 py-2 text-left hover:bg-blue-50 transition-colors text-slate-600"
                      >
                        <p className="font-medium text-sm text-slate-600">{sug}</p>
                      </button>
                    ))}
                  </div>
                )}

                {/* Sin Resultados */}
                {!showCreateOption && propiosFiltrados.length === 0 && sugerenciasFiltradas.length === 0 && (
                  <div className="p-4 text-center text-gray-500 text-sm">
                    No hay resultados
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CentroCostosAutocomplete;
