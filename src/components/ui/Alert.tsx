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
  const baseStyles = 'rounded-lg p-4 border-l-4';
  
  const variantStyles = {
    success: 'bg-green-50 border-green-500 text-green-800',
    warning: 'bg-yellow-50 border-yellow-500 text-yellow-800',
    error: 'bg-red-50 border-red-500 text-red-800',
    info: 'bg-blue-50 border-blue-500 text-blue-800',
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
