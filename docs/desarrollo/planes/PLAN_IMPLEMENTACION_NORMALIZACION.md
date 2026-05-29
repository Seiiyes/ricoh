# Plan de Implementación - Normalización con Sincronización Automática

## 🎯 Objetivo
Normalizar las tablas de contadores y cierres para usar `user_id` (FK) en lugar de `codigo_usuario` y `nombre_usuario` (texto), implementando sincronización automática de usuarios detectados en equipos.

## 📊 Estado Actual (2026-04-07)
- **6 usuarios** en tabla `users` (registrados manualmente)
- **435 usuarios únicos** detectados en contadores
- **429 usuarios activos** sin registro en `users`
- **21,356 registros** en `contadores_usuario`
- **6,776 registros** en `cierres_mensuales_usuarios`

## 🚀 Fases de Implementación

### FASE 1: Preparación y Backup (1 día)
**Objetivo:** Asegurar que podemos revertir cambios si algo sale mal

#### Tareas:
1. ✅ Crear backup completo de producción
   - Archivo: `backups/ricoh_backup_20260407_102718.sql` (7.62 MB)
   - Verificado: Contiene todos los datos actuales

2. ⏳ Revisar y aprobar propuesta de normalización
   - Documento: `PROPUESTA_NORMALIZACION_MEJORADA.md`
   - Revisar con equipo técnico
   - Aprobar cambios en base de datos

3. ⏳ Configurar ambiente de pruebas
   - Restaurar backup en ambiente de desarrollo
   - Probar migración 012 en desarrollo
   - Validar que no rompe funcionalidad existente

**Entregables:**
- ✅ Backup de producción
- ⏳ Aprobación de propuesta
- ⏳ Ambiente de pruebas configurado

---

### FASE 2: Migración de Base de Datos (1 día)
**Objetivo:** Agregar columnas FK y sincronizar usuarios existentes

#### Tareas:
1. ⏳ Ejecutar migración 012 en desarrollo
   ```bash
   Get-Content backend/migrations/012_normalize_user_references.sql | docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet
   ```
   - Agrega columnas `user_id` a tablas
   - Crea índices para performance
   - Agrega FK constraints
   - Crea vistas de compatibilidad

2. ⏳ Sincronización masiva inicial (429 usuarios)
   - Ejecutar script de sincronización
   - Crear usuarios faltantes con permisos deshabilitados
   - Poblar `user_id` en registros existentes
   - Verificar integridad de datos

3. ⏳ Validar migración en desarrollo
   - Verificar que todos los usuarios se crearon
   - Verificar que `user_id` está poblado
   - Verificar que queries funcionan
   - Verificar que vistas funcionan

**Entregables:**
- ⏳ Migración 012 ejecutada en desarrollo
- ⏳ 429 usuarios sincronizados
- ⏳ Validación exitosa

**Tiempo estimado:** 2-5 minutos para ejecutar migración

---

### FASE 3: Desarrollo del Código (1 semana)
**Objetivo:** Implementar sincronización automática en el backend

#### Tareas:
1. ⏳ Crear `UserSyncService`
   - Archivo: `backend/services/user_sync_service.py`
   - Método: `sync_user_from_counter()` - Sincroniza un usuario
   - Método: `sync_all_users_from_counters()` - Sincronización masiva
   - Tests unitarios

2. ⏳ Modificar `counter_service.py`
   - Integrar `UserSyncService.sync_user_from_counter()`
   - Guardar `user_id` en nuevos contadores
   - Mantener `codigo_usuario` y `nombre_usuario` para compatibilidad
   - Tests unitarios

3. ⏳ Modificar `cierre_service.py`
   - Usar `user_id` en lugar de `codigo_usuario`
   - Mantener campos antiguos para históricos
   - Tests unitarios

4. ⏳ Actualizar modelos SQLAlchemy
   - Agregar relaciones FK en `ContadorUsuario`
   - Agregar relaciones FK en `CierreMensualUsuario`
   - Actualizar schemas Pydantic

**Entregables:**
- ⏳ `UserSyncService` implementado y testeado
- ⏳ `counter_service.py` modificado
- ⏳ `cierre_service.py` modificado
- ⏳ Tests unitarios pasando

---

### FASE 4: Testing y Validación (3 días)
**Objetivo:** Asegurar que todo funciona correctamente

#### Tareas:
1. ⏳ Tests de integración
   - Leer contadores desde impresora
   - Verificar que usuarios se crean automáticamente
   - Verificar que `user_id` se guarda correctamente
   - Crear cierre mensual
   - Verificar que usa `user_id`

2. ⏳ Tests de performance
   - Comparar queries antes/después
   - Medir tiempo de lectura de contadores
   - Medir tiempo de creación de cierres
   - Validar que hay mejora de 2-3x

3. ⏳ Tests de compatibilidad
   - Verificar que código antiguo sigue funcionando
   - Verificar que vistas funcionan
   - Verificar que reportes funcionan
   - Verificar que frontend funciona

4. ⏳ Validación con usuarios finales
   - Probar lectura de contadores
   - Probar gestión de usuarios
   - Probar creación de cierres
   - Probar reportes

**Entregables:**
- ⏳ Tests de integración pasando
- ⏳ Mejora de performance validada
- ⏳ Compatibilidad verificada
- ⏳ Validación de usuarios finales

---

### FASE 5: Despliegue a Producción (1 día)
**Objetivo:** Implementar cambios en producción

#### Tareas:
1. ⏳ Ventana de mantenimiento (5-10 minutos)
   - Notificar a usuarios
   - Detener servicios
   - Ejecutar migración 012
   - Sincronizar 429 usuarios
   - Reiniciar servicios

