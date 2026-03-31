# Changelog - Ricoh Suite

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

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
