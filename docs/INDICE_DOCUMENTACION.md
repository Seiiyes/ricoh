# 📚 Índice General de Documentación - Ricoh Fleet Management

**Última actualización**: 6 de Julio de 2026  
**Versión**: 4.1.5 (Actualizado)

---

## 📂 Estructura General de Carpetas

Toda la documentación técnica, operativa y de usuario del proyecto está categorizada en las siguientes carpetas:

```
docs/
├── api/                    # Especificaciones y referencias de APIs REST
├── arquitectura/           # Diagramas, flujos y diseños arquitectónicos de UI/UX
├── deployment/             # Guías de instalación, configuración SSH y despliegue prod
├── desarrollo/             # Notas técnicas de desarrollo y auditorías de código
│   ├── actualizaciones/    # Historial de actualizaciones de servicios
│   ├── analisis/           # Reportes de análisis técnicos
│   ├── auditorias/         # Resultados de auditorías y reportes de optimización
│   ├── bugs/               # Reportes detallados de errores
│   ├── completados/        # Documentación de módulos finalizados
│   ├── correcciones/       # Correcciones arquitectónicas
│   ├── diagnosticos/       # Diagnósticos del sistema
│   ├── fases/              # Detalle de fases de sprints pasados
│   ├── limpieza/           # Tareas de saneamiento de base de datos
│   ├── mejoras/            # Mejoras de UI/UX premium
│   ├── migraciones/        # Guías de migraciones SQL
│   ├── modulos/            # Especificaciones de módulos
│   ├── planes/             # Planes de trabajo antiguos
│   ├── pruebas/            # Reportes de testing
│   ├── refactorizacion/    # Reestructuraciones de código
│   ├── soluciones/         # Soluciones técnicas
│   └── verificacion/       # Pruebas de verificación e integración
│── fixes/                  # Documentación de bugs específicos corregidos
├── guias/                  # Manuales de usuario, pruebas QA e instrucciones
├── resumen/                # Hitos, progresos semanales e históricos
└── seguridad/              # Políticas de seguridad, DDoS y autenticación JWT
```

---

## 🆕 Documentación de la Sesión Reciente (Junio-Julio 2026)

### 📅 Resúmenes de Trabajo y Fixes Recientes
*   **[PORTAL_AUDITORIA_SEGURIDAD_INDEPENDIENTE_JULIO_2026.md](seguridad/PORTAL_AUDITORIA_SEGURIDAD_INDEPENDIENTE_JULIO_2026.md)**
    *   *Descripción:* Documentación técnica y guía de uso del Portal de Auditoría de Seguridad independiente que corre en el puerto `8088` con base de datos SQLite y autenticación bcrypt.
*   **[REPORTE_QA_UX_Y_PAGINACION_TRABAJOS_IMPRESION_07_JULIO_2026.md](desarrollo/pruebas/REPORTE_QA_UX_Y_PAGINACION_TRABAJOS_IMPRESION_07_JULIO_2026.md)**
    *   *Descripción:* Informe de control de calidad (QA) sobre el comportamiento responsivo, el desborde horizontal de la tabla y la sincronización de la doble paginación en vivo en producción.
*   **[FIX_UX_RESPONSIVO_Y_SPACING_TRABAJOS_IMPRESION_07_JULIO_2026.md](fixes/FIX_UX_RESPONSIVO_Y_SPACING_TRABAJOS_IMPRESION_07_JULIO_2026.md)**
    *   *Descripción:* Solución al subaprovechamiento horizontal en escritorio, remoción de ID Trabajo irrelevante y erradicación del scroll horizontal mediante reajuste de paddings y max-widths.
*   **[FIX_CONTADOR_IMPRESORAS_Y_RENDER_DESACTIVACION_06_JULIO_2026.md](fixes/FIX_CONTADOR_IMPRESORAS_Y_RENDER_DESACTIVACION_06_JULIO_2026.md)**
    *   *Descripción:* Solución a la inconsistencia visual de cantidad de impresoras en fila principal para usuarios con asignaciones inactivas en base de datos.
*   **[RESUMEN_TRABAJO_01_JULIO_2026.md](resumen/RESUMEN_TRABAJO_01_JULIO_2026.md)**
    *   *Descripción:* Implementación de detección de deriva, bucle de reintentos por impresoras ocupadas (BUSY), restauración de live-diagnostics y remoción de console.logs en producción.
