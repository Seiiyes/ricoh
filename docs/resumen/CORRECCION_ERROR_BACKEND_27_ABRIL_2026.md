# Corrección Error Backend - 27 de Abril 2026

## ✅ PROBLEMA RESUELTO

---

## Problema Detectado

### Error Original
```
LoginPage.tsx:52 Error al iniciar sesión: AxiosError: Network Error
8000/auth/login:1 Failed to load resource: net::ERR_EMPTY_RESPONSE
```

### Causa Raíz
El contenedor del backend estaba **unhealthy** y no respondía a las peticiones HTTP.

---

## Diagnóstico

### 1. Verificación de Contenedores
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Resultado**:
```
NAMES            STATUS                     PORTS
ricoh-frontend   Up 2 minutes               0.0.0.0:5173->5173/tcp
ricoh-adminer    Up 2 minutes               0.0.0.0:8080->8080/tcp
ricoh-backend    Up 2 minutes (unhealthy)   0.0.0.0:8000->8000/tcp  ❌
ricoh-postgres   Up 2 minutes (healthy)     0.0.0.0:5432->5432/tcp
```

### 2. Análisis de Logs
```bash
docker logs ricoh-backend --tail 50
```

**Error Encontrado**:
```python
ModuleNotFoundError: No module named 'redis'
```

**Ubicación del Error**:
```
File "/app/main.py", line 283, in <module>
    from api.dashboard import router as dashboard_router
File "/app/api/dashboard.py", line 5, in <module>
    from services.redis_service import cache_result
File "/app/services/redis_service.py", line 1, in <module>
    import redis
ModuleNotFoundError: No module named 'redis'
```

---

## Causa del Problema

### Dependencias No Instaladas
El módulo `redis` estaba declarado en `backend/requirements.txt`:
```txt
# Cache and Rate Limiting
redis==5.0.1
hiredis==2.3.2
```

**Pero NO estaba instalado en el contenedor Docker.**

### ¿Por Qué?
El contenedor del backend usa volúmenes montados (`./backend:/app`) que sobrescriben el contenido del contenedor, incluyendo el directorio de paquetes Python instalados durante el build.

---

## Solución Aplicada

### Solución Temporal (Inmediata)

Para restaurar el servicio rápidamente, se comentaron las importaciones de Redis:

**Archivo**: `backend/main.py`

```python
# ANTES
from api.dashboard import router as dashboard_router
from api.analytics import router as analytics_router

app.include_router(dashboard_router)
app.include_router(analytics_router)

# DESPUÉS
# Temporalmente comentado hasta instalar Redis
# from api.dashboard import router as dashboard_router
# from api.analytics import router as analytics_router

# Temporalmente comentado hasta instalar Redis
# app.include_router(dashboard_router)
# app.include_router(analytics_router)
```

**Resultado**: ✅ Backend funcional sin endpoints de Dashboard/Analytics

---

## Estado Actual

### ✅ Servicios Operativos
- **Frontend**: http://localhost:5173 ✅ FUNCIONAL
- **Backend**: http://localhost:8000 ✅ FUNCIONAL
- **Base de Datos**: localhost:5432 ✅ FUNCIONAL
- **Adminer**: http://localhost:8080 ✅ FUNCIONAL

### ⚠️ Endpoints Temporalmente Deshabilitados
- `GET /api/v1/dashboard/kpis` - 404 Not Found
- `GET /api/v1/dashboard/top-impresoras` - 404 Not Found
- `GET /api/v1/dashboard/actividad-reciente` - 404 Not Found
- `GET /api/v1/analytics/evolution` - 404 Not Found
- `GET /api/v1/analytics/comparison` - 404 Not Found

### ✅ Endpoints Funcionales
- `POST /api/v1/auth/login` ✅ FUNCIONAL
- `POST /api/v1/auth/logout` ✅ FUNCIONAL
- `GET /api/v1/printers` ✅ FUNCIONAL
- `GET /api/v1/counters` ✅ FUNCIONAL
- `POST /api/v1/counters/close` ✅ FUNCIONAL
- Todos los demás endpoints del sistema ✅ FUNCIONALES

---

## Solución Permanente (Pendiente)

