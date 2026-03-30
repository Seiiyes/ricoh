import { sileo } from 'sileo';

/**
 * Hook personalizado para manejar notificaciones con Sileo
 * Proporciona una API consistente para mostrar notificaciones en toda la aplicación
 */
export const useNotification = () => {
  return {
    success: (message: string, description?: string) => {
      sileo.success(message, { description });
    },
    
    error: (message: string, description?: string) => {
      sileo.error(message, { description });
    },
    
    info: (message: string, description?: string) => {
      sileo.info(message, { description });
    },
    
    warning: (message: string, description?: string) => {
      sileo.warning(message, { description });
    },
    
    loading: (message: string, description?: string) => {
      return sileo.loading(message, { description });
    },
    
    promise: <T,>(
      promise: Promise<T>,
      messages: {
        loading: string;
        success: string | ((data: T) => string);
        error: string | ((error: any) => string);
      }
    ) => {
      return sileo.promise(promise, messages);
    },
  };
};
