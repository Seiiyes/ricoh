# 🔒 Guía de Respaldo de Base de Datos

## ⚠️ Problema Identificado

Sin respaldo de la base de datos, al cambiar de equipo o actualizar el código, puedes perder todos los usuarios e impresoras registradas.

---

## 🎯 Soluciones Recomendadas

### Opción 1: Respaldo Automático con Scripts (RECOMENDADO) ⭐

Esta es la solución más simple y no requiere servicios externos.

#### Paso 1: Crear Script de Respaldo

Crea un archivo `backup-db.bat` en la raíz del proyecto:

```batch
@echo off
echo ========================================
echo   RESPALDO DE BASE DE DATOS
echo ========================================
echo.

REM Crear carpeta de respaldos si no existe
if not exist "backups" mkdir backups

REM Generar nombre con fecha y hora
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=backups\ricoh_backup_%TIMESTAMP%.sql

echo Creando respaldo en: %BACKUP_FILE%
echo.

REM Exportar base de datos
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > %BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Respaldo creado exitosamente
    echo   Archivo: %BACKUP_FILE%
    echo.
    echo Tamaño del archivo:
    dir "%BACKUP_FILE%" | find "%BACKUP_FILE%"
) else (
    echo.
    echo ✗ Error al crear respaldo
)

echo.
echo ========================================
pause
```

#### Paso 2: Crear Script de Restauración

Crea un archivo `restore-db.bat`:

```batch
@echo off
echo ========================================
echo   RESTAURAR BASE DE DATOS
echo ========================================
echo.

REM Listar respaldos disponibles
echo Respaldos disponibles:
echo.
dir /b backups\*.sql
echo.

set /p BACKUP_FILE="Ingresa el nombre del archivo a restaurar: "

if not exist "backups\%BACKUP_FILE%" (
    echo.
    echo ✗ Archivo no encontrado: backups\%BACKUP_FILE%
    pause
    exit /b
)

echo.
echo ⚠️  ADVERTENCIA: Esto sobrescribirá la base de datos actual
set /p CONFIRM="¿Estás seguro? (S/N): "

if /i not "%CONFIRM%"=="S" (
    echo.
    echo Operación cancelada
    pause
    exit /b
)

echo.
echo Restaurando base de datos...
echo.

REM Restaurar base de datos
docker exec -i ricoh-postgres psql -U ricoh_admin ricoh_fleet < backups\%BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Base de datos restaurada exitosamente
) else (
    echo.
    echo ✗ Error al restaurar base de datos
)

echo.
echo ========================================
pause
```

#### Paso 3: Uso

**Crear respaldo:**
```cmd
backup-db.bat
```

**Restaurar respaldo:**
```cmd
restore-db.bat
```

**Resultado:**
- Carpeta `backups/` con archivos `.sql`
- Ejemplo: `ricoh_backup_20260218_143022.sql`

---

### Opción 2: Subir a GitHub (Respaldos Versionados) 🔄

Puedes versionar tus respaldos en el mismo repositorio.

#### Configuración

1. **Agregar carpeta de respaldos al .gitignore (opcional)**

Si NO quieres subir los respaldos a GitHub:
```
# .gitignore
backups/*.sql
```

Si SÍ quieres subirlos (recomendado para respaldos):
```
# No agregar nada, dejar que se suban
```

2. **Crear respaldo y subir**

```cmd
REM Crear respaldo
backup-db.bat

REM Subir a GitHub
git add backups/
git commit -m "Respaldo de base de datos - %date%"
git push
```

**Ventajas:**
- ✅ Historial de cambios
- ✅ Gratis
- ✅ Accesible desde cualquier lugar

**Desventajas:**
- ⚠️ Si el repo es público, los datos son visibles
- ⚠️ Límite de tamaño de archivo (100MB por archivo)

---

### Opción 3: Google Drive / OneDrive (Respaldo en la Nube) ☁️

Sincroniza la carpeta `backups/` con tu nube personal.

#### Google Drive

1. Instala Google Drive Desktop
2. Mueve la carpeta `backups/` a tu carpeta de Google Drive
3. Crea un enlace simbólico:

```cmd
mklink /D "C:\ruta\proyecto\backups" "C:\Users\TuUsuario\Google Drive\ricoh-backups"
```

#### OneDrive (Ya viene con Windows)

1. Mueve `backups/` a tu carpeta de OneDrive
2. Crea enlace simbólico igual que arriba

**Ventajas:**
- ✅ Automático
- ✅ Gratis (15GB Google, 5GB OneDrive)
- ✅ Accesible desde cualquier dispositivo

---

### Opción 4: Volumen Persistente de Docker (Ya lo tienes) 📦

Docker ya está guardando tus datos en un volumen persistente.

#### Verificar volumen

```cmd
docker volume ls
```

Deberías ver: `ricoh-postgres-data`

