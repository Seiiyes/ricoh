# 📚 Índice General de Documentación - Ricoh Fleet Management

**Última actualización**: 22 de Mayo de 2026  
**Versión**: 4.0.0 (Consolidado)

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
├── fixes/                  # Documentación de bugs específicos corregidos
├── guias/                  # Manuales de usuario, pruebas QA e instrucciones
├── resumen/                # Hitos, progresos semanales e históricos
└── seguridad/              # Políticas de seguridad, DDoS y autenticación JWT
```

---

## 🆕 Documentación de la Sesión Reciente (Mayo 2026)

### 🧪 Planificación de Calidad y Continuidad
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

### 🔌 Especificaciones de APIs REST
*   **[API_CIERRES_MENSUALES.md](api/API_CIERRES_MENSUALES.md):** Endpoints, parámetros y respuestas para la gestión de cierres.
*   **[API_CONTADORES.md](api/API_CONTADORES.md):** Documentación técnica de captura de contadores y lecturas de red.
*   **[API_REFERENCE_CIERRES.md](api/API_REFERENCE_CIERRES.md):** Referencia técnica detallada para el módulo de comparativas.

---

## 🚀 2. Despliegue, Infraestructura y Operación

### 🚀 Despliegue en Producción
*   **[DEPLOYMENT_PRODUCTION.md](deployment/DEPLOYMENT_PRODUCTION.md):** Guía exhaustiva de despliegue paso a paso en entorno de producción.
*   **[DIFERENCIAS_LOCAL_VS_PRODUCCION.md](deployment/DIFERENCIAS_LOCAL_VS_PRODUCCION.md):** Checklist de diferencias de variables, puertos y políticas de seguridad entre local y prod.
*   **[INSTALACION_SSH_REMOTA.md](deployment/INSTALACION_SSH_REMOTA.md):** Manual detallado para configuración y acceso seguro mediante túneles SSH.
*   **[INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md](deployment/INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md):** Instrucciones resumidas de comandos para DevOps.
*   **[TROUBLESHOOTING_DOCKER.md](deployment/TROUBLESHOOTING_DOCKER.md):** Guía de resolución de problemas comunes del contenedor.

### 🔐 Seguridad y Autenticación
*   **[SISTEMA_AUTENTICACION_COMPLETADO.md](seguridad/SISTEMA_AUTENTICACION_COMPLETADO.md):** Mecanismo de autenticación JWT y roles del sistema.
*   **[CRITICAL_SECURITY_IMPLEMENTATION.md](seguridad/CRITICAL_SECURITY_IMPLEMENTATION.md):** Detalles del endurecimiento de seguridad en API y base de datos.
*   **[DDOS_PROTECTION.md](seguridad/DDOS_PROTECTION.md):** Configuración de rate limiting con Redis.

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
*   **[FIX_EXPORTACION_EXCEL_SOLO_10_USUARIOS.md](fixes/FIX_EXPORTACION_EXCEL_SOLO_10_USUARIOS.md):** Solución al límite de descarga Excel y CSV con mapeo de campos.
*   **[FIX_BUSY_Y_CONTRASENA_ESCANER.md](fixes/FIX_BUSY_Y_CONTRASENA_ESCANER.md):** Estrategia de dos pasadas para impresoras ocupadas.
*   **[FIX_SERIALIZACION_EMPRESA_Y_SYNC_USUARIOS.md](fixes/FIX_SERIALIZACION_EMPRESA_Y_SYNC_USUARIOS.md):** Corrección de relaciones foráneas de usuarios y empresas en la API.
*   **[FIX_CORS_EXPORTACIONES_Y_SINCRONIZACION.md](fixes/FIX_CORS_EXPORTACIONES_Y_SINCRONIZACION.md):** Configuración de headers CORS de salida en FastAPI.

---

## 📊 4. Resúmenes Históricos de Trabajo

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
