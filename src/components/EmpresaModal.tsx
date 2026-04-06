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
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-100 w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-slide-up flex flex-col">
        <div className="flex items-center justify-between p-6 border-b border-slate-100 bg-slate-50/80 sticky top-0 z-10 backdrop-blur-sm">
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            {empresa ? 'Editar Empresa' : 'Nueva Empresa'}
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-ricoh-red hover:bg-red-50 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:ring-offset-1"
          >
            <X size={20} />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {errors.general && (
            <div className="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-xl text-sm font-medium animate-fade-in">
              {errors.general}
            </div>
          )}
          
          <div className="grid grid-cols-2 gap-5">
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                Razón Social <span className="text-ricoh-red">*</span>
              </label>
              <input
                type="text"
                value={formData.razon_social}
                onChange={(e) => setFormData({ ...formData, razon_social: e.target.value })}
                className={`w-full px-4 py-2.5 border bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:bg-white transition-colors shadow-sm ${
                  errors.razon_social ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-transparent'
                }`}
              />
              {errors.razon_social && (
                <p className="text-red-500 text-xs mt-1.5 font-medium">{errors.razon_social}</p>
              )}
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                Nombre Comercial <span className="text-ricoh-red">*</span>
              </label>
              <input
                type="text"
                value={formData.nombre_comercial}
                onChange={(e) => setFormData({ ...formData, nombre_comercial: e.target.value })}
                className={`w-full px-4 py-2.5 border bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:bg-white transition-colors shadow-sm ${
                  errors.nombre_comercial ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-transparent'
                }`}
                placeholder="mi-empresa"
              />
              {errors.nombre_comercial && (
                <p className="text-red-500 text-xs mt-1.5 font-medium">{errors.nombre_comercial}</p>
              )}
              <p className="text-slate-400 text-xs mt-1.5">Formato kebab-case (solo minúsculas, números y guiones)</p>
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">NIT</label>
              <input
                type="text"
                value={formData.nit}
                onChange={(e) => setFormData({ ...formData, nit: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-200 bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent focus:bg-white transition-colors shadow-sm"
              />
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Teléfono</label>
              <input
                type="text"
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-200 bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent focus:bg-white transition-colors shadow-sm"
              />
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Dirección</label>
              <input
                type="text"
                value={formData.direccion}
                onChange={(e) => setFormData({ ...formData, direccion: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-200 bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent focus:bg-white transition-colors shadow-sm"
              />
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className={`w-full px-4 py-2.5 border bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:bg-white transition-colors shadow-sm ${
                  errors.email ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-transparent'
                }`}
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1.5 font-medium">{errors.email}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Nombre de Contacto</label>
              <input
                type="text"
                value={formData.contacto_nombre}
                onChange={(e) => setFormData({ ...formData, contacto_nombre: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-200 bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent focus:bg-white transition-colors shadow-sm"
              />
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Cargo de Contacto</label>
              <input
                type="text"
                value={formData.contacto_cargo}
                onChange={(e) => setFormData({ ...formData, contacto_cargo: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-200 bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent focus:bg-white transition-colors shadow-sm"
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3 pt-6 border-t border-slate-100 bg-slate-50/50 -mx-6 -mb-6 px-6 py-4 rounded-b-2xl">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-slate-600 font-medium bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="relative overflow-hidden px-6 py-2.5 bg-ricoh-red text-white font-semibold rounded-xl hover:bg-red-700 transition-all shadow-[0_4px_14px_0_rgba(227,6,19,0.2)] hover:shadow-[0_6px_20px_rgba(227,6,19,0.3)] disabled:opacity-70 disabled:cursor-not-allowed hover:-translate-y-0.5 active:translate-y-0"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Guardando...
                </span>
              ) : (
                'Guardar Empresa'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmpresaModal;
