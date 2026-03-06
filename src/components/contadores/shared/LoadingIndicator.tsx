import { Loader2 } from 'lucide-react';

interface LoadingIndicatorProps {
  message?: string;
}

export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ 
  message = 'Cargando...' 
}) => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-slate-400">
      <Loader2 className="animate-spin mb-3" size={48} />
      <p className="text-sm">{message}</p>
    </div>
  );
};
