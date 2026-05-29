# Exportación Excel Ricoh - Formato 3 Hojas Adaptativo

## Cambio Implementado

Se restauró el formato de exportación Excel Ricoh a 3 hojas y se hizo adaptativo según las capacidades de cada impresora.

### Estructura del Archivo Excel

1. **Hoja 1: Período Base (Completo)**
   - Nombre: `{serial_number} {MES1}` (ej: "W533L900719 ENERO")
   - Contenido: 52 columnas con todos los contadores del primer período
   - Incluye: Todos los usuarios con sus contadores completos + fila de totales

2. **Hoja 2: Período Comparado (Completo)**
   - Nombre: `{serial_number} {MES2}` (ej: "W533L900719 FEBRERO")
   - Contenido: 52 columnas con todos los contadores del segundo período
   - Incluye: Todos los usuarios con sus contadores completos + fila de totales

3. **Hoja 3: Comparativo (Solo Diferencias) - ADAPTATIVO**
   - Nombre: `{serial_number} COMPARATIVO`
   - Contenido: Se adapta según las capacidades de la impresora
   
   **Información de la Impresora (primeras filas):**
   - Serial Number
   - Hostname
   - Dirección IP
   - Ubicación
   - ID de la impresora
   - Tipo (Color o Solo B/N)

#### Para Impresoras CON Color (has_color = True):
   - Columnas:
     - A: Código de usuario
     - B: Nombre de usuario
     - C: Consumo B/N
     - D: Consumo Color
     - E: Consumo Total
     - F: Total contador período 1 (última fila)
     - G: Total contador período 2 (última fila)
   
   - Filas finales:
     - Penúltima fila: Totales de cada período (columnas F y G)
     - Última fila: 
       - Columna C: Suma del consumo B/N de todos los usuarios
       - Columna D: Suma del consumo Color de todos los usuarios
       - Columna E: Suma del consumo Total de todos los usuarios
       - Columna F: Diferencia del contador total de la impresora
       - Columna G: Diferencia (páginas de prueba u otros)

#### Para Impresoras SOLO B/N (has_color = False):
   - Columnas:
     - A: Código de usuario
     - B: Nombre de usuario
     - C: Consumo Total (B/N)
     - D: (vacío)
     - E: (vacío)
     - F: Total contador período 1 (última fila)
     - G: Total contador período 2 (última fila)
   
   - Filas finales:
     - Penúltima fila: Totales de cada período (columnas F y G)
     - Última fila: 
       - Columna C: Suma del consumo de todos los usuarios
       - Columna D: Diferencia del contador total de la impresora
       - Columna E: Diferencia (páginas de prueba u otros)

### Validación

La hoja comparativa permite validar que:
```
Suma de consumo de usuarios ≈ Diferencia del contador total
```

La diferencia representa páginas de prueba u otros consumos no asignados a usuarios.

## Archivo Modificado

- `backend/services/export_ricoh.py` - Función `exportar_comparacion_ricoh()`

## Endpoint API

- `GET /api/export/comparacion/{cierre1_id}/{cierre2_id}/excel-ricoh`

## Formato Compatible

Este formato es compatible con los archivos CSV originales de Ricoh ubicados en:
- `docs/COMPARATIVO FINAL ENERO - FEBRERO_W533L900719.csv`
- `docs/COMPARATIVO IMPRESORAS ENERO - FEBRERO/`

## Ventajas del Formato Adaptativo

- Impresoras solo B/N: Muestra solo la columna relevante (Total), sin columnas vacías de color
- Impresoras con color: Muestra desglose completo (B/N, Color, Total)
- Más limpio y fácil de leer según el tipo de impresora
- Validación automática del consumo vs contador total
