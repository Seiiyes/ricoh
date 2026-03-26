/**
 * Modal para crear/editar empresas
 */
import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Empresa, EmpresaCreate, EmpresaUpdate } from '../services/empresaService';
import { parseApiError } from '../utils/errorHandler';

interface EmpresaModalProps {
  empresa: Empresa | null;
  onClose: () => void;
  onSave: (data: EmpresaCreate | EmpresaUpdate) => Promise<void>;
}

const EmpresaModal = ({ empresa, onClose, onSave }: EmpresaModalProps) => {
  const [formData, setFormData] = useState({
    razon_social: '',
    nombre_comercial: '',
    nit: '',
    direccion: '',
    telefono: '',
    email: '',
    contacto_nombre: '',
    contacto_cargo: '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    if (empresa) {
      setFormData({
        razon_social: empresa.razon_social,
        nombre_comercial: empresa.nombre_comercial,
        nit: empresa.nit || '',
        direccion: empresa.direccion || '',
        telefono: empresa.telefono || '',
        email: empresa.email || '',
        contacto_nombre: empresa.contacto_nombre || '',
        contacto_cargo: empresa.contacto_cargo || '',
      });
    }
  }, [empresa]);
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.razon_social.trim()) {
      newErrors.razon_social = 'La razón social es requerida';
    }
    
    if (!formData.nombre_comercial.trim()) {
      newErrors.nombre_comercial = 'El nombre comercial es requerido';
    } else if (!/^[a-z0-9-]+$/.test(formData.nombre_comercial)) {
      newErrors.nombre_comercial = 'Debe estar en formato kebab-case (ej: mi-empresa)';
    }
    
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Formato de email inválido';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    try {
      const data = {
        ...formData,
        nit: formData.nit || undefined,
        direccion: formData.direccion || undefined,
        telefono: formData.telefono || undefined,
        email: formData.email || undefined,
        contacto_nombre: formData.contacto_nombre || undefined,
        contacto_cargo: formData.contacto_cargo || undefined,
      };
      
      await onSave(data);
      onClose();
    } catch (error: any) {
      const errorMessage = parseApiError(error, 'Error al guardar empresa');
      setErrors({ general: errorMessage });
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">
            {empresa ? 'Editar Empresa' : 'Nueva Empresa'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errors.general && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {errors.general}
            </div>
          )}
          
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Razón Social <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.razon_social}
                onChange={(e) => setFormData({ ...formData, razon_social: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.razon_social ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.razon_social && (
                <p className="text-red-500 text-sm mt-1">{errors.razon_social}</p>
              )}
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre Comercial <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.nombre_comercial}
                onChange={(e) => setFormData({ ...formData, nombre_comercial: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.nombre_comercial ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="mi-empresa"
              />
              {errors.nombre_comercial && (
                <p className="text-red-500 text-sm mt-1">{errors.nombre_comercial}</p>
              )}
              <p className="text-gray-500 text-xs mt-1">Formato kebab-case (solo minúsculas, números y guiones)</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">NIT</label>
              <input
                type="text"
                value={formData.nit}
                onChange={(e) => setFormData({ ...formData, nit: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
              <input
                type="text"
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
              <input
                type="text"
                value={formData.direccion}
                onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
              />
              {errors.email && (
                <p className="text-red-500 text-sm mt-1">{errors.email}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Nombre de Contacto</label>
              <input
                type="text"
                value={formData.contacto_nombre}
                onChange={(e) => setFormData({ ...formData, contacto_nombre: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Cargo de Contacto</label>
              <input
                type="text"
                value={formData.contacto_cargo}
                onChange={(e) => setFormData({ ...formData, contacto_cargo: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmpresaModal;
