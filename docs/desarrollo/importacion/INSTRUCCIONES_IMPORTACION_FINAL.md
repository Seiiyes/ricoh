# Instrucciones de Importación Final - Cierres Mensuales

## ✅ Estado: LISTO PARA IMPORTAR

Todos los archivos CSV han sido revisados y validados. Los datos son coherentes y correctos.

---

## Pasos para Importar

### Paso 1: Verificación Pre-Importación

Ejecuta el script de verificación para confirmar que todo está listo:

```bash
python backend/pre_importacion_check.py
```

Este script verifica:
- ✅ Conexión a la base de datos
- ✅ Impresoras existen en la BD
- ✅ No hay cierres duplicados
- ✅ Archivos CSV existen
- ✅ Estructura de tablas correcta

**Resultado esperado**: Todas las verificaciones deben pasar (✅)

---

### Paso 2: Dry-Run (Simulación)

Ejecuta una simulación SIN guardar datos en la BD:

```bash
python backend/importar_cierres_final.py --dry-run --mes 2 --anio 2026
```

Este comando:
- 🔍 Simula la importación completa
- 📊 Muestra qué datos se importarían
- ❌ NO guarda nada en la base de datos
- ✅ Permite revisar antes de importar realmente

**Revisa cuidadosamente**:
- Número de usuarios por impresora
- Contadores totales
- Diferencias mensuales
- Usuarios saltados (SYSTEM, sin consumo)

---

### Paso 3: Importación Real - FEBRERO 2026

Si el dry-run es exitoso, ejecuta la importación real:

```bash
python backend/importar_cierres_final.py --mes 2 --anio 2026
```

⚠️ **IMPORTANTE**: Este comando SÍ guardará los datos en la base de datos.

---

### Paso 4 (Opcional): Importar Enero 2026

Si también necesitas importar enero:

```bash
# Dry-run primero
python backend/importar_cierres_final.py --dry-run --mes 1 --anio 2026

# Importación real
python backend/importar_cierres_final.py --mes 1 --anio 2026
```

---

### Paso 5 (Opcional): Importar Solo Una Impresora

Para importar una impresora específica:

```bash
# Dry-run
python backend/importar_cierres_final.py --dry-run --mes 2 --serial W533L900719

# Importación real
python backend/importar_cierres_final.py --mes 2 --serial W533L900719
```

---

## Datos que se Importarán

### Febrero 2026

| Serial | Nombre | Contador Feb | Diferencia | Usuarios |
|--------|--------|--------------|------------|----------|
| W533L900719 | 3ER PISO ELITE BOYACA REAL COLOR | 1,010,592 | 22,005 | 25 |
| E174M210096 | 2DO PISO ELITE BOYACA REAL | 451,657 | 12,507 | 40 |
| E174MA11130 | 3ER PISO ELITE BOYACA REAL B/N | 364,942 | 18,731 | 69 |
| G986XA16285 | 1ER PISO ELITE BOYACA REAL | 261,159 | 8,791 | 11 |
| E176M460020 | 2DO PISO SARUPETROL | 913,835 | 11,885 | 0 |

**Total**: 5 impresoras, 145 usuarios con consumo

---

## Qué Hace el Script de Importación

### Para cada impresora:

1. **Verifica** que la impresora existe en la BD
2. **Verifica** que no existe un cierre duplicado
3. **Crea** registro en `cierres_mensuales`:
   - `total_paginas`: Contador real de febrero
   - `diferencia_total`: Consumo mensual (feb - ene)
   - `fecha_cierre`: 2026-02-28

4. **Lee** archivo comparativo de diferencias
5. **Procesa** cada usuario:
   - Limpia código (remueve `[]` y `.0`)
   - Limpia nombre (remueve `[]`)
   - Salta usuarios SYSTEM o sin consumo
   - Extrae breakdown (B/N, Color, Copier, Printer, etc.)

6. **Crea** registros en `cierres_mensuales_usuarios`

---

## Casos Especiales Manejados

