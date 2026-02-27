# Migración 002: Renombrar Campos a Español

## Fecha
2026-02-27

## Objetivo
Hacer la base de datos más semántica y amigable para usuarios en español, renombrando:
- `email` → `empresa`
- `department` → `centro_costos`

## Cambios Realizados

### 1. Base de Datos (SQL)
- ✅ Eliminado índice UNIQUE de `email` (múltiples usuarios pueden tener la misma empresa)
- ✅ Renombrado columna `email` → `empresa`
- ✅ Renombrado columna `department` → `centro_costos`
- ✅ Creados índices para mejorar búsquedas en ambos campos

### 2. Backend (Python)
- ✅ Actualizado modelo SQLAlchemy (`backend/db/models.py`)
- ✅ Actualizado schemas Pydantic (`backend/api/schemas.py`)
- ✅ Actualizado repository (`backend/db/repository.py`)
- ✅ Actualizado API de usuarios (`backend/api/users.py`)
- ✅ Actualizado servicio de provisioning (`backend/services/provisioning.py`)

### 3. Frontend (TypeScript/React)
- ✅ Actualizado tipos (`src/types/usuario.ts`)
- ✅ Actualizado servicios (`src/services/servicioUsuarios.ts`)
- ✅ Actualizado componentes:
  - `ModificarUsuario.tsx`
  - `FilaUsuario.tsx`
  - `TablaUsuarios.tsx`
  - `AdministracionUsuarios.tsx`

## Instrucciones para Aplicar la Migración

### Paso 1: Backup de la Base de Datos
```bash
# Ya se creó automáticamente en backups/
# Verificar que existe:
ls backups/ricoh_backup_antes_migracion_campos_*.sql
```

### Paso 2: Aplicar Migración SQL
```bash
# Opción A: Usando el script Python
cd backend
python apply_migration_002.py

# Opción B: Manualmente con psql
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet < backend/migrations/002_rename_email_department_to_spanish.sql
```

### Paso 3: Reiniciar Backend
```bash
docker-compose restart backend
```

### Paso 4: Verificar Cambios
```bash
# Verificar estructura de la tabla
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "\d users"

# Verificar que los campos existen
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT id, name, empresa, centro_costos FROM users LIMIT 5;"
```

## Rollback (Si es necesario)

Si algo sale mal, puedes restaurar el backup:

```bash
# Detener servicios
docker-compose down

# Restaurar backup
docker-compose up -d postgres
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet < backups/ricoh_backup_antes_migracion_campos_YYYYMMDD_HHMMSS.sql

# Reiniciar servicios
docker-compose up -d
```

## Validación Post-Migración

1. ✅ Verificar que la tabla `users` tiene las columnas `empresa` y `centro_costos`
2. ✅ Verificar que NO existe la columna `email` ni `department`
3. ✅ Verificar que los índices `ix_users_empresa` y `ix_users_centro_costos` existen
4. ✅ Verificar que el backend arranca sin errores
5. ✅ Verificar que el frontend muestra correctamente "Empresa" y "Centro de costos"
6. ✅ Probar crear/editar un usuario con estos campos

## Notas Importantes

- El campo `empresa` ya NO tiene restricción UNIQUE (múltiples usuarios pueden pertenecer a la misma empresa)
- Los datos existentes se preservan durante la migración (solo se renombran las columnas)
- La migración es compatible con versiones anteriores del código (si se revierte el código, solo cambiarán los nombres de las columnas)

## Impacto

- ✅ Sin pérdida de datos
- ✅ Sin downtime significativo (solo reinicio del backend)
- ✅ Mejora la claridad semántica del sistema
- ✅ Más amigable para usuarios hispanohablantes
