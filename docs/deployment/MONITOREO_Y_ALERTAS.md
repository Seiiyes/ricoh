#  Manual de Monitoreo, Log y Alertas de Producción

Este manual describe la ubicación de los logs del sistema, los comandos esenciales de monitoreo y la interpretación de alertas comunes en el entorno de producción de **Ricoh Equipment Manager**.

---

## ️ 1. Ubicación de Archivos de Log

El sistema orquesta múltiples servicios cuyos logs se almacenan en diferentes puntos:

### 1.1 Logs de Contenedores Docker (Consola)
Todos los servicios envían sus logs a la salida estándar (`stdout`/`stderr`), la cual es capturada por el demonio de Docker.
*   **Comando de lectura general**:
    ```bash
    docker-compose logs -f --tail=100
    ```
*   **Logs de un contenedor específico**:
    ```bash
    docker logs -f ricoh-backend
    docker logs -f ricoh-nginx
    ```

### 1.2 Logs en Sistema de Archivos
*   **Logs de la API Backend**: `/app/logs/` (montado en el volumen persistente `ricoh-backend-logs` del host).
*   **Bitácora de Auditoría SQLite**: Guardado en `/app/logs/audit.db`. Contiene el registro inmutable de transacciones e inicios de sesión, consultable mediante el Portal de Auditoría en el puerto `8088`.
*   **Logs de Nginx (Peticiones HTTP/HTTPS)**: `/var/log/nginx/access.log` y `error.log` (montado en el volumen `ricoh-nginx-logs`).

---

##  2. Comandos Útiles de Monitoreo en Servidor

### 2.1 Verificar consumo de recursos del host
```bash
# Ver uso de CPU y memoria en tiempo real de todos los contenedores
docker stats
```

### 2.2 Consultar estado de salud de contenedores
```bash
# Lista contenedores y muestra su estado de salud (healthy / starting / unhealthy)
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

##  3. Guía de Alertas y Resolución de Errores Comunes

### 1. `Device binding violation` (HTTP 401)
*   **Qué significa**: Un token JWT fue rechazado porque la IP o la cabecera `User-Agent` del cliente no coinciden con las registradas al iniciar sesión.
*   **Causa común**: El usuario cambió de red WiFi, activó una VPN o el proxy inverso Nginx no está propagando correctamente la cabecera `X-Real-IP`.
*   **Solución**: Forzar al usuario a iniciar sesión nuevamente para regenerar el token con la IP actual.

### 2. `Demasiados intentos. Por favor, intente más tarde.` (HTTP 429)
*   **Qué significa**: El rate limiter en memoria bloqueó la dirección IP del cliente por exceder el número máximo de solicitudes permitidas por minuto (prevención DDoS / Fuerza bruta).
*   **Solución**: Esperar 60 segundos a que el contador de Redis expire. Si el bloqueo es erróneo, se puede vaciar el caché en Redis:
    ```bash
    docker exec -it ricoh-redis redis-cli flushall
    ```

### 3. `Error: Este dispositivo está siendo utilizado por otras funciones` (Timeouts WIM)
*   **Qué significa**: El adaptador `RicohWebClient` intentó aprovisionar o leer datos en una impresora Ricoh que está siendo ocupada físicamente por un operario o procesando un trabajo de impresión pesado.
*   **Acción del sistema**: El backend ejecutará automáticamente un bucle de hasta 12 reintentos con esperas de 5.0 segundos.
*   **Solución**: Si el log muestra que los 12 reintentos fallaron, avise al operario que libere el panel físico del equipo antes de reintentar la acción desde el portal.
