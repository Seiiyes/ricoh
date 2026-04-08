# Auditoría de Normalización de Base de Datos

## 📋 Resumen Ejecutivo

Auditoría completa de la base de datos `ricoh_fleet` para identificar:
- Tablas no utilizadas
- Campos redundantes
- Oportunidades de normalización adicional

**Fecha:** 2026-04-08

---

## 📊 Estado Actual de Tablas

### Tablas Activas (11)

| Tabla | Tamaño | Columnas | Registros | Estado |
|-------|--------|----------|-----------|--------|
| `contadores_usuario` | 15 MB | 30 | 21,356 | ✅ Activa |
| `cierres_mensuales_usuarios` | 3.4 MB | 19 | 6,866 | ✅ Activa |
| `users` | 384 KB | 21 | 440 | ✅ Activa |
| `cierres_mensuales` | 256 KB | 26 | ~300 | ✅ Activa |
| `printers` | 200 KB | 24 | 5 | ✅ Activa |
| `admin_sessions` | 160 KB | 10 | ~1000 | ✅ Activa |
| `contadores_impresora` | 160 KB | 21 | ~500 | ✅ Activa |
| `admin_audit_log` | 128 KB | 11 | ~500 | ✅ Activa |
| `admin_users` | 112 KB | 13 | ~10 | ✅ Activa |
| `empresas` | 96 KB | 14 | 2 | ✅ Activa |
| `user_printer_assignments` | 64 KB | 15 | ~100 | ✅ Activa |

### Tablas Eliminadas (3)

| Tabla | Razón |
|-------|-------|
| `_backup_contadores_usuario_campos` | ✅ Backup temporal de migración 013 |
| `_backup_cierres_usuarios_campos` | ✅ Backup temporal de migración 013 |
| `backup_cierres_mensuales_20260316` | ✅ Backup antiguo no necesario |

**Espacio liberado:** ~72 KB

---

## 🔍 Análisis de Redundancia por Tabla

### 1. Tabla `contadores_usuario` (15 MB, 30 columnas)

#### Campos Redundantes Identificados

**A. Campos Calculables**

```sql
-- REDUNDANTE: total_bn y total_color se pueden calcular
total_bn = copiadora_bn + impresora_bn + escaner_bn + fax_bn + revelado_negro
total_color = copiadora_mono_color + copiadora_dos_colores + copiadora_todo_color + 
              impresora_mono_color + impresora_dos_colores + impresora_color + 
              escaner_todo_color + revelado_color_ymc
```

**Impacto:**
- Ahorro: ~2 columnas × 4 bytes × 21,356 registros = ~171 KB
- Riesgo: BAJO - Se pueden calcular en queries o vistas
- Beneficio: Elimina inconsistencias si los valores no coinciden

**Recomendación:** ⚠️ EVALUAR
- Crear vista calculada para compatibilidad
- Eliminar columnas físicas en migración futura
- Verificar que no afecte performance de reportes

**B. Índices Duplicados**

```sql
-- DUPLICADOS
"idx_contadores_usuario_printer_id" btree (printer_id)
"ix_contadores_usuario_printer_id" btree (printer_id)

"idx_contadores_usuario_fecha_lectura" btree (fecha_lectura)
"ix_contadores_usuario_fecha_lectura" btree (fecha_lectura)
```

**Impacto:**
- Ahorro: ~50-100 KB por índice duplicado
- Riesgo: NINGUNO - Son completamente redundantes

**Recomendación:** ✅ ELIMINAR INMEDIATAMENTE

---

### 2. Tabla `printers` (200 KB, 24 columnas)

#### Campos Redundantes Identificados

**A. Capacidades Duplicadas**

```sql
-- REDUNDANTE: Información duplicada en capabilities_json
has_color               boolean
has_scanner             boolean
has_fax                 boolean

-- VS

capabilities_json       jsonb  -- Contiene la misma información
```

**Ejemplo de `capabilities_json`:**
```json
{
  "has_color": true,
  "has_scanner": true,
  "has_fax": false,
  "has_duplex": true,
  ...
}
```

**Impacto:**
- Ahorro: 3 columnas × 1 byte × 5 registros = ~15 bytes (mínimo)
- Riesgo: MEDIO - Requiere actualizar queries existentes
- Beneficio: Elimina inconsistencias, centraliza capacidades

**Recomendación:** ⚠️ EVALUAR
- Migrar queries para usar `capabilities_json`
- Crear índices GIN en campos JSON específicos
- Eliminar columnas booleanas en migración futura

**B. Índices Duplicados**

```sql
-- DUPLICADOS
"idx_printers_serial_number" btree (serial_number)
"ix_printers_serial_number" btree (serial_number)

"ix_printers_empresa_id" btree (empresa_id)
"idx_printers_empresa" btree (empresa_id)
```

**Recomendación:** ✅ ELIMINAR INMEDIATAMENTE

---

### 3. Tabla `users` (384 KB, 21 columnas)

#### Campos Analizados

