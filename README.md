# Ricoh Suite

Sistema integral de gestión de impresoras Ricoh con autenticación JWT, multi-tenancy y tres módulos principales: Governance (Aprovisionamiento), Contadores y Cierres Mensuales.

**Versión**: 2.1.0 | **Estado**: ✅ Producción | **Última actualización**: 30 de Marzo de 2026

## 🚀 Inicio Rápido

### ⚡ Opción 1: Con Docker (Recomendado)

```cmd
docker-start.bat
```

Luego abre: http://localhost:5173

### 🔧 Opción 2: Desarrollo Local

**1. Iniciar Backend:**
```cmd
cd backend
start-backend.bat
```
Deja la ventana abierta.

**2. Iniciar Frontend:**
```cmd
start-dev.bat
```

**3. Abrir:** http://localhost:5173

📖 **Guía completa**: Ver `docs/INICIO_RAPIDO.md`

---

## 📋 Módulos del Sistema

### 1. Sistema de Autenticación y Multi-Tenancy
- Login con JWT (access token + refresh token)
- Gestión de empresas y usuarios administradores
- Multi-tenancy con filtrado automático
- Auditoría completa de acciones
- Rate limiting y bloqueo de cuenta

### 2. Governance (Aprovisionamiento)
- Descubrimiento automático de impresoras en red
- Configuración de usuarios y perfiles
- Sincronización de configuraciones
- Soporte para contraseñas vacías

### 3. Contadores
- Lectura automática de contadores totales
- Lectura de contadores por usuario
- Soporte para contador ecológico
- Historial de lecturas

### 4. Cierres Mensuales
- Creación de cierres mensuales automáticos
- Snapshot de contadores por usuario
- Comparación entre cierres
- Exportación a Excel (formato Ricoh de 3 hojas)
- Validación de integridad de datos

### 5. Sistema de Notificaciones
- Notificaciones modernas con Sileo
- Animaciones basadas en física
- Mensajes amigables en español

---

## ⚠️ Solución de Problemas

### Error: "Error al sincronizar usuarios"
**Causa**: Backend no está corriendo  
**Solución**: Ejecuta `backend\start-backend.bat`

📖 **Guía completa**: Ver `docs/SOLUCION_ERROR_SINCRONIZACION.md`

---

## 📦 Respaldos

```cmd
REM Crear respaldo
backup-db.bat

REM Restaurar respaldo
restore-db.bat
```

## 📚 Documentación

Toda la documentación está organizada en la carpeta `docs/`:

### Estado del Proyecto
- `docs/ESTADO_PROYECTO_2026_03_30.md` - 📊 Estado actual completo (ACTUALIZADO)
- `docs/README.md` - Índice de documentación
- `docs/INDICE_DOCUMENTACION_ACTUALIZADO.md` - Índice detallado

### Inicio y Uso
- `docs/guias/INICIO_RAPIDO.md` - 🚀 Guía de inicio rápido
- `docs/guias/GUIA_DE_USO.md` - Guía completa de uso
- `docs/guias/GUIA_USUARIO.md` - Manual de usuario

### Técnica y API
- `docs/arquitectura/ARCHITECTURE.md` - Arquitectura del sistema
- `docs/api/API_CONTADORES.md` - API de contadores
- `docs/api/API_CIERRES_MENSUALES.md` - API de cierres mensuales
- `docs/seguridad/SISTEMA_AUTENTICACION_COMPLETADO.md` - Sistema de autenticación

### Desarrollo y Fixes
- `docs/desarrollo/` - Documentación de desarrollo (100+ archivos)
- `docs/fixes/` - Correcciones de bugs documentadas (18 archivos)
- `docs/resumen/` - Resúmenes de sesiones (25 archivos)

## 🛠️ Desarrollo

### Stack Tecnológico

**Frontend:**
- React 19.2.0 + TypeScript 5.9.3
- Vite 7.3.1, Zustand 5.0.11
- Tailwind CSS 4.1.18
- Sileo 0.1.5 (notificaciones)
- Axios 1.13.6, Recharts 3.7.0

**Backend:**
- Python 3.11+ + FastAPI 0.109.0
- SQLAlchemy 2.0.25, PostgreSQL 16
- JWT (PyJWT 2.8.0), bcrypt 4.1.2
- Cryptography 42.0.0 (AES-256)

**Infraestructura:**
- Docker + Docker Compose
- Adminer (DB admin UI)
- WebSocket (real-time)

### Estructura del Proyecto
```
proyecto/
├── src/                    # Frontend React + TypeScript
├── backend/                # Backend FastAPI + Python
│   ├── api/               # Endpoints REST
│   ├── services/          # Lógica de negocio
│   ├── db/                # Modelos y base de datos
│   └── scripts/           # Scripts de utilidad
├── docs/                   # Documentación
│   └── desarrollo/        # Docs de desarrollo
└── scripts/                # Scripts de automatización
```

### Comandos Útiles
```cmd
REM Instalar dependencias locales (para el editor)
npm install

REM Ver logs
docker-compose logs -f
```

## 📞 Soporte

Ver documentación completa en `docs/`
