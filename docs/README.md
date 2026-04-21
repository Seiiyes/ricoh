# 📚 Documentación - Ricoh Fleet Manager

## 📂 Estructura de Documentación

La documentación está organizada en las siguientes carpetas:

### 🏗️ [arquitectura/](arquitectura/)
Arquitectura del sistema, diagramas de flujo y diseños UI
- Arquitectura completa 2026
- Diagramas de flujo
- Diseños de interfaces

### 🔌 [api/](api/)
Documentación de APIs y referencias técnicas
- API de contadores
- API de cierres mensuales
- Referencias de endpoints

### 🔐 [seguridad/](seguridad/)
Seguridad, autenticación y protección de datos
- Sistema de autenticación JWT
- Protección DDoS
- Implementaciones de seguridad crítica

### 🚀 [deployment/](deployment/)
Guías de instalación y despliegue
- Instrucciones de despliegue en producción
- Instalación en nuevos equipos
- Troubleshooting Docker

### 📖 [guias/](guias/)
Guías de usuario y manuales
- Guía de usuario completa
- Guía rápida
- Testing y migration guides

### 🔧 [fixes/](fixes/)
Documentación de correcciones y bugs resueltos
- [FIX_EXPORTACION_EXCEL_SOLO_10_USUARIOS.md](fixes/FIX_EXPORTACION_EXCEL_SOLO_10_USUARIOS.md) - Exportación completa de usuarios en Excel/CSV con mapeo correcto de campos
- [FIX_BUSY_Y_CONTRASENA_ESCANER.md](fixes/FIX_BUSY_Y_CONTRASENA_ESCANER.md) - Estrategia dos pasadas para impresoras ocupadas y configuración automática de contraseña
- [FIX_SERIALIZACION_EMPRESA_Y_SYNC_USUARIOS.md](fixes/FIX_SERIALIZACION_EMPRESA_Y_SYNC_USUARIOS.md) - Serialización de empresa en UserResponse y sincronización correcta de usuarios con foreign keys
- [FIX_ERROR_ASIGNAR_EMPRESA_USUARIO.md](fixes/FIX_ERROR_ASIGNAR_EMPRESA_USUARIO.md) - ⚠️ DEPRECADO - Conversión automática de nombre de empresa a ID (reemplazado por fix de serialización)
- Fixes de CORS
- Correcciones de sincronización
- Soluciones de errores específicos

### 📊 [resumen/](resumen/)
Resúmenes de sesiones y progreso del proyecto
- [RESUMEN_TRABAJO_20_ABRIL_2026.md](resumen/RESUMEN_TRABAJO_20_ABRIL_2026.md) - Fix exportación Excel/CSV mapeo de campos + Mejora UI botones de cierre
- [RESUMEN_TRABAJO_15_MARZO_09_ABRIL_2026.md](resumen/RESUMEN_TRABAJO_15_MARZO_09_ABRIL_2026.md) - Sistema de autenticación, bugs críticos, modernización UI/UX
- [RESUMEN_TRABAJO_13_16_ABRIL_2026.md](resumen/RESUMEN_TRABAJO_13_16_ABRIL_2026.md) - Fixes de impresoras BUSY, contraseña escáner, asignación empresa
- Progreso de implementaciones
- Snapshots del proyecto

### 💻 [desarrollo/](desarrollo/)
Documentación técnica de desarrollo
- [MEJORA_UI_BOTONES_CIERRE.md](desarrollo/MEJORA_UI_BOTONES_CIERRE.md) - Reorganización de botones de cierre y mejora de etiquetas
- Análisis y planificación
- Refactorizaciones
- Verificaciones y auditorías
- Migraciones de base de datos

## 🎯 Documentos Principales

### Para Nuevos Desarrolladores
- [arquitectura/ARQUITECTURA_COMPLETA_2026.md](arquitectura/ARQUITECTURA_COMPLETA_2026.md)
- [desarrollo/ESTADO_ACTUAL_PROYECTO.md](desarrollo/ESTADO_ACTUAL_PROYECTO.md)
- [guias/GUIA_RAPIDA.md](guias/GUIA_RAPIDA.md)

### Para Usuarios Finales
- [guias/GUIA_USUARIO.md](guias/GUIA_USUARIO.md)
- [guias/INICIO_RAPIDO.md](guias/INICIO_RAPIDO.md)
- [guias/EJEMPLOS_USO.md](guias/EJEMPLOS_USO.md)

### Para DevOps
- [deployment/INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md](deployment/INSTRUCCIONES_DESPLIEGUE_PRODUCCION.md)
- [deployment/TROUBLESHOOTING_DOCKER.md](deployment/TROUBLESHOOTING_DOCKER.md)
- [guias/GUIA_RESPALDO_BASE_DATOS.md](guias/GUIA_RESPALDO_BASE_DATOS.md)

### Para Seguridad
- [seguridad/SISTEMA_AUTENTICACION_COMPLETADO.md](seguridad/SISTEMA_AUTENTICACION_COMPLETADO.md)
- [seguridad/CRITICAL_SECURITY_IMPLEMENTATION.md](seguridad/CRITICAL_SECURITY_IMPLEMENTATION.md)
- [seguridad/README_SEGURIDAD.md](seguridad/README_SEGURIDAD.md)

## 📋 Índice Completo

Para ver el índice completo de todos los documentos, consulta:
- [INDICE_DOCUMENTACION_ACTUALIZADO.md](INDICE_DOCUMENTACION_ACTUALIZADO.md)

---

**Última actualización:** 20 de Abril de 2026