**A. Funciones de Usuario (8 columnas booleanas)**

```sql
func_copier                boolean
func_copier_color          boolean
func_printer               boolean
func_printer_color         boolean
func_document_server       boolean
func_fax                   boolean
func_scanner               boolean
func_browser               boolean
```

**Análisis:**
- ¿Se pueden normalizar? SÍ - Podrían ser una tabla `user_functions`
- ¿Vale la pena? NO - Solo 440 usuarios, overhead de JOIN no justifica
- Estado: ✅ MANTENER COMO ESTÁ

**B. Campos SMB**

```sql
smb_server                 varchar(255)  -- Siempre el mismo valor?
smb_port                   integer       -- Siempre 21 (FTP) o 445 (SMB)?
smb_path                   varchar(500)  -- Único por usuario
```

**Análisis:**
```sql
-- Verificar si smb_server y smb_port son siempre iguales
SELECT smb_server, smb_port, COUNT(*) 
FROM users 
GROUP BY smb_server, smb_port;
```

**Recomendación:** 🔍 INVESTIGAR
- Si `smb_server` y `smb_port` son siempre iguales, normalizar a tabla `smb_config`
- Si varían, mantener como está

---

### 4. Tabla `cierres_mensuales` (256 KB, 26 columnas)

#### Campos Redundantes Identificados

**A. Campos de Fecha Duplicados**

```sql
-- Campos de período
fecha_inicio               date
fecha_fin                  date
anio                       integer  -- ← REDUNDANTE (se puede extraer de fecha_inicio)
mes                        integer  -- ← REDUNDANTE (se puede extraer de fecha_inicio)
```

**Impacto:**
- Ahorro: 2 columnas × 4 bytes × 300 registros = ~2.4 KB
- Riesgo: BAJO - Se pueden calcular con `EXTRACT(YEAR FROM fecha_inicio)`
- Beneficio: Elimina inconsistencias

**Recomendación:** ⚠️ EVALUAR
- Crear índices funcionales: `CREATE INDEX ON cierres_mensuales (EXTRACT(YEAR FROM fecha_inicio))`
- Eliminar columnas `anio` y `mes` en migración futura

**B. Campos Calculables**

```sql
-- REDUNDANTE: diferencia_* se puede calcular restando cierres
diferencia_total           integer
diferencia_copiadora       integer
diferencia_impresora       integer
diferencia_escaner         integer
diferencia_fax             integer
```

**Análisis:**
- ¿Se usan frecuentemente? SÍ - En reportes y comparaciones
- ¿Vale la pena eliminar? NO - Performance es más importante
- Estado: ✅ MANTENER COMO ESTÁ (optimización de lectura)

---

### 5. Tabla `cierres_mensuales_usuarios` (3.4 MB, 19 columnas)

#### Estado: ✅ BIEN NORMALIZADA

Después de la migración 013, esta tabla está correctamente normalizada:
- Solo `user_id` como referencia
- No hay campos redundantes
- Estructura óptima

---

### 6. Tabla `user_printer_assignments` (64 KB, 15 columnas)

#### Campos Analizados

**A. Funciones por Dispositivo (8 columnas booleanas)**

```sql
func_copier                boolean
func_copier_color          boolean
func_printer               boolean
func_printer_color         boolean
func_document_server       boolean
func_fax                   boolean
func_scanner               boolean
func_browser               boolean
```

**Análisis:**
- Duplican las funciones de `users`
- Pero permiten permisos diferentes por impresora
- Estado: ✅ MANTENER (necesario para permisos granulares)

---

## 📝 Recomendaciones Priorizadas

### Prioridad ALTA - Implementar Inmediatamente

#### 1. Eliminar Índices Duplicados

**Impacto:** Ahorro inmediato de ~200-300 KB, mejora de performance en escrituras

```sql
-- Tabla contadores_usuario
DROP INDEX IF EXISTS ix_contadores_usuario_printer_id;  -- Mantener idx_contadores_usuario_printer_id
DROP INDEX IF EXISTS ix_contadores_usuario_fecha_lectura;  -- Mantener idx_contadores_usuario_fecha_lectura

-- Tabla printers
DROP INDEX IF EXISTS ix_printers_serial_number;  -- Mantener idx_printers_serial_number
DROP INDEX IF EXISTS ix_printers_empresa_id;  -- Mantener idx_printers_empresa (más descriptivo)
```

**Archivo:** `backend/migrations/014_remove_duplicate_indexes.sql`

---

### Prioridad MEDIA - Evaluar en 1-2 Meses

#### 2. Investigar Valores de SMB en `users`

**Objetivo:** Determinar si `smb_server` y `smb_port` se pueden normalizar

```sql
-- Query de análisis
SELECT 
    smb_server,
    smb_port,
    COUNT(*) as usuarios,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM users) * 100, 2) as porcentaje
FROM users
GROUP BY smb_server, smb_port
ORDER BY usuarios DESC;
```

