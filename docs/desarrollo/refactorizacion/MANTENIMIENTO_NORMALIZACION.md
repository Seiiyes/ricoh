# Guía de Mantenimiento - Sistema Normalizado

## 📋 Descripción

Este documento describe las tareas de mantenimiento necesarias para el sistema normalizado de gestión de usuarios e impresoras Ricoh.

---

## 🔄 Sincronización Automática

### Funcionamiento

La sincronización de usuarios ocurre automáticamente cuando:

1. Se leen contadores desde una impresora
2. Se detecta un usuario nuevo (no existe en tabla `users`)
3. Se crea el usuario con:
   - Permisos deshabilitados
   - Ruta SMB por defecto: `\\PENDIENTE\Escaner`
   - Credenciales de red por defecto

### Verificar Sincronización

```bash
# Ver usuarios sincronizados recientemente
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    codigo_de_usuario,
    name,
    smb_path,
    is_active,
    created_at
FROM users
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC
LIMIT 20;
"
```

### Forzar Sincronización Manual

```bash
# Sincronizar todos los usuarios desde contadores
curl -X POST http://localhost:8000/api/sync/users \
  -H "Authorization: Bearer YOUR_TOKEN"

# O desde el contenedor
docker exec ricoh-backend python -c "
from db.database import SessionLocal
from services.user_sync_service import UserSyncService

db = SessionLocal()
stats = UserSyncService.sync_all_users_from_counters(db, days=30)
print(f'Creados: {stats[\"created\"]}')
print(f'Existentes: {stats[\"existing\"]}')
print(f'Total: {stats[\"total\"]}')
db.close()
"
```

---

## 🔍 Verificación de Integridad

### Verificar user_id en Todas las Tablas

```bash
# Verificar contadores_usuario
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    COUNT(*) as total,
    COUNT(user_id) as con_user_id,
    COUNT(*) - COUNT(user_id) as sin_user_id,
    ROUND(COUNT(user_id)::numeric / COUNT(*) * 100, 2) as porcentaje
FROM contadores_usuario;
"

# Verificar cierres_mensuales_usuarios
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    COUNT(*) as total,
    COUNT(user_id) as con_user_id,
    COUNT(*) - COUNT(user_id) as sin_user_id,
    ROUND(COUNT(user_id)::numeric / COUNT(*) * 100, 2) as porcentaje
FROM cierres_mensuales_usuarios;
"
```

### Verificar Integridad Referencial

```bash
# Buscar user_id que no existen en tabla users
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    'contadores_usuario' as tabla,
    COUNT(*) as registros_huerfanos
FROM contadores_usuario cu
WHERE cu.user_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = cu.user_id)
UNION ALL
SELECT 
    'cierres_mensuales_usuarios',
    COUNT(*)
FROM cierres_mensuales_usuarios cmu
WHERE cmu.user_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = cmu.user_id);
"
```

**Resultado esperado:** 0 registros huérfanos

---

## 📊 Monitoreo de Rutas SMB

### Ver Distribución de Rutas SMB

```bash
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    CASE 
        WHEN smb_path = '\\\\PENDIENTE\\Escaner' THEN 'Por defecto'
        ELSE 'Específica'
    END as tipo_ruta,
    COUNT(*) as cantidad,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM users WHERE is_active = true) * 100, 2) as porcentaje
FROM users
WHERE is_active = true
GROUP BY tipo_ruta
ORDER BY cantidad DESC;
"
```

### Usuarios sin Ruta SMB Específica

```bash
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    codigo_de_usuario,
    name,
    smb_path,
    created_at
FROM users
WHERE is_active = true
  AND smb_path = '\\\\PENDIENTE\\Escaner'
ORDER BY created_at DESC
LIMIT 20;
"
```

### Sincronizar Rutas SMB desde Impresoras

```bash
# Sincronizar todas las impresoras
docker exec ricoh-backend python scripts/sync_all_5_printers_to_db.py

# Verificar resultado
docker exec ricoh-backend python scripts/quick_verify_5_printers.py
```

---

## 🔧 Mantenimiento de Cierres

### Verificar Cierres Recientes

```bash
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    cm.id,
    p.hostname,
    cm.tipo_periodo,
    cm.fecha_inicio,
    cm.fecha_fin,
    cm.total_paginas,
    COUNT(cmu.id) as usuarios,
    COUNT(cmu.user_id) as usuarios_con_id
FROM cierres_mensuales cm
JOIN printers p ON cm.printer_id = p.id
LEFT JOIN cierres_mensuales_usuarios cmu ON cm.id = cmu.cierre_mensual_id
WHERE cm.fecha_cierre >= NOW() - INTERVAL '7 days'
GROUP BY cm.id, p.hostname, cm.tipo_periodo, cm.fecha_inicio, cm.fecha_fin, cm.total_paginas
ORDER BY cm.fecha_cierre DESC;
"
```

### Probar Creación de Cierre

```bash
# Ejecutar script de prueba
docker exec ricoh-backend python scripts/test_cierre_normalizado.py
```

---

## 🚨 Resolución de Problemas

### Problema: Usuarios sin user_id en Contadores

**Síntoma:**
```sql
SELECT COUNT(*) FROM contadores_usuario WHERE user_id IS NULL;
-- Resultado: > 0
```

