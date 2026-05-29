# Plan de Control de Calidad (QA) y Guía de Continuidad para la Siguiente Sesión

> [!IMPORTANT]
> **Accesibilidad de este Documento:** Para evitar restricciones de acceso por sandboxing entre sesiones independientes, este archivo ha sido guardado tanto en el directorio de la conversación actual (`brain`) como en la carpeta del repositorio del proyecto en [docs/documentacion_siguiente_sesion.md](file:///c:/Users/juan.lizarazo/Desktop/ricoh/docs/documentacion_siguiente_sesion.md) y [docs/PLAN_QA_SIGUIENTE_SESION.md](file:///c:/Users/juan.lizarazo/Desktop/ricoh/docs/PLAN_QA_SIGUIENTE_SESION.md). Esto garantiza disponibilidad total e inmediata en la siguiente sesión de desarrollo.

Este plan detallado está estructurado para que el equipo de control de calidad (QA) y el desarrollador entrante puedan ejecutar **pruebas rápidas, automatizadas e interactivas** con la máxima eficiencia posible.

---

## 1. Estado del Sistema y Credenciales de Prueba

Antes de iniciar las pruebas, asegúrese de tener configurado el entorno local con los siguientes datos:

* **Dirección del Backend:** `http://localhost:8000` (Documentación Interactiva Swagger en `http://localhost:8000/docs`)
* **Dirección del Frontend (Desarrollo):** `http://localhost:5173`
* **Base de Datos Postgres (Docker):**
  - **Host/Container:** `ricoh-postgres`
  - **Puerto Local:** `5432`
  - **Base de Datos:** `ricoh_fleet`
  - **Usuario:** `ricoh_admin`
  - **Contraseña:** `ricoh_secure_2024`
* **Credenciales de Prueba (Frontend/API):**
  - **Usuario Admin:** `admin@ricoh.com` / `admin123` (Empresa ID: `1`)
  - **Usuario Empresa A:** `test_user_a@empresa1.com` / `password123` (Empresa ID: `1`)
  - **Usuario Empresa B (Para verificar Multi-Tenancy):** `test_user_b@empresa2.com` / `password123` (Empresa ID: `2`)

---

## 2. Bloque Técnico A: Verificaciones Automatizadas en Base de Datos y Backend (CLI)

Ejecute los siguientes scripts de verificación desde su terminal PowerShell o Bash para comprobar de forma rápida que la infraestructura está funcionando correctamente.

### 🧪 Tarea A.1: Estado y Conectividad de los Contenedores
Ejecute la siguiente línea para comprobar que los 5 contenedores principales de la suite Ricoh estén arriba y saludables:
```bash
docker compose ps
```
* **Resultado Esperado:** `ricoh-backend`, `ricoh-frontend`, `ricoh-postgres`, `ricoh-redis` y `ricoh-adminer` deben tener el estado `Up` o `healthy`.

### 🧪 Tarea A.2: Integridad del Esquema y Nuevos Índices de Rendimiento
Acceda a la base de datos y consulte la estructura para validar la inyección de la migración `017_comparaciones_guardadas.sql`:
```bash
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "\d comparaciones_guardadas"
```
* **Resultado Esperado:** El motor debe retornar la descripción de la tabla `comparaciones_guardadas` con las columnas `id`, `empresa_id`, `usuario_id`, `nombre`, `descripcion`, `cierre_id_base`, `cierre_id_comparado`, `fecha_creacion`, `desglose_snapshot` y los constraints de llaves foráneas asignados.

Consulte que el índice compuesto optimizado para búsquedas por usuario esté activo:
```bash
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'cierres_mensuales_usuarios';"
```
* **Resultado Esperado:** Debe listarse el índice `idx_cierres_usuarios_cierre_consumo` estructurado sobre las columnas `(cierre_mensual_id, usuario_id)`.

### 🧪 Tarea A.3: Prueba de Aislamiento de Datos (Multi-Tenancy)
Para asegurar que un usuario de la Empresa A no pueda acceder bajo ningún concepto a las comparaciones de la Empresa B, pruebe la restricción del backend enviando una consulta sin token o con token ajeno:
```powershell
# Intento de acceso sin autenticación
Invoke-RestMethod -Uri "http://localhost:8000/api/counters/comparaciones" -Method Get -SkipHttpErrorCheck
```
* **Resultado Esperado:** La respuesta HTTP debe ser estrictamente `401 Unauthorized` o `403 Forbidden` con detalle `Not authenticated` o similar.

---

## 3. Bloque Técnico B: Pruebas Funcionales e Interactivas de la UI

Siga esta secuencia paso a paso directamente en el navegador (`http://localhost:5173`) para garantizar la excelencia en la experiencia de usuario y el cumplimiento de las directrices visuales premium.

### 🧪 Tarea B.1: Flujo Completo de Comparaciones Guardadas (Módulo Cierres)

| ID | Acción de Prueba | Detalle Visual a Validar | Resultado Esperado | ¿Pasó? |
|---|---|---|---|:---:|
| **B.1.1** | **Ingreso a Cierres:** Inicie sesión con `test_user_a@empresa1.com` e ingrece al panel de Cierres. | El diseño debe cargar con tipografía limpia (Inter) y un fondo glassmorphic adaptativo. | Carga en menos de 1 segundo sin saltos visuales bruscos. | [ ] |
| **B.1.2** | **Seleccionar Períodos:** Seleccione un equipo activo y dos cierres de meses consecutivos en la vista comparativa. | La tabla detallada debe renderizar las diferencias de contadores en verde (si es ahorro) o rojo (si es incremento). | Todos los textos alineados, sin desbordamientos de columnas. | [ ] |
| **B.1.3** | **Guardar Comparación:** Haga clic en el botón superior **"💾 Guardar comparación"** que posee el icono `Save` de Lucide. | Debe desplegarse el modal con efecto `backdrop-blur-md` (desenfoque de fondo) y un título autogenerado consistente con las fechas. | Se abre de manera fluida y suave en pantalla. | [ ] |
| **B.1.4** | **Completar Formulario:** Escriba un título alternativo ("Comparativa Q1 Ricoh Principal") y una descripción breve, y presione "Guardar". | Se debe invocar la API asíncronamente mostrando el Toast de carga y luego el **Toast de éxito de Sileo** en la parte superior. | El modal se cierra automáticamente tras el guardado exitoso. | [ ] |
| **B.1.5** | **Ver Historial:** Al pie de la vista de cierres, localice la sección de acordeón **"Historial de Comparaciones Guardadas"**. | La comparación recién guardada debe figurar al inicio de la lista con su título, fecha de creación y descripción. | Se actualiza en caliente inmediatamente sin requerir F5 (recarga del navegador). | [ ] |
| **B.1.6** | **Carga de Snapshot:** Haga clic en el botón **"Ver"** del registro de la comparación en el historial. | La aplicación debe redirigir dinámicamente y cargar los datos exactos del snapshot inmutable de inmediato en la tabla de comparación. | La UI refleja de forma idéntica los valores almacenados previamente. | [ ] |
| **B.1.7** | **Eliminación en Caliente:** Haga clic en el icono de papelera (`Trash2`) al lado del registro en el historial. | Se debe disparar un Toast de confirmación de Sileo. Al aceptar, el registro desaparece con una transición de desvanecimiento fluida. | El registro se elimina tanto en el frontend como en la tabla `comparaciones_guardadas` de PostgreSQL. | [ ] |

---

### 🧪 Tarea B.2: Revolución de Analytics y Desglose Tridimensional de Consumo

| ID | Acción de Prueba | Detalle Visual a Validar | Resultado Esperado | ¿Pasó? |
|---|---|---|---|:---:|
| **B.2.1** | **Ingreso a Analytics:** Navegue al panel de **Analytics** en el menú de navegación principal. | Las tarjetas superiores de métricas clave deben mostrar información estructurada en bloques con bordes sutiles y sombras premium. | Carga del panel completo y llamadas API exitosas. | [ ] |
| **B.2.2** | **Gráfico de Distribución Real:** Observe el gráfico circular de **Resumen General de Consumo**. | El gráfico debe calcular y reflejar porcentajes **reales y dinámicos** basados en el consumo real cargado en base de datos. | Quedaron 100% eliminados los valores dummy prefijados (70%, 20%, 10%). | [ ] |
| **B.2.3** | **Tarjeta Top 5 Consumidores:** Revise el listado del ranking de los Top 5 usuarios que consumen más páginas. | Cada fila del ranking debe incluir el nombre del usuario, volumen total y una **barra de progreso con gradiente** fluida. | Visualmente armonioso y fácil de leer. Las barras de progreso deben llenarse de forma responsiva. | [ ] |
| **B.2.4** | **Filtros Reactivos:** Cambie los filtros superiores de rango de fechas, impresora específica y el campo de búsqueda rápida por nombre. | El listado de usuarios debe reaccionar de forma instantánea filtrando los datos en pantalla localmente o mediante consulta al backend. | Filtrado reactivo sin colapsos de UI y manteniendo el estado de los filtros. | [ ] |
| **B.2.5** | **Desglose Expandible:** Haga clic sobre cualquier fila del listado de consumo de usuarios. | La fila debe expandirse suavemente hacia abajo revelando un panel contenedor con efecto glassmorphic y fondo difuminado. | Transición fluida de apertura (mínimo delay, sin saltos tipográficos). | [ ] |
| **B.2.6** | **Métricas Tridimensionales de Consumo:** Analice los datos mostrados en el sub-panel expandido de la fila de usuario. | Debe mostrarse la distribución de páginas: B/N vs Color (barra comparativa) y las métricas detalladas por función (Copiadora, Impresora, Escáner, Fax). | Las métricas muestran datos numéricos correctos (o '-' / '0' si el valor nulo) sin romper la UI. | [ ] |

---

## 4. Bloque Técnico C: Pruebas de Resiliencia, Casos Límite y Edge Cases

Para garantizar que el código escrito sea altamente resiliente en producción, QA debe ejecutar los siguientes escenarios extremos:

### 🧪 Tarea C.1: Valores de Consumo Nulos o Parciales en Base de Datos
* **Procedimiento:** Si un usuario tiene registros de consumo de impresora en blanco (nulos) porque no usa la copiadora ni el escáner (lo cual ocurre comúnmente en usuarios administrativos que solo imprimen en B/N):
* **Resultado Esperado:** La fila expandida en el listado de consumo de Analytics debe renderizar `0` o `-` de forma ordenada, en lugar de crasear la interfaz (pantalla blanca) o lanzar excepciones de tipo en la consola del desarrollador. (Validado mediante tipos TypeScript opcionales/nulos en `TablaComparacionSimplificada.tsx`).

### 🧪 Tarea C.2: Gestión de Cadenas Largas y Caracteres Especiales
* **Procedimiento:** Al guardar una comparación en el modal, introduzca un título con más de 100 caracteres y emojis (ej: `Comparativa Ricoh Master Principal 🚀 - Q1 - Edificio 3 Piso 2 Centralizada de Contabilidad $$$ 12345`).
* **Resultado Esperado:**
  - El backend debe sanitizar e ingresar la información de forma exitosa.
  - La tarjeta de historial en el frontend debe truncar el texto con puntos suspensivos (`text-ellipsis`) de manera estética, evitando que el texto largo deforme la cuadrícula del panel.

### 🧪 Tarea C.3: Concurrencia y Cancelación de Modales
* **Procedimiento:** Abra el modal de guardado, escriba un título de prueba, y luego haga clic fuera del modal (backdrop click) o presione la tecla `Escape`.
* **Resultado Esperado:** El modal debe cerrarse limpiamente sin enviar ninguna petición al backend y sin dejar estados colgados en el frontend. Al volver a abrirlo, el formulario debe reiniciarse limpio.

---

## 5. Script de Reinicio y Mantenimiento de QA (Limpieza Rápida)

Si desea resetear los datos generados durante su sesión de pruebas de control de calidad para iniciar una nueva iteración de QA limpia, ejecute el siguiente comando que elimina las comparaciones registradas en base de datos de forma directa:

```bash
docker exec -it ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "DELETE FROM comparaciones_guardadas WHERE nombre LIKE 'Comparativa%' OR descripcion LIKE '%Prueba%';"
```

* **Resultado Esperado:** Mensaje indicando `DELETE N` (donde N es el número de registros creados en sus pruebas). El historial en la web volverá a quedar vacío de inmediato al refrescar.

---

## 6. Tarea Pendiente Destacada: Eliminación de CSV (Consolidación de Excel XLS/XLSX)

Como directriz crítica para la siguiente sesión, el cliente ha solicitado **eliminar por completo el formato CSV** del sistema y basar todas las exportaciones exclusivamente en Excel (.xls / .xlsx). Para mantener la compatibilidad operativa temporal en esta sesión de QA, se conservaron intactos los endpoints CSV de backend y los botones en frontend, pero se estructuró un plan de acción definitivo:

*   **Documento Técnico del Plan:** [PLAN_ELIMINACION_CSV.md](file:///c:/Users/juan.lizarazo/Desktop/ricoh/docs/desarrollo/planes/PLAN_ELIMINACION_CSV.md)
*   **Acciones Pendientes para la Próxima Sesión:**
    1.  Eliminar endpoints `/api/export/cierre/{id}` y `/api/export/comparacion/{id1}/{id2}` del backend (`backend/api/export.py`).
    2.  Remover los botones y handlers de exportación CSV en `AnalyticsPage.tsx`, `ComparacionPage.tsx`, `ComparacionModal.tsx` y `CierreDetalleModal.tsx`.
    3.  Limpiar utilidades CSV en `exportUtils.ts` y métodos en `exportService.ts`.
    4.  Asegurar que la compilación siga siendo limpia (`npm run build`) y que no existan dependencias rotas.

---

## 7. Firma y Aceptación de Pruebas de Regresión
* **Responsable de la Sesión:** [Espacio para Desarrollador/QA de la siguiente sesión]
* **Fecha de Ejecución:** [DD-MM-YYYY]
* **Estatus de Salida:** `[ ] APROBADO / [ ] RECHAZADO`
* **Notas Adicionales de Feedback:**

---

## 8. Tarea Pendiente Destacada: Expansión de Dashboard Premium y Validación SNMP/HTTP de Flota

En esta sesión se planificó y estructuró completamente la expansión del dashboard y los servicios de monitoreo de red de impresoras:

*   **Documento Técnico del Plan:** [PLAN_EXPANSION_DASHBOARD.md](file:///c:/Users/juan.lizarazo/Desktop/ricoh/docs/desarrollo/planes/PLAN_EXPANSION_DASHBOARD.md)
*   **Checklist de Tareas Completo:** [TAREAS_EXPANSION_DASHBOARD.md](file:///c:/Users/juan.lizarazo/Desktop/ricoh/docs/desarrollo/planes/TAREAS_EXPANSION_DASHBOARD.md) (y la copia en los artefactos del sistema de la sesión: [task.md](file:///C:/Users/juan.lizarazo/.gemini/antigravity-ide/brain/3555d2fe-dc2c-4fc9-bc04-b823c27ba0ed/task.md))
*   **Acciones Pendientes para la Próxima Sesión:**
    1.  **Corrección en el Backend:** Agregar `from db.models import Printer` a `backend/api/dashboard.py` para solucionar el error `NameError: Printer` en `/toner-alertas`.
    2.  **Hook de Tendencia:** Implementar `useEvolutionData` en el frontend apuntando a `/api/v1/analytics/evolution?meses=6`.
    3.  **Visualizaciones Premium (Frontend):** Diseñar el gráfico de evolución analítica (`AreaChart` con degradado), el panel ecológico (Árboles, CO2, Agua) y el Operations Desk para diagnosticar de forma interactiva equipos offline o con tóner crítico (<15%).
    4.  **Validación SNMP y Fallback HTTP:** Implementar la validación activa en el puerto 161 de la impresora y el parser de raspado HTTP (Web Image Monitor) de Ricoh en el backend si SNMP está inactivo.

