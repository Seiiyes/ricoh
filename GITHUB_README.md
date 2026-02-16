# 🖨️ Ricoh Multi-Fleet Governance Suite

[![Version](https://img.shields.io/badge/version-3.3-blue.svg)](https://github.com/Seiiyes/ricoh)
[![License](https://img.shields.io/badge/license-Private-red.svg)](https://github.com/Seiiyes/ricoh)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-19.2-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.9-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-16-blue.svg)](https://www.postgresql.org/)

Sistema completo de gestión y aprovisionamiento automático de usuarios para impresoras Ricoh en red.

---

## 🎯 Características Principales

- ✅ **Descubrimiento Automático** - Escaneo asíncrono de red para detectar impresoras
- ✅ **Gestión de Flota** - CRUD completo con actualización SNMP en tiempo real
- ✅ **Aprovisionamiento Masivo** - Crear usuarios en 1, varias, o todas las impresoras simultáneamente
- ✅ **Monitoreo en Tiempo Real** - WebSocket con logs en vivo estilo terminal
- ✅ **Seguridad** - Encriptación AES-256 de credenciales
- ✅ **Reintentos Automáticos** - Manejo inteligente de impresoras ocupadas (v3.3)
- ✅ **Interfaz Amigable** - Lenguaje simplificado para usuarios no técnicos
- ✅ **Docker Ready** - Despliegue con un solo comando

---

## 🏗️ Arquitectura

```
Frontend (React + TypeScript)
    ↕ HTTP REST + WebSocket
Backend (FastAPI + Python)
    ↕ SQL
Database (PostgreSQL 16)
```

**Stack Completo:**
- Frontend: React 19, TypeScript, Vite, Zustand, Tailwind CSS
- Backend: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- Infraestructura: Docker Compose, Adminer, WebSocket

---

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

**Windows:**
```cmd
docker-start.bat
```

**Linux/Mac:**
```bash
chmod +x docker-start.sh
./docker-start.sh
```

### Opción 2: Manual

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
npm install
npm run dev
```

---

## 🌐 Acceso a Servicios

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:5173 | Interfaz de usuario |
| Backend API | http://localhost:8000 | API REST |
| API Docs | http://localhost:8000/docs | Documentación Swagger |
| Adminer | http://localhost:8080 | Administración de BD |

---

## 📖 Documentación

### 📚 Guías Principales
- [README.md](README.md) - Documentación completa
- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido
- [GUIA_DE_USO.md](GUIA_DE_USO.md) - Guía de uso paso a paso
- [RESUMEN_COMPLETO_PROYECTO.md](RESUMEN_COMPLETO_PROYECTO.md) - Resumen exhaustivo

### 🔧 Documentación Técnica
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura detallada
- [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md) - Estado del proyecto (v3.3)
- [backend/TESTING_GUIDE.md](backend/TESTING_GUIDE.md) - Guía de pruebas

### 📝 Notas Importantes
- [MEJORA_REINTENTOS_AUTOMATICOS.md](MEJORA_REINTENTOS_AUTOMATICOS.md) - Reintentos automáticos (v3.3)
- [backend/NOTA_INDICE_AUTOINCREMENTAL.md](backend/NOTA_INDICE_AUTOINCREMENTAL.md) - Solución del índice (v3.2)
- [SIMPLIFICACION_LENGUAJE.md](SIMPLIFICACION_LENGUAJE.md) - Mejoras de UX

---

## ✨ Novedades v3.3

### 🔄 Reintentos Automáticos para Impresoras Ocupadas

El sistema ahora reintenta automáticamente cuando una impresora está ocupada:

- **3 intentos** con 5 segundos de espera
- **Detección inteligente** del error "BUSY"
- **Mejora la tasa de éxito** del ~70% al ~95%
- **Transparente** para el usuario

**Ejemplo:**
```
📡 Provisionando a impresora: 192.168.91.250
   ⏳ Impresora ocupada, reintentando...
   🔄 Reintento 2/3 (esperando 5s...)
   Resultado: ✅ ÉXITO
```

---

## 📊 Estadísticas

- **~6,700 líneas de código**
- **101 archivos**
- **15+ endpoints API**
- **25+ tests**
- **15+ documentos**
- **~12 horas de desarrollo**

---

## 🎨 Capturas de Pantalla

### Panel Principal
- **Izquierdo:** Formulario de usuario con configuración completa
- **Derecho:** Grid de impresoras con selección múltiple
- **Inferior:** Registro de actividad en tiempo real

### Funcionalidades
- Descubrimiento de red con modal profesional
- Edición de impresoras
- Consultas SNMP en tiempo real
- Logs con códigos de color

---

## 🔐 Seguridad

- ✅ Encriptación AES-256 de contraseñas
- ✅ Validación de inputs con Pydantic
- ✅ Prevención de SQL injection (ORM)
- ✅ CORS configurado
- ✅ Timeouts en conexiones

---

## 🧪 Testing

```bash
# Frontend
npm run test

# Backend
cd backend
python test_final_v2.py
python test_multi_printer_provisioning.py
```

---

## 📝 Changelog

### v3.3 (2026-02-16)
- ✅ Reintentos automáticos para impresoras ocupadas
- ✅ Mejora de tasa de éxito al ~95%

### v3.2 (2026-02-13)
- ✅ Índice autoincremental por impresora
- ✅ Usuarios aparecen correctamente en impresoras

### v3.1 (2026-02-13)
- ✅ Simplificación de lenguaje en UI
- ✅ Corrección de typos y ejemplos

### v3.0 (2026-02-13)
- ✅ Sistema completamente funcional
- ✅ Aprovisionamiento masivo
- ✅ Encriptación de credenciales

---

## 🤝 Contribuir

Este es un proyecto privado. Para contribuir:

1. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
2. Commit: `git commit -m 'feat: nueva funcionalidad'`
3. Push: `git push origin feature/nueva-funcionalidad`
4. Abre un Pull Request

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la [documentación](README.md)
2. Consulta [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md)
3. Verifica logs: `docker-compose logs -f`
4. Abre un issue en GitHub

---

## 📄 Licencia

Este proyecto es privado y propietario.

---

## 🙏 Créditos

Desarrollado para Reliteltda por Juan Lizarazo.

Sistema de gestión eficiente de flotas de impresoras Ricoh con arquitectura empresarial escalable.

---

**Estado:** ✅ Producción  
**Versión:** 3.3  
**Última actualización:** 16 de Febrero de 2026
