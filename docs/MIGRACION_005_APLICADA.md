# ✅ Migración 005 Aplicada Exitosamente

**Fecha de Aplicación:** 2 de Marzo de 2026  
**Estado:** ✅ COMPLETADA  
**Base de Datos:** ricoh_fleet (PostgreSQL en Docker)

---

## 📊 Resumen de la Aplicación

La migración 005 se aplicó exitosamente a la base de datos `ricoh_fleet`.

---

## ✅ Verificación de Tablas Creadas

### Tablas de Contadores

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'contadores%' OR table_name LIKE 'cierres%'
ORDER BY table_name;
```

**Resultado:**
- ✅ `cierres_mensuales` - Creada
- ✅ `contadores_impresora` - Creada
- ✅ `contadores_usuario` - Creada

---

## ✅ Verificación de Campos en `printers`

```sql
SELECT id, hostname, tiene_contador_usuario, usar_contador_ecologico 
FROM printers 
ORDER BY id;
```

**Resultado:**

| ID | Hostname | tiene_contador_usuario | usar_contador_ecologico |
|----|----------|------------------------|-------------------------|
| 3 | RNP0026737FFBB8 | ✅ TRUE | ❌ FALSE |
| 4 | RNP00267391F283 | ✅ TRUE | ❌ FALSE |
| 5 | RNP002673CA501E | ✅ TRUE | ❌ FALSE |
| 6 | RNP002673721B98 | ❌ FALSE | ✅ TRUE |
| 7 | RNP002673C01D88 | ✅ TRUE | ❌ FALSE |

**Nota:** La impresora ID 6 (192.168.91.253) está correctamente configurada para usar contador ecológico porque es un modelo B/N sin `getUserCounter.cgi`.

---

## 📋 Estructura de las Tablas

### Tabla `contadores_impresora`

```sql
\d contadores_impresora
```

**Campos principales:**
- `id` (PK)
- `printer_id` (FK → printers.id)
- `total` - Contador total de páginas
- Contadores por función (18 campos):
  - Copiadora (4 campos)
  - Impresora (4 campos)
  - Fax (1 campo)
  - Enviar/TX Total (2 campos)
  - Transmisión por fax (1 campo)
  - Envío por escáner (2 campos)
  - Otras funciones (2 campos)
- `fecha_lectura` - Timestamp de lectura
- `created_at` - Timestamp de creación

**Índices:**
- `idx_contadores_impresora_printer_id`
- `idx_contadores_impresora_fecha_lectura`

---

### Tabla `contadores_usuario`

```sql
\d contadores_usuario
```

**Campos principales:**
- `id` (PK)
- `printer_id` (FK → printers.id)
- `codigo_usuario` - Código del usuario
- `nombre_usuario` - Nombre del usuario
- Totales (3 campos)
- Contadores por función (18 campos):
  - Copiadora (4 campos)
  - Impresora (4 campos)
  - Escáner (2 campos)
  - Fax (2 campos)
  - Revelado (2 campos)
- Métricas ecológicas (3 campos)
- `tipo_contador` - "usuario" o "ecologico"
- `fecha_lectura` - Timestamp de lectura
- `created_at` - Timestamp de creación

**Índices:**
- `idx_contadores_usuario_printer_id`
- `idx_contadores_usuario_codigo`
- `idx_contadores_usuario_fecha_lectura`

---

### Tabla `cierres_mensuales`

```sql
\d cierres_mensuales
```

**Campos principales:**
- `id` (PK)
- `printer_id` (FK → printers.id)
- `anio` - Año del cierre
- `mes` - Mes del cierre (1-12)
- Contadores totales (5 campos)
- Diferencias con mes anterior (5 campos)
- `fecha_cierre` - Timestamp del cierre
- `cerrado_por` - Usuario que realizó el cierre
- `notas` - Notas adicionales
- `created_at` - Timestamp de creación

**Constraints:**
- `UNIQUE(printer_id, anio, mes)` - Solo un cierre por impresora por mes

**Índices:**
- `idx_cierres_mensuales_printer_id`
- `idx_cierres_mensuales_anio`
- `idx_cierres_mensuales_mes`

---

## 🎯 Próximos Pasos

### Fase 3: Servicio de Lectura de Contadores

Ahora que las tablas están creadas, el siguiente paso es implementar el servicio de lectura de contadores.

**Archivo a crear:** `backend/services/counter_service.py`

**Funcionalidades a implementar:**

1. **Lectura de Contadores Totales**
   ```python
   def read_printer_counters(printer_id: int) -> ContadorImpresora:
       """
       Lee contadores totales de una impresora y los guarda en la DB
       Usa parsear_contadores.py
       """
   ```

2. **Lectura de Contadores por Usuario**
   ```python
   def read_user_counters(printer_id: int) -> List[ContadorUsuario]:
       """
       Lee contadores por usuario y los guarda en la DB
       Detecta automáticamente si usar getUserCounter o getEcoCounter
       según los campos tiene_contador_usuario y usar_contador_ecologico
       """
   ```

3. **Cierre Mensual**
   ```python
   def close_month(printer_id: int, year: int, month: int) -> CierreMensual:
       """
       Realiza cierre mensual:
       - Obtiene contadores actuales
       - Compara con mes anterior
       - Calcula diferencias
       - Guarda en cierres_mensuales
       """
   ```

4. **Lectura Masiva**
   ```python
   def read_all_printers() -> Dict[int, Dict]:
       """
       Lee contadores de todas las impresoras activas
       Útil para lectura programada (cron job)
       """
   ```

---

## 📝 Comandos Útiles

### Consultar Contadores de una Impresora

```sql
-- Último contador registrado
SELECT * FROM contadores_impresora 
WHERE printer_id = 4 
ORDER BY fecha_lectura DESC 
LIMIT 1;
```

### Consultar Contadores de Usuarios

```sql
-- Top 10 usuarios con más impresiones
SELECT codigo_usuario, nombre_usuario, total_paginas
FROM contadores_usuario
WHERE printer_id = 4
ORDER BY total_paginas DESC
LIMIT 10;
```

### Consultar Cierres Mensuales

```sql
-- Cierres del año 2026
SELECT printer_id, anio, mes, total_paginas, diferencia_total
FROM cierres_mensuales
WHERE anio = 2026
ORDER BY printer_id, mes;
```

### Histórico de Contadores

```sql
-- Evolución de contadores en el tiempo
SELECT 
    DATE(fecha_lectura) as fecha,
    total,
    impresora_bn + impresora_color as total_impresora,
    copiadora_bn + copiadora_color as total_copiadora
