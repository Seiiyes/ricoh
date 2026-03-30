# Troubleshooting Docker - Ricoh Suite

## Problema Actual: Error 500 y CORS

El backend está respondiendo con error 500, lo que indica un problema en el código del servidor.

## Solución 1: Ver los Logs del Backend

```bash
docker-compose logs backend --tail=100
```

Busca errores como:
- `ModuleNotFoundError: No module named 'bcrypt'`
- `ModuleNotFoundError: No module named 'PyJWT'`
- Errores de importación en `auth_middleware.py`
- Errores de importación en `auth_service.py`

## Solución 2: Reconstruir el Backend

Si ves errores de módulos faltantes:

```bash
# Detener todo
docker-compose down

# Reconstruir el backend (esto reinstala todas las dependencias)
docker-compose build --no-cache backend

# Levantar todo
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

Espera a ver:
```
✅ Database initialized
🌐 Server ready!
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Solución 3: Correr Backend Localmente (Más Rápido)

Si Docker sigue dando problemas, corre el backend localmente:

### Paso 1: Detener el backend de Docker

```bash
docker-compose stop backend
```

### Paso 2: Configurar el backend local

```bash
cd backend

# Crear entorno virtual (si no existe)
python -m venv venv

# Activar entorno virtual
# Windows PowerShell:
venv\Scripts\Activate.ps1

# Windows CMD:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno

Crear archivo `backend/.env` con:

```
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@localhost:5432/ricoh_fleet
SECRET_KEY=ricoh-secret-key-change-in-production
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Paso 5: Ejecutar migraciones

```bash
python scripts/run_migrations.py
```

### Paso 6: Inicializar superadmin

```bash
python scripts/init_superadmin.py
```

Guarda la contraseña que se genera.

### Paso 7: Iniciar el backend

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Paso 8: Probar el backend

Abre http://localhost:8000/docs en tu navegador. Deberías ver la documentación de Swagger.

## Solución 4: Verificar que el Frontend Puede Conectarse

Una vez que el backend esté corriendo sin errores:

1. Abre http://localhost:5173
2. Haz login con superadmin
3. Deberías poder ver las páginas sin errores de CORS

## Comandos Útiles

### Ver logs en tiempo real
```bash
docker-compose logs -f backend
```

### Reiniciar un servicio
```bash
docker-compose restart backend
```

### Ver estado de los contenedores
```bash
docker-compose ps
```

### Entrar al contenedor del backend
```bash
docker exec -it ricoh-backend bash
```

### Limpiar todo y empezar de cero
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Errores Comunes

### Error: ModuleNotFoundError: No module named 'bcrypt'

**Solución**: Reconstruir el backend
```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Error: CORS policy

**Causa**: El backend no está respondiendo correctamente.

**Solución**: Ver los logs del backend para identificar el error real.

### Error: Connection refused

**Causa**: El backend no está corriendo.

**Solución**: Verificar que el contenedor esté corriendo:
```bash
docker-compose ps
```

Si no está corriendo, iniciarlo:
```bash
docker-compose up -d backend
```

## Contacto

Si ninguna de estas soluciones funciona, comparte:
1. Los logs del backend (`docker-compose logs backend --tail=100`)
2. El output de `docker-compose ps`
3. El error exacto que ves en el navegador

---

**Última actualización**: 20 de Marzo de 2026
