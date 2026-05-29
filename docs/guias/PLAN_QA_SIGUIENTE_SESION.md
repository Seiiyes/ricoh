# Plan de Control de Calidad (QA) y Guía de Continuidad para la Siguiente Sesión

> [!IMPORTANT]
> **Accesibilidad de este Documento:** Este archivo está disponible en el repositorio del proyecto en `docs/guias/PLAN_QA_SIGUIENTE_SESION.md`. Garantiza disponibilidad total e inmediata en la siguiente sesión de desarrollo.

> [!NOTE]
> **Estado al 29 Mayo 2026:** El **Bloque A (verificaciones automatizadas)** fue ejecutado y **pasó al 100%** durante la sesión del 29 mayo 2026. Los bloques B y C (pruebas manuales en browser) **siguen pendientes** y son la prioridad de la próxima sesión.

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
* **Credenciales Reales del Sistema (superadmin):**
  - **Usuario Superadmin:** `superadmin` / `Admin1234!` (rol: `superadmin`, sin empresa_id)
  - **Usar este usuario** para pruebas de escritura (guardar comparaciones, exportar, etc.)

> [!WARNING]
> Las credenciales de prueba `admin@ricoh.com / admin123` y `test_user_a@empresa1.com` eran placeholders de diseño. **Usar `superadmin / Admin1234!`** para todas las pruebas de esta sesión.

---

## 2. Bloque Técnico A: Verificaciones Automatizadas ✅ COMPLETADO (29 Mayo 2026)

> [!NOTE]
> Estas verificaciones ya fueron ejecutadas el 29 de mayo de 2026 con resultados exitosos. Se incluyen aquí como referencia para futuras sesiones.

### ✅ Tarea A.1: Estado y Conectividad de los Contenedores — PASÓ
```bash
docker compose ps
```
**Resultado obtenido (29/05/2026):** Los 5 contenedores `ricoh-backend` (healthy), `ricoh-frontend` (Up), `ricoh-postgres` (healthy), `ricoh-redis` (healthy) y `ricoh-adminer` (Up) — todos operativos.

### ✅ Tarea A.2: Integridad del Esquema y Índices — PASÓ
```bash
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "\d comparaciones_guardadas"
```
**Resultado:** Tabla con 10 columnas, 5 índices y 4 foreign keys. Columnas presentes: `id`, `titulo`, `descripcion`, `cierre1_id`, `cierre2_id`, `snapshot_json`, `creado_por`, `admin_user_id`, `empresa_id`, `created_at`.

```bash
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "SELECT indexname FROM pg_indexes WHERE tablename = 'cierres_mensuales_usuarios';"
```
**Resultado:** Índice `idx_cierres_usuarios_cierre_consumo` presente y activo ✅

### ✅ Tarea A.3: Prueba de Aislamiento de Datos (Multi-Tenancy) — PASÓ
```powershell
try { Invoke-RestMethod -Uri "http://localhost:8000/api/counters/comparaciones" -Method Get } catch { $_.Exception.Response.StatusCode.value__ }
```
**Resultado:** `403` — Forbidden. Aislamiento multi-tenant funcionando correctamente ✅

---

## 3. Bloque Técnico B: Pruebas Funcionales en la UI — ⏳ PENDIENTE

Siga esta secuencia paso a paso directamente en el navegador (`http://localhost:5173`).

**Login:** Usar `superadmin / Admin1234!`

### 🧪 Tarea B.1: Flujo Completo de Comparaciones Guardadas (Módulo Cierres)

| ID | Acción de Prueba | Detalle Visual a Validar | Resultado Esperado | ¿Pasó? |
|---|---|---|---|:---:|
| **B.1.1** | **Ingreso a Cierres:** Login con `superadmin` e ingreso al panel de Cierres. | El diseño debe cargar con tipografía limpia (Inter) y fondo glassmorphic. | Carga en menos de 1 segundo sin saltos visuales. | [ ] |
| **B.1.2** | **Seleccionar Períodos:** Seleccione un equipo activo y dos cierres de meses consecutivos. | La tabla debe mostrar diferencias en verde (ahorro) o rojo (incremento). | Todos los textos alineados, sin desbordamientos de columnas. | [ ] |
| **B.1.3** | **Guardar Comparación:** Clic en el botón superior **"💾 Guardar comparación"**. | Modal con efecto `backdrop-blur-md` y título autogenerado con las fechas. | Se abre fluida y suavemente. | [ ] |
| **B.1.4** | **Completar Formulario:** Escriba un título y descripción, presione "Guardar". | Toast Sileo de carga y luego Toast de éxito en la parte superior. | El modal se cierra automáticamente tras guardado exitoso. | [ ] |
| **B.1.5** | **Ver Historial:** En la sección de acordeón **"Historial de Comparaciones Guardadas"**. | La comparación recién guardada debe aparecer al inicio de la lista. | Se actualiza en caliente sin requerir F5. | [ ] |
| **B.1.6** | **Carga de Snapshot:** Clic en el botón **"Ver"** del registro en el historial. | La app carga los datos exactos del snapshot inmutable en la tabla. | La UI refleja idénticamente los valores almacenados. | [ ] |
| **B.1.7** | **Eliminación en Caliente:** Clic en el icono de papelera (`Trash2`). | Toast de confirmación Sileo. Al aceptar, el registro desaparece con fade. | El registro se elimina en frontend y en `comparaciones_guardadas` de PostgreSQL. | [ ] |

---

### 🧪 Tarea B.2: Analytics y Desglose Tridimensional de Consumo

