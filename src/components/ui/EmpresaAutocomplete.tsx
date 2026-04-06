/**
 * EmpresaAutocomplete Component
 * Componente de autocompletado para seleccionar empresas
 * Con búsqueda en tiempo real y límite de resultados para rendimiento
 */
import { useState, useEffect, useRef } from 'react';
import { Building2, ChevronDown, X, Search } from 'lucide-react';
import empresaService, { Empresa } from '@/services/empresaService';

interface EmpresaAutocompleteProps {
  label?: string;
  value: string;
  onChange: (value: string, empresaId?: number) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  error?: string;
}

export const EmpresaAutocomplete = ({
  label = 'Empresa',
  value,
  onChange,
  placeholder = 'Buscar o seleccionar empresa...',
  disabled = false,
  required = false,
  error,
}: EmpresaAutocompleteProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Cargar empresas al abrir el dropdown o al buscar
  useEffect(() => {
    if (isOpen || searchTerm) {
      loadEmpresas();
    }
  }, [isOpen, searchTerm]);

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadEmpresas = async () => {
    try {
      setLoading(true);
      const response = await empresaService.getAll({
        page: 1,
        page_size: 50, // Límite para rendimiento
        search: searchTerm || undefined,
      });
      setEmpresas(response.items);
    } catch (error) {
      console.error('Error al cargar empresas:', error);
      setEmpresas([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (empresa: Empresa) => {
    onChange(empresa.razon_social, empresa.id);
    setSearchTerm('');
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange('', undefined);
    setSearchTerm('');
    inputRef.current?.focus();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setSearchTerm(newValue);
    onChange(newValue);
    if (!isOpen) setIsOpen(true);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-semibold text-slate-700 mb-1.5">
          {label}
          {required && <span className="text-red-500 ml-1 opacity-80">*</span>}
        </label>
      )}

      {/* Input Container */}
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          <Building2 size={18} />
        </div>

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          disabled={disabled}
          className={`
            w-full pl-10 pr-20 py-2.5 border rounded-xl shadow-sm transition-all duration-300
            focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent bg-slate-50/50 hover:bg-white
            disabled:bg-slate-100 disabled:cursor-not-allowed
            ${error ? 'border-red-400 focus:ring-red-500 hover:border-red-500' : 'border-slate-200 hover:border-slate-300'}
          `}
        />

        {/* Botones de acción */}
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {value && !disabled && (
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
            onClick={() => !disabled && setIsOpen(!isOpen)}
            className="p-1 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600"
            disabled={disabled}
          >
            <ChevronDown size={16} className={`transition-transform ${isOpen ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}

      {/* Dropdown */}
      {isOpen && !disabled && (
        <div className="absolute z-50 w-full mt-2 bg-white/95 backdrop-blur-md border border-slate-100 rounded-2xl shadow-2xl overflow-hidden animate-slide-up">
          {/* Search Input */}
          <div className="p-2 border-b border-slate-100 bg-slate-50/80">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar empresa..."
                className="w-full pl-9 pr-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-ricoh-red bg-white shadow-sm"
              />
            </div>
          </div>

          {/* Lista de empresas */}
          <div className="overflow-y-auto max-h-52">
            {loading ? (
              <div className="p-4 text-center text-gray-500 text-sm">
                Cargando empresas...
              </div>
            ) : empresas.length === 0 ? (
              <div className="p-4 text-center text-gray-500 text-sm">
                {searchTerm ? 'No se encontraron empresas' : 'No hay empresas disponibles'}
              </div>
            ) : (
              <>
                {empresas.map((empresa) => (
                  <button
                    key={empresa.id}
                    type="button"
                    onClick={() => handleSelect(empresa)}
                    className={`
                      w-full px-4 py-3 text-left hover:bg-red-50 transition-colors
                      border-b border-slate-50 last:border-b-0
                      ${value === empresa.razon_social ? 'bg-red-50/60' : ''}
                    `}
                  >
                    <div className="flex items-start gap-3">
                      <Building2 size={16} className="text-slate-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-slate-800 truncate">
                          {empresa.razon_social}
                        </p>
                        {empresa.nombre_comercial !== empresa.razon_social && (
                          <p className="text-xs text-slate-500 truncate mt-0.5">
                            {empresa.nombre_comercial}
                          </p>
                        )}
                        {empresa.nit && (
                          <p className="text-xs font-medium text-slate-400 mt-0.5">
                            NIT: {empresa.nit}
                          </p>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
                
                {empresas.length === 50 && (
                  <div className="p-3 text-xs text-center font-medium text-slate-500 bg-slate-50 border-t border-slate-100">
                    Mostrando primeras 50 empresas. Use la búsqueda para filtrar.
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EmpresaAutocomplete;
