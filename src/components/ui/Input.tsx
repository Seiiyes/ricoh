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
  const baseStyles = 'w-full py-2 px-3 text-sm transition-colors focus:outline-none';
  
  const variantStyles = {
    default: `border rounded-lg ${
      error 
        ? 'border-red-500 focus:ring-2 focus:ring-red-500' 
        : 'border-gray-300 focus:ring-2 focus:ring-ricoh-red focus:border-ricoh-red'
    }`,
    underline: `border-0 border-b-2 rounded-none px-0 ${
      error 
        ? 'border-red-500 focus:border-red-600' 
        : 'border-gray-200 focus:border-ricoh-red'
    }`,
  };
  
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-xs font-bold text-gray-600 uppercase">
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
