# Análisis de Normalización - Base de Datos Ricoh

## 📋 Resumen Ejecutivo

Se identificaron oportunidades de normalización en las tablas de cierres y contadores que almacenan datos redundantes de usuarios. La implementación de llaves foráneas mejorará la integridad referencial, el rendimiento y reducirá el espacio en disco.

---

## 🔍 Problemas Identificados

### 1. Redundancia en `cierres_mensuales_usuarios`

**Situación Actual:**
- **6,776 registros** almacenan `codigo_usuario` (varchar 8) y `nombre_usuario` (varchar 100)
- Cada usuario se repite múltiples veces (ej: MIGUEL GUILLEN aparece 39 veces)
- **429 usuarios históricos** que ya no existen en la tabla `users`

**Impacto:**
- Espacio desperdiciado: ~90 KB
- Búsquedas lentas por comparación de strings
- Sin integridad referencial
- Riesgo de inconsistencias si cambia el nombre de un usuario

### 2. Redundancia en `contadores_usuario`

**Situación Actual:**
- **21,356 registros** con los mismos campos redundantes
- Mismos 429 usuarios históricos sin FK

**Impacto:**
- Espacio desperdiciado: ~284 KB
- Índices más grandes y lentos
- Consultas JOIN ineficientes

### 3. Campos de Auditoría sin Normalizar

**Tabla:** `cierres_mensuales`

**Campos Problemáticos:**
- `cerrado_por` (varchar 100): Valores como "admin", "Super Administrador", "SCRIPT_VERIFICACION"
- `modified_by` (varchar 100): Sin FK a `admin_users`

**Impacto:**
- No se puede rastrear quién realmente hizo el cierre
- Riesgo de typos
- Sin integridad referencial

---

## ✅ Solución Propuesta

### Migración 012: Normalización de Referencias

La migración `012_normalize_user_references.sql` implementa:

#### 1. Agregar `user_id` a Tablas de Datos

```sql
ALTER TABLE cierres_mensuales_usuarios ADD COLUMN user_id INTEGER;
ALTER TABLE contadores_usuario ADD COLUMN user_id INTEGER;
```

#### 2. Poblar `user_id` con Datos Existentes

```sql
UPDATE cierres_mensuales_usuarios cmu
SET user_id = u.id
FROM users u
WHERE u.codigo_de_usuario = cmu.codigo_usuario;
```

#### 3. Crear Foreign Keys

```sql
ALTER TABLE cierres_mensuales_usuarios
ADD CONSTRAINT fk_cierres_usuarios_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
```

**Nota:** Se usa `ON DELETE SET NULL` para preservar registros históricos si se elimina un usuario.

#### 4. Normalizar Campos de Auditoría

```sql
ALTER TABLE cierres_mensuales
ADD COLUMN cerrado_por_admin_id INTEGER,
ADD COLUMN modified_by_admin_id INTEGER;

ALTER TABLE cierres_mensuales
ADD CONSTRAINT fk_cierres_cerrado_por_admin 
FOREIGN KEY (cerrado_por_admin_id) REFERENCES admin_users(id);
```

#### 5. Crear Vistas de Compatibilidad

```sql
CREATE VIEW v_cierres_mensuales_usuarios AS
SELECT 
    cmu.*,
    COALESCE(u.codigo_de_usuario, cmu.codigo_usuario) as codigo_usuario_actual,
    COALESCE(u.name, cmu.nombre_usuario) as nombre_usuario_actual
FROM cierres_mensuales_usuarios cmu
LEFT JOIN users u ON cmu.user_id = u.id;
```

---

## 📊 Beneficios Esperados

### 1. Integridad Referencial

✅ Garantiza que los registros apunten a usuarios válidos  
✅ Previene inconsistencias por cambios de nombre  
✅ Permite rastrear auditoría de forma confiable

### 2. Rendimiento

✅ JOINs por enteros (4 bytes) vs strings (8-100 bytes)  
✅ Índices más pequeños y eficientes  
✅ Consultas 2-3x más rápidas en tablas grandes

**Ejemplo de mejora:**

```sql
-- ANTES (lento)
SELECT * FROM contadores_usuario cu
JOIN users u ON u.codigo_de_usuario = cu.codigo_usuario;

-- DESPUÉS (rápido)
SELECT * FROM contadores_usuario cu
JOIN users u ON u.id = cu.user_id;
```

### 3. Ahorro de Espacio

| Tabla | Registros | Ahorro Estimado |
|-------|-----------|-----------------|
| `cierres_mensuales_usuarios` | 6,776 | 90 KB |
| `contadores_usuario` | 21,356 | 284 KB |
| **Total** | **28,132** | **~374 KB** |

**Nota:** El ahorro real será mayor con el crecimiento de datos.