*   **[RESUMEN_TRABAJO_23_JUNIO_2026.md](resumen/RESUMEN_TRABAJO_23_JUNIO_2026.md)**
    *   *Descripción:* Solución de IndentationError en el cliente web Ricoh, despliegue en caliente y optimización de tiempos de aprovisionamiento en paralelo.
*   **[RESUMEN_TRABAJO_18_JUNIO_2026.md](resumen/RESUMEN_TRABAJO_18_JUNIO_2026.md)**
    *   *Descripción:* Análisis de puertos Telnet y desarrollo de la eliminación lógica de usuarios con deactivación paralela de permisos en impresoras.
*   **[OPORTUNIDADES_APROVECHAMIENTO_PUERTOS.md](desarrollo/analisis/OPORTUNIDADES_APROVECHAMIENTO_PUERTOS.md)**
    *   *Descripción:* Análisis de puertos y servicios abiertos de la flota Ricoh y cómo pueden ser aprovechados por el proyecto.
*   **[OPTIMIZACION_GESTION_USUARIOS.md](desarrollo/analisis/OPTIMIZACION_GESTION_USUARIOS.md)**
    *   *Descripción:* Diagnóstico y plan de optimización de la gestión de usuarios cruzando base de datos, backend y protocolos de impresora.
*   **[RECONFIGURACION_SERVIDOR_131.md](deployment/RECONFIGURACION_SERVIDOR_131.md)**
    *   *Descripción:* Reconfiguración de seguridad, desactivación de bloqueos de cuenta, retorno a HTTP plano en puertos 80 y 8000, y herramientas de sincronización local/remoto para el servidor 131.
*   **[RESUMEN_TRABAJO_11_JUNIO_2026.md](resumen/RESUMEN_TRABAJO_11_JUNIO_2026.md)**
    *   *Descripción:* Protección de endpoints de documentación API (/docs, /redoc, /openapi.json) con Basic Auth e informe de auditoría/sincronización de base de datos local vs. servidor.
*   **[RESUMEN_TRABAJO_01_03_JUNIO_2026.md](resumen/RESUMEN_TRABAJO_01_03_JUNIO_2026.md)**
    *   *Descripción:* Resumen completo de la modernización de suministros por HTTP, simetría UI de Dashboard y corrección de totales en comparación de cierres.
*   **[ACTUALIZACION_SISTEMA_SUMINISTROS_Y_SIMETRIA_DASHBOARD.md](desarrollo/actualizaciones/ACTUALIZACION_SISTEMA_SUMINISTROS_Y_SIMETRIA_DASHBOARD.md)**
    *   *Descripción:* Detalle de desarrollo de la implementación de raspado de suministros HTTP y simetría de tarjetas de tóner monocromáticas en el dashboard.
*   **[FIX_CONTADORES_Y_SUMINISTROS_JUNIO_2026.md](fixes/FIX_CONTADORES_Y_SUMINISTROS_JUNIO_2026.md)**
    *   *Descripción:* Detalle técnico de la solución a scope shadowing, cálculo con contadores generales e inhabilitación de columnas redundantes en monocromáticas.
*   **[ACTUALIZACION_FACTURACION_Y_CENTRO_COSTOS.md](desarrollo/actualizaciones/ACTUALIZACION_FACTURACION_Y_CENTRO_COSTOS.md)**
    *   *Descripción:* Resumen de la implementación del módulo de facturación consolidada, jerarquía de centros de costos interactiva (Excel-like) y adaptación de UI jerárquica.
*   **[FIX_CONTAMINACION_TESTS_SEGURIDAD_JUNIO.md](fixes/FIX_CONTAMINACION_TESTS_SEGURIDAD_JUNIO.md)**
    *   *Descripción:* Solución técnica al "State Leakage" en la suite de Pytest tras la inyección de middleware de seguridad y configuración de almacenamiento de rate limiter/CSRF.
*   **[FIX_SEGURIDAD_RICOH_CLIENT_DDOS_MIDDLEWARE.md](fixes/FIX_SEGURIDAD_RICOH_CLIENT_DDOS_MIDDLEWARE.md)**
    *   *Descripción:* Validación de credenciales vacías en RicohWebClient y control del DDoS middleware para pruebas.
