# Checklist de Actualización - Migración 015

## Cambios en la Base de Datos (Migración 015)

### Tablas Nuevas Creadas
- ✅ `smb_servers` - Configuración SMB normalizada
- ✅ `network_credentials` - Credenciales de red normalizadas

### Cambios en Tabla `users`
- ✅ Agregada columna `smb_server_id` (FK a smb_servers, NOT NULL)
- ✅ Agregada columna `network_credential_id` (FK a network_credentials, NOT NULL)
- ⚠️ Columnas antiguas MANTENIDAS para compatibilidad:
  - `smb_server`, `smb_port`, `smb_path`
  - `network_username`, `network_password_encrypted`

## Actualizaciones Realizadas en Backend

### ✅ Modelos ORM (backend/db/models.py)
- [x] Creado modelo `SMBServer`
- [x] Creado modelo `NetworkCredential`
- [x] Actualizado modelo `User`:
  - [x] Agregadas columnas `smb_server_id`, `network_credential_id`
  - [x] Agregadas relaciones `smb_server_rel`, `network_credential_rel`
  - [x] Mantenidas columnas antiguas para compatibilidad

### ✅ Repositorios (backend/db/repository.py)
- [x] Actualizado `UserRepository.create()`:
  - [x] Busca o crea registro en `smb_servers`
  - [x] Busca o crea registro en `network_credentials`
  - [x] Asigna IDs a las foreign keys
  - [x] Mantiene compatibilidad con columnas antiguas

### ✅ API Endpoints (backend/api/users.py)
- [x] Corregido error de serialización en respuesta
- [x] Mejorado manejo de errores con traceback completo

### ✅ Logging (backend/main.py)
- [x] Mejorado filtro de logging para no ocultar errores con "password"

## Archivos que NO Necesitan Cambios

### Servicios que Usan Columnas Antiguas (Compatibles)
- ✅ `backend/services/provisioning.py` - Usa `user.network_username`, `user.smb_server`, etc.
- ✅ `backend/services/user_sync_service.py` - Usa `user.smb_path`
- ✅ `backend/services/export_ricoh.py` - Solo usa `user.codigo_de_usuario` y `user.name`

### Scripts
- ✅ `backend/scripts/sync_all_5_printers_to_db.py` - Usa `user.smb_path`
- ✅ `backend/scripts/sync_users_from_addressbooks.py` - Usa `user.smb_path`
- ✅ `backend/scripts/check_smb_paths_status.py` - Usa `user.smb_path`

### Frontend
- ✅ `src/services/printerService.ts` - Estructura de request correcta
- ✅ Componentes de UI - No necesitan cambios

## Estado Actual

### ✅ Completado
1. Modelos ORM actualizados
2. Repositorio actualizado para manejar normalización
3. Manejo de errores mejorado
4. Compatibilidad con código existente mantenida

### ⚠️ Consideraciones Importantes

#### Columnas Duplicadas
Las columnas antiguas (`smb_server`, `smb_port`, `smb_path`, `network_username`, `network_password_encrypted`) todavía existen en la base de datos. Esto es INTENCIONAL para:
1. Mantener compatibilidad con código existente
2. Permitir rollback si es necesario
3. Facilitar migración gradual

El paso 5 de la migración (eliminar columnas redundantes) está COMENTADO y debe ejecutarse solo después de:
- Validar que todo funciona correctamente
- Esperar al menos 1 semana en producción
- Confirmar que no hay problemas

#### Sincronización de Datos
El repositorio actualizado ahora:
1. Crea/busca registro en `smb_servers`
2. Crea/busca registro en `network_credentials`
3. Asigna los IDs a las foreign keys
4. TAMBIÉN llena las columnas antiguas para compatibilidad

Esto significa que:
- ✅ Nuevos usuarios tendrán datos en ambos lugares
- ✅ Código antiguo seguirá funcionando
- ✅ Código nuevo puede usar las relaciones normalizadas

## Pruebas Recomendadas

### Pruebas Funcionales
- [ ] Crear usuario nuevo desde frontend
- [ ] Verificar que se crea registro en `smb_servers`
- [ ] Verificar que se crea registro en `network_credentials`
- [ ] Verificar que usuario tiene `smb_server_id` y `network_credential_id`
- [ ] Verificar que columnas antiguas también se llenan
- [ ] Provisionar usuario a impresora
- [ ] Exportar datos de usuarios
- [ ] Sincronizar usuarios desde impresoras

### Pruebas de Integridad
- [ ] Verificar que no hay usuarios con `smb_server_id` NULL
- [ ] Verificar que no hay usuarios con `network_credential_id` NULL
- [ ] Verificar que foreign keys funcionan correctamente
- [ ] Verificar que relaciones ORM funcionan

## Comandos Útiles

### Verificar Estado de la Base de Datos
```sql
-- Contar usuarios sin foreign keys
SELECT COUNT(*) FROM users WHERE smb_server_id IS NULL OR network_credential_id IS NULL;

-- Ver servidores SMB únicos
SELECT * FROM smb_servers;

-- Ver credenciales de red únicas
SELECT * FROM network_credentials;

-- Ver usuarios con sus relaciones
SELECT u.id, u.name, u.codigo_de_usuario, s.server_address, nc.username
FROM users u
JOIN smb_servers s ON u.smb_server_id = s.id
JOIN network_credentials nc ON u.network_credential_id = nc.id
LIMIT 10;
```

### Verificar Logs
```bash
# Ver logs de creación de usuarios
docker-compose logs --tail=100 backend | grep "User created"

# Ver errores
docker-compose logs --tail=100 backend | grep "ERROR"
```

## Próximos Pasos (Futuro)

### Cuando Todo Esté Validado (1+ semana)
1. Descomentar paso 5 de la migración 015
2. Ejecutar para eliminar columnas redundantes
3. Actualizar código para usar solo relaciones normalizadas
4. Actualizar tests

### Optimizaciones Futuras
- Crear índices adicionales si es necesario
- Implementar caché para servidores SMB y credenciales
- Considerar agregar validaciones adicionales

## Documentación Relacionada
- `backend/migrations/015_final_normalization.sql` - Migración completa
- `backend/MIGRATION_015_ISSUES.md` - Documentación del error encontrado
- `backend/db/models.py` - Modelos actualizados
- `backend/db/repository.py` - Repositorio actualizado
