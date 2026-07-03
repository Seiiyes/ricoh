# Changelog - Ricoh Suite

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [2.7.0] - 2026-07-02

### 🐛 Fixed — Bugs Críticos en Módulo de Usuarios

- **React Error #31 — `createPortal` bloqueaba todos los clics** — `ModificarUsuario.tsx` usaba `createPortal(JSX, document.body)` que en el bundle de producción (Vite + esbuild) generaba un crash silencioso del árbol de componentes, deshabilitando todos los event listeners de la página. Solución: retornar JSX directamente usando clases `fixed inset-0 z-50` que posicionan el modal flotante sin necesidad de portal.
- **`window.confirm()` bloqueado por Chrome en HTTP** — El diálogo de confirmación de desactivación nunca se mostraba porque Chrome bloquea silenciosamente `window.confirm()` en páginas servidas por HTTP. Solución: reemplazado por modal de confirmación propio en React con overlay, nombre del usuario, botones Cancelar / Sí-desactivar y spinner durante el proceso.
- **Asignaciones duplicadas en BD para usuario 7104** — Eliminados 5 registros duplicados de `user_printer_assignments` mediante `deployment/deduplicate_assignments.py`. La selección de impresoras en el modal de edición ahora se basa en el `id` único de la asignación (no en `printer_id`) para evitar colisiones entre impresoras del mismo modelo.

### ✨ Added — Mejoras de UX

- **Filtro de estado como toggle opcional** — Los botones "Activos" e "Inactivos" ahora son deseleccionables. Por defecto (al entrar) se muestran **todos** los usuarios. Un usuario es activo si tiene ≥1 permiso en ≥1 impresora.
- **Estado visual de desactivación por fila** — Al desactivar un usuario, solo su fila se bloquea y el botón cambia a `🔄 Desactivando...` (rojo coral, `animate-spin`). Elimina la pantalla de carga global y previene envíos duplicados.
- **Notificaciones flotantes en guardado** — `ModificarUsuario.tsx` ahora usa `useNotification` para emitir alertas premium con detalle de qué acción se realizó (guardar perfil, sincronizar permisos base a todas las impresoras, aplicar permisos en impresora específica, errores parciales).
- **Interceptor JWT con refresco transparente** — `apiClient.ts` ahora encola peticiones fallidas por token expirado, refresca el JWT vía `/auth/refresh` y las reintenta de forma transparente, eliminando redirecciones abruptas al login.

---

## [2.6.0] - 2026-06-01


### ✨ Added

- **Vista Consolidada de Consumo de Usuarios** — Implementado un sistema de agregación dinámica en el frontend (`AnalyticsPage.tsx`) que consolida los consumos mensuales de usuarios que utilizan múltiples equipos (por ejemplo, hasta 5 impresoras asignadas).
- **Conmutador de Vista (Segmented UI)** — Añadido un control segmentado glassmorphic para alternar entre "Vista por Impresora" (auditoría clásica por cierres) y "Consolidado por Usuario" (agrupación y ordenación por volumen total).
- **Sub-paneles y KPI cards** — Renderizado dinámico de tarjetas de resumen con la distribución consolidada por función (Copiadora, Impresora, Escáner, Color vs B/N) al expandir la fila de un usuario consolidado.
- **Sub-tabla interna de equipos utilizados** — Listado interactivo detallando IP, ubicación, volumen y acciones para cada impresora que haya registrado consumos del usuario.
- **Selector de tamaño de página** — Control flexible para elegir el paginado (15, 25, 50, 100 registros) facilitando auditorías masivas de consumos.

### 🧪 Testing

- **TypeScript compilation check** — Validado compilación limpia de frontend React sin errores de tipado o de interfaces.
- **Backend QA Regression** — 10/10 en verify_session y 27/27 en qa_bloques_bc pasados exitosamente sin incidencias.

---

## [2.5.0] - 2026-05-29

### 🔧 Fixed — Bugs Críticos Backend

- **`AttributeError: current_user.name`** — El modelo `User` usa `nombre_completo`. Reemplazado en todos los endpoints de `counters.py` que accedían al nombre del usuario autenticado.
- **`IntegrityError: empresa_id NULL`** en `ComparacionGuardada` — Implementado fallback `empresa_id = printer.empresa_id or current_user.empresa_id` para impresoras sin empresa asignada.
- **`NameError: Printer`** en `dashboard.py` — Agregado `from db.models import Printer` faltante en el endpoint de tóner-alertas.
- **`AttributeError: User.nombre`** en `users.py` L230 — Corregido bug latente en la búsqueda global de usuarios sustituyéndolo por el atributo de ORM correcto `User.name`.