*   **[FIX_SUITE_TESTS_COMPLETA_JUNIO_2026.md](fixes/FIX_SUITE_TESTS_COMPLETA_JUNIO_2026.md)**
    *   *Descripción:* Estabilización y corrección de 19 fallos en la suite de Pytest a nivel de base de datos, Hypothesis y mocks de red.
*   **[FIX_FILTRO_CENTRO_COSTOS_SUBSTRING_MISMATCH.md](fixes/FIX_FILTRO_CENTRO_COSTOS_SUBSTRING_MISMATCH.md)**
    *   *Descripción:* Corrección de coincidencia parcial en el filtro por Centro de Costos, rediseño de filtros usando dropdown de períodos de cierre y formato dinámico de subtítulos.

### 🧪 Planificación de Calidad y Continuidad
*   **[REPORTE_QA_UX_Y_PAGINACION_TRABAJOS_IMPRESION_07_JULIO_2026.md](desarrollo/pruebas/REPORTE_QA_UX_Y_PAGINACION_TRABAJOS_IMPRESION_07_JULIO_2026.md)**
    *   *Descripción:* Informe de control de calidad (QA) sobre la responsividad y la doble paginación del consolidado de trabajos.
*   **[VERIFICACION_SUITE_TESTS_JUNIO_2026.md](desarrollo/verificacion/VERIFICACION_SUITE_TESTS_JUNIO_2026.md)**
    *   *Descripción:* Informe de verificación y ejecución de la suite completa de pruebas de frontend (Vitest) y backend (Pytest) (Actualizado al 11 de Junio de 2026).
*   **[PLAN_QA_SIGUIENTE_SESION.md](guias/PLAN_QA_SIGUIENTE_SESION.md)**
    *   *Descripción:* Plan detallado para el control de calidad (QA) del módulo de cierres y la revolución de analytics, con credenciales de prueba, casos de uso límites y scripts automáticos.
*   **[documentacion_siguiente_sesion.md](resumen/documentacion_siguiente_sesion.md)**
    *   *Descripción:* Guía de traspaso para la siguiente sesión de desarrollo, detallando estado, plan de regresión y siguientes pasos técnicos.
*   **[PROGRESO_SESION_HOY.md](resumen/PROGRESO_SESION_HOY.md)**
    *   *Descripción:* Resumen histórico y progreso detallado de la sesión actual de desarrollo.

---

## 🏗️ 1. Arquitectura y APIs

### 🏗️ Arquitectura del Sistema
*   **[ARQUITECTURA_COMPLETA_2026.md](arquitectura/ARQUITECTURA_COMPLETA_2026.md):** Diseño global y arquitectura modular.
*   **[ESTRUCTURA_BASE_DATOS_ACTUAL.md](arquitectura/ESTRUCTURA_BASE_DATOS_ACTUAL.md):** Diagrama y definición de tablas Postgres.
*   **[DIAGRAMA_FLUJO.md](arquitectura/DIAGRAMA_FLUJO.md):** Flujo de sincronización y autenticación.
*   **[DISENO_UI_CIERRES_MEJORADO.md](arquitectura/DISENO_UI_CIERRES_MEJORADO.md):** Diseño conceptual para el flujo de cierres y contadores.
*   **[COMPATIBILIDAD_DASHBOARD_VS_ANALYTICS.md](arquitectura/COMPATIBILIDAD_DASHBOARD_VS_ANALYTICS.md):** Análisis de diseño arquitectónico y no-redundancia entre el Dashboard y el módulo de Analytics.
*   **[APROVECHAMIENTO_STACK_TECNOLOGICO.md](arquitectura/APROVECHAMIENTO_STACK_TECNOLOGICO.md):** Análisis detallado del aprovechamiento del stack tecnológico (FastAPI, Redis, Postgres, React).

### 🔌 Especificaciones de APIs REST
*   **[API_CIERRES_MENSUALES.md](api/API_CIERRES_MENSUALES.md):** Endpoints, parámetros y respuestas para la gestión de cierres.
*   **[API_CONTADORES.md](api/API_CONTADORES.md):** Documentación técnica de captura de contadores y lecturas de red.
*   **[API_REFERENCE_CIERRES.md](api/API_REFERENCE_CIERRES.md):** Referencia técnica detallada para el módulo de comparativas.

