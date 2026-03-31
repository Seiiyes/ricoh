# CLI del Sistema de Auditoría

Interfaz de línea de comandos para ejecutar auditorías de código con opciones configurables.

## Instalación

No requiere instalación adicional. El CLI usa los mismos componentes del sistema de auditoría.

## Uso Básico

### Opción 1: Script Simple (Recomendado para Ricoh Suite)

```bash
python run_audit.py
```

Este script ejecuta una auditoría completa del proyecto Ricoh Suite:
- Analiza `backend/` y `frontend/src/`
- Genera reporte en `docs/OPTIMIZACION_HALLAZGOS.md`
- Muestra progreso en consola

### Opción 2: CLI Completo

```bash
python audit_system/cli.py -p <ruta_proyecto>
```

## Opciones del CLI

### Argumentos Requeridos

- `-p, --project-path`: Ruta del proyecto a auditar
  ```bash
  python audit_system/cli.py -p .
  python audit_system/cli.py --project-path /path/to/project
  ```

### Argumentos Opcionales

- `-o, --output`: Ruta del archivo de reporte (default: `docs/OPTIMIZACION_HALLAZGOS.md`)
  ```bash
  python audit_system/cli.py -p . -o custom/report.md
  ```

- `-v, --verbose`: Habilitar logging detallado
  ```bash
  python audit_system/cli.py -p . --verbose
  ```

- `-c, --categories`: Filtrar categorías de análisis (funcionalidad futura)
  ```bash
  python audit_system/cli.py -p . -c performance,security
  ```

## Ejemplos

### 1. Auditoría Básica

```bash
python audit_system/cli.py -p .
```

### 2. Auditoría con Reporte Personalizado

```bash
python audit_system/cli.py -p . -o reports/audit_2024.md
```

### 3. Auditoría con Logging Detallado

```bash
python audit_system/cli.py -p . --verbose
```

### 4. Auditoría con Categorías Específicas

```bash
python audit_system/cli.py -p . -c performance,security
```

### 5. Auditoría Completa

```bash
python audit_system/cli.py -p . -o custom.md -v -c all
```

## Códigos de Salida

- `0`: Auditoría completada exitosamente
- `1`: Error durante la auditoría
- `130`: Auditoría cancelada por el usuario (Ctrl+C)

## Ayuda

Para ver todas las opciones disponibles:

```bash
python audit_system/cli.py --help
```

## Estructura de Archivos

```
audit_system/
├── cli.py              # Interfaz CLI con argparse
├── test_cli.py         # Tests unitarios del CLI
└── demo_cli.py         # Demo de uso del CLI

run_audit.py            # Script simple de ejecución
```

## Logging

Los logs se guardan en `audit_system/logs/audit.log`.

Para ver logs detallados en consola, use la opción `--verbose`:

```bash
python audit_system/cli.py -p . --verbose
```

## Notas

- El argumento `--categories` está disponible pero el filtrado aún no está implementado
- El CLI valida que la ruta del proyecto exista y sea un directorio
- Los errores se manejan gracefully con mensajes informativos
- Se puede cancelar la auditoría en cualquier momento con Ctrl+C
