import React from 'react';

export interface BadgeProps {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'neutral',
  size = 'md',
  children,
  className = '',
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-full shadow-sm border backdrop-blur-sm transition-all';
  
  const variantStyles = {
    success: 'bg-green-100/80 text-green-800 border-green-200',
    warning: 'bg-yellow-100/80 text-yellow-800 border-yellow-200',
    error: 'bg-red-100/80 text-ricoh-red border-red-200',
    info: 'bg-blue-100/80 text-blue-800 border-blue-200',
    neutral: 'bg-slate-100/80 text-slate-800 border-slate-200',
  };
  
  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  };
  
  return (
    <span className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}>
      {children}
    </span>
  );
};
