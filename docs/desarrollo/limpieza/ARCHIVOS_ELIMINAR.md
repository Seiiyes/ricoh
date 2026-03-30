# Análisis de Archivos a Eliminar

**Fecha:** 17 de marzo de 2026

## RESUMEN

Después de analizar el proyecto, estos archivos pueden eliminarse de forma segura:

## 1. SCRIPTS DE IMPORTACIÓN CSV (8 archivos)

**Razón:** La importación de cierres históricos desde CSV ya se completó.
Los datos ya están en la base de datos. Estos scripts fueron one-time.

### Eliminar:
```
backend/scripts/importacion/importar_cierres_correcto.py
backend/scripts/importacion/importar_cierres_desde_csv.py
backend/scripts/importacion/importar_cierres_febrero_correcto.py
backend/scripts/importacion/importar_cierres_final.py
backend/scripts/importacion/pre_importacion_check.py
backend/scripts/importacion/validar_estructura_cierre.py
backend/scripts/importacion/validar_estructura_csv.py
backend/scripts/importacion/validar_importacion_csv.py
```

## 2. SCRIPTS DE ANÁLISIS CSV (11 archivos)

**Razón:** Análisis one-time de archivos CSV durante importación.
Ya no se necesitan.

### Eliminar:
```
backend/scripts/analisis/analisis_completo_contadores.py
backend/scripts/analisis/analisis_completo_todos_csv.py
backend/scripts/analisis/analizar_comparacion_febrero_w533.py
backend/scripts/analisis/analizar_csv_comparativos.py
backend/scripts/analisis/analizar_e176_detallado.py
backend/scripts/analisis/analizar_e176_febrero_csv.py
backend/scripts/analisis/analizar_e176_febrero.py
backend/scripts/analisis/analizar_estructura_completa_csv.py
backend/scripts/analisis/analizar_importacion_csv.py
backend/scripts/analisis/analizar_negativos_w533.py
backend/scripts/analisis/analizar_numeros_negativos.py
```

## 3. SCRIPTS DE VERIFICACIÓN CSV (27 archivos)

**Razón:** Verificaciones one-time de importación CSV.
Los datos ya están validados en la BD.

### Eliminar todos los archivos en:
```
backend/scripts/verificacion/
```

## 4. SCRIPTS DE UTILIDADES (Revisar caso por caso)

### ELIMINAR (14 archivos):
```
backend/scripts/utilidades/aplicar_correccion_contadores.py  # One-time
backend/scripts/utilidades/borrar_cierres_enero_febrero.py   # One-time
backend/scripts/utilidades/comparar_csv_vs_db_simple.py      # CSV
backend/scripts/utilidades/comparar_todos_csv.py             # CSV
backend/scripts/utilidades/contar_usuarios_reales.py         # CSV
backend/scripts/utilidades/debug_importacion.py              # CSV
backend/scripts/utilidades/estado_final_cierres.py           # CSV
backend/scripts/utilidades/estado_importacion.py             # CSV
backend/scripts/utilidades/extraer_contadores_reales_todos.py # CSV
backend/scripts/utilidades/extraer_todos_contadores_reales.py # CSV
backend/scripts/utilidades/mapeo_detallado_campos.py         # CSV
backend/scripts/utilidades/revisar_todos_archivos_csv.py     # CSV
backend/scripts/utilidades/test_match_nombres.py             # CSV
backend/scripts/utilidades/test_parse_enero.py               # CSV
```

### MANTENER (5 archivos útiles):
```
backend/scripts/utilidades/corregir_capacidades_impresoras.py  # Útil
backend/scripts/utilidades/listar_impresoras_db.py             # Útil
backend/scripts/utilidades/probar_comparaciones_simple.py      # Útil
backend/scripts/utilidades/probar_comparaciones_todas.py       # Útil
backend/scripts/utilidades/resumen_final_cierres.py            # Útil
```

## 5. ARCHIVOS CSV EN DOCS (58 archivos)

**Razón:** Archivos CSV históricos ya importados a la BD.
Ocupan espacio y ya no se necesitan.

### Eliminar carpetas completas:
```
docs/CONTADOR IMPRESORAS ENERO/
docs/CONTADOR IMPRESORAS FEBRERO/
docs/CSV_COMPARATIVOS/
docs/COMPARATIVO IMPRESORAS DICIEMBRE - ENERO/
docs/COMPARATIVO IMPRESORAS
 ENERO - FEBRERO/
```

## 6. ARCHIVOS .BAT TEMPORALES

### Eliminar:
```
scripts/importacion/importar-cierres-dry-run.bat
scripts/importacion/importar-cierres-final.bat
scripts/importacion/importar-cierres.bat
scripts/importacion/importar-febrero-2026.bat
scripts/comparar-csv.bat
scripts/estado-importacion.bat
scripts/validar-importacion.bat
scripts/verificar-importacion.bat
backend/scripts/comparar-csv-db.bat
backend/scripts/verificar-datos.bat
```

### Mantener:
```
backend/scripts/listar-impresoras.bat  # Útil
backend/scripts/start-*.bat            # Útiles
```

## 7. ARCHIVOS EXCEL EN DOCS (2 archivos)

### Eliminar:
```
docs/COMPARATIVO FINAL ENERO - FEBRERO.xlsx
docs/COMPARATIVO FINAL IMPRESORAS DICIEMBRE - ENERO.xlsx
```

## RESUMEN DE ELIMINACIÓN

| Categoría | Cantidad | Espacio Estimado |
|-----------|----------|------------------|
| Scripts Python | 60 | ~2 MB |
| Archivos CSV | 58 | ~5-10 MB |
| Archivos .bat | 10 | ~50 KB |
| Archivos Excel | 2 | ~500 KB |
| **TOTAL** | **130** | **~8-13 MB** |

## ARCHIVOS A MANTENER

- Scripts de utilidades útiles (5)
- Documentación en docs/desarrollo/
- Archivos .bat de inicio
- README files
