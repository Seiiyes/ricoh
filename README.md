# Ricoh Multi-Fleet Governance Suite v2.0

Sistema completo de gestión y aprovisionamiento de impresoras Ricoh con PostgreSQL, Docker, y actualizaciones en tiempo real.

## 🎯 Características v2.0

- ✅ **PostgreSQL Database** - Persistencia real con SQLAlchemy ORM
- ✅ **Docker Compose** - Orquestación completa de servicios
- ✅ **Repository Pattern** - Arquitectura escalable y mantenible
- ✅ **WebSocket Real-time** - Logs en vivo sin polling
- ✅ **Network Discovery** - Escaneo asíncrono de red
- ✅ **Bulk Provisioning** - Aprovisionamiento masivo de usuarios
- ✅ **Database Admin UI** - Adminer para inspección visual
- ✅ **Professional Modal** - UI moderna para descubrimiento
- ✅ **Industrial Clarity** - Diseño Ricoh consistente

## 🏗️ Arquitectura

### Stack Completo
- **Frontend**: React 19 + TypeScript + Vite + Zustand
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy
- **Database**: PostgreSQL 16 Alpine
- **Admin UI**: Adminer
- **Orchestration**: Docker Compose
- **Real-time**: WebSockets

### Estructura de Base de Datos
```sql
users (id, name, pin, smb_path, email, department)
    ↓ 1:N
user_printer_assignments (user_id, printer_id, provisioned_at)
    ↓ N:1
printers (id, hostname, ip_address, status, toner_levels, capabilities)
```

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

## 🌐 Acceso a Servicios

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Database Admin**: http://localhost:8080

### Credenciales de Base de Datos
```
Server:   postgres
Database: ricoh_fleet
User:     ricoh_admin
Password: ricoh_secure_2024
```

## 📖 Uso del Sistema

### 1. Descubrir Impresoras

1. Haz clic en **"Discover Printers"**
2. Ingresa rango IP (ej: `192.168.1.0/24`)
3. Haz clic en **"Scan Network"**
4. Selecciona dispositivos encontrados
5. Haz clic en **"Register X Printer(s)"**

### 2. Aprovisionar Usuario

1. Completa el formulario:
   - Nombre completo
   - PIN seguro
   - Ruta SMB
2. Selecciona impresoras del grid (click en las tarjetas)
3. Haz clic en **"Push Configuration"**
4. Observa logs en tiempo real en la consola

### 3. Monitorear Sistema

- **Consola en Vivo**: Logs en tiempo real vía WebSocket
- **Database Admin**: Inspecciona datos en Adminer
- **API Docs**: Prueba endpoints en Swagger UI

## 🎨 Componentes Principales

### ProvisioningPanel
- Panel izquierdo: Formulario de usuario
- Panel derecho: Grid de impresoras
- Panel inferior: Consola en vivo

### DiscoveryModal
- Escaneo de red con progreso
- Selección múltiple de dispositivos
- Registro masivo a base de datos

### PrinterCard
- Estado online/offline con animación
- Niveles de tóner CMYK
- Capacidades (color, scanner)

## 📡 API Endpoints

### Discovery
- `POST /discovery/scan` - Escanear red
- `POST /discovery/register-discovered` - Registrar dispositivos

### Printers
- `GET /printers/` - Listar impresoras
- `POST /printers/` - Crear impresora
- `PUT /printers/{id}` - Actualizar
- `DELETE /printers/{id}` - Eliminar

### Users
- `GET /users/` - Listar usuarios
- `POST /users/` - Crear usuario
- `PUT /users/{id}` - Actualizar
- `DELETE /users/{id}` - Eliminar

### Provisioning
- `POST /provisioning/provision` - Aprovisionar usuario
- `GET /provisioning/user/{id}` - Estado de aprovisionamiento
- `GET /provisioning/printer/{id}` - Usuarios de impresora

### WebSocket
- `WS /ws/logs` - Logs en tiempo real

## 🔧 Configuración

### Variables de Entorno - Backend

```env
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet
DEMO_MODE=true
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SECRET_KEY=ricoh-secret-key-change-in-production
```

### Variables de Entorno - Frontend

```env
VITE_API_URL=http://localhost:8000
```

## 🐳 Comandos Docker

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Detener servicios
docker-compose down

# Reconstruir servicios
docker-compose up --build

# Limpiar todo (incluyendo volúmenes)
docker-compose down -v
```

## 🧪 Testing

### Frontend
```bash
npm run test          # Single run
npm run test:watch    # Watch mode
```

### Backend
```bash
cd backend
python test_api.py
```

### Base de Datos
1. Abre http://localhost:8080
2. Conéctate con las credenciales
3. Explora tablas y datos

## 📁 Estructura del Proyecto

```
ricoh-suite/
├── backend/
│   ├── api/              # API routes
│   │   ├── discovery.py
│   │   ├── printers.py
│   │   ├── users.py
│   │   ├── provisioning.py
│   │   └── schemas.py
│   ├── db/               # Database layer
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── init.sql
│   ├── services/         # Business logic
│   │   ├── network_scanner.py
│   │   └── provisioning.py
│   ├── main.py           # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── src/
│   ├── components/
│   │   ├── discovery/
│   │   │   └── DiscoveryModal.tsx
│   │   ├── fleet/
│   │   │   └── PrinterCard.tsx
│   │   └── governance/
│   │       └── ProvisioningPanel.tsx
│   ├── services/
│   │   └── printerService.ts
│   └── store/
│       └── usePrinterStore.ts
├── docker-compose.yml
├── docker-start.sh
├── docker-start.bat
├── ARCHITECTURE.md
└── README.md
```

## 🔐 Seguridad

### Implementado
- ✅ CORS configurado
- ✅ Validación de inputs (Pydantic)
- ✅ Prevención SQL injection (ORM)
- ✅ Connection pooling
- ✅ Health checks

### Producción (Pendiente)
- ⏳ Autenticación JWT
- ⏳ Hash de contraseñas (bcrypt)
- ⏳ Rate limiting
- ⏳ HTTPS/TLS
- ⏳ API keys
- ⏳ Audit logging

## 📊 Modo Demo vs Producción

### Modo Demo (Default)
- Retorna 10 impresoras ficticias
- No requiere hardware físico
- Ideal para desarrollo y demos

### Modo Producción
```bash
# En backend/.env o docker-compose.yml
DEMO_MODE=false
```
- Escanea red real
- Detecta impresoras por puertos 80, 443, 161
- Requiere permisos de red

## 🐛 Troubleshooting

### Docker no inicia
```bash
# Verificar Docker
docker info