---

## 🚀 2. Despliegue, Infraestructura y Operación

### 🚀 Despliegue en Producción
*   **[DEPLOYMENT_PRODUCTION.md](deployment/DEPLOYMENT_PRODUCTION.md):** Guía exhaustiva de despliegue paso a paso en entorno de producción.
*   **[RECONFIGURACION_SERVIDOR_131.md](deployment/RECONFIGURACION_SERVIDOR_131.md):** Historial y pasos de reconfiguración a HTTP y sincronización para el servidor 192.168.91.131.
*   **[DIFERENCIAS_LOCAL_VS_PRODUCCION.md](deployment/DIFERENCIAS_LOCAL_VS_PRODUCCION.md):** Checklist de diferencias de variables, puertos y políticas de seguridad entre local y prod.
*   **[INSTALACION_SSH_REMOTA.md](deployment/INSTALACION_SSH_REMOTA.md):** Manual detallado para configuración y acceso seguro mediante túneles SSH.
*   **[INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md](deployment/INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md):** Instrucciones resumidas de comandos para DevOps.
*   **[TROUBLESHOOTING_DOCKER.md](deployment/TROUBLESHOOTING_DOCKER.md):** Guía de resolución de problemas comunes del contenedor.

### 🔐 Seguridad y Autenticación
*   **[SISTEMA_AUTENTICACION_COMPLETADO.md](seguridad/SISTEMA_AUTENTICACION_COMPLETADO.md):** Mecanismo de autenticación JWT y roles del sistema.
*   **[CRITICAL_SECURITY_IMPLEMENTATION.md](seguridad/CRITICAL_SECURITY_IMPLEMENTATION.md):** Detalles del endurecimiento de seguridad en API y base de datos.
*   **[DDOS_PROTECTION.md](seguridad/DDOS_PROTECTION.md):** Configuración de rate limiting con Redis.
*   **[WALKTHROUGH_SEGURIDAD.md](seguridad/WALKTHROUGH_SEGURIDAD.md):** Guía de verificación, correcciones de WebSockets y auditoría general de seguridad (Junio 2026).

---

## 💻 3. Desarrollo, Auditorías y Fixes

### 🔍 Auditorías de Código y Calidad
*   **[OPTIMIZACION_HALLAZGOS.md](desarrollo/auditorias/OPTIMIZACION_HALLAZGOS.md):** Reporte de optimización completo generado por el sistema de auditoría (~5000+ hallazgos analizados).
*   **[OPTIMIZACION_HALLAZGOS_DEMO.md](desarrollo/auditorias/OPTIMIZACION_HALLAZGOS_DEMO.md):** Demostración del plan de priorización e impacto de optimizaciones de código.
*   **[AUDITORIA_BASE_DATOS.md](desarrollo/auditorias/AUDITORIA_BASE_DATOS.md):** Evaluación de índices y rendimiento PostgreSQL.
*   **[ANALISIS_RENDIMIENTO_ANALYTICS.md](desarrollo/auditorias/ANALISIS_RENDIMIENTO_ANALYTICS.md):** Auditoría exhaustiva de performance, índices Postgres y análisis de caché (Redis) para el panel analítico.

### 📋 Planes de Trabajo y Tareas Pendientes
*   **[PLAN_ELIMINACION_CSV.md](desarrollo/planes/PLAN_ELIMINACION_CSV.md):** Plan detallado paso a paso para remover todas las exportaciones CSV del frontend y backend, consolidando el uso exclusivo de Excel (XLS/XLSX).
*   **[PLAN_EXPANSION_DASHBOARD.md](desarrollo/planes/PLAN_EXPANSION_DASHBOARD.md):** Plan detallado para expandir el dashboard principal con widgets premium, analítica de 6 meses, cálculo de sostenibilidad ecológica, diagnóstico de conectividad y validación/fallback SNMP e HTTP de tóneres.
*   **[TAREAS_EXPANSION_DASHBOARD.md](desarrollo/planes/TAREAS_EXPANSION_DASHBOARD.md):** Hoja de ruta interactiva y checklist detallado paso a paso para la implementación técnica de la expansión del dashboard y validaciones de tóner.


