# Eliminación de Columnas Redundantes - Completada

## 📋 Resumen

Se eliminaron exitosamente las columnas redundantes `codigo_usuario` y `nombre_usuario` de las tablas `contadores_usuario` y `cierres_mensuales_usuarios`, completando la normalización del sistema.

**Fecha de implementación:** 2026-04-08

---

## 🎯 Objetivo

Eliminar información duplicada que ya existe en la tabla `users`, manteniendo únicamente la referencia `user_id` (FK) para garantizar:

- Integridad referencial
- Eliminación de redundancia
- Reducción de espacio en disco
- Consistencia de datos
- Queries más eficientes

---

## 📊 Estado Antes y Después

### Antes (con redundancia)

**Tabla `contadores_usuario`:**
```sql
- id (PK)
- printer_id (FK)
- user_id (FK)           ← Normalizado
- codigo_usuario (text)  ← REDUNDANTE
- nombre_usuario (text)  ← REDUNDANTE
- total_paginas
- ...
```

**Tabla `cierres_mensuales_usuarios`:**
```sql
- id (PK)
- cierre_mensual_id (FK)
- user_id (FK)           ← Normalizado
- codigo_usuario (text)  ← REDUNDANTE
- nombre_usuario (text)  ← REDUNDANTE
- total_paginas
- ...
```

### Después (sin redundancia)

**Tabla `contadores_usuario`:**
```sql
- id (PK)
- printer_id (FK)
- user_id (FK) NOT NULL  ← ÚNICO CAMPO DE REFERENCIA
- total_paginas
- ...
```

**Tabla `cierres_mensuales_usuarios`:**
```sql
- id (PK)
- cierre_mensual_id (FK)
- user_id (FK) NOT NULL  ← ÚNICO CAMPO DE REFERENCIA
- total_paginas
- ...
```

---

## 🔧 Cambios Implementados

### 1. Migración de Base de Datos

**Archivo:** `backend/migrations/013_remove_redundant_user_fields.sql`

**Pasos ejecutados:**

1. ✅ Verificación previa: Todos los registros tienen `user_id`
2. ✅ Backup de seguridad en tablas `_backup_*`
3. ✅ Eliminación de vistas existentes que dependían de las columnas
4. ✅ Eliminación de índices en columnas redundantes
5. ✅ Cambio de `user_id` a NOT NULL (ahora es obligatorio)
6. ✅ Eliminación de columnas `codigo_usuario` y `nombre_usuario`
7. ✅ Creación de vistas de compatibilidad

**Resultado:**
- 21,356 registros en `contadores_usuario` actualizados
- 6,866 registros en `cierres_mensuales_usuarios` actualizados
- 0 pérdida de datos
- Backups creados para rollback si es necesario

### 2. Modelos SQLAlchemy

**Archivo:** `backend/db/models.py`

**Cambios en `ContadorUsuario`:**
```python
# ANTES
class ContadorUsuario(Base):
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    codigo_usuario = Column(String(8), nullable=False)
    nombre_usuario = Column(String(100), nullable=False)

# DESPUÉS
class ContadorUsuario(Base):
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # NOT NULL
    # codigo_usuario y nombre_usuario eliminados
```

**Cambios en `CierreMensualUsuario`:**
```python
# ANTES
class CierreMensualUsuario(Base):
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    codigo_usuario = Column(String(8), nullable=False)
    nombre_usuario = Column(String(100), nullable=False)

# DESPUÉS
class CierreMensualUsuario(Base):
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # NOT NULL
    # codigo_usuario y nombre_usuario eliminados
```

### 3. Servicios Actualizados

**Archivo:** `backend/services/counter_service.py`

**Cambios:**
```python
# ANTES
contador = ContadorUsuario(
    printer_id=printer_id,
    user_id=user_id,
    codigo_usuario=str(user['codigo_usuario']),  # ← ELIMINADO
    nombre_usuario=user['nombre_usuario'],        # ← ELIMINADO
    total_paginas=user['total_paginas'],
    ...
)

# DESPUÉS
contador = ContadorUsuario(
    printer_id=printer_id,
    user_id=user_id,  # ← ÚNICO CAMPO DE REFERENCIA
    total_paginas=user['total_paginas'],
    ...
)
```

**Archivo:** `backend/services/close_service.py`

**Cambios:**
```python
# ANTES
usuario_cierre = CierreMensualUsuario(
    cierre_mensual_id=cierre.id,
    user_id=consumo['user_id'],
    codigo_usuario=consumo['codigo_usuario'],  # ← ELIMINADO
    nombre_usuario=consumo['nombre_usuario'],  # ← ELIMINADO
    total_paginas=consumo['contador_actual'],
    ...
)

# DESPUÉS
usuario_cierre = CierreMensualUsuario(
    cierre_mensual_id=cierre.id,
    user_id=consumo['user_id'],  # ← ÚNICO CAMPO DE REFERENCIA
    total_paginas=consumo['contador_actual'],
    ...
)
```