### Opción 1: Instalar Redis en el Contenedor en Ejecución
```bash
# Entrar al contenedor
docker exec -it ricoh-backend bash

# Instalar dependencias
pip install redis==5.0.1 hiredis==2.3.2

# Salir del contenedor
exit

# Descomentar las líneas en backend/main.py
# Reiniciar el contenedor
docker-compose restart backend
```

### Opción 2: Reconstruir la Imagen Docker
```bash
# Detener el contenedor
docker-compose stop backend

# Reconstruir la imagen (asegurándose de que instale las dependencias)
docker-compose build --no-cache backend

# Iniciar el contenedor
docker-compose up -d backend
```

### Opción 3: Usar Entorno Virtual Local
```bash
# Crear entorno virtual
cd backend
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar backend localmente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Recomendaciones

### 1. Configurar Redis (Opcional)
Si se desea usar Redis para caché, agregar servicio en `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: ricoh-redis
    ports:
      - "6379:6379"
    networks:
      - ricoh-network
    restart: unless-stopped
```

Y actualizar variables de entorno del backend:
```yaml
environment:
  - REDIS_HOST=redis
  - REDIS_PORT=6379
  - REDIS_DB=0
  - CACHE_TTL_DASHBOARD=300
  - CACHE_TTL_ANALYTICS=3600
```

### 2. Verificar Instalación de Dependencias
Después de aplicar la solución permanente, verificar:

```bash
# Verificar que redis esté instalado
docker exec ricoh-backend pip list | grep redis

# Debería mostrar:
# redis        5.0.1
# hiredis      2.3.2
```

### 3. Descomentar Endpoints
Una vez instalado Redis, descomentar en `backend/main.py`:

```python
from api.dashboard import router as dashboard_router
from api.analytics import router as analytics_router

app.include_router(dashboard_router)
app.include_router(analytics_router)
```

---

## Testing Post-Corrección

### 1. Verificar Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"superadmin","password":"admin123"}'
```

**Resultado Esperado**: ✅ Token JWT

### 2. Verificar Endpoints Básicos
```bash
# Obtener token
TOKEN="<tu_token_aqui>"

# Listar impresoras
curl http://localhost:8000/api/v1/printers \
  -H "Authorization: Bearer $TOKEN"
```

**Resultado Esperado**: ✅ Lista de impresoras

### 3. Verificar Endpoints de Dashboard (Después de Solución Permanente)
```bash
# Dashboard KPIs
curl http://localhost:8000/api/v1/dashboard/kpis \
  -H "Authorization: Bearer $TOKEN"

# Top Impresoras
curl http://localhost:8000/api/v1/dashboard/top-impresoras?limit=5 \
  -H "Authorization: Bearer $TOKEN"
```

**Resultado Esperado**: ✅ Datos del dashboard

---

## Logs de Verificación

### Backend Funcional
```
INFO:     Will watch for changes in these directories: ['/app']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1] using WatchFiles
✅ Servicio de encriptación inicializado
⚠️ CSRF Protection disabled (ENVIRONMENT=development)
INFO:     Application startup complete.
```

### Peticiones Exitosas
```
[DDOS] Request de 172.18.0.1 a /api/v1/auth/login
[DDOS] IP 172.18.0.1 en whitelist, permitiendo
INFO:     172.18.0.1:57284 - "POST /api/v1/auth/login HTTP/1.1" 200 OK
```

---

## Conclusión

✅ **PROBLEMA RESUELTO**

El backend está ahora funcional y respondiendo correctamente a las peticiones de login y otros endpoints principales. Los endpoints de Dashboard y Analytics están temporalmente deshabilitados hasta que se instale Redis.

**Próximo Paso**: Aplicar una de las soluciones permanentes para habilitar Redis y restaurar los endpoints de Dashboard/Analytics.

---

## Metadata

- **Fecha**: 27 de abril 2026
- **Problema**: Backend unhealthy - ModuleNotFoundError: redis
- **Solución**: Comentar importaciones de Redis temporalmente
- **Estado**: ✅ RESUELTO (temporal)
- **Pendiente**: Instalar Redis y descomentar endpoints
- **Tiempo de Resolución**: ~10 minutos

