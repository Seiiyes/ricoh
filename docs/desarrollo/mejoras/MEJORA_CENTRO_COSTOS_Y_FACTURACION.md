# Mejora: Autocompletado de Centros de Costos y Reporte de Facturación Jerárquico

**Fecha de Implementación:** 3 de Junio de 2026
**Módulo:** Suministros, Analítica y Usuarios

---

## 1. Contexto y Objetivos

El sistema carecía de una manera estandarizada y normalizada de ingresar los **Centros de Costos** (o Áreas) a las cuales pertenecían los usuarios. Al ser un campo de texto libre, existía un alto riesgo de inconsistencias tipográficas (ej. "OPERACIONES", "operaciones", "Operaciones"), afectando la generación de reportes posteriores.
Además, se requería implementar un **Reporte Final de Facturación** para proveedores con un desglose altamente detallado y en formato de tabla dinámica o esquema plegable en Excel.

**Objetivos principales:**
1. Crear un componente UI para seleccionar o crear un Centro de Costos de manera guiada.
2. Limitar o agrupar sugerencias de Centro de Costos basados en la Empresa del usuario actual, pero ofrecer acceso a las áreas globales creadas por otras empresas.
3. Generar un exportable de Excel (Reporte de Facturación) que estructure la jerarquía: `Empresa -> Centro de Costos -> Usuario -> Impresora` con capacidades de colapso visual (`+` / `-`).

---

## 2. Desarrollo: Autocompletado de Centro de Costos

### Backend: Extracción de Áreas
Se diseñó un nuevo endpoint que obtiene el listado de áreas ya existentes en base al registro histórico de usuarios de cada empresa:

- **Endpoint:** `GET /api/empresas/{empresa_id}/centro-costos`
- **Archivo:** `backend/api/empresas.py`
- **Lógica:**
  - Extrae las áreas (`CentroCosto`) asociadas a los usuarios de la `empresa_id` objetivo (Sugerencias **Propias**).
  - Extrae las áreas asociadas a usuarios de otras empresas (Sugerencias **Globales**).
  - Garantiza unicidad para evitar duplicados en la interfaz de usuario.

### Frontend: UI Inteligente
Se desarrolló el componente `CentroCostosAutocomplete.tsx` tomando inspiración del componente de Empresa.
- **Componente:** `src/components/ui/CentroCostosAutocomplete.tsx`
- **Comportamiento:**
  - Solo se activa si se ha seleccionado previamente una **Empresa** (dependencia de datos).
  - Muestra un listado ordenado categorizado en "Propias de la empresa" y "Sugerencias Globales".
  - Si el usuario escribe una nueva área (ej. "AUDITORIA INTERNA") y no se encuentra coincidencia, el componente habilita el botón "**+ Agregar**", permitiendo la creación de nuevos centros al vuelo.
  - El backend se encarga de instanciar y guardar este nuevo `CentroCosto` en base de datos si es que no existe al momento de guardar al Usuario.

---

## 3. Desarrollo: Reporte Jerárquico de Facturación

Para la facturación a proveedores, se solicitó replicar un reporte que asemeje el comportamiento de una Tabla Dinámica nativa en Excel.

### Backend: Generador de Excel y Outline Levels
Se desestimó el uso de librerías front-end de JS por limitaciones técnicas y se delegó el trabajo al servidor usando la potente librería `openpyxl`.

- **Servicio:** `backend/services/export_facturacion.py`
- **Endpoint:** `GET /api/export/facturacion/{empresa_id}`
- **Lógica del Algoritmo:**
  1. Extrae todas las impresoras de la empresa.
  2. Extrae todos los cierres mensuales correspondientes al rango de fechas (`fecha_inicio`, `fecha_fin`).
  3. Carga el consumo total de páginas impresas por cada usuario, cruzando las llaves foráneas.
  4. Genera un diccionario anidado estructurando `Área -> Usuario -> Impresora`.
  5. Crea una primera hoja resumen de consumo por máquina (impresoras con más uso).
  6. Crea una segunda hoja llamada "Desglose Facturación" utilizando la propiedad `ws.row_dimensions[row].outline_level = X`.
  7. Aplica propiedades ocultas por defecto (`ws.row_dimensions[row].hidden = True`) a los niveles de Usuario e Impresora, asegurando que el Excel nazca "contraído" a nivel Área para mayor orden.

### Frontend: Inyección en Analítica
Se integró esta capacidad de generación en el panel general:
- **Pantalla:** `src/pages/AnalyticsPage.tsx`
- **Cambios realizados:**
  - Se removió el texto harcodeado `"Empresa: Ricoh Global"`.
  - Se agregó el `EmpresaAutocomplete` en los filtros superiores.
  - Se agregó un botón de exportación dedicado (verde) llamado **Exportar Facturación**, el cual captura la empresa y las fechas para iniciar la descarga del blob de Excel.

---

## 4. Impacto

1. **Estandarización de BD:** El uso de centros de costos está ahora semi-restringido por la interfaz y altamente orientado a la reutilización, cortando de raíz la proliferación de áreas escritas de distinta forma ("TI", "Sistemas", "TIC").
2. **Exportación Autónoma:** Los administradores ya no necesitan procesar el listado plano mensual de usuarios ni generar sus propias tablas dinámicas para facturar. El sistema hace todo el trabajo y entrega el documento de Excel listo para reenviar a los proveedores (Auditorías de Terceros).
3. **Escalabilidad Visual:** Analítica ahora soporta segregación y partición de reportes por la empresa `empresaId`, habilitando análisis multi-tenant reales en un mismo servidor.