**Si >90% usan los mismos valores:**
- Crear tabla `smb_servers` con configuraciones comunes
- Agregar `smb_server_id` FK a `users`
- Mantener `smb_path` (único por usuario)

---

#### 3. Eliminar Campos Booleanos de Capacidades en `printers`

**Objetivo:** Usar solo `capabilities_json`

**Pasos:**
1. Migrar queries para usar `capabilities_json->>'has_color'`
2. Crear índices GIN: `CREATE INDEX ON printers USING GIN (capabilities_json jsonb_path_ops);`
3. Verificar performance
4. Eliminar columnas `has_color`, `has_scanner`, `has_fax`

**Beneficio:** Centralización de capacidades, más flexible para agregar nuevas

---

### Prioridad BAJA - Considerar en 3-6 Meses

#### 4. Eliminar Campos Calculables en `contadores_usuario`

**Objetivo:** Eliminar `total_bn` y `total_color`

**Pasos:**
1. Crear vista calculada:
```sql
CREATE VIEW v_contadores_usuario_con_totales AS
SELECT 
    cu.*,
    (cu.copiadora_bn + cu.impresora_bn + cu.escaner_bn + cu.fax_bn + cu.revelado_negro) as total_bn,
    (cu.copiadora_mono_color + cu.copiadora_dos_colores + cu.copiadora_todo_color + 
     cu.impresora_mono_color + cu.impresora_dos_colores + cu.impresora_color + 
     cu.escaner_todo_color + cu.revelado_color_ymc) as total_color
FROM contadores_usuario cu;
```

2. Migrar queries para usar vista
3. Verificar performance (puede ser más lento)
4. Si performance es aceptable, eliminar columnas físicas

**Beneficio:** Elimina inconsistencias, ahorra ~171 KB

---

#### 5. Eliminar Campos `anio` y `mes` en `cierres_mensuales`

**Objetivo:** Usar solo `fecha_inicio` y `fecha_fin`

**Pasos:**
1. Crear índices funcionales:
```sql
CREATE INDEX idx_cierres_anio ON cierres_mensuales (EXTRACT(YEAR FROM fecha_inicio));
CREATE INDEX idx_cierres_mes ON cierres_mensuales (EXTRACT(MONTH FROM fecha_inicio));
```

2. Migrar queries:
```sql
-- ANTES
WHERE anio = 2026 AND mes = 4

-- DESPUÉS
WHERE EXTRACT(YEAR FROM fecha_inicio) = 2026 
  AND EXTRACT(MONTH FROM fecha_inicio) = 4
```

3. Verificar performance
4. Eliminar columnas `anio` y `mes`

**Beneficio:** Elimina redundancia, ahorra ~2.4 KB

---

## 📊 Resumen de Ahorros Potenciales

| Acción | Prioridad | Ahorro Espacio | Ahorro Mantenimiento | Riesgo |
|--------|-----------|----------------|---------------------|--------|
| Eliminar índices duplicados | ALTA | ~300 KB | Alto | Ninguno |
| Normalizar SMB config | MEDIA | ~50 KB | Medio | Bajo |
| Eliminar capacidades booleanas | MEDIA | ~15 bytes | Alto | Medio |
| Eliminar total_bn/total_color | BAJA | ~171 KB | Medio | Medio |
| Eliminar anio/mes | BAJA | ~2.4 KB | Bajo | Bajo |
| **TOTAL** | | **~523 KB** | | |

---

## 🚀 Plan de Implementación

### Fase 1: Limpieza Inmediata (Esta Semana)

- [x] Eliminar tablas de backup temporales
- [ ] Eliminar índices duplicados (migración 014)
- [ ] Documentar cambios

### Fase 2: Investigación (1-2 Meses)

- [ ] Analizar valores de `smb_server` y `smb_port`
- [ ] Medir performance de queries con `capabilities_json`
- [ ] Evaluar impacto de eliminar campos calculables

### Fase 3: Normalización Adicional (3-6 Meses)

- [ ] Implementar cambios de prioridad MEDIA
- [ ] Monitorear performance
- [ ] Ajustar según resultados

### Fase 4: Optimización Final (6-12 Meses)

- [ ] Implementar cambios de prioridad BAJA
- [ ] Auditoría completa de performance
- [ ] Documentación final

---

## 📞 Comandos Útiles

### Verificar Índices Duplicados

```bash
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
"
```

### Analizar Tamaño de Tablas

```bash
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size('public.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size('public.'||tablename) - pg_relation_size('public.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.'||tablename) DESC;
"
```

### Verificar Valores de SMB

```bash
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    smb_server,
    smb_port,
    COUNT(*) as usuarios,
    ROUND(COUNT(*)::numeric / (SELECT COUNT(*) FROM users) * 100, 2) as porcentaje
FROM users
GROUP BY smb_server, smb_port
ORDER BY usuarios DESC;
"
```

---

**Fecha de creación:** 2026-04-08  
**Última actualización:** 2026-04-08  
**Próxima revisión:** 2026-06-08  
**Responsable:** Equipo de desarrollo
