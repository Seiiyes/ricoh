---
inclusion: auto
priority: high
description: "Contexto general del proyecto: arquitectura, estructura, módulos principales, comandos útiles y convenciones de código"
---

# 📋 Contexto del Proyecto - Sistema de Gestión de Impresoras Ricoh

Este documento proporciona contexto automático sobre el proyecto actual.

---

## 🎯 DESCRIPCIÓN DEL PROYECTO

Sistema web para gestión y monitoreo de impresoras Ricoh con módulo de contadores y cierres mensuales.

### Stack Tecnológico
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React 18, TypeScript, Vite, TailwindCSS
- **Infraestructura:** Docker, Docker Compose
- **Base de datos:** PostgreSQL 15

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ricoh/
├── backend/              # API REST en FastAPI
│   ├── api/             # Endpoints REST
│   ├── db/              # Modelos y base de datos
│   ├── services/        # Lógica de negocio
│   └── migrations/      # Migraciones SQL
├── src/                 # Frontend React
│   └── components/      # Componentes React
├── docs/                # Documentación
└── .kiro/              # Configuración Kiro
    ├── steering/       # Guías de contexto
    └── lessons-learned/ # Lecciones aprendidas
```

---

## 🔑 MÓDULOS PRINCIPALES

### 1. Gestión de Impresoras
- CRUD de impresoras
- Monitoreo de estado
- Lectura de contadores

### 2. Contadores de Usuarios
- Sincronización desde impresoras
- Histórico de lecturas
- Desglose por función (copia, impresión, escaneo, fax)

### 3. Sistema de Cierres (COMPLETADO)
- Cierres diarios, semanales, mensuales, personalizados
- Snapshots inmutables de usuarios
- Comparación entre períodos
- Validaciones robustas

---

## 🗄️ MODELOS DE BASE DE DATOS

### Principales Tablas
- `printers` - Impresoras registradas
- `contador_impresora` - Contadores totales de impresoras
- `contador_usuario` - Contadores por usuario
- `cierres_mensuales` - Cierres de períodos
- `cierres_mensuales_usuarios` - Snapshot de usuarios en cierres

---

## 🌐 ENDPOINTS PRINCIPALES

### Impresoras
- `GET /printers` - Lista de impresoras
- `POST /printers` - Crear impresora
- `GET /printers/{id}` - Detalle de impresora

### Contadores
- `GET /api/counters/closes/{printer_id}` - Lista de cierres
- `POST /api/counters/close` - Crear cierre
- `GET /api/counters/monthly/{id}/detail` - Detalle con usuarios
- `GET /api/counters/closes/{id1}/compare/{id2}` - Comparar cierres

---

## 🚀 COMANDOS ÚTILES

### Backend
```bash
# Iniciar servicios
cd backend
docker-compose up -d

# Ver logs
docker logs ricoh-backend

# Ejecutar script
docker exec ricoh-backend python script.py

# Reiniciar backend
docker-compose restart backend
```

### Frontend
```bash
# Ya está en Docker, acceder en:
http://localhost:5173
```

### Base de Datos
```bash
# Backup
docker exec ricoh-postgres pg_dump -U ricoh ricoh > backup.sql

# Restore
docker exec -i ricoh-postgres psql -U ricoh ricoh < backup.sql
```

---

## 📚 DOCUMENTACIÓN CLAVE

### Técnica
- `docs/ARQUITECTURA_CIERRES_ANALISIS_COMPLETO.md` - Arquitectura del sistema
- `docs/API_REFERENCE_CIERRES.md` - Referencia de API
- `docs/BACKEND_SISTEMA_UNIFICADO_COMPLETO.md` - Backend completo

### Estado
- `ESTADO_ACTUAL_PROYECTO.md` - Estado actual (actualizado frecuentemente)
- `PROYECTO_COMPLETADO.md` - Resumen de lo completado

### Troubleshooting
- `TROUBLESHOOTING_FRONTEND.md` - Guía de resolución de problemas
- `.kiro/lessons-learned/` - Errores documentados

---

## ⚙️ CONFIGURACIÓN

### Variables de Entorno
```bash
# Backend (.env)
DATABASE_URL=postgresql://ricoh:ricoh@postgres:5432/ricoh
CORS_ORIGINS=http://localhost:5173

# Frontend
VITE_API_BASE=http://localhost:8000
```

### Puertos
- Backend: 8000
- Frontend: 5173
- PostgreSQL: 5432
- Adminer: 8080

---

## 🎯 ESTADO ACTUAL

### Completado ✅
- Backend 100% funcional
- Frontend 100% funcional
- Sistema de cierres completo
- Validaciones robustas
- Documentación completa

### En Desarrollo 🔄
- Ninguno (sistema completo)

### Futuro (Opcional) 🔮
- Exportación a Excel/PDF
- Gráficos de tendencias
- Automatización de cierres
- Reportes avanzados

---

## 🔍 CONVENCIONES DE CÓDIGO

### Python
- PEP 8 style guide
- Type hints en funciones
- Docstrings en métodos públicos
- Imports organizados (stdlib, third-party, local)

### TypeScript
- ESLint + Prettier
- Interfaces para props
- Functional components
- Hooks para estado

### SQL
- Snake_case para nombres
- Índices en foreign keys
- Constraints explícitos

---

## 🚨 REGLAS IMPORTANTES

1. **NUNCA** modificar snapshots de cierres (son inmutables)
2. **SIEMPRE** validar datos antes de crear cierres
3. **SIEMPRE** usar transacciones para operaciones críticas
4. **NUNCA** hardcodear rutas de API en frontend
5. **SIEMPRE** documentar errores en `.kiro/lessons-learned/`

---

**Última actualización:** 4 de marzo de 2026  
**Mantenido por:** Sistema Kiro

