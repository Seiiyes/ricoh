# Problemas con Migración 015 - Normalización de Base de Datos

## Fecha del Incidente
2026-04-09

## Problema
Error 500 al crear usuarios después de aplicar la migración 015 de normalización.

## Causa Raíz
La migración 015 (`backend/migrations/015_final_normalization.sql`) normalizó la base de datos creando dos nuevas tablas:
- `smb_servers` - Para configuración SMB normalizada
- `network_credentials` - Para credenciales de red normalizadas

Y agregó dos columnas NOT NULL a la tabla `users`:
- `smb_server_id` (FK a smb_servers)
- `network_credential_id` (FK a network_credentials)

**El problema:** Los modelos ORM de SQLAlchemy no fueron actualizados para reflejar estos cambios, causando que:
1. El modelo `User` no tenía las columnas `smb_server_id` y `network_credential_id`
2. No existían los modelos `SMBServer` y `NetworkCredential`
3. El repositorio intentaba crear usuarios sin proporcionar estos campos obligatorios

## Error Específico
```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.NotNullViolation) 
null value in column "smb_server_id" of relation "users" violates not-null constraint
```

## Solución Aplicada

### 1. Creados nuevos modelos ORM (backend/db/models.py)
```python
class SMBServer(Base):
    __tablename__ = "smb_servers"
    id, server_address, port, description, is_default, created_at, updated_at

class NetworkCredential(Base):
    __tablename__ = "network_credentials"
    id, username, password_encrypted, description, is_default, created_at, updated_at
```

### 2. Actualizado modelo User (backend/db/models.py)
- Agregadas columnas: `smb_server_id`, `network_credential_id`
- Agregadas relaciones: `smb_server_rel`, `network_credential_rel`

### 3. Actualizado UserRepository (backend/db/repository.py)
- Método `create()` ahora:
  1. Busca o crea registro en `smb_servers`
  2. Busca o crea registro en `network_credentials`
  3. Asigna los IDs al crear el usuario
  4. Mantiene compatibilidad con columnas antiguas

## Lecciones Aprendidas

### ⚠️ REGLA CRÍTICA
**Cuando se modifica el esquema de base de datos, SIEMPRE actualizar:**
1. ✅ Modelos ORM (backend/db/models.py)
2. ✅ Repositorios (backend/db/repository.py)
3. ✅ Schemas de API (backend/api/schemas.py) - si aplica
4. ✅ Servicios que usan los modelos
5. ✅ Frontend - si los cambios afectan la API

### Checklist para Migraciones Futuras
- [ ] Ejecutar migración SQL
- [ ] Actualizar modelos ORM
- [ ] Actualizar repositorios
- [ ] Actualizar schemas de Pydantic
- [ ] Verificar servicios afectados
- [ ] Probar endpoints afectados
- [ ] Actualizar frontend si es necesario
- [ ] Documentar cambios

## Estado Actual
- ✅ Modelos actualizados
- ✅ Repositorio actualizado
- ⏳ Pendiente: Revisar otros archivos afectados
- ⏳ Pendiente: Verificar frontend

## Archivos Modificados
1. `backend/db/models.py` - Agregados SMBServer, NetworkCredential, actualizadas relaciones User
2. `backend/db/repository.py` - Actualizado UserRepository.create()
3. `backend/api/users.py` - Corregido manejo de respuesta (error de serialización)
4. `backend/main.py` - Mejorado filtro de logging para no ocultar errores

## Próximos Pasos
1. Revisar TODOS los archivos que usan el modelo User
2. Verificar que los schemas de API estén actualizados
3. Revisar servicios de exportación (export_ricoh.py, etc.)
4. Verificar frontend
5. Probar flujo completo de creación de usuarios
