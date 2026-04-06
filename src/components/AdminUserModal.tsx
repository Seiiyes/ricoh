/**
 * Modal para crear/editar usuarios admin
 */
import { useState, useEffect } from 'react';
import { X, Eye, EyeOff } from 'lucide-react';
import { AdminUser } from '../services/authService';
import { AdminUserCreate, AdminUserUpdate } from '../services/adminUserService';
import empresaService, { Empresa } from '../services/empresaService';
import { parseApiError } from '../utils/errorHandler';

interface AdminUserModalProps {
  adminUser: AdminUser | null;
  onClose: () => void;
  onSave: (data: AdminUserCreate | AdminUserUpdate) => Promise<void>;
}

const AdminUserModal = ({ adminUser, onClose, onSave }: AdminUserModalProps) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    nombre_completo: '',
    email: '',
    rol: 'admin' as 'superadmin' | 'admin' | 'viewer' | 'operator',
    empresa_id: null as number | null,
  });
  
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);
  
  useEffect(() => {
    loadEmpresas();
    
    if (adminUser) {
      setFormData({
        username: adminUser.username,
        password: '',
        nombre_completo: adminUser.nombre_completo,
        email: adminUser.email,
        rol: adminUser.rol,
        empresa_id: adminUser.empresa_id,
      });
    }
  }, [adminUser]);
  
  const loadEmpresas = async () => {
    try {
      const response = await empresaService.getAll({ page_size: 100 });
      setEmpresas(response.items.filter(e => e.is_active));
    } catch (error) {
      console.error('Error al cargar empresas:', error);
    }
  };
  
  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    return strength;
  };
  
  const handlePasswordChange = (password: string) => {
    setFormData({ ...formData, password });
    setPasswordStrength(calculatePasswordStrength(password));
  };
  
  const getPasswordStrengthColor = () => {
    if (passwordStrength <= 2) return 'bg-red-500';
    if (passwordStrength === 3) return 'bg-yellow-500';
    if (passwordStrength === 4) return 'bg-blue-500';
    return 'bg-green-500';
  };
  
  const getPasswordStrengthText = () => {
    if (passwordStrength <= 2) return 'Débil';
    if (passwordStrength === 3) return 'Media';
    if (passwordStrength === 4) return 'Fuerte';
    return 'Muy fuerte';
  };
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!adminUser && !formData.username.trim()) {
      newErrors.username = 'El username es requerido';
    } else if (!adminUser && !/^[a-z0-9_-]+$/.test(formData.username)) {
      newErrors.username = 'Solo minúsculas, números, guiones y guiones bajos';
    }
    
    if (!adminUser && !formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (!adminUser && formData.password) {
      const passwordErrors = [];
      if (formData.password.length < 8) passwordErrors.push('mínimo 8 caracteres');
      if (!/[a-z]/.test(formData.password)) passwordErrors.push('una minúscula');
      if (!/[A-Z]/.test(formData.password)) passwordErrors.push('una mayúscula');
      if (!/[0-9]/.test(formData.password)) passwordErrors.push('un número');
      if (!/[^a-zA-Z0-9]/.test(formData.password)) passwordErrors.push('un carácter especial');
      
      if (passwordErrors.length > 0) {
        newErrors.password = `La contraseña debe contener: ${passwordErrors.join(', ')}`;
      }
    }
    
    if (!formData.nombre_completo.trim()) {
      newErrors.nombre_completo = 'El nombre completo es requerido';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Formato de email inválido';
    }
    
    if (formData.rol === 'superadmin' && formData.empresa_id !== null) {
      newErrors.empresa_id = 'Superadmin no debe tener empresa asignada';
    }
    
    if (formData.rol !== 'superadmin' && formData.empresa_id === null) {
      newErrors.empresa_id = 'Debe seleccionar una empresa';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    try {
      const data: any = {
        nombre_completo: formData.nombre_completo,
        email: formData.email,
        rol: formData.rol,
        empresa_id: formData.empresa_id,
      };
      
      if (!adminUser) {
        data.username = formData.username;
        data.password = formData.password;
      }
      
      await onSave(data);
      onClose();
    } catch (error: any) {
      const errorMessage = parseApiError(error, 'Error al guardar usuario');
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
            {adminUser ? 'Editar Usuario Admin' : 'Nuevo Usuario Admin'}
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
            {!adminUser && (
              <div className="col-span-2">
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                  Username <span className="text-ricoh-red">*</span>
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value.toLowerCase() })}
                  className={`w-full px-4 py-2.5 border bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:bg-white transition-colors shadow-sm ${
                    errors.username ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-transparent'
                  }`}
                  placeholder="usuario_admin"
                />
                {errors.username && (
                  <p className="text-red-500 text-xs mt-1.5 font-medium">{errors.username}</p>
                )}
                <p className="text-slate-400 text-xs mt-1.5">Solo minúsculas, números, guiones y guiones bajos</p>
              </div>
            )}
            
            {!adminUser && (
              <div className="col-span-2">
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                  Contraseña <span className="text-ricoh-red">*</span>
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => handlePasswordChange(e.target.value)}
                    className={`w-full px-4 py-2.5 border bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:bg-white transition-colors shadow-sm pr-10 ${
                      errors.password ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-transparent'
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none focus:text-ricoh-red"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
                
                {/* Requisitos de contraseña */}
                {formData.password && (
                  <div className="mt-2.5 space-y-2">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full transition-all duration-300 ${getPasswordStrengthColor()}`}
                          style={{ width: `${(passwordStrength / 5) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">{getPasswordStrengthText()}</span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-xs font-medium">
                      <div className={`flex items-center gap-1.5 ${formData.password.length >= 8 ? 'text-green-600' : 'text-slate-400'}`}>
                        <span>{formData.password.length >= 8 ? '✓' : '○'}</span>
                        <span>Mínimo 8 caracteres</span>
                      </div>
                      <div className={`flex items-center gap-1.5 ${/[a-z]/.test(formData.password) ? 'text-green-600' : 'text-slate-400'}`}>
                        <span>{/[a-z]/.test(formData.password) ? '✓' : '○'}</span>
                        <span>Una minúscula (a-z)</span>
                      </div>
                      <div className={`flex items-center gap-1.5 ${/[A-Z]/.test(formData.password) ? 'text-green-600' : 'text-slate-400'}`}>
                        <span>{/[A-Z]/.test(formData.password) ? '✓' : '○'}</span>
                        <span>Una mayúscula (A-Z)</span>
                      </div>
                      <div className={`flex items-center gap-1.5 ${/[0-9]/.test(formData.password) ? 'text-green-600' : 'text-slate-400'}`}>
                        <span>{/[0-9]/.test(formData.password) ? '✓' : '○'}</span>
                        <span>Un número (0-9)</span>
                      </div>
                      <div className={`flex items-center gap-1.5 ${/[^a-zA-Z0-9]/.test(formData.password) ? 'text-green-600' : 'text-slate-400'}`}>
                        <span>{/[^a-zA-Z0-9]/.test(formData.password) ? '✓' : '○'}</span>
                        <span>Un carácter especial</span>
                      </div>
                    </div>
                  </div>
                )}
                
                {errors.password && (
                  <p className="text-red-500 text-xs mt-1.5 font-medium">{errors.password}</p>
                )}
              </div>
            )}
            
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                Nombre Completo <span className="text-ricoh-red">*</span>
              </label>
              <input
                type="text"
                value={formData.nombre_completo}
                onChange={(e) => setFormData({ ...formData, nombre_completo: e.target.value })}
                className={`w-full px-4 py-2.5 border bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:bg-white transition-colors shadow-sm ${
                  errors.nombre_completo ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-transparent'
                }`}
              />
              {errors.nombre_completo && (
                <p className="text-red-500 text-xs mt-1.5 font-medium">{errors.nombre_completo}</p>
              )}
            </div>
            
            <div className="col-span-2">
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                Email <span className="text-ricoh-red">*</span>
              </label>
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
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                Rol <span className="text-ricoh-red">*</span>
              </label>
              <select
                value={formData.rol}
                onChange={(e) => {
                  const newRol = e.target.value as typeof formData.rol;
                  setFormData({
                    ...formData,
                    rol: newRol,
                    empresa_id: newRol === 'superadmin' ? null : formData.empresa_id,
                  });
                }}
                className="w-full px-4 py-2.5 border border-slate-200 bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red focus:border-transparent shadow-sm transition-colors"
              >
                <option value="admin">Admin</option>
                <option value="superadmin">Superadmin</option>
                <option value="viewer">Viewer</option>
                <option value="operator">Operator</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                Empresa {formData.rol !== 'superadmin' && <span className="text-ricoh-red">*</span>}
              </label>
              <select
                value={formData.empresa_id || ''}
                onChange={(e) => setFormData({ ...formData, empresa_id: e.target.value ? Number(e.target.value) : null })}
                disabled={formData.rol === 'superadmin'}
                className={`w-full px-4 py-2.5 border bg-slate-50/50 hover:bg-white rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-ricoh-red disabled:opacity-60 disabled:bg-slate-100 disabled:cursor-not-allowed shadow-sm transition-colors ${
                  errors.empresa_id ? 'border-red-400 focus:border-red-500' : 'border-slate-200 focus:border-transparent'
                }`}
              >
                <option value="">Seleccionar empresa</option>
                {empresas.map((empresa) => (
                  <option key={empresa.id} value={empresa.id}>
                    {empresa.razon_social}
                  </option>
                ))}
              </select>
              {errors.empresa_id && (
                <p className="text-red-500 text-xs mt-1.5 font-medium">{errors.empresa_id}</p>
              )}
              {formData.rol === 'superadmin' && (
                <p className="text-slate-400 text-xs mt-1.5">Superadmin no requiere empresa</p>
              )}
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
                'Guardar Usuario'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminUserModal;