### 1. W533L900719
- CSV tipo "simple" (sin breakdown detallado)
- Solo importa `total_impresiones`
- No tiene datos de B/N, Color separados

### 2. E176M460020 (Sarupetrol)
- No tiene usuarios en el comparativo
- Solo se crea el cierre mensual
- No se crean registros de usuarios

### 3. Códigos de Usuario
- `[3581]` → `3581`
- `3581.0` → `3581`
- `[-]` → Saltado (SYSTEM)
- `[SYSTEM]` → Saltado

### 4. Primera Fila del Comparativo
- Contiene el total mensual
- Se salta al importar usuarios
- Evita duplicar el consumo total

---

## Verificación Post-Importación

Después de importar, verifica los datos:

```sql
-- Ver cierres creados
SELECT 
    i.serial,
    i.nombre,
    cm.mes,
    cm.anio,
    cm.total_paginas,
    cm.diferencia_total,
    COUNT(cmu.id) as num_usuarios
FROM cierres_mensuales cm
JOIN impresoras i ON i.id = cm.impresora_id
LEFT JOIN cierres_mensuales_usuarios cmu ON cmu.cierre_id = cm.id
WHERE cm.anio = 2026 AND cm.mes = 2
GROUP BY i.serial, i.nombre, cm.mes, cm.anio, cm.total_paginas, cm.diferencia_total
ORDER BY i.serial;

-- Ver top usuarios por impresora
SELECT 
    i.serial,
    cmu.codigo_usuario,
    cmu.nombre_usuario,
    cmu.total_impresiones
FROM cierres_mensuales_usuarios cmu
JOIN cierres_mensuales cm ON cm.id = cmu.cierre_id
JOIN impresoras i ON i.id = cm.impresora_id
WHERE cm.anio = 2026 AND cm.mes = 2
ORDER BY i.serial, cmu.total_impresiones DESC;
```

---

## Rollback (Si Algo Sale Mal)

Si necesitas deshacer la importación:

```sql
-- Ver IDs de cierres a eliminar
SELECT id, impresora_id, mes, anio 
FROM cierres_mensuales 
WHERE anio = 2026 AND mes = 2;

-- Eliminar usuarios primero (por foreign key)
DELETE FROM cierres_mensuales_usuarios 
WHERE cierre_id IN (
    SELECT id FROM cierres_mensuales 
    WHERE anio = 2026 AND mes = 2
);

-- Eliminar cierres
DELETE FROM cierres_mensuales 
WHERE anio = 2026 AND mes = 2;
```

O usa el script de borrado que ya creamos:

```bash
python backend/borrar_cierres_enero_febrero.py
```

---

## Archivos Creados

### Scripts de Importación
- `backend/importar_cierres_final.py` - Script principal de importación
- `backend/pre_importacion_check.py` - Verificación pre-importación

### Scripts de Análisis
- `backend/verificacion_final_importacion.py` - Verificación de coherencia CSV
- `backend/analisis_completo_todos_csv.py` - Análisis exhaustivo

### Documentación
- `ANALISIS_FINAL_CSV_COMPLETO.md` - Análisis detallado completo
- `RESUMEN_REVISION_CSV.md` - Resumen ejecutivo
- Este archivo - Instrucciones paso a paso

---

## Soporte

Si encuentras algún error durante la importación:

1. **Revisa el mensaje de error** - El script muestra información detallada
2. **Verifica los archivos CSV** - Asegúrate que no fueron modificados
3. **Revisa la conexión a BD** - Verifica credenciales en `.env`
4. **Ejecuta dry-run nuevamente** - Para ver qué está pasando sin guardar datos

---

## Checklist Final

Antes de importar, confirma:

- [ ] Ejecuté `pre_importacion_check.py` y todas las verificaciones pasaron
- [ ] Ejecuté dry-run y revisé los resultados
- [ ] Los contadores y diferencias son correctos
- [ ] El número de usuarios es razonable
- [ ] Tengo backup de la base de datos (opcional pero recomendado)
- [ ] Estoy listo para importar

**¡Listo para importar!** 🚀