#### Respaldar volumen

```cmd
REM Crear respaldo del volumen
docker run --rm -v ricoh-postgres-data:/data -v %cd%/backups:/backup alpine tar czf /backup/postgres-volume-backup.tar.gz /data
```

#### Restaurar volumen

```cmd
REM Restaurar volumen
docker run --rm -v ricoh-postgres-data:/data -v %cd%/backups:/backup alpine tar xzf /backup/postgres-volume-backup.tar.gz -C /
```

**Ventajas:**
- ✅ Respaldo completo del volumen
- ✅ Incluye configuraciones

**Desventajas:**
- ⚠️ Archivo más grande
- ⚠️ Menos portable

---

### Opción 5: Servicios de Base de Datos Gratis en la Nube 🌐

#### ElephantSQL (PostgreSQL Gratis)

**Plan Gratis:**
- 20MB de almacenamiento
- Suficiente para ~1000 usuarios

**Pasos:**
1. Regístrate en https://www.elephantsql.com/
2. Crea una instancia gratis
3. Obtén la URL de conexión
4. Actualiza `docker-compose.yml`:

```yaml
# Comentar el servicio postgres local
# postgres:
#   ...

# Actualizar backend
backend:
  environment:
    - DATABASE_URL=postgres://usuario:password@servidor.elephantsql.com:5432/database
```

#### Supabase (PostgreSQL + Extras)

**Plan Gratis:**
- 500MB de almacenamiento
- 2GB de transferencia

**Pasos:**
1. Regístrate en https://supabase.com/
2. Crea un proyecto
3. Obtén la URL de conexión
4. Actualiza variables de entorno

#### Railway (Hosting Completo)

**Plan Gratis:**
- $5 de crédito mensual
- Suficiente para desarrollo

**Pasos:**
1. Regístrate en https://railway.app/
2. Conecta tu repositorio de GitHub
3. Railway detecta Docker Compose automáticamente
4. Despliega con un click

---

## 🎯 Recomendación Final

### Para Desarrollo Local (Tu caso actual):

**Combinación perfecta:**

1. **Script de respaldo automático** (Opción 1)
   - Ejecutar `backup-db.bat` antes de cambios importantes
   - Rápido y simple

2. **Subir respaldos a GitHub** (Opción 2)
   - Versionar los archivos `.sql`
   - Accesible desde cualquier equipo

3. **Sincronizar con OneDrive** (Opción 3)
   - Respaldo adicional automático
   - Ya viene con Windows

### Rutina Recomendada:

```
Antes de cambiar de equipo o hacer cambios grandes:
1. Ejecutar backup-db.bat
2. git add backups/
3. git commit -m "Respaldo antes de [descripción]"
4. git push
```

### Para Producción (Futuro):

- **Railway** o **Supabase** para hosting completo
- Respaldos automáticos diarios
- Acceso desde cualquier lugar

---

## 📋 Checklist de Implementación

### Ahora Mismo (5 minutos):

- [ ] Crear `backup-db.bat`
- [ ] Crear `restore-db.bat`
- [ ] Ejecutar primer respaldo
- [ ] Verificar que se creó el archivo en `backups/`

### Antes de Cambiar de Equipo:

- [ ] Ejecutar `backup-db.bat`
- [ ] Subir respaldo a GitHub
- [ ] Copiar carpeta `backups/` a USB/nube
- [ ] Verificar que tienes el archivo `.sql`

### En el Nuevo Equipo:

- [ ] Clonar repositorio
- [ ] Iniciar Docker
- [ ] Ejecutar `restore-db.bat`
- [ ] Verificar que los datos están

---

## 🆘 Recuperación de Emergencia

Si perdiste datos y NO tienes respaldo:

1. **Revisar volumen de Docker:**
   ```cmd
   docker volume inspect ricoh-postgres-data
   ```

2. **Buscar archivos temporales:**
   - Carpeta `postgres_data/` (si existe)
   - Logs de Docker

3. **Recrear usuarios manualmente:**
   - Usar la interfaz de aprovisionamiento
   - Importar desde Excel si tienes lista

---

## 📞 Comandos Útiles

```cmd
REM Ver tamaño de la base de datos
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT pg_size_pretty(pg_database_size('ricoh_fleet'));"

REM Listar tablas y cantidad de registros
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT schemaname,relname,n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC;"

REM Exportar solo usuarios
docker exec ricoh-postgres pg_dump -U ricoh_admin -d ricoh_fleet -t users > backups/solo_usuarios.sql

REM Exportar solo impresoras
docker exec ricoh-postgres pg_dump -U ricoh_admin -d ricoh_fleet -t printers > backups/solo_impresoras.sql
```

---

**Fecha:** 18 de Febrero de 2026  
**Versión:** 1.0  
**Estado:** Guía Completa de Respaldo
