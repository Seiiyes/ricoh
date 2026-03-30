# Migración 005: Tablas de Contadores

**Fecha:** 2 de Marzo de 2026  
**Estado:** ✅ Lista para aplicar  
**Archivo SQL:** `backend/migrations/005_add_contador_tables.sql`  
**Script Python:** `backend/apply_migration_005.py`

---

## 📋 Resumen

Esta migración agrega las tablas necesarias para almacenar los contadores de las impresoras Ricoh, tanto contadores totales como contadores por usuario.

---

## 🎯 Objetivos

1. Crear tabla `contadores_impresora` para almacenar contadores totales
2. Crear tabla `contadores_usuario` para almacenar contadores por usuario
3. Crear tabla `cierres_mensuales` para almacenar snapshots mensuales
4. Agregar campos de configuración a la tabla `printers`
5. Configurar impresora ID 6 para usar contador ecológico

---

## 📊 Cambios en la Base de Datos

### 1. Tabla `printers` - Nuevos Campos

```sql
ALTER TABLE printers 
ADD COLUMN tiene_contador_usuario BOOLEAN DEFAULT TRUE NOT NULL;

ALTER TABLE printers 
ADD COLUMN usar_contador_ecologico BOOLEAN DEFAULT FALSE NOT NULL;
```

**Campos agregados:**
- `tiene_contador_usuario`: Indica si la impresora tiene `getUserCounter.cgi` disponible
- `usar_contador_ecologico`: Indica si se debe usar `getEcoCounter.cgi` para usuarios

**Configuración especial:**
- Impresora ID 6 (192.168.91.253 - B/N): `tiene_contador_usuario = FALSE`, `usar_contador_ecologico = TRUE`

---

### 2. Tabla `contadores_impresora`

Almacena los contadores totales de cada impresora (obtenidos de `getUnificationCounter.cgi`).

**Campos principales:**
- `printer_id`: Referencia a la impresora
- `total`: Contador total de páginas
- Contadores por función:
  - Copiadora (B/N, Color, Color personalizado, Dos colores)
  - Impresora (B/N, Color, Color personalizado, Dos colores)
  - Fax (B/N)
  - Enviar/TX Total (B/N, Color)
  - Transmisión por fax (Total)
  - Envío por escáner (B/N, Color)
  - Otras funciones (A3/DLT, Dúplex)
- `fecha_lectura`: Timestamp de cuándo se leyó el contador
- `created_at`: Timestamp de creación del registro

**Índices:**
- `idx_contadores_impresora_printer_id` en `printer_id`
- `idx_contadores_impresora_fecha_lectura` en `fecha_lectura`

---

### 3. Tabla `contadores_usuario`

Almacena los contadores individuales por usuario (obtenidos de `getUserCounter.cgi` o `getEcoCounter.cgi`).

**Campos principales:**
- `printer_id`: Referencia a la impresora
- `codigo_usuario`: Código del usuario (8 caracteres)
- `nombre_usuario`: Nombre del usuario
- Totales:
  - `total_paginas`: Total de páginas
  - `total_bn`: Total B/N
  - `total_color`: Total color
- Contadores por función:
  - Copiadora (B/N, Mono color, Dos colores, Todo color)
  - Impresora (B/N, Mono color, Dos colores, Color)
  - Escáner (B/N, Todo color)
  - Fax (B/N, Páginas transmitidas)
  - Revelado (Negro, Color YMC)
- Métricas ecológicas (solo para `getEcoCounter.cgi`):
  - `eco_uso_2_caras`
  - `eco_uso_combinar`
  - `eco_reduccion_papel`
- `tipo_contador`: "usuario" o "ecologico"
- `fecha_lectura`: Timestamp de cuándo se leyó el contador
- `created_at`: Timestamp de creación del registro

**Índices:**
- `idx_contadores_usuario_printer_id` en `printer_id`
- `idx_contadores_usuario_codigo` en `codigo_usuario`
- `idx_contadores_usuario_fecha_lectura` en `fecha_lectura`

---

### 4. Tabla `cierres_mensuales`

Almacena snapshots mensuales de contadores para comparación mes a mes.

**Campos principales:**
- `printer_id`: Referencia a la impresora
- Período:
  - `anio`: Año del cierre
  - `mes`: Mes del cierre (1-12)
- Contadores totales al cierre:
  - `total_paginas`
  - `total_copiadora`
  - `total_impresora`
  - `total_escaner`
  - `total_fax`
- Diferencias con mes anterior:
  - `diferencia_total`
  - `diferencia_copiadora`
  - `diferencia_impresora`
  - `diferencia_escaner`
  - `diferencia_fax`
- Metadata:
  - `fecha_cierre`: Timestamp del cierre
  - `cerrado_por`: Usuario que realizó el cierre
  - `notas`: Notas adicionales
  - `created_at`: Timestamp de creación

**Constraints:**
- `UNIQUE(printer_id, anio, mes)`: Solo un cierre por impresora por mes

**Índices:**
- `idx_cierres_mensuales_printer_id` en `printer_id`
- `idx_cierres_mensuales_anio` en `anio`
- `idx_cierres_mensuales_mes` en `mes`

---

## 🚀 Cómo Aplicar la Migración