### 📖 Guías de Desarrollo y Manuales
*   **[GUIA_USUARIO.md](guias/GUIA_USUARIO.md):** Manual operativo completo para el cliente final.
*   **[GUIA_RAPIDA.md](guias/GUIA_RAPIDA.md) / [INICIO_RAPIDO.md](guias/INICIO_RAPIDO.md):** Inducciones ágiles para nuevos usuarios.
*   **[TESTING_GUIDE.md](guias/TESTING_GUIDE.md):** Guía detallada para correr la suite de tests en backend y frontend.
*   **[ENV_FILES_GUIDE.md](guias/ENV_FILES_GUIDE.md):** Buenas prácticas de gestión de secretos y configuración `.env`.
*   **[LEEME_PRIMERO_RESPONSIVE.md](guias/LEEME_PRIMERO_RESPONSIVE.md):** Documento introductorio sobre la actualización responsive global.
*   **[COMO_VER_LOS_CAMBIOS.md](guias/COMO_VER_LOS_CAMBIOS.md) / [INSTRUCCIONES_LIMPIAR_CACHE.md](guias/INSTRUCCIONES_LIMPIAR_CACHE.md):** Guías rápidas para forzar recargas y limpiar caché de navegadores.
*   **[INSTRUCCIONES_VISUALES.md](guias/INSTRUCCIONES_VISUALES.md):** Manual visual para verificar la adaptación y responsive en laptops y móviles.

### 🔧 Fixes y Soluciones de Bugs Importantes
*   **[FIX_CONTADOR_IMPRESORAS_Y_RENDER_DESACTIVACION_06_JULIO_2026.md](fixes/FIX_CONTADOR_IMPRESORAS_Y_RENDER_DESACTIVACION_06_JULIO_2026.md):** Solución a la inconsistencia visual de cantidad de impresoras en fila principal para usuarios con asignaciones inactivas.
*   **[FIX_FILTRO_CENTRO_COSTOS_SUBSTRING_MISMATCH.md](fixes/FIX_FILTRO_CENTRO_COSTOS_SUBSTRING_MISMATCH.md):** Corrección de coincidencia parcial en el filtro por Centro de Costos, evitando que 'TIC' coincida dentro de 'LOGISTICA'.
*   **[FIX_SEGURIDAD_RICOH_CLIENT_DDOS_MIDDLEWARE.md](fixes/FIX_SEGURIDAD_RICOH_CLIENT_DDOS_MIDDLEWARE.md):** Validación de credenciales en RicohWebClient y habilitación/deshabilitación del DDoS middleware via variables de entorno.
*   **[FIX_SUITE_TESTS_COMPLETA_JUNIO_2026.md](fixes/FIX_SUITE_TESTS_COMPLETA_JUNIO_2026.md):** Corrección y estabilización de la suite completa de pytest (19 fallos corregidos a 0).
*   **[FIX_CONTADORES_Y_SUMINISTROS_JUNIO_2026.md](fixes/FIX_CONTADORES_Y_SUMINISTROS_JUNIO_2026.md):** Corrección de scope shadowing, cálculo de totales usando contadores generales y remoción de columnas B/N en monocromáticas.
*   **[FIX_EXPORTACION_EXCEL_SOLO_10_USUARIOS.md](fixes/FIX_EXPORTACION_EXCEL_SOLO_10_USUARIOS.md):** Solución al límite de descarga Excel y CSV con mapeo de campos.
*   **[FIX_BUSY_Y_CONTRASENA_ESCANER.md](fixes/FIX_BUSY_Y_CONTRASENA_ESCANER.md):** Estrategia de dos pasadas para impresoras ocupadas.
*   **[FIX_SERIALIZACION_EMPRESA_Y_SYNC_USUARIOS.md](fixes/FIX_SERIALIZACION_EMPRESA_Y_SYNC_USUARIOS.md):** Corrección de relaciones foráneas de usuarios y empresas en la API.
*   **[FIX_CORS_EXPORTACIONES_Y_SINCRONIZACION.md](fixes/FIX_CORS_EXPORTACIONES_Y_SINCRONIZACION.md):** Configuración de headers CORS de salida en FastAPI.

