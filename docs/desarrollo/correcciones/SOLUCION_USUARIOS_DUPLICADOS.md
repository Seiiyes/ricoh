# Solución: Usuarios Duplicados

## 🎯 Problema Resuelto

Usuarios aparecían duplicados con códigos diferentes que representan al mismo usuario:
- ADRIANA MAQUILLO: códigos "0547" y "547"
- Otros 5 usuarios con el mismo problema

## ✅ Solución Implementada

### 1. Normalización de Códigos de Usuario

Se implementó función `normalize_user_code()` que:
- Elimina ceros a la izquierda: `"0547"` → `"547"`
- Maneja casos especiales: `"0000"` → `"0"`
- Se aplica ANTES de buscar/crear usuarios

### 2. Actualización de UserSyncService

Archivo: `backend/services/user_sync_service.py`

Cambios:
- ✅ Función `normalize_user_code()` agregada
- ✅ `sync_user_from_counter()` normaliza códigos antes de buscar/crear
- ✅ `sync_users_from_printer_addressbook()` normaliza códigos
- ✅ Logging mejorado muestra cuando se normaliza un código

### 3. Script de Consolidación

Archivo: `backend/scripts/consolidate_duplicate_users.py`

Funcionalidad:
- Identifica usuarios con códigos que normalizan al mismo valor
- Selecciona usuario "principal" por grupo
- Actualiza todas las referencias FK:
  - `contadores_usuario.user_id`
  - `cierre_mensual_usuario.user_id`
  - `user_printer_assignments.user_id`
- Elimina usuarios duplicados
- Normaliza códigos de usuarios principales

### 4. Migración de Base de Datos

Archivo: `backend/migrations/016_fix_duplicate_users.sql`

Cambios:
- ✅ Constraint UNIQUE en `users.codigo_de_usuario`
- ✅ Comentario documentando normalización requerida
- ✅ Verificaciones de integridad

### 5. Tests Unitarios

Archivo: `backend/services/test_user_sync_service.py`

Cobertura:
- ✅ Tests de normalización de códigos
- ✅ Tests de prevención de duplicados
- ✅ Tests de sincronización con códigos variantes

### 6. Documentación

Archivo: `backend/DOCUMENTACION_USUARIOS_DUPLICADOS.md`

Contenido:
- Análisis completo del problema
- Causa raíz identificada
- Flujo de datos documentado
- Solución detallada
- Guías de prevención futura

## 🚀 Pasos de Implementación

### Paso 1: Consolidar Usuarios Duplicados ⚠️ EJECUTAR PRIMERO

```bash
# Ejecutar desde el contenedor backend
docker exec -it ricoh-backend python scripts/consolidate_duplicate_users.py
```

Este script:
1. Identifica 5 grupos de usuarios duplicados
2. Consolida cada grupo en un usuario principal
3. Actualiza todas las referencias FK
4. Elimina usuarios duplicados

### Paso 2: Aplicar Migración (Constraint UNIQUE)

```bash
# Ejecutar migración SQL
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -f /app/migrations/016_fix_duplicate_users.sql
```

Esta migración:
1. Verifica que no hay duplicados
2. Agrega constraint UNIQUE a `codigo_de_usuario`
3. Previene duplicados futuros a nivel de base de datos

### Paso 3: Reiniciar Backend

```bash
# Reiniciar para cargar código actualizado
docker restart ricoh-backend
```

### Paso 4: Verificación

```bash
# Verificar que no hay duplicados
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT codigo_de_usuario, COUNT(*) as count 
FROM users 
GROUP BY codigo_de_usuario 
HAVING COUNT(*) > 1;
"

# Debe retornar 0 filas
```

### Paso 5: Prueba de Lectura de Contadores

```bash
# Leer contadores de una impresora para verificar que no se crean duplicados
# Desde el frontend o usando curl:
curl -X POST http://localhost:8000/api/counters/read-user-counters/1
```

Verificar en logs que:
- Usuarios existentes se reutilizan (no se crean duplicados)
- Códigos se normalizan correctamente
- Mensajes de log muestran normalización cuando aplica

## 📊 Resultados Esperados

### Antes de la Solución

```sql
SELECT id, name, codigo_de_usuario FROM users WHERE name ILIKE '%ADRIANA%';
 id  |       name       | codigo_de_usuario 
-----+------------------+-------------------
 197 | ADRIANA MAQUILLO | 0547              ← Duplicado
 296 | ADRIANA MAQUILLO | 547               ← Duplicado
 349 | ADRIANA VARGAS   | 3905
 108 | ADRIANA ESPINOSA | 8599
```

### Después de la Solución

```sql
SELECT id, name, codigo_de_usuario FROM users WHERE name ILIKE '%ADRIANA%';
 id  |       name       | codigo_de_usuario 
-----+------------------+-------------------
 197 | ADRIANA MAQUILLO | 547               ← Consolidado (código normalizado)
 349 | ADRIANA VARGAS   | 3905
 108 | ADRIANA ESPINOSA | 8599
```

## 🔒 Prevención Futura

### A Nivel de Código

1. **Normalización automática**: Todos los códigos se normalizan antes de buscar/crear
2. **Logging detallado**: Se registra cuando un código se normaliza
3. **Tests unitarios**: Previenen regresiones

### A Nivel de Base de Datos

1. **Constraint UNIQUE**: Imposible crear usuarios con mismo código
2. **Comentarios en schema**: Documentan normalización requerida

### Checklist para Nuevas Funcionalidades

Cuando se agregue código que cree o busque usuarios:

- [ ] ¿Se usa `normalize_user_code()` antes de buscar?
- [ ] ¿Se usa `normalize_user_code()` antes de crear?
- [ ] ¿Se maneja el caso de código vacío?
- [ ] ¿Se tiene test unitario?

## 📝 Archivos Modificados

### Código Actualizado
- ✅ `backend/services/user_sync_service.py` - Normalización implementada
- ✅ `backend/services/test_user_sync_service.py` - Tests agregados

### Scripts Nuevos
- ✅ `backend/scripts/consolidate_duplicate_users.py` - Consolidación de duplicados
- ✅ `backend/migrations/016_fix_duplicate_users.sql` - Constraint UNIQUE

### Documentación Nueva
- ✅ `backend/DOCUMENTACION_USUARIOS_DUPLICADOS.md` - Análisis completo
- ✅ `backend/SOLUCION_USUARIOS_DUPLICADOS.md` - Este archivo

## 🎉 Beneficios

1. **Integridad de datos**: No más usuarios duplicados
2. **Consistencia**: Todos los códigos normalizados
3. **Prevención**: Constraint UNIQUE previene duplicados futuros
4. **Mantenibilidad**: Código documentado y testeado
5. **Confiabilidad**: Usuarios se reutilizan correctamente

## ⚠️ Notas Importantes

1. **Ejecutar en orden**: Consolidación → Migración → Reinicio
2. **Backup recomendado**: Hacer backup de tabla `users` antes de consolidar
3. **Verificar logs**: Revisar logs durante primera lectura de contadores
4. **Monitorear**: Verificar que no se crean duplicados en próximas lecturas

---

**Fecha**: 2026-04-08
**Estado**: ✅ Implementado - Pendiente de Ejecución
**Próximo Paso**: Ejecutar script de consolidación
