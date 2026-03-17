# 007 - Backend Unhealthy Durante Inicio de PostgreSQL

**Fecha:** 9 de marzo de 2026  
**Severidad:** Media  
**Módulo:** Docker / Infraestructura  
**Tags:** #docker #postgres #healthcheck #startup

---

## 🐛 Descripción del Error

Después de reiniciar el stack de Docker con `docker-compose down` y `docker-compose up`, el backend queda en estado "unhealthy" porque intenta conectarse a PostgreSQL mientras la base de datos todavía está iniciándose.

## 🔍 Síntomas

- Backend muestra estado "unhealthy" en `docker-compose ps`
- Logs del backend muestran: `sqlalchemy.exc.OperationalError: connection to server at "postgres" failed: FATAL: the database system is starting up`
- PostgreSQL muestra: `database system is ready to accept connections`
- Frontend funciona pero no puede conectarse al backend

### Logs de Error
```
ricoh-backend  | sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) 
connection to server at "postgres" (172.18.0.5), port 5432 failed: 
FATAL:  the database system is starting up
```

## 🎯 Causa Raíz

### Secuencia de Eventos
1. `docker-compose up` inicia todos los contenedores simultáneamente
2. PostgreSQL comienza su proceso de recuperación (puede tomar 10-30 segundos)
3. Backend intenta conectarse inmediatamente al iniciar
4. PostgreSQL rechaza la conexión porque todavía está en modo "starting up"
5. Backend falla al iniciar y queda en estado "unhealthy"
6. PostgreSQL termina de iniciar y queda "healthy"
7. Backend NO se reinicia automáticamente

### Por Qué Ocurre
- Docker Compose inicia contenedores en paralelo por defecto
- El `depends_on` solo espera que el contenedor esté "running", NO que el servicio esté listo
- PostgreSQL necesita tiempo para recuperación después de un shutdown
- Backend no tiene retry logic en el startup

## ✅ Solución Implementada

### Solución Inmediata
Reiniciar el backend manualmente después de que PostgreSQL esté listo:

```bash
# Verificar estado
docker-compose ps

# Esperar a que postgres esté "healthy"
# Luego reiniciar backend
docker-compose restart backend

# Verificar que backend esté "healthy"
docker-compose ps backend
```

### Solución Preventiva (Recomendada)

Agregar healthcheck y depends_on con condition en `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ricoh"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 10s
    # ... resto de configuración

  backend:
    build: ./backend
    depends_on:
      postgres:
        condition: service_healthy  # ⭐ Esperar a que postgres esté healthy
    # ... resto de configuración
```

### Solución Alternativa: Retry Logic en Backend

Agregar retry logic en `backend/db/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import time

def create_db_engine(max_retries=5, retry_delay=2):
    """Crear engine con retry logic"""
    for attempt in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database not ready, retrying in {retry_delay}s... ({attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                raise
```

## 🛡️ Prevención Futura

### Checklist al Reiniciar Stack
- [ ] Ejecutar `docker-compose down` para detener todo
- [ ] Ejecutar `docker-compose up -d` para iniciar en background
- [ ] Esperar 10-15 segundos para que PostgreSQL inicie
- [ ] Verificar estado: `docker-compose ps`
- [ ] Si backend está "unhealthy", reiniciar: `docker-compose restart backend`

### Mejoras Recomendadas
1. **Implementar healthcheck con condition** (más confiable)
2. **Agregar retry logic en backend** (más robusto)
3. **Usar `docker-compose up -d --wait`** (espera a healthchecks)
4. **Monitorear logs durante startup** para detectar problemas temprano

### Comandos Útiles
```bash
# Ver estado de todos los servicios
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs postgres --tail 50
docker-compose logs backend --tail 50

# Reiniciar un servicio específico
docker-compose restart backend

# Reiniciar todo el stack
docker-compose restart

# Ver logs en tiempo real
docker-compose logs -f backend
```

## 📚 Referencias

- [Docker Compose depends_on](https://docs.docker.com/compose/compose-file/compose-file-v3/#depends_on)
- [Docker Compose healthcheck](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck)
- [PostgreSQL startup process](https://www.postgresql.org/docs/current/server-start.html)

## 💡 Lecciones Clave

1. **depends_on no es suficiente**: Solo espera que el contenedor esté running, no que el servicio esté listo
2. **Usar healthcheck + condition**: La forma correcta de esperar a que un servicio esté listo
3. **Retry logic es importante**: Los servicios deben ser resilientes a fallos temporales
4. **Monitorear logs durante startup**: Ayuda a detectar problemas temprano
5. **PostgreSQL necesita tiempo**: Especialmente después de un shutdown, puede tomar 10-30 segundos

## 🔧 Validación

### Verificar que Backend Está Healthy
```bash
docker-compose ps backend
# Debe mostrar: Up X seconds (healthy)
```

### Probar Conexión al Backend
```bash
curl http://localhost:8000/printers
# Debe retornar JSON con lista de impresoras
```

### Verificar Logs Sin Errores
```bash
docker-compose logs backend --tail 20
# No debe mostrar errores de conexión
```

---

## 📊 Impacto

- **Tiempo de detección:** 5 minutos
- **Tiempo de corrección:** 2 minutos (restart manual)
- **Frecuencia:** Cada vez que se reinicia el stack
- **Severidad real:** Media (fácil de resolver pero molesto)

---

## 🔄 Estado

- ✅ Problema identificado
- ✅ Solución inmediata aplicada (restart manual)
- ⏳ Solución preventiva pendiente (healthcheck + condition)
- ⏳ Retry logic pendiente

---

**Documentado por:** Sistema Kiro  
**Revisado por:** Equipo de desarrollo  
**Estado:** ✅ Resuelto (temporal)

**Última actualización:** 9 de marzo de 2026