**Solución:**
```bash
# Sincronizar usuarios faltantes
docker exec ricoh-backend python -c "
from db.database import SessionLocal
from services.user_sync_service import UserSyncService

db = SessionLocal()
stats = UserSyncService.sync_all_users_from_counters(db, days=365)
print(f'Usuarios sincronizados: {stats[\"created\"]}')
db.close()
"

# Actualizar user_id en contadores
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
UPDATE contadores_usuario cu
SET user_id = u.id
FROM users u
WHERE cu.codigo_usuario = u.codigo_de_usuario
  AND cu.user_id IS NULL;
"
```

### Problema: Usuarios sin user_id en Cierres

**Síntoma:**
```sql
SELECT COUNT(*) FROM cierres_mensuales_usuarios WHERE user_id IS NULL;
-- Resultado: > 0
```

**Solución:**
```bash
# Actualizar user_id en cierres
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
UPDATE cierres_mensuales_usuarios cmu
SET user_id = u.id
FROM users u
WHERE cmu.codigo_usuario = u.codigo_de_usuario
  AND cmu.user_id IS NULL;
"
```

### Problema: Rutas SMB Genéricas

**Síntoma:**
```sql
SELECT COUNT(*) FROM users WHERE smb_path = '\\PENDIENTE\Escaner';
-- Resultado: > 100
```

**Solución:**
```bash
# Sincronizar rutas SMB desde impresoras
docker exec ricoh-backend python scripts/sync_all_5_printers_to_db.py

# Verificar resultado
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    COUNT(*) as total,
    COUNT(CASE WHEN smb_path = '\\\\PENDIENTE\\Escaner' THEN 1 END) as genericas,
    COUNT(CASE WHEN smb_path != '\\\\PENDIENTE\\Escaner' THEN 1 END) as especificas
FROM users
WHERE is_active = true;
"
```

### Problema: Performance Lenta en Cierres

**Síntoma:**
- Creación de cierres tarda más de 30 segundos

**Diagnóstico:**
```bash
# Verificar índices
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('contadores_usuario', 'cierres_mensuales_usuarios')
  AND indexname LIKE '%user_id%';
"
```

**Solución:**
```bash
# Recrear índices si es necesario
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
REINDEX INDEX idx_contadores_usuario_user_id;
REINDEX INDEX idx_cierres_usuarios_user_id;
ANALYZE contadores_usuario;
ANALYZE cierres_mensuales_usuarios;
"
```

---

## 📈 Métricas de Salud

### Dashboard de Salud del Sistema

```bash
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    'Usuarios activos' as metrica,
    COUNT(*)::text as valor
FROM users WHERE is_active = true
UNION ALL
SELECT 
    'Usuarios con SMB específico',
    COUNT(*)::text
FROM users 
WHERE is_active = true AND smb_path != '\\\\PENDIENTE\\Escaner'
UNION ALL
SELECT 
    'Contadores con user_id',
    ROUND(COUNT(user_id)::numeric / COUNT(*) * 100, 2)::text || '%'
FROM contadores_usuario
UNION ALL
SELECT 
    'Cierres con user_id',
    ROUND(COUNT(user_id)::numeric / COUNT(*) * 100, 2)::text || '%'
FROM cierres_mensuales_usuarios
UNION ALL
SELECT 
    'Cierres últimos 30 días',
    COUNT(*)::text
FROM cierres_mensuales
WHERE fecha_cierre >= NOW() - INTERVAL '30 days';
"
```

**Valores esperados:**
- Usuarios activos: ~440
- Usuarios con SMB específico: ~328 (74%)
- Contadores con user_id: 100%
- Cierres con user_id: 100%
- Cierres últimos 30 días: Variable

---

## 🔄 Tareas de Mantenimiento Periódicas

### Diarias
- [ ] Verificar logs del backend para errores de sincronización
- [ ] Monitorear performance de queries

### Semanales
- [ ] Verificar integridad referencial
- [ ] Revisar usuarios nuevos sincronizados
- [ ] Verificar rutas SMB genéricas

### Mensuales
- [ ] Sincronizar rutas SMB desde impresoras
- [ ] Analizar performance de cierres
- [ ] Revisar y optimizar índices
- [ ] Backup de base de datos

### Trimestrales
- [ ] Auditoría completa de usuarios
- [ ] Limpieza de usuarios inactivos
- [ ] Revisión de permisos
- [ ] Actualización de documentación

---

## 📞 Comandos Útiles

### Backup

```bash
# Crear backup
docker exec ricoh-postgres pg_dump -U ricoh_admin -d ricoh_fleet > backups/ricoh_backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
cat backups/ricoh_backup_YYYYMMDD_HHMMSS.sql | docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet
```

### Logs

```bash
# Ver logs del backend
docker logs ricoh-backend --tail 100 -f

# Buscar errores
docker logs ricoh-backend | grep -i error

# Buscar sincronizaciones
docker logs ricoh-backend | grep -i sync
```

### Reiniciar Servicios

```bash
# Reiniciar backend
docker compose restart backend

# Reiniciar todo
docker compose restart
```

---

## 📚 Referencias

- [Propuesta de Normalización](./PROPUESTA_NORMALIZACION_MEJORADA.md)
- [Plan de Implementación](./PLAN_IMPLEMENTACION_NORMALIZACION.md)
- [Sincronización de Rutas SMB](./SINCRONIZACION_RUTAS_SMB.md)
- [Normalización de Cierres](./NORMALIZACION_CIERRES_COMPLETADA.md)
- [Resumen Completo](./RESUMEN_NORMALIZACION_COMPLETA.md)

---

**Fecha de creación:** 2026-04-08  
**Última actualización:** 2026-04-08  
**Responsable:** Equipo de desarrollo
