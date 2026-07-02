# Fix de CORS y Endpoint de Trabajos de Impresión - 12 de Junio de 2026

**Fecha**: 12 de Junio de 2026  
**Severidad**: Crítica (Bloqueo de funcionalidad principal de visualización de trabajos de impresión)  
**Estado**: Resuelto y Verificado en Producción  

---

## 🔍 Diagnóstico del Problema

El frontend presentaba el siguiente error en la consola del navegador al intentar cargar la cola de trabajos de impresión de la impresora 6 (IP `192.168.91.250`):

```
Access to XMLHttpRequest at 'http://192.168.91.131:8000/printers/6/jobs' from origin 'http://192.168.91.131' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
printerService.ts:322 Failed to fetch print jobs for printer 6: AxiosError: Network Error
```

Al revisar los logs de FastAPI del contenedor `ricoh-backend` en producción (`192.168.91.131`), se encontró la causa raíz:

```
2026-06-12 17:32:17,961 - api.printers - ERROR - Error getting print jobs for printer 6: 'RicohWebClient' object has no attribute 'get_stored_jobs'
```

### Explicación Técnica
1. **Falta de Despliegue de Código**: La lógica del backend local ya tenía implementada la función `get_stored_jobs` en la clase `RicohWebClient`. Sin embargo, el servidor de producción no tenía estos cambios actualizados en su volumen `/app/services/ricoh_web_client.py`.
2. **Efecto Colateral de CORS en FastAPI**: En FastAPI, cuando ocurre una excepción no controlada (`AttributeError` en este caso) antes o durante la ejecución del endpoint, la petición falla arrojando un error interno `500`. En este flujo de error, la respuesta final se formula de tal manera que las cabeceras CORS del middleware (`CORSMiddleware`) no se adjuntan, resultando en un error de CORS en el navegador en lugar de mostrar explícitamente el código `500` con el mensaje del error.

---

## 🛠️ Solución Implementada

1. **Sincronización y Reconstrucción**: Se ejecutó el script de despliegue completo `python deployment/deploy_to_server131.py` para subir los archivos correctos de backend y frontend.
2. **Reconstrucción del Contenedor**: Docker Compose reconstruyó la imagen `ricoh-app-backend` incorporando el método `get_stored_jobs` en la clase `RicohWebClient`.
3. **Re-inicialización de Credenciales**: Se ejecutó `docker exec ricoh-backend python scripts/init_superadmin.py` en producción para re-inicializar el superusuario administrador y garantizar la consistencia en el inicio de sesión.
4. **Verificación de CORS**: Al reintentar la carga de la página, las peticiones HTTP GET a `http://192.168.91.131:8000/api/v1/printers/6/jobs` se completaron con código HTTP `200 OK` de manera exitosa y las cabeceras CORS adecuadas se inyectaron correctamente en la respuesta.

---

## 🧪 Verificación Realizada

La visualización de trabajos de impresión fue verificada utilizando pruebas manuales e interacciones mediante navegador automatizado en el servidor de producción `http://192.168.91.131`:
- **Inicio de sesión**: Exitoso usando el usuario `superadmin`.
- **Navegación**: Carga del panel "Trabajos de Impresión".
- **Visualización**: Se obtuvo con éxito la lista de 10 trabajos de impresión activos en la impresora 6 (ej. `4560381_20250906_891805_001` enviado por `GEORGER`), demostrando que no existen bloqueos de CORS ni errores de red.
