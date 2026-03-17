# Ricoh Equipment Manager

Sistema integral de gestión de impresoras Ricoh con módulos de aprovisionamiento, monitoreo de contadores y cierres mensuales.

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

### 1. Governance (Aprovisionamiento)
- Descubrimiento automático de impresoras en red
- Configuración de usuarios y perfiles
- Sincronización de configuraciones

### 2. Contadores
- Lectura automática de contadores totales
- Lectura de contadores por usuario
- Soporte para contador ecológico
- Historial de lecturas

### 3. Cierres Mensuales
- Creación de cierres mensuales automáticos
- Snapshot de contadores por usuario
- Comparación entre cierres
- Exportación a Excel (formato Ricoh)
- Validación de integridad de datos

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

Toda la documentación está en la carpeta `docs/`:

### Inicio y Uso
- `docs/INICIO_RAPIDO.md` - 🚀 Guía de inicio rápido
- `docs/GUIA_DE_USO.md` - Guía completa de uso
- `docs/SOLUCION_ERROR_SINCRONIZACION.md` - 🔧 Solución a errores comunes

### Técnica
- `docs/ARCHITECTURE.md` - Arquitectura del sistema
- `docs/API_CONTADORES.md` - API de contadores
- `docs/API_CIERRES_MENSUALES.md` - API de cierres mensuales
- `docs/PROTECCION_DATOS.md` - Sistema de respaldos
- `docs/API_REVERSE_ENGINEERING_EXITOSO.md` - Ingeniería inversa de API Ricoh

### Desarrollo
- `docs/ESTADO_ACTUAL_PROYECTO.md` - Estado del proyecto
- `docs/desarrollo/` - Documentación de desarrollo (análisis, verificaciones, importaciones)

## 🛠️ Desarrollo

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
