# Migración a Entorno de Producción y Diagnóstico del Servidor

## ¿Qué se hizo hasta ahora (Diagnóstico)?

Se realizó un escrutinio profundo a la arquitectura actual (contenedores Docker, configuración de Nginx, Uvicorn, logs y conectividad) buscando la causa de que ciertas funcionalidades fallaran esporádicamente o se quedaran colgadas. Se encontraron los siguientes problemas:

1.  **Fallo al cargar Permisos de Usuarios (Error 404 y Bucle Infinito):**
    *   **Diagnóstico:** El backend utiliza un "Singleton" (una sola instancia) de `RicohWebClient`. Cuando el frontend pedía asíncronamente permisos de varias impresoras a la vez, se mezclaban los tokens de sesión de Ricoh, provocando que las peticiones fueran rechazadas (`BADFLOW`) y regresaran un 404. El frontend, al recibir el 404, reintentaba infinitamente porque no recordaba que ya había fallado.
    *   **Solución Aplicada:** 
        *   Se corrigió el frontend (`ModificarUsuario.tsx`) para detener el bucle infinito al primer fallo.
        *   Se parcheó el backend (`api/discovery.py`) para aislar cada petición en su propia instancia de cliente, solucionando el choque de tokens.

2.  **Lentitud General y Saturación (Single Worker & Reload):**
    *   **Diagnóstico:** El backend está configurado en `docker-compose.yml` con el comando `uvicorn ... --reload`. Esto arranca Python con un único "trabajador" (Worker) y dedica muchos recursos a vigilar si hay cambios en los archivos (hot-reloading). En un entorno real, si 3 usuarios usan la plataforma, el único hilo se asfixia rápidamente.

3.  **Inestabilidad de Interfaz (Vite Dev Server en Producción):**
    *   **Diagnóstico:** El frontend corre mediante `npm run dev`. Esto levanta un servidor de desarrollo diseñado para programar, no para despachar la app final. Cuando hay inestabilidad en la red, los WebSockets de desarrollo fallan y la página se desconecta en silencio (parece que los botones no hacen nada).

4.  **Caché Ausente (Redis Desperdiciado):**
    *   **Diagnóstico:** El contenedor de Redis está activo y saludable, pero el código del backend solo lo emplea para protección CSRF. Todos los endpoints (lista de impresoras, usuarios, analíticas) van a golpear la base de datos de nuevo, lo cual es ineficiente.

5.  **Expiración de Sesión (Tokens JWT):**
    *   **Diagnóstico:** Los tokens JWT expiran, pero el frontend no siempre redirige proactivamente al login en ciertas operaciones secundarias, provocando un fallo "silencioso" (401 Unauthorized).

---

## ¿Qué se va a hacer (Plan de Acción)?

Para convertir este servidor de desarrollo en un **Entorno de Producción Estable, Rápido y Confiable**, aplicaremos la siguiente reestructuración:

### Fase 1: Optimización del Backend (Capacidad de Carga)
*   Modificaremos el `docker-compose.yml` para remover el modo `--reload`.
*   Aumentaremos la concurrencia utilizando `uvicorn --workers 3` (3 trabajadores paralelos en lugar de 1).
*   **Impacto:** El sistema aguantará múltiples usuarios concurrentes y las peticiones no harán cola, eliminando los cuelgues temporales de la interfaz.

### Fase 2: Compilación del Frontend (Despliegue Estático)
*   Modificaremos cómo se despliega React. En lugar de usar `npm run dev`, crearemos un `Dockerfile.frontend` multiplataforma (Multi-stage) que ejecute `npm run build` y aloje los archivos resultantes en un Nginx extremadamente ligero.
*   Actualizaremos el Nginx principal (`ricoh.conf`) para enrutar el tráfico al nuevo servidor estático.
*   **Impacto:** Los tiempos de carga de la web bajarán drásticamente, el navegador cacheará los componentes y se eliminará el problema de la "desconexión silenciosa" del HMR.

### Fase 3: Activación del Caché de Datos (Redis)
*   Implementaremos un decorador (o inyección directa) de Redis en los endpoints más consultados (`/discovery/user-details`, `/api/printers`, y `/api/analytics`).
*   **Impacto:** Reduciremos la carga de la base de datos en un 80% y las páginas cargarán casi instantáneamente al cambiar de pestañas.

### Fase 4: Manejo Robusto de Sesión
*   Ajustaremos el interceptor global de Axios en el frontend para asegurar que cualquier petición que devuelva un 401 (incluyendo las ocultas) fuerce la redirección a la pantalla de Login con un mensaje claro.

---
> **Nota:** La aplicación de estos cambios implicará un reinicio completo de los contenedores (`docker-compose down && docker-compose up -d --build`). Se recomienda hacerlo en un horario de bajo tráfico.
