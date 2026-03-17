# Instrucciones para Importación de Cierres Mensuales desde CSV

## 📋 Resumen

Este documento explica cómo importar los cierres mensuales de Enero y Febrero 2026 desde los archivos CSV a la base de datos.

## ✅ Preparación Completada

1. ✅ Análisis de estructura CSV completado
2. ✅ Identificación de casos especiales:
   - Códigos con `.0` (W533L900719)
   - Códigos con corchetes `[]` (G986XA16285, E174MA11130)
   - Valores con guiones `-`
   - Usuario SYSTEM (no se importa)
3. ✅ Mapeo de campos CSV → BD documentado
4. ✅ Scripts de importación creados
5. ✅ Cierres incorrectos de Enero y Febrero eliminados

## 🔧 Scripts Disponibles

### 1. Validación Pre-Importación
```bash
validar-importacion.bat
```
**Qué hace:**
- Verifica que todos los archivos CSV existan
- Lee y valida los datos de cada impresora
- Calcula coherencia entre contadores y usuarios
- Muestra preview de datos sin guardar nada

**Ejecutar PRIMERO** para verificar que todo esté correcto.

### 2. Importación Dry-Run (Preview)
```bash
importar-cierres-dry-run.bat
```
**Qué hace:**
- Procesa todos los CSV como si fuera a importar
- Muestra exactamente qué se guardará
- NO guarda nada en la base de datos
- Útil para verificar antes de importar

### 3. Importación Real
```bash
importar-cierres.bat
```
**Qué hace:**
- Importa los cierres mensuales a la base de datos
- Crea registros en `cierres_mensuales`
- Crea registros en `cierres_mensuales_usuarios`
- **GUARDA DATOS PERMANENTEMENTE**

## 📊 Datos que se Importarán

### Impresoras Configuradas

1. **W533L900719** - 3ER PISO ELITE BOYACA REAL COLOR
   - Formato: Simple (solo total páginas)
   - CSV Contador: `W533L900719 16.02.2026.csv`
   - CSV Comparativo: `W533L900719 ENERO - FEBRERO_W533L900719 ENERO - FEBRERO.csv`
   - Usuarios con actividad: ~89
   - Casos especiales: Códigos con `.0`

2. **G986XA16285** - 1ER PISO ELITE BOYACA REAL
   - Formato: Detallado (desglose completo)
   - CSV Contador: `G986XA16285 16.02.2026.csv`
   - CSV Comparativo: `G986XA16285 ENERO - FEBRERO_G986XA16285 COMPARATIVO.csv`
   - Usuarios con actividad: ~22
   - Casos especiales: Códigos con corchetes `[]`

3. **E174MA11130** - 3ER PISO ELITE BOYACA REAL B/N
   - Formato: Detallado (desglose completo)
   - CSV Contador: `E174MA11130 16.02.2026.csv`
   - CSV Comparativo: `E174MA11130 ENERO - FEBRERO_E174MA11130 COMPARATIVO.csv`
   - Usuarios con actividad: ~119
   - Casos especiales: Códigos con corchetes `[]`

## 🔄 Proceso de Importación

### Paso 1: Validar Datos
```bash
validar-importacion.bat
```
Revisa el output y verifica:
- ✅ Todos los archivos encontrados
- ✅ Contadores reales detectados
- ✅ Usuarios con actividad encontrados
- ✅ Coherencia entre contadores y usuarios

### Paso 2: Preview (Dry-Run)
```bash
importar-cierres-dry-run.bat
```
Revisa el output y verifica:
- ✅ Datos de cada impresora
- ✅ Contadores reales (Enero y Febrero)
- ✅ Diferencia mensual
- ✅ Top 5 usuarios por consumo
- ✅ Total de usuarios a importar

### Paso 3: Importar
```bash
importar-cierres.bat
```
Confirma con `S` cuando se solicite.

