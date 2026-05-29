# Sincronización de Rutas SMB desde Impresoras Ricoh

## Resumen

Este documento describe el proceso de sincronización de rutas SMB desde las libretas de direcciones de las 5 impresoras Ricoh hacia la base de datos del sistema.

## Problema Identificado

Inicialmente, las rutas SMB de los usuarios se estaban leyendo incorrectamente debido a que cada modelo de impresora Ricoh tiene un formato diferente en su respuesta AJAX.

### Formatos Detectados

Las 5 impresoras tienen 3 formatos diferentes:

1. **Formato con 9 campos** (RNP002673CA501E - 192.168.91.252)
   - Carpeta SMB en posición `[8]`
   - Ejemplo: `[231,1,'00001','YESICA GARCIA','1717','timestamp','','','\\\\CFP-10900\\scanner']`

2. **Formato con 8 campos** (RNP0026737FFBB8, RNP00267391F283, RNP002673C01D88)
   - Carpeta SMB en posición `[7]`
   - Ejemplo: `[167,1,'00001','JULIAN','0116','timestamp','','\\\\TIC0712\\Escaner']`

3. **Formato .253 con 11 campos** (RNP002673721B98 - 192.168.91.253)
   - Campo vacío al inicio
   - Carpeta SMB en posición `[10]`
   - Código de usuario en posición `[8]`
   - Ejemplo: `['',1,'00001','YESICA GARCIA',1,'AB','','','1717','','\\\\CFP-10900\\scanner']`

## Solución Implementada

### 1. Detección Automática de Formato

Se modificó `backend/services/ricoh_web_client.py` para detectar automáticamente el formato basándose en:
- Si el primer campo está vacío (formato .253)
- La cantidad total de campos en la respuesta

```python
if entry[0] == '' and len(entry) >= 11:
    # Formato .253
    folder = str(entry[10])
elif len(entry) == 9:
    # Formato con 9 campos
    folder = str(entry[8])
elif len(entry) == 8:
    # Formato con 8 campos
    folder = str(entry[7])
```

### 2. Scripts de Sincronización

#### `sync_all_5_printers_to_db.py`
Script principal para sincronizar rutas SMB desde las 5 impresoras a la base de datos.

**Funcionalidad:**
- Lee usuarios de las 5 impresoras usando `read_users_from_printer(fast_list=True)`
- Recolecta rutas SMB específicas (que contienen `\\\\`)
- Actualiza usuarios en la base de datos
- Solo actualiza si la ruta actual es genérica o diferente

**Uso:**
```bash
docker exec ricoh-backend python scripts/sync_all_5_printers_to_db.py
```

#### `quick_verify_5_printers.py`
Script de verificación rápida para confirmar que las 5 impresoras se leen correctamente.

**Uso:**
```bash
docker exec ricoh-backend python scripts/quick_verify_5_printers.py
```

#### `analyze_all_printer_formats.py`
Script de análisis para identificar el formato de cada impresora.

**Uso:**
```bash
docker exec ricoh-backend python scripts/analyze_all_printer_formats.py
```

## Resultados

### Estado Final de las 5 Impresoras

| Impresora | IP | Total Usuarios | Con SMB | % |
|-----------|-----|----------------|---------|---|
| RNP002673CA501E | 192.168.91.252 | 90 | 74 | 82% |
| RNP0026737FFBB8 | 192.168.91.250 | 241 | 212 | 87% |
| RNP002673721B98 | 192.168.91.253 | 195 | 174 | 89% |
| RNP00267391F283 | 192.168.91.251 | 274 | 232 | 84% |
| RNP002673C01D88 | 192.168.110.250 | 82 | 6 | 7% |
| **TOTAL** | | **882** | **698** | **79%** |

### Estado Final en Base de Datos

- **440 usuarios activos** en total
- **328 usuarios (74%)** con rutas SMB específicas de impresoras
- **112 usuarios (25%)** con ruta SMB por defecto (`\\\\192.168.91.5\\Escaner`)
- **0 usuarios** con rutas genéricas con errores

### Ejemplos de Rutas SMB Sincronizadas

```
\\CFP-10900\scanner
\\TIC0712\Escaner
\\RECEPCIONCIEN\scaner
\\COMERCIAL-SARU\Escaner
\\DESKTOP-CEI434C\Escaner
\\ANALISTACONSUMO\Escaner
```

## Notas Importantes

1. **Impresora 192.168.110.250**: Solo 6 de 82 usuarios tienen carpeta SMB configurada. La mayoría de usuarios en esta impresora no tienen carpeta configurada (campo vacío), lo cual es correcto y esperado.

2. **Usuarios sin ruta en impresoras**: Los 112 usuarios con ruta por defecto son usuarios que:
   - No están en ninguna de las 5 impresoras activas
   - Fueron creados manualmente en la BD
   - Fueron eliminados de las libretas de direcciones

3. **Duplicados**: El sistema filtra automáticamente usuarios duplicados basándose en el `entry_index`.

## Mantenimiento

### Sincronización Periódica

Para mantener las rutas SMB actualizadas, ejecutar periódicamente:

```bash
docker exec ricoh-backend python scripts/sync_all_5_printers_to_db.py
```

### Verificación

Para verificar el estado actual:

```bash
docker exec ricoh-backend python scripts/quick_verify_5_printers.py
docker exec ricoh-backend python scripts/check_smb_paths_status.py
```

## Archivos Modificados

- `backend/services/ricoh_web_client.py` - Detección automática de formatos
- `backend/scripts/sync_all_5_printers_to_db.py` - Script de sincronización
- `backend/scripts/quick_verify_5_printers.py` - Script de verificación
- `backend/scripts/analyze_all_printer_formats.py` - Script de análisis

## Fecha de Implementación

8 de Abril de 2026
