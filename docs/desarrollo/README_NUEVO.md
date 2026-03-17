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

## 📦 Respaldos

```cmd
REM Crear respaldo
backup-db.bat

REM Restaurar respaldo
restore-db.bat
```

Los respaldos se guardan en `backups/` con timestamp.

---

## 📚 Documentación

### Inicio y Uso
- [Inicio Rápido](docs/INICIO_RAPIDO.md) - Guía de inicio
- [Guía de Uso](docs/GUIA_DE_USO.md) - Manual completo
- [Solución de Errores](docs/SOLUCION_ERROR_SINCRONIZACION.md)

### Técnica
- [Arquitectura](docs/ARCHITECTURE.md) - Diseño del sistema
- [API Contadores](docs/API_CONTADORES.md) - Endpoints de contadores
- [API Cierres](docs/API_CIERRES_MENSUALES.md) - Endpoints de cierres
- [Deployment](docs/DEPLOYMENT.md) - Guía de despliegue

### Desarrollo
- [Estado del Proyecto](docs/ESTADO_ACTUAL_PROYECTO.md)
- [Testing Guide](docs/TESTING_GUIDE.md)
- [Documentación de Desarrollo](docs/desarrollo/) - Análisis y verificaciones

---

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
└── scripts/                # Scripts de automatización
```

### Comandos Útiles

```cmd
REM Instalar dependencias
instalar-dependencias.bat

REM Ver logs de Docker
docker-compose logs -f

REM Ejecutar tests
npm test
```

---

## ⚠️ Solución de Problemas

### Error: "Error al sincronizar usuarios"
**Causa**: Backend no está corriendo  
**Solución**: Ejecuta `backend\start-backend.bat`

### Error: "No se pueden leer contadores"
**Causa**: Impresora no accesible o credenciales incorrectas  
**Solución**: Verifica conectividad y credenciales en .env

📖 **Más soluciones**: Ver `docs/SOLUCION_ERROR_SINCRONIZACION.md`

---

## 📞 Soporte

Para más información, consulta la documentación completa en `docs/`

## 📄 Licencia

Proyecto interno - Todos los derechos reservados