### Opción 1: Script Batch (Windows)

```bash
cd backend
run-migration-005.bat
```

### Opción 2: Python Directo

```bash
cd backend
python apply_migration_005.py
```

### Opción 3: SQL Directo (psql)

```bash
psql -h localhost -U ricoh_user -d ricoh_db -f migrations/005_add_contador_tables.sql
```

---

## ✅ Verificación Post-Migración

Después de aplicar la migración, verificar:

### 1. Tablas Creadas

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('contadores_impresora', 'contadores_usuario', 'cierres_mensuales')
ORDER BY table_name;
```

Debe retornar 3 tablas.

### 2. Campos Agregados a `printers`

```sql
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'printers' 
AND column_name IN ('tiene_contador_usuario', 'usar_contador_ecologico')
ORDER BY column_name;
```

Debe retornar 2 campos.

### 3. Configuración de Impresora ID 6

```sql
SELECT id, hostname, ip_address, tiene_contador_usuario, usar_contador_ecologico
FROM printers
WHERE id = 6;
```

Debe mostrar:
- `tiene_contador_usuario = FALSE`
- `usar_contador_ecologico = TRUE`

---

## 📊 Estructura de Datos

### Ejemplo: Contador de Impresora

```json
{
  "printer_id": 4,
  "total": 372407,
  "copiadora_bn": 150000,
  "copiadora_color": 50000,
  "impresora_bn": 100000,
  "impresora_color": 50000,
  "escaner_bn": 20000,
  "escaner_color": 2407,
  "fecha_lectura": "2026-03-02T10:30:00Z"
}
```

### Ejemplo: Contador de Usuario

```json
{
  "printer_id": 4,
  "codigo_usuario": "00000001",
  "nombre_usuario": "Juan Pérez",
  "total_paginas": 5000,
  "total_bn": 4000,
  "total_color": 1000,
  "copiadora_bn": 2000,
  "impresora_bn": 2000,
  "escaner_bn": 500,
  "tipo_contador": "usuario",
  "fecha_lectura": "2026-03-02T10:30:00Z"
}
```

### Ejemplo: Cierre Mensual

```json
{
  "printer_id": 4,
  "anio": 2026,
  "mes": 2,
  "total_paginas": 372407,
  "total_copiadora": 200000,
  "total_impresora": 150000,
  "diferencia_total": 15000,
  "diferencia_copiadora": 8000,
  "diferencia_impresora": 7000,
  "fecha_cierre": "2026-02-28T23:59:59Z",
  "cerrado_por": "admin"
}
```

---

## 🔄 Rollback (Revertir Migración)

Si necesitas revertir la migración:

```sql
-- Eliminar tablas
DROP TABLE IF EXISTS cierres_mensuales;
DROP TABLE IF EXISTS contadores_usuario;
DROP TABLE IF EXISTS contadores_impresora;

-- Eliminar campos de printers
ALTER TABLE printers DROP COLUMN IF EXISTS tiene_contador_usuario;
ALTER TABLE printers DROP COLUMN IF EXISTS usar_contador_ecologico;
```

---

## 📝 Notas Importantes

1. **Backup:** Siempre hacer backup antes de aplicar migraciones
2. **Impresora ID 6:** Es la única configurada para usar contador ecológico
3. **Histórico:** Las tablas almacenan histórico completo (no se borran registros antiguos)
4. **Índices:** Los índices mejoran el rendimiento de consultas por fecha y printer_id
5. **Constraints:** El constraint UNIQUE en `cierres_mensuales` previene duplicados

---

## 🎯 Próximos Pasos

Después de aplicar esta migración:

1. **Fase 3:** Crear servicio de lectura de contadores
   - Implementar `backend/services/counter_service.py`
   - Lógica para detectar tipo de contador disponible
   - Guardar datos en las nuevas tablas

2. **Fase 4:** Crear endpoints API
   - `GET /api/counters/printer/{printer_id}` - Obtener contadores de impresora
   - `GET /api/counters/user/{printer_id}` - Obtener contadores por usuario
   - `POST /api/counters/close-month` - Realizar cierre mensual
   - `GET /api/counters/monthly/{printer_id}` - Obtener histórico mensual

3. **Fase 5:** Crear interfaz frontend
   - Dashboard de contadores
   - Vista de contadores por usuario
   - Vista de cierres mensuales
   - Gráficos de tendencias

---

## 📚 Referencias

- **Parsers implementados:**
  - `backend/parsear_contadores.py` - Contador unificado
  - `backend/parsear_contadores_usuario.py` - Contador por usuario
  - `backend/parsear_contador_ecologico.py` - Contador ecológico

- **Documentación relacionada:**
  - `docs/RESULTADOS_PRUEBA_5_IMPRESORAS.md` - Resultados de pruebas
  - `docs/FASE_1_COMPLETADA_FINAL.md` - Resumen de Fase 1
  - `docs/MODULO_CONTADORES_DESARROLLO.md` - Documentación técnica

---

**Última Actualización:** 2 de Marzo de 2026  
**Autor:** Kiro AI Assistant  
**Proyecto:** Sistema de Gestión de Impresoras Ricoh  
**Estado:** ✅ LISTA PARA APLICAR
