import React from 'react';
import { Loader2 } from 'lucide-react';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  text?: string;
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  className = '',
  text,
}) => {
  const sizeStyles = {
    sm: 16,
    md: 24,
    lg: 32,
    xl: 48,
  };
  
  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      <Loader2 size={sizeStyles[size]} className="animate-spin text-ricoh-red" />
      {text && <p className="text-sm text-gray-600">{text}</p>}
    </div>
  );
};
