# Ricoh Suite

Sistema integral de gestión de impresoras Ricoh con autenticación JWT, multi-tenancy y tres módulos principales: Governance (Aprovisionamiento), Contadores y Cierres Mensuales.

**Versión**: 2.2.0 | **Estado**: ✅ Producción | **Última actualización**: 06 de Mayo de 2026

---

## 📊 Estado Actual del Sistema (6 Mayo 2026)

### ✅ Sistema Operativo y Funcionando

**Ambiente**: Desarrollo Local  
**IP Local**: 192.168.91.34  
**Acceso**: 
- Local: http://localhost:5173
- Red: http://192.168.91.34:5173

### Servicios Activos

| Servicio | Estado | Puerto | Salud |
|----------|--------|--------|-------|
| Frontend | ✅ Running | 5173 | Healthy |
| Backend | ✅ Running | 8000 | Healthy |
| PostgreSQL | ✅ Running | 5432 | Healthy |
| Redis | ✅ Running | 6379 | Healthy |
| Adminer | ✅ Running | 8080 | Running |

### 🔒 Seguridad

**Estado**: ✅ Correcto para DESARROLLO, ❌ NO listo para PRODUCCIÓN

- ⚠️ ENVIRONMENT=development (cambiar a `production`)
- ⚠️ DEBUG=true (cambiar a `false`)
- ⚠️ CORS_ORIGINS=* (restringir dominios)
- ⚠️ Claves de ejemplo (generar nuevas únicas)
- ⚠️ Redis sin contraseña (configurar contraseña)

**Ver auditoría completa**: `docs/resumen/AUDITORIA_SEGURIDAD_6_MAYO_2026.md`

### 💡 Importante

⚠️ **Si apagas tu PC, TODO el sistema se cae**

Para entender opciones y soluciones, ver: `docs/resumen/QUE_PASA_SI_APAGO_PC.md`

---

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
- Exportación a CSV, Excel y formato Ricoh (3 hojas)
- Nombres de archivo personalizados: `SERIAL DD.MM.YYYY.extensión`
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

### 🆕 Documentación de Configuración y Despliegue (Mayo 2026)
- **`docs/INDICE_DOCUMENTACION.md`** - 📚 **Índice completo de documentación** (EMPEZAR AQUÍ)
- **`docs/DEPLOYMENT_PRODUCTION.md`** - 🚀 Guía completa de despliegue a producción (50+ páginas)
- **`docs/DIFERENCIAS_LOCAL_VS_PRODUCCION.md`** - 🔄 Comparativa Local vs Producción
- **`docs/resumen/AUDITORIA_SEGURIDAD_6_MAYO_2026.md`** - 🔒 Auditoría de seguridad completa
- **`docs/resumen/QUE_PASA_SI_APAGO_PC.md`** - 💻 Explicación sobre disponibilidad
- **`docs/resumen/RESUMEN_COMPLETO_CONFIGURACION_6_MAYO_2026.md`** - 📋 Estado actual completo

### Estado del Proyecto
- `docs/desarrollo/mejoras/MODERNIZACION_UI_UX_PREMIUM_2026.md` - 💎 **Modernización UI/UX Premium**
- `docs/PROGRESO_SESION_HOY.md` - 📊 Historial de progreso actualizado
- `docs/INDICE_DOCUMENTACION_ACTUALIZADO.md` - Índice detallado
- `CHANGELOG.md` - 📝 Registro de cambios por versión (v2.2.0)

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