### 🧹 Refactor — Limpieza de imports en `counters.py`

- Eliminados imports no usados: `joinedload`, `PrinterResponse`, `CapabilitiesResponse`
- Imports locales dentro de funciones centralizados al top-level del archivo
- Eliminado `import csv` de `export.py` (sin uso tras eliminación de CSV)

### 🗑️ Removed — Soporte CSV eliminado completamente

- **Backend:** Eliminados endpoints `GET /api/export/cierre/{id}` (CSV) y `GET /api/export/comparacion/{id1}/{id2}` (CSV)
- **Frontend:** Eliminados métodos `exportCierreCSV()`, `exportComparacionCSV()`, funciones `exportChartDataToCSV()`, `exportTableToCSV()`
- **UI:** Eliminados todos los botones "Exportar CSV" / "CSV" en `AnalyticsPage`, `ComparacionPage`, `ComparacionModal`, `CierreDetalleModal`
- Todas las exportaciones usan exclusivamente Excel (`.xlsx`)

### ✨ Added

- **Normalización de Centros de Costo por Empresa** — Diseño e implementación del modelo `CentroCosto` vinculado a `empresas(id)` con restricción `UNIQUE (empresa_id, nombre)`. Vinculación de usuarios mediante `centro_costo_id`.
- **Propiedad Retrocompatible `@property centro_costos`** en la clase `User` — Permite que la API serialice y devuelva el centro de costos en string de forma dinámica de cara al frontend, **garantizando 100% de compatibilidad sin reescribir React**.
- **Ingesta inteligente en `UserRepository`** — Adaptados `create` y `update` para buscar o crear en caliente el centro de costos estructurado por empresa a partir de payloads de texto plano.
- **Refactorización de Analytics y Cierres** — Queries de top ranking y filtrado de counters adaptadas para realizar joins estructurados con la tabla `centro_costos`.
- **`useEvolutionData` hook** en `src/hooks/useDashboardData.ts` con interfaz `EvolutionItem` tipada, consume `/api/v1/analytics/evolution`
- **Configuración Pylance/VS Code** — `.vscode/settings.json` + `backend/pyrightconfig.json` para eliminar falsos positivos de imports Docker en el editor local

### 🧪 Testing

- **QA Automatizado (Bloque A):** 10/10 pruebas de importación, índices e integridad estructural pasadas en `verify_session_29mayo.py`
- **QA Funcional y Robustez (Bloques B+C):** 27/27 pruebas de la API (Cierres, Analytics, Comparaciones guardadas, Edge cases y Excel) pasadas en `qa_bloques_bc.py`
- **Test de Centros de Costo Multitenant:** Creado y ejecutado con éxito rotundo el script `test_multitenant_centro_costos.py`, demostrando el correcto aislamiento de centros del mismo nombre en distintas empresas y su property string compatible.
- **Multi-tenancy:** Verificado 403 Forbidden en endpoints sin autenticación
- **TypeScript:** Compilación limpia con `tsc --noEmit` (0 errores)
- **Docker:** 5/5 contenedores `ricoh-backend`, `ricoh-frontend`, `ricoh-postgres`, `ricoh-redis`, `ricoh-adminer` en estado `Up/healthy`

### 📚 Documentation

- `docs/resumen/RESUMEN_TRABAJO_26_29_MAYO_2026.md` — Resumen completo de la sesión de trabajo, incluyendo el éxito del plan de pruebas funcionales y la normalización de centros de costo.
- `docs/fixes/FIX_BUGS_CRITICOS_26_MAYO_2026.md` — Documentación técnica de los 3 bugs críticos corregidos.
- `docs/desarrollo/completados/ELIMINACION_CSV_29_MAYO_2026.md` — Documentación completa de la eliminación de CSV.
- `docs/desarrollo/completados/MIGRACION_CENTROS_COSTO_29_MAYO_2026.md` — Documentación completa y cierre de la migración de centros de costo normalizada.
- `docs/guias/PLAN_QA_SIGUIENTE_SESION.md` — Plan de QA del sistema actualizado con todos los bloques A, B y C completados y aprobados al 100%.

---

## [2.2.0] - 2026-04-06

