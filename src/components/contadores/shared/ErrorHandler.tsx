import { useEffect } from 'react';
import { AlertCircle } from 'lucide-react';

interface ErrorHandlerProps {
  message: string;
  onDismiss: () => void;
  critical?: boolean;
}

export const ErrorHandler: React.FC<ErrorHandlerProps> = ({ 
  message, 
  onDismiss,
  critical = false 
}) => {
  useEffect(() => {
    if (!critical) {
      const timer = setTimeout(onDismiss, 10000);
      return () => clearTimeout(timer);
    }
  }, [critical, onDismiss]);

  return (
    <div 
      className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3"
      role="alert"
    >
      <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
      <div className="flex-1">
        <h3 className="font-bold text-red-900 text-sm">Error</h3>
        <p className="text-red-700 text-sm mt-1">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="text-xs font-bold uppercase text-red-600 hover:text-red-800"
        aria-label="Cerrar mensaje de error"
      >
        Cerrar
      </button>
    </div>
  );
};
