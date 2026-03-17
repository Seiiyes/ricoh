# Auditoría del Proyecto - Limpieza y Organización

**Fecha:** 17 de marzo de 2026

## RESUMEN EJECUTIVO

El proyecto contiene muchos archivos temporales de desarrollo:
- 42 archivos Markdown en la raíz
- 60+ scripts Python de análisis/verificación en backend
- 2 scripts de prueba en la raíz

## ARCHIVOS MARKDOWN EN RAÍZ (42 archivos)

### MANTENER EN RAÍZ
- README.md

### MOVER A docs/desarrollo/
Todos los archivos de análisis, verificación, importación, confirmación, instrucciones, resúmenes, etc.

## SCRIPTS PYTHON EN BACKEND (60+ archivos)

### MANTENER (Producción)
- main.py
- init_db.py
- create_db.py
- parsear_contadores.py
- parsear_contadores_usuario.py
- parsear_contador_ecologico.py
- uvicorn_config.py

### MOVER A backend/scripts/analisis/
Todos los archivos que empiezan con:
- analisis_*.py
- analizar_*.py

### MOVER A backend/scripts/verificacion/
Todos los archivos que empiezan con:
- verificacion_*.py
- verificar_*.py

### MOVER A backend/scripts/importacion/
Todos los archivos que empiezan con:
- importar_*.py
- pre_importacion_*.py
- validar_estructura_*.py
- validar_importacion_*.py

### MOVER A backend/scripts/utilidades/
- aplicar_*.py
- borrar_*.py
- comparar_*.py
- contar_*.py
- corregir_*.py
- debug_*.py
- estado_*.py
- extraer_*.py
- listar_*.py
- mapeo_*.py
- probar_*.py
- revisar_*.py
- test_*.py

## ARCHIVOS .BAT

### MANTENER EN RAÍZ
- backup-db.bat
- restore-db.bat
- docker-start.bat
- start-dev.bat
- start-local.bat
- instalar-dependencias.bat

### MOVER A scripts/
- comparar-csv.bat
- estado-importacion.bat
- importar-*.bat
- validar-importacion.bat
- verificar-importacion.bat

## ARCHIVOS TEMPORALES A ELIMINAR
- test_lectura_250.py
- test_parser_252.py
- ANALISIS_PROBLEMAS_CIERRES.md (vacío)
- SOLUCION_BUG_COMPARACION.md (vacío)
- backend/verificar_capacidades_reales_csv.py (vacío)

## ESTRUCTURA PROPUESTA

```
proyecto/
├── scripts/
│   ├── importacion/
│   ├── verificacion/
│   └── utilidades/
├── docs/
│   └── desarrollo/
│       ├── importacion/
│       ├── analisis/
│       └── verificacion/
└── backend/
    ├── scripts/
    │   ├── analisis/
    │   ├── verificacion/
    │   ├── importacion/
    │   └── utilidades/
    └── data/
```

## PLAN DE ACCIÓN

1. Crear carpetas nuevas
2. Mover archivos MD a docs/desarrollo/
3. Mover scripts Python a backend/scripts/
4. Mover archivos .bat a scripts/
5. Eliminar archivos temporales
6. Hacer commit

## IMPACTO

- Archivos a mover: ~100
- Archivos a eliminar: 5
- Riesgo: BAJO (solo reorganización)
- Beneficio: Proyecto más limpio y organizado
