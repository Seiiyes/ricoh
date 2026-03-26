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
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
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
            w-full pl-10 pr-20 py-2 border rounded-lg
            focus:outline-none focus:ring-2 focus:ring-blue-500
            disabled:bg-gray-100 disabled:cursor-not-allowed
            ${error ? 'border-red-500' : 'border-gray-300'}
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
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-64 overflow-hidden">
          {/* Search Input */}
          <div className="p-2 border-b border-gray-200 bg-gray-50">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar empresa..."
                className="w-full pl-9 pr-3 py-1.5 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                      w-full px-4 py-2.5 text-left hover:bg-blue-50 transition-colors
                      border-b border-gray-100 last:border-b-0
                      ${value === empresa.razon_social ? 'bg-blue-50' : ''}
                    `}
                  >
                    <div className="flex items-start gap-2">
                      <Building2 size={16} className="text-gray-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {empresa.razon_social}
                        </p>
                        {empresa.nombre_comercial !== empresa.razon_social && (
                          <p className="text-xs text-gray-500 truncate">
                            {empresa.nombre_comercial}
                          </p>
                        )}
                        {empresa.nit && (
                          <p className="text-xs text-gray-400">
                            NIT: {empresa.nit}
                          </p>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
                
                {empresas.length === 50 && (
                  <div className="p-2 text-xs text-center text-gray-500 bg-gray-50 border-t border-gray-200">
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
