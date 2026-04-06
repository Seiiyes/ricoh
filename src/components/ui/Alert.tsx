import React from 'react';
import { AlertCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-react';

export interface AlertProps {
  variant?: 'success' | 'warning' | 'error' | 'info';
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  variant = 'info',
  title,
  children,
  onClose,
  className = '',
}) => {
  const baseStyles = 'rounded-xl p-4 border-l-4 shadow-sm animate-fade-in relative overflow-hidden';
  
  const variantStyles = {
    success: 'bg-green-50/80 border-green-500 text-green-900 border border-green-100',
    warning: 'bg-yellow-50/80 border-yellow-500 text-yellow-900 border border-yellow-100',
    error: 'bg-red-50/80 border-ricoh-red text-red-900 border border-red-100',
    info: 'bg-slate-50/80 border-blue-500 text-blue-900 border border-slate-100',
  };
  
  const icons = {
    success: <CheckCircle size={20} />,
    warning: <AlertTriangle size={20} />,
    error: <AlertCircle size={20} />,
    info: <Info size={20} />,
  };
  
  return (
    <div className={`${baseStyles} ${variantStyles[variant]} ${className}`}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {icons[variant]}
        </div>
        
        <div className="flex-1">
          {title && (
            <h4 className="font-bold text-sm mb-1">{title}</h4>
          )}
          <div className="text-sm">{children}</div>
        </div>
        
        {onClose && (
          <button
            onClick={onClose}
            className="flex-shrink-0 hover:opacity-70 transition-opacity"
          >
            <X size={18} />
          </button>
        )}
      </div>
    </div>
  );
};