### ✨ Modernización UI/UX Premium
- **Glassmorphism**: Implementación de sistema de diseño basado en transparencias y desenfoque.
- **Ricoh Red**: Integración del color corporativo en toda la plataforma.
- **Core Components**: Refactorización de Button, Input, Modal, Table, Badge, Tabs.
- **Módulos**: Modernización completa de Fleet, Discovery, Governance y Contadores.
- **Tipografía**: Adopción global de la fuente Inter.
- **Animaciones**: Micro-animaciones añadidas para mejorar el feedback del usuario.

---

## [2.1.1] - 2026-03-31

### 🔧 Fixed
- **Exportaciones**: Corregido problema de CORS que bloqueaba el header `Content-Disposition`
  - Los archivos exportados ahora se descargan con el formato correcto: `SERIAL DD.MM.YYYY.extensión`
  - Ejemplo: `E174MA11130 31.03.2026.xlsx`
  - Afecta a todas las exportaciones: CSV, Excel y Excel Ricoh
  - Archivo modificado: `backend/main.py` (agregado `Content-Disposition` a `expose_headers`)
  - Documentación: `docs/fixes/FIX_EXPORT_FILENAME_CORS.md`

### 📚 Documentation
- Agregado `docs/fixes/FIX_EXPORT_FILENAME_CORS.md` - Fix detallado del problema CORS
- Agregado `docs/resumen/RESUMEN_FIX_EXPORTACIONES_31_MARZO.md` - Resumen de sesión
- Agregado `INSTRUCCIONES_APLICAR_FIX.md` - Guía rápida de despliegue
- Agregado `CHANGELOG.md` - Registro de cambios
- Actualizado `docs/INDICE_DOCUMENTACION_ACTUALIZADO.md` - Versión 3.0.1
- Agregado `docs/ESTADO_PROYECTO_2026_03_31.md` - Estado actualizado del proyecto

---

## [2.1.0] - 2026-03-30

### ✨ Added
- Sistema de exportaciones con formato personalizado de nombres
- Formato de nombres: `SERIAL DD.MM.YYYY.extensión`
- Soporte para 5 tipos de exportación diferentes

### 🔧 Fixed
- Múltiples fixes de UI y UX
- Correcciones en sistema de autenticación
- Mejoras en sincronización de usuarios

### 📚 Documentation
- 150+ documentos técnicos
- 18 fixes documentados
- Guías completas de usuario y desarrollo

---

## [2.0.0] - 2026-03-15

### ✨ Added
- **Sistema de Autenticación JWT**: Access + Refresh tokens
- **Multi-tenancy**: Gestión de empresas y usuarios administradores
- **Módulo de Cierres Mensuales**: Completo con comparaciones
- **Sistema de Exportaciones**: CSV, Excel y formato Ricoh
- **Protección DDoS**: Middleware personalizado
- **Protección CSRF**: Tokens CSRF en producción
- **Rate Limiting**: Por IP y por usuario
- **Encriptación AES-256**: Para contraseñas de impresoras

### 🔄 Changed
- Migración de SQLite a PostgreSQL
- Refactorización completa del backend
- Mejoras en arquitectura frontend

### 🔒 Security
- Implementación completa de seguridad
- Auditoría de todas las acciones
- Headers de seguridad HTTP

---

## [1.5.0] - 2026-02-28

### ✨ Added
- **Módulo de Contadores**: Lectura automática de contadores
- Soporte para contador ecológico
- Historial de lecturas
- Gráficos de consumo

### 🔧 Fixed
- Mejoras en lectura de contadores por usuario
- Correcciones en parseo de HTML

---

## [1.0.0] - 2026-02-15

### ✨ Added
- **Módulo de Governance**: Aprovisionamiento de usuarios
- Descubrimiento automático de impresoras
- Sincronización de usuarios y perfiles
- Gestión de permisos de color
- Configuración de carpetas compartidas

### 🏗️ Infrastructure
- Configuración inicial de Docker
- Base de datos SQLite
- Frontend React + TypeScript
- Backend FastAPI + Python

---

## Tipos de Cambios

- `Added` - Nuevas características
- `Changed` - Cambios en funcionalidad existente
- `Deprecated` - Características que serán removidas
- `Removed` - Características removidas
- `Fixed` - Corrección de bugs
- `Security` - Cambios de seguridad
- `Documentation` - Cambios en documentación
- `Infrastructure` - Cambios en infraestructura

---

## Enlaces

- [Documentación Completa](docs/)
- [Guía de Usuario](docs/guias/GUIA_USUARIO.md)
- [Estado del Proyecto](docs/ESTADO_PROYECTO_2026_03_31.md)
- [Fixes Documentados](docs/fixes/)