El script:
1. Crea un cierre mensual por cada impresora
2. Guarda los contadores reales de la impresora
3. Guarda los contadores individuales de cada usuario
4. Asigna el consumo mensual a cada usuario

## 📝 Mapeo de Datos

### Tabla: cierres_mensuales
- `total_paginas` = Contador real de Febrero (del CSV comparativo)
- `diferencia_total` = Febrero - Enero
- `tipo_periodo` = 'mensual'
- `fecha_inicio` = 2026-02-01
- `fecha_fin` = 2026-02-28

### Tabla: cierres_mensuales_usuarios
- `codigo_usuario` = Código limpio (sin `.0`, sin `[]`, sin ceros a la izquierda)
- `nombre_usuario` = Nombre del usuario
- `total_paginas` = Total páginas del usuario (del CSV contador)
- `total_bn` = Total B/N (si disponible)
- `total_color` = Total Color (si disponible)
- `copiadora_bn`, `copiadora_color` = Desglose copiadora (si disponible)
- `impresora_bn`, `impresora_color` = Desglose impresora (si disponible)
- `escaner_bn`, `escaner_color` = Desglose escáner (si disponible)
- `fax_bn` = Fax (si disponible)
- `consumo_total` = Consumo del mes (del CSV comparativo)

### Casos Especiales Manejados

1. **Códigos con `.0`** (W533L900719)
   - `3581.0` → `3581`
   - `1125.0` → `1125`

2. **Códigos con corchetes** (G986, E174)
   - `[2902]` → `2902`
   - `[0494]` → `494` (remueve ceros a la izquierda)

3. **Valores con guiones**
   - `-` → `0`

4. **Usuario SYSTEM**
   - Código `-` o `SYSTEM` → NO SE IMPORTA

5. **Formato Simple** (W533L900719)
   - Solo tiene "Total páginas impresión"
   - Todos los desgloses se ponen en `0`

6. **Formato Detallado** (G986, E174)
   - Tiene desglose completo por función
   - Se mapean todos los campos disponibles

## ⚠️ Notas Importantes

1. **Diferencia Normal**: Es normal que la suma de usuarios sea 60-70% del contador real
   - El resto son impresiones anónimas o del sistema

2. **Consumo por Usuario**: Se obtiene del CSV comparativo, NO del CSV contador
   - CSV Contador = Contador acumulado total
   - CSV Comparativo = Consumo del mes

3. **Validación**: Siempre ejecutar validación y dry-run antes de importar

4. **Backup**: Los cierres anteriores ya fueron eliminados, pero se recomienda tener backup de BD

## 🐛 Solución de Problemas

### Error: "Impresora no encontrada en BD"
- Verificar que la impresora existe en la tabla `printers`
- Verificar que el `serial_number` coincide exactamente

### Error: "No se encuentra archivo CSV"
- Verificar que los archivos están en:
  - `docs/CONTADOR IMPRESORAS FEBRERO/`
  - `docs/CSV_COMPARATIVOS/`

### Warning: "Usuarios sin consumo en comparativo"
- Normal si son pocos usuarios
- Revisar si son usuarios con poca actividad

### Error: "Contadores reales no detectados"
- Verificar estructura del CSV comparativo
- Verificar que tiene los contadores de Enero y Febrero

## 📞 Soporte

Si encuentras algún problema:
1. Revisa el output del script de validación
2. Verifica que los archivos CSV están completos
3. Ejecuta dry-run para ver qué se importará
4. Revisa este documento para casos especiales

## ✅ Checklist Final

Antes de importar, verifica:
- [ ] Backup de base de datos realizado
- [ ] Validación ejecutada sin errores
- [ ] Dry-run ejecutado y revisado
- [ ] Datos coherentes (contadores, usuarios, consumos)
- [ ] Cierres anteriores eliminados (ya hecho)
- [ ] Listo para importar

---

**Última actualización**: 2026-03-16
**Scripts creados por**: Kiro AI Assistant
