import { sileo } from 'sileo';

/**
 * Hook personalizado para manejar notificaciones con Sileo
 * Proporciona una API consistente para mostrar notificaciones en toda la aplicación
 */
export const useNotification = () => {
  return {
    success: (message: string, description?: string) => {
      sileo.success({ title: message, description });
    },
    
    error: (message: string, description?: string) => {
      sileo.error({ title: message, description });
    },
    
    info: (message: string, description?: string) => {
      sileo.info({ title: message, description });
    },
    
    warning: (message: string, description?: string) => {
      sileo.warning({ title: message, description });
    },
    
    loading: (message: string, description?: string) => {
      return sileo.show({ type: 'loading', title: message, description });
    },
    
    promise: <T,>(
      promise: Promise<T>,
      messages: {
        loading: string;
        success: string | ((data: T) => string);
        error: string | ((error: any) => string);
      }
    ) => {
      return sileo.promise(promise, {
        loading: { title: messages.loading, type: 'loading' },
        success: typeof messages.success === 'function'
          ? (data: T) => ({ title: (messages.success as Function)(data), type: 'success' })
          : { title: messages.success, type: 'success' },
        error: typeof messages.error === 'function'
          ? (err: any) => ({ title: (messages.error as Function)(err), type: 'error' })
          : { title: messages.error, type: 'error' }
      });
    },
  };
};