# Limpiar contenedores
docker-compose down -v
docker system prune -a
```

### Base de datos no conecta
```bash
# Ver logs de PostgreSQL
docker-compose logs postgres

# Reiniciar solo la base de datos
docker-compose restart postgres
```

### Frontend no conecta al backend
1. Verifica que el backend esté corriendo: http://localhost:8000
2. Revisa CORS en `backend/main.py`
3. Verifica `.env` tenga `VITE_API_URL=http://localhost:8000`

### WebSocket no conecta
1. Verifica que el backend esté corriendo
2. Abre consola del navegador para ver errores
3. Verifica que no haya firewall bloqueando

## 📈 Escalabilidad

### Horizontal
- Múltiples instancias de backend detrás de load balancer
- Base de datos compartida
- Redis para sesiones
- WebSocket sticky sessions

### Vertical
- Aumentar recursos de contenedores
- Optimizar queries de base de datos
- Agregar índices
- Tuning de connection pool

## 📚 Documentación

### 📖 Documentación Principal

**¡NUEVO!** Documentación completa disponible:

- **[INDICE_DOCUMENTACION.md](INDICE_DOCUMENTACION.md)** ⭐ - Índice completo de toda la documentación
- **[RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** ⭐ - Resumen ejecutivo del sistema
- **[GUIA_DE_USO.md](GUIA_DE_USO.md)** ⭐ - Guía completa de uso paso a paso
- **[EJEMPLOS_USO.md](EJEMPLOS_USO.md)** ⭐ - Ejemplos prácticos de uso

### 🔧 Documentación Técnica

- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura detallada
- [DIAGRAMA_FLUJO.md](DIAGRAMA_FLUJO.md) - Diagramas de flujo visuales
- [RESUMEN_FUNCIONALIDAD.md](RESUMEN_FUNCIONALIDAD.md) - Funcionalidades implementadas
- [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md) - Estado detallado del proyecto

### ✅ Verificación y Pruebas

- [CHECKLIST_VERIFICACION.md](CHECKLIST_VERIFICACION.md) - Checklist completo de verificación
- [backend/TESTING_GUIDE.md](backend/TESTING_GUIDE.md) - Guía de pruebas técnicas

### 🚀 Despliegue

- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido
- [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) - Guía de despliegue
- [backend/MIGRATION_GUIDE.md](backend/MIGRATION_GUIDE.md) - Guía de migraciones

### 📖 Rutas de Aprendizaje

**Usuario Nuevo (30 min):**
1. [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) (5 min)
2. [GUIA_DE_USO.md](GUIA_DE_USO.md) (10 min)
3. [EJEMPLOS_USO.md](EJEMPLOS_USO.md) (15 min)

**Administrador (1 hora):**
1. [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)
2. [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md)
3. [CHECKLIST_VERIFICACION.md](CHECKLIST_VERIFICACION.md)

**Desarrollador (2 horas):**
1. [ARCHITECTURE.md](ARCHITECTURE.md)
2. [DIAGRAMA_FLUJO.md](DIAGRAMA_FLUJO.md)
3. [backend/TESTING_GUIDE.md](backend/TESTING_GUIDE.md)

## 🎯 Próximos Pasos

### Corto Plazo
- [ ] Autenticación JWT
- [ ] Hash de contraseñas
- [ ] Paginación en listados
- [ ] Filtros avanzados
- [ ] Exportar reportes

### Mediano Plazo
- [ ] Consultas SNMP reales
- [ ] Health checks periódicos
- [ ] Alertas automáticas
- [ ] Dashboard de analytics
- [ ] Integración Active Directory

### Largo Plazo
- [ ] Mobile app (React Native)
- [ ] API pública
- [ ] Multi-tenancy
- [ ] Machine learning para predicciones
- [ ] Integración con sistemas ERP

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Changelog

### v2.0.0 (Current)
- ✅ PostgreSQL database integration
- ✅ Docker Compose orchestration
- ✅ Repository pattern implementation
- ✅ WebSocket real-time updates
- ✅ Professional discovery modal
- ✅ Bulk provisioning
- ✅ Database admin UI (Adminer)

### v1.0.0
- ✅ Initial release
- ✅ Basic network scanning
- ✅ JSON file storage
- ✅ React frontend
- ✅ FastAPI backend

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la documentación en `/docs`
2. Verifica logs: `docker-compose logs -f`
3. Consulta API docs: http://localhost:8000/docs
4. Revisa issues en el repositorio

## 📄 Licencia

Este proyecto es privado y propietario.

## 🙏 Créditos

Desarrollado para la gestión eficiente de flotas de impresoras Ricoh con arquitectura empresarial escalable.