2. ⏳ Desplegar código nuevo
   - Actualizar backend con `UserSyncService`
   - Actualizar `counter_service.py`
   - Actualizar `cierre_service.py`
   - Reiniciar servicios

3. ⏳ Monitoreo post-despliegue
   - Verificar logs de sincronización
   - Verificar que usuarios se crean automáticamente
   - Verificar que no hay errores
   - Monitorear performance

4. ⏳ Validación en producción
   - Leer contadores desde impresora real
   - Verificar que usuario nuevo se crea
   - Crear cierre mensual
   - Verificar reportes

**Entregables:**
- ⏳ Migración ejecutada en producción
- ⏳ Código desplegado
- ⏳ Monitoreo activo
- ⏳ Validación exitosa

**Tiempo de downtime:** 5-10 minutos

---

## 📋 Checklist de Implementación

### Pre-Despliegue
- [ ] Backup de producción creado y verificado
- [ ] Propuesta revisada y aprobada por equipo
- [ ] Migración 012 probada en desarrollo
- [ ] Sincronización masiva probada en desarrollo
- [ ] `UserSyncService` implementado y testeado
- [ ] `counter_service.py` modificado y testeado
- [ ] `cierre_service.py` modificado y testeado
- [ ] Tests de integración pasando
- [ ] Tests de performance validados
- [ ] Validación con usuarios finales completada

### Durante Despliegue
- [ ] Notificar usuarios de ventana de mantenimiento
- [ ] Detener servicios backend
- [ ] Ejecutar migración 012 en producción
- [ ] Verificar que migración completó exitosamente
- [ ] Sincronizar 429 usuarios faltantes
- [ ] Verificar que usuarios se crearon
- [ ] Desplegar código nuevo
- [ ] Reiniciar servicios
- [ ] Verificar que servicios están corriendo

### Post-Despliegue
- [ ] Verificar logs de sincronización
- [ ] Leer contadores desde impresora real
- [ ] Verificar que usuario nuevo se crea automáticamente
- [ ] Crear cierre mensual de prueba
- [ ] Verificar reportes funcionan
- [ ] Monitorear performance durante 24 horas
- [ ] Validar con usuarios finales

---

## 🔧 Comandos Útiles

### Backup de Base de Datos
```bash
# Crear backup
docker exec ricoh-postgres pg_dump -U ricoh_admin -d ricoh_fleet > backups/ricoh_backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup (si es necesario)
Get-Content backups/ricoh_backup_20260407_102718.sql | docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet
```

### Ejecutar Migración 012
```bash
# En desarrollo
Get-Content backend/migrations/012_normalize_user_references.sql | docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet

# Verificar resultado
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT COUNT(*) FROM users;"
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT COUNT(*) FROM contadores_usuario WHERE user_id IS NOT NULL;"
```

### Sincronización Masiva (Script Python)
```python
# backend/scripts/sync_users.py
from backend.db.database import get_db
from backend.services.user_sync_service import UserSyncService

db = next(get_db())
stats = UserSyncService.sync_all_users_from_counters(db, days=30)
print(f"Usuarios creados: {stats['created']}")
print(f"Usuarios existentes: {stats['existing']}")
print(f"Total: {stats['total']}")
```

### Verificar Sincronización
```sql
-- Ver usuarios creados
SELECT COUNT(*) FROM users;

-- Ver usuarios con actividad reciente
SELECT 
    u.codigo_de_usuario,
    u.name,
    COUNT(DISTINCT cu.printer_id) as impresoras,
    COUNT(*) as lecturas,
    MAX(cu.fecha_lectura) as ultima_actividad
FROM users u
JOIN contadores_usuario cu ON u.id = cu.user_id
WHERE cu.fecha_lectura >= NOW() - INTERVAL '7 days'
GROUP BY u.codigo_de_usuario, u.name
ORDER BY lecturas DESC
LIMIT 20;
```

---

## 📊 Métricas de Éxito

### Antes de la Implementación
- 6 usuarios en `users`
- 429 usuarios sin registro
- Queries lentas (comparación de strings)
- Gestión manual de usuarios

### Después de la Implementación
- 435 usuarios en `users` (6 + 429)
- 0 usuarios sin registro
- Queries 2-3x más rápidas (JOIN por integer)
- Sincronización automática de usuarios
- Gestión centralizada de permisos
- Visibilidad de usuarios por impresora

---

## 🚨 Plan de Rollback

Si algo sale mal durante el despliegue:

1. **Detener servicios backend**
   ```bash
   docker compose stop backend
   ```

2. **Restaurar backup de base de datos**
   ```bash
   # Eliminar base de datos actual
   docker exec -i ricoh-postgres psql -U ricoh_admin -c "DROP DATABASE ricoh_fleet;"
   docker exec -i ricoh-postgres psql -U ricoh_admin -c "CREATE DATABASE ricoh_fleet OWNER ricoh_admin;"
   
   # Restaurar backup
   Get-Content backups/ricoh_backup_20260407_102718.sql | docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet
   ```

3. **Revertir código a versión anterior**
   ```bash
   git checkout <commit-anterior>
   docker compose up -d --build backend
   ```

4. **Verificar que todo funciona**
   - Probar lectura de contadores
   - Probar creación de cierres
   - Verificar reportes

**Tiempo estimado de rollback:** 10-15 minutos

---

## 📞 Contactos

- **Responsable técnico:** [Nombre]
- **DBA:** [Nombre]
- **QA:** [Nombre]
- **Product Owner:** [Nombre]

---

**Fecha de creación:** 2026-04-07  
**Última actualización:** 2026-04-07  
**Estado:** Pendiente de aprobación