---

## 📊 4. Resúmenes Históricos de Trabajo
 
*   **[RESUMEN_TRABAJO_23_JUNIO_2026.md](resumen/RESUMEN_TRABAJO_23_JUNIO_2026.md):** Solución de IndentationError en cliente Ricoh, despliegue y pruebas concurrentes de 5 impresoras.
*   **[RESUMEN_TRABAJO_18_JUNIO_2026.md](resumen/RESUMEN_TRABAJO_18_JUNIO_2026.md):** Resumen de hallazgos de Telnet y de la función de eliminación de usuarios con desactivación física paralela.
*   **[RESUMEN_TRABAJO_12_JUNIO_2026.md](resumen/RESUMEN_TRABAJO_12_JUNIO_2026.md):** Optimización de scraping web Ricoh (fastList / lazy loading), pools de sesión y caché en Redis.
*   **[bitacora_trabajo_sena.md](resumen/bitacora_trabajo_sena.md):** Bitácora oficial de actividades Sena (15 de Mayo a 14 de Junio de 2026) verificada según modificaciones de archivos.
*   **[RESUMEN_TRABAJO_01_03_JUNIO_2026.md](resumen/RESUMEN_TRABAJO_01_03_JUNIO_2026.md):** Consolidado del ciclo de trabajo de junio para suministros, dashboard y simetría de contadores.
*   **[RESUMEN_TRABAJO_26_29_MAYO_2026.md](resumen/RESUMEN_TRABAJO_26_29_MAYO_2026.md):** Resumen de fixes de API, normalización de centros de costo y remoción de soporte CSV.
*   **[RESPONSIVE_COMPLETADO.md](resumen/RESPONSIVE_COMPLETADO.md) / [RESUMEN_FINAL_RESPONSIVE.md](resumen/RESUMEN_FINAL_RESPONSIVE.md):** Reportes del hito de implementación y adaptabilidad responsive completa.
*   **[VERIFICACION_FINAL_RESPONSIVE.md](resumen/VERIFICACION_FINAL_RESPONSIVE.md) / [VERIFICACION_RESPONSIVE_COMPLETA.md](resumen/VERIFICACION_RESPONSIVE_COMPLETA.md):** Pruebas técnicas y verificación de adaptación en laptops de 1366x768.
*   **[RESUMEN_TRABAJO_15_MARZO_09_ABRIL_2026.md](resumen/RESUMEN_TRABAJO_15_MARZO_09_ABRIL_2026.md):** Evolución del primer bloque de modernización premium.
*   **[RESUMEN_TRABAJO_13_16_ABRIL_2026.md](resumen/RESUMEN_TRABAJO_13_16_ABRIL_2026.md):** Ajuste de integraciones de red Ricoh y seguridad local.
*   **[ESTADO_PROYECTO_2026_03_30.md](resumen/ESTADO_PROYECTO_2026_03_30.md) / [ESTADO_PROYECTO_2026_03_31.md](resumen/ESTADO_PROYECTO_2026_03_31.md):** Estado del arte del suite a fines de marzo.
*   **[ORGANIZACION_DOCUMENTACION_2026_04_08.md](resumen/ORGANIZACION_DOCUMENTACION_2026_04_08.md):** Hito del primer saneamiento general de archivos.

---

## 🔍 Búsqueda Rápida

| Si estás buscando... | Consulta el documento: |
| :--- | :--- |
| **Cómo levantar el entorno y deployar** | [INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md](deployment/INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md) |
| **Cómo certificar la calidad en QA** | [PLAN_QA_SIGUIENTE_SESION.md](guias/PLAN_QA_SIGUIENTE_SESION.md) |
| **El diseño de la base de datos** | [ESTRUCTURA_BASE_DATOS_ACTUAL.md](arquitectura/ESTRUCTURA_BASE_DATOS_ACTUAL.md) |
| **Cómo probar o correr tests locales** | [TESTING_GUIDE.md](guias/TESTING_GUIDE.md) |
| **El progreso de la última sesión** | [PROGRESO_SESION_HOY.md](resumen/PROGRESO_SESION_HOY.md) |
