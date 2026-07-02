# Reconfiguración y Sincronización del Servidor 192.168.91.131

**Fecha de Ejecución:** 16 de Junio de 2026  
**Estatus:** Completado y Desplegado en Producción

Este documento detalla los cambios realizados en el sistema de gestión Ricoh para solucionar los problemas de bloqueo de cuenta, habilitar el acceso mediante HTTP directo y establecer herramientas de sincronización bidireccionales entre el entorno de desarrollo local y el servidor remoto.

---

## 📝 Resumen del Commit de Git

Si deseas realizar el commit de estos cambios en tu repositorio Git, te sugerimos usar el siguiente mensaje descriptivo:

```bash
git commit -m "chore: reconfigurar servidor 131 a HTTP, desactivar bloqueos de cuenta y agregar script de pull remoto" -m "
- Modificado docker-compose.server131.yml y ricoh.conf para desactivar HTTPS y habilitar acceso HTTP directo en puertos 80 y 8000.
- Aumentado MAX_FAILED_ATTEMPTS a 999 en auth_service.py y puenteado ddos_protection.py para evitar bloqueos del admin.
- Creado script de descarga pull_from_server131.py para sincronizar de remoto a local vía SFTP.
- Agregada guía de resolución para caché HSTS en navegadores Chrome/Edge."
```

---

## 1. Ajustes de Seguridad y Desactivación de Bloqueos

Se identificó que los usuarios administradores (como `superadmin`) sufrían bloqueos constantes debido a configuraciones estrictas en el middleware de DDoS y en el servicio de autenticación.

* **Bypass de DDoS (`backend/middleware/ddos_protection.py`):**
  Se desactivó la interceptación y rate-limiting de peticiones agregando un retorno inmediato en el middleware:
  ```python
  async def dispatch(self, request: Request, call_next):
      return await call_next(request)
  ```
* **Límite de Intentos Fallidos (`backend/services/auth_service.py`):**
  Se incrementó la constante para evitar bloqueos en la práctica:
  ```python
  MAX_FAILED_ATTEMPTS = 999
  ```
* **Reseteo de Cuenta (`superadmin`):**
  Se ejecutó un script en la base de datos de producción para:
  1. Poner a `0` la columna `failed_login_attempts`.
  2. Limpiar la columna `locked_until` (fijada en `None`).
  3. Asegurar la contraseña `ricoh2026` mediante el hash de bcrypt: `$2b$12$JzSTCPS3A/.LtN4/ifBYD.36/Ef9sII1iFFe0TmQ6ZVAjSvWqVUUm`.

---

## 2. Configuración de Acceso por HTTP Plano (Sin SSL)

Para simplificar el acceso a la aplicación en un servidor puramente local sin obligar a cada usuario a aceptar certificados SSL autofirmados, se revirtió la suite a HTTP directo.

### Cambios en Nginx (`deployment/nginx/conf.d/ricoh.conf`):
* Se removió la redirección a HTTPS y el bloque del puerto 443.
* Se configuró el puerto `80` para servir el Frontend en React de forma directa.
* Se configuró el puerto `8000` en HTTP plano para el Backend API.

### Cambios en Docker Compose (`deployment/docker-compose.server131.yml`):
* Se removió el mapeo de puerto `443` en el contenedor `ricoh-nginx`.
* Se eliminó el montaje de volúmenes de certificados SSL (`/etc/nginx/ssl`).
* Se actualizó `VITE_API_URL` a `http://192.168.91.131:8000` (HTTP).
* Se actualizaron los orígenes de CORS (`CORS_ORIGINS`) en el backend a URLs con `http`.

---

## 3. Resolución de Problemas de Caché en el Navegador (HSTS)

Si habías ingresado previamente a la versión con HTTPS, tu navegador (Chrome o Edge) habrá guardado la directiva **HSTS (HTTP Strict Transport Security)**, forzando la redirección a HTTPS automáticamente. Como ya no hay SSL, el navegador mostrará el error `ERR_CONNECTION_REFUSED`.

### Cómo solucionarlo en tu máquina local:
1. Abre una nueva pestaña en Google Chrome.
2. Ingresa a la dirección: **`chrome://net-internals/#hsts`**
3. Ve a la sección inferior **"Delete domain security policies"** (Borrar políticas de seguridad de dominio).
4. En el campo **Domain**, escribe: `192.168.91.131` y haz clic en **Delete**.
5. Abre la aplicación en una pestaña nueva o ventana de incógnito usando: **`http://192.168.91.131`**.

---

## 4. Herramientas de Sincronización Servidor <-> Local

Se cuenta con dos scripts en la carpeta `deployment/` para administrar la sincronización del código:

### Despliegue (Local -> Servidor):
* **Script:** [deploy_to_server131.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/deployment/deploy_to_server131.py)
* **Uso:** Sube los archivos modificados localmente y reconstruye/reinicia los servicios en el servidor remoto de forma automatizada.
* **Ejecutar:** `python deployment/deploy_to_server131.py`

### Descarga (Servidor -> Local):
* **Script:** [pull_from_server131.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/deployment/pull_from_server131.py)
* **Uso:** Descarga cualquier modificación realizada directamente en el servidor (por ejemplo, base de datos inicializada, migraciones generadas o archivos del backend) de vuelta a la máquina de desarrollo local.
* **Ejecutar:** `python deployment/pull_from_server131.py`