FROM contadores_impresora
WHERE printer_id = 4
ORDER BY fecha_lectura;
```

---

## 🔄 Rollback (Si es Necesario)

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

**⚠️ ADVERTENCIA:** Esto eliminará todos los datos de contadores almacenados.

---

## 📚 Referencias

### Documentación

- `docs/MIGRACION_005_TABLAS_CONTADORES.md` - Documentación completa de la migración
- `docs/FASE_2_COMPLETADA.md` - Resumen de la Fase 2
- `docs/RESULTADOS_PRUEBA_5_IMPRESORAS.md` - Resultados de pruebas

### Scripts

- `backend/apply_migration_005.py` - Script de aplicación
- `backend/migrations/005_add_contador_tables.sql` - SQL de migración

### Parsers

- `backend/parsear_contadores.py` - Contador unificado
- `backend/parsear_contadores_usuario.py` - Contador por usuario
- `backend/parsear_contador_ecologico.py` - Contador ecológico

---

## ✅ Checklist de Verificación

- [x] Migración aplicada sin errores
- [x] Tabla `contadores_impresora` creada
- [x] Tabla `contadores_usuario` creada
- [x] Tabla `cierres_mensuales` creada
- [x] Campos agregados a `printers`
- [x] Impresora ID 6 configurada correctamente
- [x] Índices creados
- [x] Constraints aplicados
- [x] Verificación en base de datos exitosa

---

**Última Actualización:** 2 de Marzo de 2026  
**Autor:** Kiro AI Assistant  
**Proyecto:** Sistema de Gestión de Impresoras Ricoh  
**Estado:** ✅ MIGRACIÓN APLICADA EXITOSAMENTE
