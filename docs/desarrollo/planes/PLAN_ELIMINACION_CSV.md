# Plan de Eliminación de CSV y Migración Exclusiva a Formatos Excel (XLS / XLSX)

## 📋 Objetivo
El cliente ha solicitado consolidar todas las exportaciones del sistema de auditoría exclusivamente en formatos de hoja de cálculo Excel (`.xls` y `.xlsx`), eliminando por completo las exportaciones a formato plano CSV. 

Este plan técnico detalla de manera exacta todas las ubicaciones, endpoints, funciones y componentes de la interfaz de usuario que deben ser eliminados o modificados en la siguiente sesión de desarrollo.

---

## 🛠️ Plan de Trabajo Paso a Paso

### 1. Backend API (FastAPI)

En el backend, se deben remover los endpoints que generan respuestas en streaming con formato `text/csv`.

#### 🔴 Archivo a Modificar: [backend/api/export.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/api/export.py)
*   **Eliminar Dependencia:**
    Remover la importación de la librería nativa de Python:
    ```python
    import csv  # <-- ELIMINAR
    ```
*   **Eliminar Endpoint de Cierre CSV:**
    Remover por completo el endpoint `@router.get("/cierre/{cierre_id}")` (líneas 27-108) el cual genera y retorna un StreamingResponse de tipo `text/csv`.
    > *Nota:* Se mantendrá intacto el endpoint de Excel `@router.get("/cierre/{cierre_id}/excel")` (línea 242) que realiza la misma exportación de forma mucho más formateada.
*   **Eliminar Endpoint de Comparativa CSV:**
    Remover por completo el endpoint `@router.get("/comparacion/{cierre1_id}/{cierre2_id}")` (líneas 111-238).
    > *Nota:* Se mantendrán intactos los endpoints `@router.get("/comparacion/{cierre1_id}/{cierre2_id}/excel")` y `/excel-ricoh`.

#### 🔴 Archivo a Modificar: [backend/scripts/test_exportaciones.py](file:///c:/Users/juan.lizarazo/Desktop/ricoh/backend/scripts/test_exportaciones.py)
*   **Eliminar Test Unitario:**
    Eliminar la función `test_exportacion_csv_simulada(db: Session)` (línea 128) y remover su registro del diccionario de pruebas para que la suite de testeo no busque referencias CSV al ser ejecutada.

---

### 2. Frontend Services & Utils (React & TypeScript)

En la capa de lógica del cliente, se deben retirar las utilidades de generación de strings CSV y los métodos de consumo del servicio de exportación.

#### 🔴 Archivo a Modificar: [src/utils/exportUtils.ts](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/utils/exportUtils.ts)
*   **Eliminar Funciones CSV:**
    Remover las funciones exportadas:
    - `exportChartDataToCSV` (línea 12)
    - `exportTableToCSV` (línea 28)
*   *Nota:* Se mantendrán las funciones `exportTableToExcel`, `exportReportToPDF` y `copyChartDataToClipboard` (esta última usa tabulaciones para portapapeles, lo cual no interfiere con archivos CSV físicos).

#### 🔴 Archivo a Modificar: [src/services/exportService.ts](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/services/exportService.ts)
*   **Eliminar Métodos CSV:**
    Eliminar del objeto `exportService` los métodos:
    - `exportCierreCSV` (línea 78)
    - `exportComparacionCSV` (línea 98)

---

### 3. Componentes e Interfaz de Usuario (React Views)

Se deben remover los botones, opciones y handlers que invocaban las descargas de archivos CSV.

#### 🔴 Vista a Modificar: [src/pages/AnalyticsPage.tsx](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/pages/AnalyticsPage.tsx)
*   **Importaciones:** Remover `exportTableToCSV` de la importación de `exportUtils`.
*   **Handlers a Eliminar:**
    - `handleExportCSV` (línea 214)
    - `handleExportUsersCSV` (línea 219)
*   **Elementos de UI a Eliminar:**
    - Botón de descarga de CSV de datos generales del gráfico (líneas 438-442).
    - Botón de "Exportar CSV" de la lista de consumo de usuarios (líneas 554-560).
    *   *Nota:* Asegurarse de mantener los botones homólogos de **Exportar Excel** / **PDF** intactos.

#### 🔴 Vista a Modificar: [src/components/contadores/cierres/ComparacionPage.tsx](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/components/contadores/cierres/ComparacionPage.tsx)
*   **Handlers:** Remover la lógica del bloque `case 'csv'` dentro del menú de exportaciones (líneas 534-536).
*   **UI:** Eliminar el botón o item de dropdown de tipo `CSV` (línea 544).

#### 🔴 Modal a Modificar: [src/components/contadores/cierres/ComparacionModal.tsx](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/components/contadores/cierres/ComparacionModal.tsx)
*   **Handlers:** Eliminar la llamada `exportService.exportComparacionCSV` y el toast de éxito correspondiente (líneas 462-464).
*   **UI:** Eliminar el botón con etiqueta `CSV` en el panel de acciones de exportación (línea 470).

#### 🔴 Modal a Modificar: [src/components/contadores/cierres/CierreDetalleModal.tsx](file:///c:/Users/juan.lizarazo/Desktop/ricoh/src/components/contadores/cierres/CierreDetalleModal.tsx)
*   **Handlers:** Eliminar el bloque de try/catch que llama a `exportService.exportCierreCSV` (líneas 418-423).
*   **UI:** Eliminar el botón de "Exportar CSV" en las acciones del pie de página del modal (línea 426).

---

## 🚦 Plan de Validación y Verificación

Una vez que se hayan eliminado todas las referencias a CSV:

1.  **Validar Compilación de TypeScript:**
    Ejecutar en la carpeta `ricoh/`:
    ```bash
    npm run build
    ```
    *Criterio de éxito:* La compilación debe ser 100% exitosa sin errores de dependencias de tipos (`tsc`) o referencias faltantes en las vistas.
2.  **Validar Tests del Backend:**
    Correr las pruebas automatizadas del servidor:
    ```bash
    docker exec -it ricoh-backend pytest
    ```
    *Criterio de éxito:* Todos los tests del backend deben pasar exitosamente.
3.  **Verificación Visual:**
    Ingresar al frontend, abrir los paneles de Cierres y Analytics, y confirmar visualmente que **solo** figuran los botones de **Excel / PDF / XLS / XLSX**, habiendo desaparecido la opción CSV por completo.