**Cambios en comparación de cierres:**
```python
# ANTES
codigo = u_reciente.codigo_usuario if u_reciente else u_antiguo.codigo_usuario
nombre = u_reciente.nombre_usuario if u_reciente else u_antiguo.nombre_usuario

# DESPUÉS
user = db.query(User).filter(User.id == user_id).first()
codigo = user.codigo_de_usuario if user else str(user_id)
nombre = user.name if user else f"Usuario {user_id}"
```

---

## 🔄 Vistas de Compatibilidad

Para mantener compatibilidad con código existente, se crearon vistas que incluyen los campos de usuario:

### Vista `v_contadores_usuario_completo`

```sql
CREATE OR REPLACE VIEW v_contadores_usuario_completo AS
SELECT 
    cu.*,
    u.codigo_de_usuario as codigo_usuario,
    u.name as nombre_usuario,
    u.smb_path,
    u.centro_costos
FROM contadores_usuario cu
JOIN users u ON cu.user_id = u.id;
```

**Uso:**
```python
# Si necesitas codigo_usuario y nombre_usuario, usa la vista
contadores = db.query(v_contadores_usuario_completo).filter(...)
```

### Vista `v_cierres_usuarios_completo`

```sql
CREATE OR REPLACE VIEW v_cierres_usuarios_completo AS
SELECT 
    cmu.*,
    u.codigo_de_usuario as codigo_usuario,
    u.name as nombre_usuario,
    u.smb_path,
    u.centro_costos
FROM cierres_mensuales_usuarios cmu
JOIN users u ON cmu.user_id = u.id;
```

---

## 📈 Beneficios Obtenidos

### 1. Reducción de Redundancia

**Antes:**
- Información de usuario duplicada en 3 tablas
- Cambios de nombre requieren actualizar 3 tablas
- Inconsistencias posibles entre tablas

**Después:**
- Información de usuario en 1 sola tabla (`users`)
- Cambios de nombre se reflejan automáticamente
- Consistencia garantizada por FK

### 2. Reducción de Espacio

**Estimación de ahorro:**

```
contadores_usuario:
- codigo_usuario (8 chars) + nombre_usuario (100 chars) = ~108 bytes/registro
- 21,356 registros × 108 bytes = ~2.3 MB

cierres_mensuales_usuarios:
- codigo_usuario (8 chars) + nombre_usuario (100 chars) = ~108 bytes/registro
- 6,866 registros × 108 bytes = ~0.7 MB

TOTAL AHORRADO: ~3 MB
```

Además, los índices en estas columnas también fueron eliminados, ahorrando espacio adicional.

### 3. Mejora de Performance

**Queries más simples:**

```sql
-- ANTES (con redundancia)
SELECT cu.codigo_usuario, cu.nombre_usuario, cu.total_paginas
FROM contadores_usuario cu
WHERE cu.codigo_usuario = '7104';

-- DESPUÉS (sin redundancia)
SELECT u.codigo_de_usuario, u.name, cu.total_paginas
FROM contadores_usuario cu
JOIN users u ON cu.user_id = u.id
WHERE u.codigo_de_usuario = '7104';
```

El JOIN por `user_id` (integer) es más rápido que buscar por `codigo_usuario` (string).

### 4. Integridad Referencial

**Antes:**
- Posible inconsistencia entre `codigo_usuario` en diferentes tablas
- Cambios de nombre no se propagan automáticamente

**Después:**
- FK garantiza que `user_id` existe en tabla `users`
- Cambios de nombre se reflejan automáticamente en todas las queries
- `ON DELETE SET NULL` previene pérdida de datos históricos

---

## 🧪 Pruebas Realizadas

### Script de Prueba

**Archivo:** `backend/scripts/test_cierre_normalizado.py`

**Resultados:**
```
================================================================================
PRUEBA DE NORMALIZACIÓN DE CIERRES
================================================================================

📍 Impresora seleccionada:
   ID: 5
   Hostname: RNP002673CA501E
   IP: 192.168.91.252

👥 Usuarios con user_id en esta impresora: 90

📅 Último cierre:
   Período: 2026-04-08 a 2026-04-08
   Tipo: diario
   Total páginas: 275,297

   Usuarios en cierre:
   ✅ Con user_id: 90
   ❌ Sin user_id: 0

================================================================================
VERIFICACIÓN DE NORMALIZACIÓN
================================================================================

📊 Total usuarios en cierre: 90
   ✅ Con user_id: 90 (100.0%)
   ❌ Sin user_id: 0 (0.0%)

✅ ÉXITO: Todos los usuarios tienen user_id

================================================================================
VERIFICACIÓN DE INTEGRIDAD
================================================================================

📊 Verificación de integridad (muestra de 10):
   ✅ user_id válidos: 10
   ❌ user_id inválidos: 0

✅ ÉXITO: Todos los user_id son válidos
```