| ID | Acción de Prueba | Detalle Visual a Validar | Resultado Esperado | ¿Pasó? |
|---|---|---|---|:---:|
| **B.2.1** | **Ingreso a Analytics:** Navegar al panel de **Analytics**. | Tarjetas superiores de métricas con bordes y sombras premium. | Carga del panel completo y llamadas API exitosas (sin errores 500). | [ ] |
| **B.2.2** | **Gráfico de Distribución Real:** Gráfico circular de **Resumen General de Consumo**. | El gráfico refleja porcentajes **reales y dinámicos** de la DB. | Eliminados los valores dummy prefijados (70%, 20%, 10%). | [ ] |
| **B.2.3** | **Tarjeta Top 5 Consumidores:** Listado del ranking de los 5 usuarios con más páginas. | Nombre, volumen total y **barra de progreso con gradiente** fluida. | Visualmente armonioso, barras responsivas. | [ ] |
| **B.2.4** | **Filtros Reactivos:** Cambiar filtros de rango de fechas y búsqueda por nombre. | El listado reacciona instantáneamente filtrando los datos. | Filtrado reactivo sin colapsos y manteniendo el estado de filtros. | [ ] |
| **B.2.5** | **Desglose Expandible:** Clic sobre cualquier fila del listado de consumo. | La fila se expande con panel glassmorphic y fondo difuminado. | Transición fluida (sin saltos tipográficos). | [ ] |
| **B.2.6** | **Métricas Tridimensionales:** Analice los datos del sub-panel expandido. | Distribución B/N vs Color y métricas por función (Copiadora, Impresora, Escáner, Fax). | Datos numéricos correctos (o `0` si son nulos) sin romper la UI. | [ ] |
| **B.2.7** | **Botón Exportar Excel:** Clic en el botón "Exportar Excel" en la sección de usuarios. | El botón ya **no dice "CSV"** — dice "Excel". El archivo descargado es `.xlsx`. | Descarga exitosa de archivo `.xlsx` con todos los registros. | [ ] |

---

## 4. Bloque Técnico C: Pruebas de Resiliencia y Edge Cases — ⏳ PENDIENTE

### 🧪 Tarea C.1: Valores de Consumo Nulos o Parciales
* **Procedimiento:** Buscar un usuario que solo imprime en B/N y no usa copiadora/escáner.
* **Resultado Esperado:** La fila expandida en Analytics muestra `0` o `-` de forma ordenada. **No pantalla blanca** ni excepción en consola del desarrollador.

### 🧪 Tarea C.2: Gestión de Cadenas Largas y Caracteres Especiales
* **Procedimiento:** En el modal de guardar comparación, ingresar un título con más de 100 caracteres y emojis (ej: `Comparativa Ricoh Master Principal 🚀 - Q1 - Edificio 3 Piso 2 Centralizada de Contabilidad $$$ 12345`).
* **Resultado Esperado:**
  - El backend guarda exitosamente (máx 200 chars en el campo `titulo`).
  - La tarjeta en el historial trunca el texto con `...` (text-ellipsis) sin deformar la cuadrícula.

### 🧪 Tarea C.3: Cancelación de Modales
* **Procedimiento:** Abrir el modal de guardado, escribir un título, y luego hacer clic fuera del modal (backdrop) o presionar `Escape`.
* **Resultado Esperado:** El modal se cierra sin enviar ninguna petición al backend. Al reabrirlo, el formulario está limpio.

### 🧪 Tarea C.4: Exportación Excel (nuevo — CSV ya eliminado)
* **Procedimiento:** En `CierreDetalleModal`, hacer clic en "Exportar Excel". En `ComparacionPage`, verificar que **solo** aparecen botones "Excel Ricoh" y "Excel Simple" (sin botón CSV).
* **Resultado Esperado:** Descarga exitosa de `.xlsx`. No existe ningún botón "CSV" en toda la interfaz.

---

## 5. Script de Limpieza de Datos QA

Si desea resetear los datos generados durante las pruebas:

```bash
docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "DELETE FROM comparaciones_guardadas WHERE titulo LIKE 'Comparativa%' OR descripcion LIKE '%Prueba%';"
```

**Resultado Esperado:** Mensaje `DELETE N`. El historial en la web queda vacío al refrescar.

---

## 6. Verificación Pre-Commit (Script Automatizado)

Para verificar que los cambios de la sesión son correctos antes de commitear:

```bash
docker exec ricoh-backend python /app/verify_session_29mayo.py
```

**Resultado Esperado:** `=== TODOS LOS CHECKS PASARON - LISTO PARA COMMIT ===` (10/10 checks) ✅

---

## 7. Tarea Pendiente Prioritaria para la Próxima Sesión

### Dashboard — Widgets Premium (Fase 2B)
Ver detalles en `task.md`:
1. **AreaChart evolución** — integrar `useEvolutionData` en `OverviewDashboard.tsx`
2. **Widget "Ricoh Green"** — árboles, CO2, agua (glassmorphism)
3. **Fleet Operations Desk** — equipos offline, alertas tóner < 15%, SNMP vs HTTP

### SNMP/HTTP Fallback
- Validación activa puerto 161
- Parser HTTP: `getDeviceStatus.cgi` + `configuration.cgi`
- Indicador visual: "📡 Monitoreado vía HTTP (SNMP Inactivo)"

---

## 8. Firma y Aceptación de Pruebas

* **Responsable de la Sesión:** [Espacio para Desarrollador/QA de la siguiente sesión]
* **Fecha de Ejecución:** [DD-MM-YYYY]
* **Estatus Bloque A:** ✅ APROBADO (29/05/2026)
* **Estatus Bloque B:** `[ ] APROBADO / [ ] RECHAZADO`
* **Estatus Bloque C:** `[ ] APROBADO / [ ] RECHAZADO`
* **Notas Adicionales de Feedback:**

