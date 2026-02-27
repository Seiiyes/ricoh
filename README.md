# Ricoh Equipment Manager

Sistema de gestión y aprovisionamiento de impresoras Ricoh.

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
- `docs/INICIO_RAPIDO.md` - 🚀 Guía de inicio rápido (NUEVO)
- `docs/SOLUCION_ERROR_SINCRONIZACION.md` - 🔧 Solución a errores comunes (NUEVO)
- `docs/QUICKSTART.md` - Inicio rápido con Docker
- `docs/GUIA_DE_USO.md` - Guía completa de uso

### Técnica
- `docs/ARCHITECTURE.md` - Arquitectura del sistema
- `docs/PROTECCION_DATOS.md` - Sistema de respaldos
- `docs/API_REVERSE_ENGINEERING_EXITOSO.md` - Ingeniería inversa de API Ricoh
- `docs/SOLUCION_HABILITAR_SCAN.md` - Habilitar funciones programáticamente

## 🛠️ Desarrollo

```cmd
REM Instalar dependencias locales (para el editor)
npm install

REM Ver logs
docker-compose logs -f
```

## 📞 Soporte

Ver documentación completa en `docs/`
