import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  variant?: 'default' | 'underline';
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  variant = 'default',
  className = '',
  ...props
}) => {
  const baseStyles = 'w-full py-2.5 px-4 text-sm transition-all duration-300 focus:outline-none bg-slate-50/50 hover:bg-white shadow-sm';
  
  const variantStyles = {
    default: `border rounded-xl ${
      error 
        ? 'border-red-400 focus:ring-2 focus:ring-red-500 focus:border-red-500 bg-red-50/30' 
        : 'border-slate-200 focus:ring-2 focus:ring-ricoh-red focus:border-transparent focus:bg-white'
    }`,
    underline: `border-0 border-b-2 rounded-none px-0 bg-transparent shadow-none hover:bg-transparent ${
      error 
        ? 'border-red-400 focus:border-red-500' 
        : 'border-slate-200 focus:border-ricoh-red'
    }`,
  };
  
  return (
    <div className="space-y-1.5">
      {label && (
        <label className="block text-sm font-semibold text-slate-700">
          {label}
        </label>
      )}
      
      <input
        className={`${baseStyles} ${variantStyles[variant]} ${className}`}
        {...props}
      />
      
      {error && (
        <p className="text-xs text-red-600">{error}</p>
      )}
      
      {helperText && !error && (
        <p className="text-xs text-gray-500">{helperText}</p>
      )}
    </div>
  );
};
