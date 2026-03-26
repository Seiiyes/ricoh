/**
 * Utilidad para manejo consistente de errores de API
 * Convierte diferentes formatos de error a mensajes legibles
 */

/**
 * Parsea un error de API a un mensaje legible para el usuario
 * 
 * Maneja diferentes formatos de error:
 * - Arrays de errores de validación (422)
 * - Strings simples
 * - Objetos con message
 * - Cualquier otro formato
 * 
 * @param err - Error capturado en catch
 * @param defaultMessage - Mensaje por defecto si no se puede parsear
 * @returns Mensaje de error legible
 */
export function parseApiError(err: any, defaultMessage: string = 'Error desconocido'): string {
  // Intentar obtener detail del response
  if (err.response?.data?.detail) {
    const detail = err.response.data.detail;
    
    // Si detail es un array de errores de validación (422)
    if (Array.isArray(detail)) {
      return detail.map((e: any) => {
        if (typeof e === 'object' && e.msg) {
          // Formato: "campo: mensaje"
          const location = e.loc ? e.loc.filter((l: any) => l !== 'body').join('.') : '';
          return location ? `${location}: ${e.msg}` : e.msg;
        }
        return String(e);
      }).join(', ');
    } 
    // Si detail es un string
    else if (typeof detail === 'string') {
      return detail;
    }
    // Si detail es un objeto con message
    else if (typeof detail === 'object' && detail.message) {
      return detail.message;
    }
    // Cualquier otro caso, convertir a JSON
    else {
      try {
        return JSON.stringify(detail);
      } catch {
        return String(detail);
      }
    }
  } 
  // Si no hay detail, usar message del error
  else if (err.message) {
    return err.message;
  }
  
  // Mensaje por defecto
  return defaultMessage;
}

/**
 * Parsea errores específicos de autenticación
 * 
 * @param err - Error capturado en catch
 * @returns Mensaje de error específico de autenticación
 */
export function parseAuthError(err: any): string {
  const status = err.response?.status;
  
  if (status === 401) {
    return 'Usuario o contraseña incorrectos';
  } else if (status === 403) {
    const detail = err.response?.data?.detail || '';
    if (typeof detail === 'string') {
      if (detail.includes('bloqueada')) {
        return 'Cuenta bloqueada. Intenta nuevamente en 15 minutos';
      } else if (detail.includes('desactivada')) {
        return 'Cuenta desactivada. Contacta al administrador';
      }
    }
    return 'Acceso denegado';
  } else if (status === 429) {
    return 'Demasiados intentos. Espera un momento e intenta nuevamente';
  }
  
  return parseApiError(err, 'Error al iniciar sesión. Intenta nuevamente');
}

/**
 * Verifica si un error es de validación (422)
 * 
 * @param err - Error capturado en catch
 * @returns true si es error de validación
 */
export function isValidationError(err: any): boolean {
  return err.response?.status === 422;
}

/**
 * Verifica si un error es de autenticación (401/403)
 * 
 * @param err - Error capturado en catch
 * @returns true si es error de autenticación
 */
export function isAuthError(err: any): boolean {
  const status = err.response?.status;
  return status === 401 || status === 403;
}

/**
 * Verifica si un error es de rate limiting (429)
 * 
 * @param err - Error capturado en catch
 * @returns true si es error de rate limiting
 */
export function isRateLimitError(err: any): boolean {
  return err.response?.status === 429;
}
