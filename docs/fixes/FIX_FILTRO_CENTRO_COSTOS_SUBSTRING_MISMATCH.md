# Corrección de Filtro de Centro de Costos y Filtro por Período de Cierre

**Fecha**: 5 de Junio de 2026  
**Módulos Afectados**:
*   Backend: `backend/api/counters.py` (Endpoints `/api/counters/monthly/users/all` y `/api/counters/monthly`)
*   Frontend: `src/hooks/useAnalyticsData.ts`, `src/pages/AnalyticsPage.tsx`
**Tipo**: Corrección de bug de filtrado y optimización de filtros de usuario (UX)

---

## 1. Problema de Coincidencia Parcial (Bug Original)

Al aplicar el filtro por "Centro de Costos" en la pestaña de **Consumo de Usuarios** (Módulo de Reportes y Analíticas), al seleccionar o buscar `TIC` el sistema listaba erróneamente a usuarios del área de `LOGISTICA` (como *Huber Zapata*).

### Causa Raíz
En la base de datos, el usuario *Huber Zapata* tiene asignado el centro de costos `LOGISTICA` (ID 28). La lógica de filtrado del backend en `backend/api/counters.py` implementaba una coincidencia parcial mediante `ilike` con comodines `%`:

```python
# Causa del error (coincidencia parcial abusiva)
query = query.filter(CentroCosto.nombre.ilike(f"%{centro_costos}%"))
```

Dado que la subcadena `"TIC"` está contenida exactamente en medio de la palabra `"LOGISTICA"` (`LOGIS-TIC-A`), la consulta de base de datos arrojaba un falso positivo.

### Solución Aplicada
Se modificó la cláusula de filtrado en el backend ([counters.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/api/counters.py#L956)) para realizar una **coincidencia exacta insensible a mayúsculas/minúsculas**:

```python
# Solución implementada
query = query.filter(CentroCosto.nombre.ilike(centro_costos))
```

---

## 2. Rediseño del Filtro de Fechas (Períodos de Cierre)

El usuario reportó que el uso de dos selectores de fecha tradicionales ("Fecha Inicio" y "Fecha Fin") resultaba confuso para filtrar el consumo de usuarios, ya que dicho consumo depende estrictamente de los cierres emitidos y sus fechas exactas.

### A. Cambios en el Backend ([counters.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/api/counters.py#L532-L547))
Se modificó el endpoint `GET /api/counters/monthly` para hacer que el parámetro de consulta `printer_id` sea **opcional**:
* Si no se provee `printer_id`, el backend consulta todos los cierres mensuales registrados.
* Si el usuario no es superadmin, se aplica una política de multi-tenancy filtrando por `Printer.empresa_id == current_user.empresa_id`.
* Esto permite al frontend obtener la lista global de períodos en los que existen cierres para poblar dinámicamente un selector.

### B. Cambios en el Frontend ([useAnalyticsData.ts](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/hooks/useAnalyticsData.ts), [AnalyticsPage.tsx](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/pages/AnalyticsPage.tsx))
* **Hook React Query**: Se creó `useMonthlyCloses` para consumir el endpoint global.
* **Extractor de Períodos**: Se calcula un arreglo de períodos únicos (`fecha_inicio` al `fecha_fin`) en base a los cierres existentes.
* **Selector Único (Dropdown)**: Se removieron los dos campos de fecha manuales en la pestaña de Consumo de Usuarios y se reemplazaron por una lista desplegable: **Período de Cierre**.
  * Al seleccionar un cierre (ej: *"Cierre del 20/05/2026"*), se definen automáticamente los filtros de fecha interna para llamar a la API, trayendo el consumo real precalculado del cierre.

---

## 3. Corrección del Formateo de Períodos Idénticos (Cero Días)

Dado que en la base de datos los cierres a menudo se registran con la misma fecha de inicio y de fin (por ejemplo, `2026-05-20` al `2026-05-20`), el subtítulo del reporte mostraba `"Período 2026-05-20 al 2026-05-20"`, lo cual resultaba contradictorio y confuso para los usuarios.

### Solución UI ([AnalyticsPage.tsx](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/pages/AnalyticsPage.tsx#L1072))
Se implementó un formateador dinámico que detecta si el inicio y fin del período de cierre son idénticos:
* **Si coinciden**: Muestra de forma descriptiva **`Cierre del DD/MM/YYYY`** (ej: `Cierre del 20/05/2026`).
* **Si no coinciden**: Muestra el rango tradicional: `Período del DD/MM/YYYY al DD/MM/YYYY`.

---

## 4. Pruebas de Verificación Realizadas

1. **Prueba de API (TIC)**: La petición `GET /api/counters/monthly/users/all?centro_costos=TIC` devuelve exactamente 80 ítems y **excluye correctamente a Huber Zapata** (Logística).
2. **Prueba de dropdown y títulos (UI)**: Verificada la navegación real con éxito: la lista desplegable de cierres opera de forma fluida y los subtítulos cambian dinámicamente según la regla de igualdad de fechas.
3. **TypeScript**: Validación estricta ejecutada y aprobada:
   ```bash
   docker exec -t ricoh-frontend npx tsc --noEmit  # Completado con éxito
   ```
