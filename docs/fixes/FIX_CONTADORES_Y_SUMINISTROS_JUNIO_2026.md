# Fix: Consistencia de Contadores e Interfaz en Cierres Mensuales (Junio 2026)

## Resumen Ejecutivo

Durante la sesión del 01-03 de Junio de 2026 se corrigieron discrepancias matemáticas en las tarjetas globales de la comparación de cierres mensuales (B/N y Color), se solucionó un conflicto de ámbito en Python (scope shadowing) y se refinó la interfaz de comparación ocultando columnas redundantes en impresoras monocromáticas.

---

## Bug 1: Conflicto de Ámbito (Scope Shadowing) en Variables Globales

### Síntoma
Las tarjetas superiores de la comparación de cierres mostraban totales de B/N y Color que correspondían únicamente al último usuario procesado en el bucle, en lugar del acumulado general o del cálculo global de la máquina.

### Causa raíz
En `backend/services/close_service.py`, dentro de la función `comparar_cierres`, las variables globales acumuladoras `diferencia_bn` y `diferencia_color` eran sobreescritas dentro del bucle de usuarios `for u in usuarios_cierre:` porque se definieron variables internas con el mismo nombre exacto.

### Fix aplicado
**Archivo:** `backend/services/close_service.py`

Se renombraron las variables internas del bucle para evitar el conflicto de nombres con las variables del ámbito superior:

```python
# ANTES
diferencia_bn = (u.total_bn - ant_u.total_bn)
diferencia_color = (u.total_color - ant_u.total_color)

# DESPUÉS
user_diferencia_bn = (u.total_bn - ant_u.total_bn)
user_diferencia_color = (u.total_color - ant_u.total_color)
```

---

## Bug 2: Discrepancia entre Suma de Usuarios y Contador Físico

### Síntoma
La suma de las páginas consumidas por todos los usuarios no coincidía con el total de páginas reportadas físicamente por la máquina en la comparación de periodos (faltaban páginas impresas de forma local o anónima).

### Causa raíz
Anteriormente, los totales globales de B/N y Color mostrados en las tarjetas superiores se intentaban computar agregando o sumando los datos de consumo de los usuarios individuales. Sin embargo, en cualquier entorno de red, existen páginas impresas sin usuario autenticado (páginas de prueba de red, reportes del sistema, impresiones directas locales, etc.).

### Fix aplicado
**Archivo:** `backend/services/close_service.py`

Se modificó la lógica para obtener los snapshots de los contadores generales (`ContadorImpresora`) correspondientes a cada cierre directamente de la base de datos y calcular la diferencia global real del dispositivo físico:

```python
# Obtener contadores generales asociados a los cierres
contador_ini = db.query(ContadorImpresora).filter(...).first()
contador_fin = db.query(ContadorImpresora).filter(...).first()

# Calcular diferencias físicas reales
diferencia_bn = (contador_fin.copiadora_bn + contador_fin.impresora_bn + contador_fin.fax_bn) - \
                (contador_ini.copiadora_bn + contador_ini.impresora_bn + contador_ini.fax_bn)
diferencia_color = (contador_fin.copiadora_color + contador_fin.impresora_color) - \
                   (contador_ini.copiadora_color + contador_ini.impresora_color)
```
Esto garantiza que la diferencia B/N + Color coincida exactamente al 100% con la diferencia de páginas físicas totales registradas por el hardware de la impresora.

---

## Bug 3: Inflado de Totales Físicos por Escaneo y Fallback de Contador Ecológico

### Síntoma
Las impresoras monocromáticas o con contadores ecológicos mostraban totales inflados (donde intervenían páginas escaneadas) o totales en `0` (cuando el desglose no estaba disponible).

### Causa raíz
1. El cálculo fallback sumaba los contadores de escáner (`escaner_bn` / `escaner_color`) a los totales físicos impresos, lo cual es incorrecto porque el escaneo no consume papel ni tinta de impresión.
2. Los contadores ecológicos en impresoras B/N almacenan `0` para desgloses detallados de B/N, dejando solo el total acumulador de páginas.

### Fix aplicado
**Archivo:** `backend/services/close_service.py`

1. Se eliminaron los campos de escáner del fallback de totales de impresión:
   ```python
   # Eliminados de la sumatoria de impresión:
   # - c.escaner_bn
   # - c.escaner_color
   ```
2. Se implementó una lógica de fallback para equipos B/N con contadores ecológicos: si los desgloses de B/N son `0`, pero la impresora es monocromática (`hasColor=False`), el total de páginas impresas se mapea directamente al diferencial de B/N.

---

## Redundancia en Interfaz Frontend: Ocultación de Columna B/N

### Síntoma
En impresoras monocromáticas (Blanco y Negro), la tabla de comparación mostraba la columna **Total**, la columna **Color** (vacía/oculta) y la columna **B/N**. La columna B/N mostraba valores exactamente idénticos a la columna Total, saturando la pantalla de forma redundante.

### Fix aplicado
**Archivos:**  
- `src/components/contadores/cierres/ComparacionPage.tsx`  
- `src/components/contadores/cierres/TablaComparacionSimplificada.tsx`  

1. Se mapearon los valores correctos de consumo de tarjetas desde la respuesta de la API (`u.diferencia_bn` y `u.diferencia_color`).
2. Se condicionó la visualización de la columna **B/N** para que se oculte cuando `hasColor` sea `false`. Así, en impresoras monocromáticas, solo se visualiza la columna **Total**, eliminando la redundancia y optimizando la interfaz visual.
3. Se adaptaron dinámicamente los spans (`colSpan`) en las secciones de encabezados compuestos y pie de tabla (sumas) para evitar desalineaciones de columnas.

---

*Fix documentado el 03 de Junio de 2026.*