### 4. Mantenibilidad

✅ Código más limpio y fácil de entender  
✅ Menos riesgo de bugs por datos inconsistentes  
✅ Facilita futuras migraciones

---

## 🚨 Consideraciones Importantes

### 1. Usuarios Históricos

**Problema:** 429 usuarios en cierres/contadores que ya no existen en `users`

**Solución:** 
- Se mantienen los campos `codigo_usuario` y `nombre_usuario` para referencia histórica
- `user_id` será NULL para estos registros
- Los datos históricos se preservan intactos

### 2. Compatibilidad con Código Existente

**Estrategia:**
- Los campos antiguos NO se eliminan inmediatamente
- Se crean vistas (`v_cierres_mensuales_usuarios`, `v_contadores_usuario`) que combinan ambos enfoques
- El código existente sigue funcionando
- El código nuevo debe usar `user_id`

### 3. Migración Gradual

**Fase 1 (Actual):** Agregar `user_id` y mantener campos antiguos  
**Fase 2 (Futuro):** Migrar código para usar `user_id`  
**Fase 3 (Opcional):** Eliminar campos redundantes si ya no se necesitan

---

## 🔧 Implementación

### Ejecutar la Migración

```bash
# Opción 1: Desde el contenedor
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet < backend/migrations/012_normalize_user_references.sql

# Opción 2: Desde PowerShell
Get-Content backend/migrations/012_normalize_user_references.sql | docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet
```

### Verificar Resultados

```sql
-- Ver estadísticas
SELECT 
    'cierres_mensuales_usuarios' as tabla,
    COUNT(*) as total,
    COUNT(user_id) as con_fk,
    COUNT(*) - COUNT(user_id) as sin_fk
FROM cierres_mensuales_usuarios
UNION ALL
SELECT 
    'contadores_usuario',
    COUNT(*),
    COUNT(user_id),
    COUNT(*) - COUNT(user_id)
FROM contadores_usuario;
```

---

## 📝 Guía para Desarrolladores

### Insertar Nuevos Registros

```python
# SIEMPRE incluir user_id cuando se crea un contador
contador = ContadorUsuario(
    printer_id=printer.id,
    user_id=user.id,  # ✅ NUEVO: FK normalizada
    codigo_usuario=user.codigo_de_usuario,  # Mantener para compatibilidad
    nombre_usuario=user.name,  # Mantener para compatibilidad
    total_paginas=100,
    # ... otros campos
)
```

### Consultas Optimizadas

```python
# ANTES (lento)
contadores = session.query(ContadorUsuario)\
    .join(User, User.codigo_de_usuario == ContadorUsuario.codigo_usuario)\
    .filter(User.name.like('%JUAN%'))\
    .all()

# DESPUÉS (rápido)
contadores = session.query(ContadorUsuario)\
    .join(User, User.id == ContadorUsuario.user_id)\
    .filter(User.name.like('%JUAN%'))\
    .all()
```

### Usar Vistas para Compatibilidad

```python
# Si necesitas datos combinados automáticamente
from sqlalchemy import text

result = session.execute(text("""
    SELECT * FROM v_contadores_usuario
    WHERE codigo_usuario_actual = :codigo
"""), {"codigo": "7104"})
```

---

## 📈 Métricas de Éxito

Después de la migración, verificar:

1. ✅ Todos los registros nuevos tienen `user_id` poblado
2. ✅ Las consultas JOIN son más rápidas (medir con EXPLAIN ANALYZE)
3. ✅ No hay errores de integridad referencial
4. ✅ El código existente sigue funcionando
5. ✅ Los reportes históricos se mantienen intactos

---

## 🔮 Próximos Pasos (Opcional)

### Fase 2: Migración Completa del Código

1. Actualizar todos los modelos SQLAlchemy para usar `user_id`
2. Actualizar todas las consultas para usar FK
3. Actualizar la lógica de inserción

### Fase 3: Limpieza Final (Solo si es necesario)

```sql
-- SOLO después de verificar que todo funciona con user_id
ALTER TABLE cierres_mensuales_usuarios 
DROP COLUMN codigo_usuario,
DROP COLUMN nombre_usuario;

ALTER TABLE contadores_usuario 
DROP COLUMN codigo_usuario,
DROP COLUMN nombre_usuario;
```

**⚠️ ADVERTENCIA:** No ejecutar Fase 3 hasta estar 100% seguro de que no se necesitan los campos antiguos.

---

## 📚 Referencias

- [PostgreSQL Foreign Keys](https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK)
- [Database Normalization](https://en.wikipedia.org/wiki/Database_normalization)
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/14/orm/relationships.html)

---

**Fecha de Análisis:** 2026-04-07  
**Versión de Migración:** 012  
**Estado:** Listo para implementar