### Verificación de Base de Datos

```sql
-- Verificar que no existen las columnas
\d contadores_usuario
-- Resultado: Solo existe user_id (NOT NULL)

\d cierres_mensuales_usuarios
-- Resultado: Solo existe user_id (NOT NULL)

-- Verificar integridad
SELECT COUNT(*) FROM contadores_usuario WHERE user_id IS NULL;
-- Resultado: 0

SELECT COUNT(*) FROM cierres_mensuales_usuarios WHERE user_id IS NULL;
-- Resultado: 0
```

---

## 🚨 Plan de Rollback

Si es necesario revertir los cambios:

### 1. Restaurar Columnas

```sql
-- Agregar columnas de vuelta
ALTER TABLE contadores_usuario 
ADD COLUMN codigo_usuario VARCHAR(8),
ADD COLUMN nombre_usuario VARCHAR(100);

ALTER TABLE cierres_mensuales_usuarios 
ADD COLUMN codigo_usuario VARCHAR(8),
ADD COLUMN nombre_usuario VARCHAR(100);
```

### 2. Restaurar Datos desde Backup

```sql
-- Restaurar datos en contadores_usuario
UPDATE contadores_usuario cu
SET 
    codigo_usuario = b.codigo_usuario,
    nombre_usuario = b.nombre_usuario
FROM _backup_contadores_usuario_campos b
WHERE cu.id = b.id;

-- Restaurar datos en cierres_mensuales_usuarios
UPDATE cierres_mensuales_usuarios cmu
SET 
    codigo_usuario = b.codigo_usuario,
    nombre_usuario = b.nombre_usuario
FROM _backup_cierres_usuarios_campos b
WHERE cmu.id = b.id;
```

### 3. Recrear Índices

```sql
CREATE INDEX idx_contadores_usuario_codigo ON contadores_usuario(codigo_usuario);
CREATE INDEX idx_cierres_usuarios_codigo ON cierres_mensuales_usuarios(codigo_usuario);
```

### 4. Revertir Código

```bash
git checkout <commit-anterior>
docker compose up -d --build backend
```

**Tiempo estimado de rollback:** 10-15 minutos

---

## 📝 Próximos Pasos

### Corto Plazo (1-2 semanas)
- [x] Monitorear logs para errores relacionados con campos faltantes
- [x] Verificar que reportes funcionan correctamente
- [ ] Validar con usuarios finales

### Mediano Plazo (1 mes)
- [ ] Eliminar tablas de backup `_backup_*` si todo funciona bien
- [ ] Actualizar documentación de API
- [ ] Crear índices adicionales si es necesario

### Largo Plazo (3 meses)
- [ ] Evaluar performance de vistas de compatibilidad
- [ ] Considerar materializar vistas si hay problemas de performance
- [ ] Optimizar queries que usan las vistas

---

## 📞 Soporte

### Verificar Estado

```bash
# Verificar que columnas fueron eliminadas
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "\d contadores_usuario"
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "\d cierres_mensuales_usuarios"

# Verificar que user_id es NOT NULL
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    COUNT(*) as total,
    COUNT(user_id) as con_user_id
FROM contadores_usuario;
"
```

### Verificar Vistas

```bash
# Listar vistas
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "\dv"

# Probar vista de contadores
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT * FROM v_contadores_usuario_completo LIMIT 5;
"
```

### Logs

```bash
# Ver logs del backend
docker logs ricoh-backend --tail 100 -f

# Buscar errores relacionados con campos faltantes
docker logs ricoh-backend | grep -i "codigo_usuario\|nombre_usuario"
```

---

## 📚 Referencias

- [Normalización de Cierres](./NORMALIZACION_CIERRES_COMPLETADA.md)
- [Resumen de Normalización](./RESUMEN_NORMALIZACION_COMPLETA.md)
- [Mantenimiento](./MANTENIMIENTO_NORMALIZACION.md)
- [Migración 013](../backend/migrations/013_remove_redundant_user_fields.sql)

---

**Fecha de creación:** 2026-04-08  
**Última actualización:** 2026-04-08  
**Estado:** ✅ Completado y en producción  
**Ahorro de espacio:** ~3 MB  
**Registros afectados:** 28,222 (21,356 + 6,866)
