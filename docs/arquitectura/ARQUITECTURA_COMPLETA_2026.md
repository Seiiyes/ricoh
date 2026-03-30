# Arquitectura Completa - Ricoh Equipment Manager 2026

**Fecha**: 26 de Marzo de 2026  
**Versión**: 2.1.0  
**Estado**: ✅ PRODUCCIÓN

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Base de Datos](#base-de-datos)
5. [Backend (FastAPI)](#backend-fastapi)
6. [Frontend (React)](#frontend-react)
7. [Módulos del Sistema](#módulos-del-sistema)
8. [Flujos de Datos](#flujos-de-datos)
9. [Seguridad](#seguridad)
10. [Deployment](#deployment)

---

## 🎯 Resumen Ejecutivo

Ricoh Equipment Manager es un sistema integral de gestión de impresoras Ricoh que incluye:

- **Descubrimiento automático** de impresoras en red
- **Aprovisionamiento** de usuarios en impresoras
- **Gestión de contadores** (totales y por usuario)
- **Cierres periódicos** (diarios, semanales, mensuales, personalizados)
- **Multi-tenancy** con gestión de empresas
- **Autenticación JWT** con roles (superadmin, admin, viewer, operator)
- **Exportación** a Excel con formato Ricoh oficial

### Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Módulos Principales | 4 (Governance, Usuarios, Contadores, Cierres) |
| Endpoints API | 35+ endpoints |
| Componentes React | 25+ componentes |
| Tablas Base de Datos | 11 tablas |
| Tests Implementados | 48+ tests |
| Líneas de Código | ~15,000 líneas |

---

## 🛠️ Stack Tecnológico

### Backend
- **Framework**: FastAPI 0.109.0
- **Lenguaje**: Python 3.11+
- **Base de Datos**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0.25
- **Autenticación**: JWT (PyJWT 2.8.0) + bcrypt 4.1.2
- **Web Scraping**: BeautifulSoup4 4.12.3 + Selenium 4.16.0
- **Servidor**: Uvicorn 0.27.0

### Frontend
- **Framework**: React 19.2.0
- **Lenguaje**: TypeScript 5.9.3
- **Build Tool**: Vite 7.3.1
- **Routing**: React Router DOM 7.13.1
- **Estado**: Zustand 5.0.11 + Context API
- **Estilos**: Tailwind CSS 4.1.18
- **Gráficos**: Recharts 3.7.0
- **Exportación**: jsPDF 4.2.0 + xlsx 0.18.5
- **HTTP Client**: Axios 1.13.6

### DevOps
- **Containerización**: Docker + Docker Compose
- **Base de Datos**: PostgreSQL 16 Alpine
- **Admin DB**: Adminer (puerto 8080)
- **Networking**: Bridge network (ricoh-network)

### Testing
- **Framework**: Vitest 4.0.18
- **Testing Library**: @testing-library/react 16.3.2
- **Property Testing**: fast-check 4.5.3
- **Coverage**: ~80% código crítico

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │   Adminer    │  │   Backend    │          │
│  │   Port 5432  │  │   Port 8080  │  │   Port 8000  │          │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘          │
│         │                                     │                  │
│         └─────────────────────────────────────┘                  │
│                    ricoh-network (bridge)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + TS)                       │
│                         Port 5173                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Pages                                                     │ │
│  │  - LoginPage (Autenticación)                              │ │
│  │  - Dashboard (Layout principal)                           │ │
│  │  - EmpresasPage (Gestión empresas - superadmin)          │ │
│  │  - AdminUsersPage (Gestión usuarios admin - superadmin)  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Módulos Principales                                       │ │
│  │  - ProvisioningPanel (Descubrimiento + Aprovisionamiento) │ │
│  │  - AdministracionUsuarios (Gestión usuarios impresoras)   │ │
│  │  - ContadoresModule (Lecturas + Cierres + Comparación)    │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Services                                                  │ │
│  │  - apiClient (Interceptores JWT automáticos)              │ │
│  │  - authService, printerService, counterService            │ │
│  │  - closeService, exportService, empresaService            │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  State Management                                          │ │
│  │  - AuthContext (Usuario actual, login, logout)            │ │
│  │  - Zustand Stores (Printers, Usuarios)                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↕ REST API
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  API Routes (/api)                                         │ │
│  │  - /auth/* (Login, logout, refresh, me)                   │ │
│  │  - /empresas/* (CRUD empresas)                            │ │
│  │  - /admin-users/* (CRUD usuarios admin)                   │ │
│  │  - /printers/* (CRUD impresoras)                          │ │
│  │  - /users/* (CRUD usuarios impresoras)                    │ │
│  │  - /provisioning/* (Aprovisionamiento)                    │ │
│  │  - /discovery/* (Descubrimiento red)                      │ │
│  │  - /counters/* (Lecturas contadores)                      │ │
│  │  - /export/* (Exportaciones Excel/CSV)                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Services (Lógica de Negocio)                             │ │
│  │  - auth_service (Autenticación, bloqueo cuenta)           │ │
│  │  - password_service (Hashing bcrypt)                      │ │
│  │  - jwt_service (Generación/validación tokens)             │ │
│  │  - ricoh_web_client (Scraping web impresoras)             │ │
│  │  - counter_service (Lectura contadores)                   │ │
│  │  - close_service (Gestión cierres)                        │ │
│  │  - export_ricoh (Exportación formato oficial)             │ │
│  │  - network_scanner (Descubrimiento red)                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Middleware                                                │ │
│  │  - auth_middleware (Validación JWT)                       │ │
│  │  - ddos_protection (Rate limiting)                        │ │
│  │  - csrf_protection (CSRF tokens)                          │ │
│  │  - https_redirect (Forzar HTTPS en prod)                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Database Layer (SQLAlchemy)                              │ │
│  │  - Models (ORM)                                            │ │
│  │  - Repository Pattern                                      │ │
│  │  - Migrations (SQL scripts)                                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↕ SQL
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                           │
│  - empresas (Tenants)                                           │
│  - admin_users (Usuarios sistema)                               │
│  - admin_sessions (Sesiones JWT)                                │
│  - admin_audit_log (Auditoría)                                  │
│  - printers (Impresoras)                                        │
│  - users (Usuarios impresoras)                                  │
│  - user_printer_assignments (Asignaciones)                      │
│  - contadores_impresora (Contadores totales)                    │
│  - contadores_usuario (Contadores por usuario)                  │
│  - cierres_mensuales (Cierres periódicos)                       │
│  - cierres_mensuales_usuarios (Snapshots usuarios)              │
└─────────────────────────────────────────────────────────────────┘
```

---


## 🗄️ Base de Datos

### Esquema Completo

```sql
-- AUTENTICACIÓN Y MULTI-TENANCY

CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    razon_social VARCHAR(255) NOT NULL UNIQUE,
    nombre_comercial VARCHAR(50) NOT NULL UNIQUE,
    nit VARCHAR(20) UNIQUE,
    direccion TEXT,
    telefono VARCHAR(50),
    email VARCHAR(255),
    contacto_nombre VARCHAR(255),
    contacto_cargo VARCHAR(100),
    logo_url VARCHAR(500),
    config_json JSON DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    rol VARCHAR(20) NOT NULL, -- superadmin, admin, viewer, operator
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE admin_sessions (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL UNIQUE,
    refresh_token VARCHAR(500) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    refresh_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_user_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL,
    accion VARCHAR(100) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    entidad_tipo VARCHAR(50),
    entidad_id INTEGER,
    detalles JSON,
    resultado VARCHAR(20) NOT NULL, -- success, error
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GESTIÓN DE IMPRESORAS

CREATE TABLE printers (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    location VARCHAR(255),
    empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE RESTRICT,
    status VARCHAR(20) DEFAULT 'offline', -- online, offline, error, maintenance
    detected_model VARCHAR(100),
    serial_number VARCHAR(100),
    has_color BOOLEAN DEFAULT FALSE,
    has_scanner BOOLEAN DEFAULT FALSE,
    has_fax BOOLEAN DEFAULT FALSE,
    tiene_contador_usuario BOOLEAN DEFAULT TRUE,
    usar_contador_ecologico BOOLEAN DEFAULT FALSE,
    formato_contadores VARCHAR(50) DEFAULT 'estandar',
    capabilities_json JSONB,
    inconsistency_count INTEGER DEFAULT 0,
    toner_cyan INTEGER DEFAULT 0,
    toner_magenta INTEGER DEFAULT 0,
    toner_yellow INTEGER DEFAULT 0,
    toner_black INTEGER DEFAULT 0,
    last_seen TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    codigo_de_usuario VARCHAR(8) NOT NULL,
    network_username VARCHAR(255) NOT NULL DEFAULT 'reliteltda\\scaner',
    network_password_encrypted TEXT NOT NULL,
    smb_server VARCHAR(255) NOT NULL,
    smb_port INTEGER DEFAULT 21,
    smb_path VARCHAR(500) NOT NULL,
    func_copier BOOLEAN DEFAULT FALSE,
    func_copier_color BOOLEAN DEFAULT FALSE,
    func_printer BOOLEAN DEFAULT FALSE,
    func_printer_color BOOLEAN DEFAULT FALSE,
    func_document_server BOOLEAN DEFAULT FALSE,
    func_fax BOOLEAN DEFAULT FALSE,
    func_scanner BOOLEAN DEFAULT FALSE,
    func_browser BOOLEAN DEFAULT FALSE,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE RESTRICT,
    centro_costos VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE user_printer_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    provisioned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    entry_index VARCHAR(10),
    func_copier BOOLEAN DEFAULT FALSE,
    func_copier_color BOOLEAN DEFAULT FALSE,
    func_printer BOOLEAN DEFAULT FALSE,
    func_printer_color BOOLEAN DEFAULT FALSE,
    func_document_server BOOLEAN DEFAULT FALSE,
    func_fax BOOLEAN DEFAULT FALSE,
    func_scanner BOOLEAN DEFAULT FALSE,
    func_browser BOOLEAN DEFAULT FALSE
);

-- CONTADORES

CREATE TABLE contadores_impresora (
    id SERIAL PRIMARY KEY,
    printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    total INTEGER DEFAULT 0,
    copiadora_bn INTEGER DEFAULT 0,
    copiadora_color INTEGER DEFAULT 0,
    copiadora_color_personalizado INTEGER DEFAULT 0,
    copiadora_dos_colores INTEGER DEFAULT 0,
    impresora_bn INTEGER DEFAULT 0,
    impresora_color INTEGER DEFAULT 0,
    impresora_color_personalizado INTEGER DEFAULT 0,
    impresora_dos_colores INTEGER DEFAULT 0,
    fax_bn INTEGER DEFAULT 0,
    enviar_total_bn INTEGER DEFAULT 0,
    enviar_total_color INTEGER DEFAULT 0,
    transmision_fax_total INTEGER DEFAULT 0,
    envio_escaner_bn INTEGER DEFAULT 0,
    envio_escaner_color INTEGER DEFAULT 0,
    otras_a3_dlt INTEGER DEFAULT 0,
    otras_duplex INTEGER DEFAULT 0,
    fecha_lectura TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE contadores_usuario (
    id SERIAL PRIMARY KEY,
    printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    codigo_usuario VARCHAR(8) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    total_paginas INTEGER DEFAULT 0,
    total_bn INTEGER DEFAULT 0,
    total_color INTEGER DEFAULT 0,
    copiadora_bn INTEGER DEFAULT 0,
    copiadora_mono_color INTEGER DEFAULT 0,
    copiadora_dos_colores INTEGER DEFAULT 0,
    copiadora_todo_color INTEGER DEFAULT 0,
    copiadora_hojas_2_caras INTEGER DEFAULT 0,
    copiadora_paginas_combinadas INTEGER DEFAULT 0,
    impresora_bn INTEGER DEFAULT 0,
    impresora_mono_color INTEGER DEFAULT 0,
    impresora_dos_colores INTEGER DEFAULT 0,
    impresora_color INTEGER DEFAULT 0,
    impresora_hojas_2_caras INTEGER DEFAULT 0,
    impresora_paginas_combinadas INTEGER DEFAULT 0,
    escaner_bn INTEGER DEFAULT 0,
    escaner_todo_color INTEGER DEFAULT 0,
    fax_bn INTEGER DEFAULT 0,
    fax_paginas_transmitidas INTEGER DEFAULT 0,
    revelado_negro INTEGER DEFAULT 0,
    revelado_color_ymc INTEGER DEFAULT 0,
    eco_uso_2_caras VARCHAR(50),
    eco_uso_combinar VARCHAR(50),
    eco_reduccion_papel VARCHAR(50),
    tipo_contador VARCHAR(20) DEFAULT 'usuario',
    fecha_lectura TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- CIERRES PERIÓDICOS

CREATE TABLE cierres_mensuales (
    id SERIAL PRIMARY KEY,
    printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    tipo_periodo VARCHAR(20) DEFAULT 'mensual', -- diario, semanal, mensual, personalizado
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    total_paginas INTEGER DEFAULT 0,
    total_copiadora INTEGER DEFAULT 0,
    total_impresora INTEGER DEFAULT 0,
    total_escaner INTEGER DEFAULT 0,
    total_fax INTEGER DEFAULT 0,
    diferencia_total INTEGER DEFAULT 0,
    diferencia_copiadora INTEGER DEFAULT 0,
    diferencia_impresora INTEGER DEFAULT 0,
    diferencia_escaner INTEGER DEFAULT 0,
    diferencia_fax INTEGER DEFAULT 0,
    fecha_cierre TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cerrado_por VARCHAR(100),
    notas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    modified_at TIMESTAMP WITH TIME ZONE,
    modified_by VARCHAR(100),
    hash_verificacion VARCHAR(64)
);

CREATE TABLE cierres_mensuales_usuarios (
    id SERIAL PRIMARY KEY,
    cierre_mensual_id INTEGER NOT NULL REFERENCES cierres_mensuales(id) ON DELETE CASCADE,
    codigo_usuario VARCHAR(8) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    total_paginas INTEGER NOT NULL,
    total_bn INTEGER NOT NULL,
    total_color INTEGER NOT NULL,
    copiadora_bn INTEGER NOT NULL,
    copiadora_color INTEGER NOT NULL,
    impresora_bn INTEGER NOT NULL,
    impresora_color INTEGER NOT NULL,
    escaner_bn INTEGER NOT NULL,
    escaner_color INTEGER NOT NULL,
    fax_bn INTEGER NOT NULL,
    consumo_total INTEGER NOT NULL,
    consumo_copiadora INTEGER NOT NULL,
    consumo_impresora INTEGER NOT NULL,
    consumo_escaner INTEGER NOT NULL,
    consumo_fax INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Índices Principales

```sql
-- Índices de búsqueda
CREATE INDEX idx_empresas_razon_social ON empresas(razon_social);
CREATE INDEX idx_empresas_nombre_comercial ON empresas(nombre_comercial);
CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_rol ON admin_users(rol);
CREATE INDEX idx_admin_users_empresa_id ON admin_users(empresa_id);
CREATE INDEX idx_printers_ip_address ON printers(ip_address);
CREATE INDEX idx_printers_empresa_id ON printers(empresa_id);
CREATE INDEX idx_printers_serial_number ON printers(serial_number);
CREATE INDEX idx_users_codigo_usuario ON users(codigo_de_usuario);
CREATE INDEX idx_users_empresa_id ON users(empresa_id);

-- Índices de fechas
CREATE INDEX idx_contadores_impresora_fecha ON contadores_impresora(fecha_lectura);
CREATE INDEX idx_contadores_usuario_fecha ON contadores_usuario(fecha_lectura);
CREATE INDEX idx_cierres_anio_mes ON cierres_mensuales(anio, mes);
CREATE INDEX idx_cierres_fecha_inicio ON cierres_mensuales(fecha_inicio);
CREATE INDEX idx_cierres_fecha_fin ON cierres_mensuales(fecha_fin);

-- Índices de sesiones
CREATE INDEX idx_admin_sessions_token ON admin_sessions(token);
CREATE INDEX idx_admin_sessions_expires_at ON admin_sessions(expires_at);

-- Índices de auditoría
CREATE INDEX idx_audit_log_user_id ON admin_audit_log(admin_user_id);
CREATE INDEX idx_audit_log_accion ON admin_audit_log(accion);
CREATE INDEX idx_audit_log_created_at ON admin_audit_log(created_at);
```

---


## 🔧 Backend (FastAPI)

### Estructura de Directorios

```
backend/
├── api/                          # Endpoints REST
│   ├── auth.py                  # Autenticación (login, logout, refresh, me)
│   ├── auth_schemas.py          # Schemas de autenticación
│   ├── empresas.py              # CRUD empresas
│   ├── empresa_schemas.py       # Schemas de empresas
│   ├── admin_users.py           # CRUD usuarios admin
│   ├── admin_user_schemas.py    # Schemas usuarios admin
│   ├── printers.py              # CRUD impresoras
│   ├── users.py                 # CRUD usuarios impresoras
│   ├── provisioning.py          # Aprovisionamiento
│   ├── discovery.py             # Descubrimiento red
│   ├── counters.py              # Contadores
│   ├── export.py                # Exportaciones
│   ├── ddos_admin.py            # Admin DDoS protection
│   └── schemas.py               # Schemas generales
├── db/                           # Base de datos
│   ├── database.py              # Engine y sesión SQLAlchemy
│   ├── models.py                # Modelos ORM principales
│   ├── models_auth.py           # Modelos autenticación
│   ├── repository.py            # Repository pattern
│   └── migrations/              # Scripts SQL de migración
├── services/                     # Lógica de negocio
│   ├── auth_service.py          # Autenticación y bloqueo
│   ├── password_service.py      # Hashing bcrypt
│   ├── jwt_service.py           # Generación/validación JWT
│   ├── audit_service.py         # Auditoría de acciones
│   ├── ricoh_web_client.py      # Scraping web impresoras
│   ├── counter_service.py       # Lectura contadores
│   ├── close_service.py         # Gestión cierres
│   ├── export_ricoh.py          # Exportación Excel
│   ├── network_scanner.py       # Descubrimiento red
│   ├── provisioning.py          # Lógica aprovisionamiento
│   ├── encryption_service.py    # Encriptación contraseñas
│   ├── company_filter_service.py # Filtrado multi-tenancy
│   └── parsers/                 # Parsers HTML
├── middleware/                   # Middleware
│   ├── auth_middleware.py       # Validación JWT
│   ├── ddos_protection.py       # Rate limiting
│   ├── csrf_protection.py       # CSRF tokens
│   └── https_redirect.py        # Forzar HTTPS
├── jobs/                         # Jobs background
│   └── cleanup_sessions.py      # Limpieza sesiones
├── tests/                        # Tests
│   ├── test_auth_endpoints.py
│   ├── test_password_service.py
│   ├── test_jwt_service.py
│   └── conftest.py
├── scripts/                      # Scripts utilidad
│   ├── init_superadmin.py       # Crear superadmin
│   ├── run_migrations.py        # Ejecutar migraciones
│   └── deploy.sh                # Script deployment
├── main.py                       # Aplicación FastAPI
├── requirements.txt              # Dependencias
└── Dockerfile                    # Container config
```

### Endpoints Principales

#### Autenticación (`/auth`)
- `POST /auth/login` - Login con JWT
- `POST /auth/logout` - Cerrar sesión
- `POST /auth/refresh` - Renovar access token
- `GET /auth/me` - Usuario actual
- `POST /auth/change-password` - Cambiar contraseña
- `POST /auth/rotate-token` - Rotar token automáticamente

#### Empresas (`/empresas`) - Solo Superadmin
- `GET /empresas/` - Listar empresas (paginado)
- `POST /empresas/` - Crear empresa
- `GET /empresas/{id}` - Obtener empresa
- `PUT /empresas/{id}` - Actualizar empresa
- `DELETE /empresas/{id}` - Desactivar empresa
- `GET /empresas/search/{query}` - Buscar empresas

#### Usuarios Admin (`/admin-users`) - Solo Superadmin
- `GET /admin-users/` - Listar usuarios (paginado, filtros)
- `POST /admin-users/` - Crear usuario admin
- `GET /admin-users/{id}` - Obtener usuario
- `PUT /admin-users/{id}` - Actualizar usuario
- `DELETE /admin-users/{id}` - Desactivar usuario

#### Impresoras (`/printers`)
- `GET /printers/` - Listar impresoras (filtrado por empresa)
- `POST /printers/` - Crear impresora
- `GET /printers/{id}` - Obtener impresora
- `PUT /printers/{id}` - Actualizar impresora
- `DELETE /printers/{id}` - Eliminar impresora

#### Usuarios Impresoras (`/users`)
- `GET /users/` - Listar usuarios (filtrado por empresa)
- `POST /users/` - Crear usuario
- `GET /users/{id}` - Obtener usuario
- `PUT /users/{id}` - Actualizar usuario
- `DELETE /users/{id}` - Eliminar usuario

#### Aprovisionamiento (`/provisioning`)
- `POST /provisioning/provision` - Aprovisionar usuario en impresoras
- `POST /provisioning/update-assignment` - Actualizar asignación
- `GET /provisioning/user/{id}` - Estado aprovisionamiento usuario
- `GET /provisioning/printer/{id}` - Usuarios en impresora

#### Descubrimiento (`/discovery`)
- `POST /discovery/scan` - Escanear red
- `POST /discovery/register-discovered` - Registrar impresoras
- `POST /discovery/sync-users` - Sincronizar usuarios desde impresora

#### Contadores (`/counters`)
- `POST /counters/read/{printer_id}` - Lectura manual
- `GET /counters/printer/{printer_id}` - Historial impresora
- `GET /counters/user/{printer_id}` - Historial usuarios
- `POST /counters/close` - Crear cierre
- `GET /counters/closes` - Listar cierres
- `GET /counters/close/{id}` - Detalle cierre
- `GET /counters/close/{id}/users` - Usuarios del cierre
- `POST /counters/compare` - Comparar cierres

#### Exportación (`/export`)
- `POST /export/comparison` - Exportar comparación Excel
- `POST /export/close/{id}` - Exportar cierre Excel
- `POST /export/users-csv` - Exportar usuarios CSV

### Servicios Clave

#### RicohWebClient
Servicio principal para interactuar con la interfaz web de las impresoras Ricoh.

**Funciones principales:**
- `get_user_list()` - Obtener lista de usuarios
- `provision_user()` - Crear usuario en impresora
- `update_user()` - Actualizar usuario existente
- `set_user_functions()` - Configurar permisos (copiadora, impresora, escáner, etc.)
- `read_counters()` - Leer contadores totales
- `read_user_counters()` - Leer contadores por usuario

**Lógica de Permisos:**
- `BW` (Black & White) = Blanco y Negro
- `FC` (Full Color) = A todo color
- `TC` (Two Colors) = Dos colores → COLOR
- `MC` (Multi Color) = Color personalizado → COLOR

#### CounterService
Gestión de lecturas de contadores.

**Funciones:**
- `read_printer_counters()` - Lectura total impresora
- `read_user_counters()` - Lectura usuarios
- `get_counter_history()` - Historial lecturas
- `detect_counter_format()` - Detectar formato (18 cols, 13 cols, ecológico)

#### CloseService
Gestión de cierres periódicos.

**Funciones:**
- `create_close()` - Crear cierre (snapshot inmutable)
- `get_closes()` - Listar cierres con filtros
- `get_close_detail()` - Detalle completo cierre
- `compare_closes()` - Comparar dos cierres
- `calculate_consumption()` - Calcular consumo período

---


## ⚛️ Frontend (React)

### Estructura de Directorios

```
src/
├── components/                   # Componentes React
│   ├── contadores/              # Módulo Contadores
│   │   ├── ContadoresModule.tsx
│   │   ├── LecturaManual.tsx
│   │   ├── HistorialLecturas.tsx
│   │   ├── cierres/
│   │   │   ├── CierresTab.tsx
│   │   │   ├── CierreModal.tsx
│   │   │   ├── CierreDetailModal.tsx
│   │   │   └── ComparacionTab.tsx
│   │   └── ...
│   ├── discovery/               # Descubrimiento
│   │   └── DiscoveryModal.tsx
│   ├── fleet/                   # Gestión impresoras
│   │   ├── PrinterCard.tsx
│   │   └── EditPrinterModal.tsx
│   ├── governance/              # Aprovisionamiento
│   │   └── ProvisioningPanel.tsx
│   ├── usuarios/                # Gestión usuarios
│   │   ├── AdministracionUsuarios.tsx
│   │   ├── UserFormModal.tsx
│   │   └── SyncModal.tsx
│   ├── ui/                      # Componentes UI base
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Alert.tsx
│   │   ├── Card.tsx
│   │   └── EmpresaAutocomplete.tsx
│   ├── AdminUserModal.tsx       # Modal usuarios admin
│   ├── EmpresaModal.tsx         # Modal empresas
│   └── ProtectedRoute.tsx       # Protección rutas
├── contexts/                     # Contextos React
│   └── AuthContext.tsx          # Contexto autenticación
├── pages/                        # Páginas principales
│   ├── LoginPage.tsx            # Login
│   ├── Dashboard.tsx            # Layout principal
│   ├── EmpresasPage.tsx         # Gestión empresas
│   ├── AdminUsersPage.tsx       # Gestión usuarios admin
│   └── UnauthorizedPage.tsx     # Sin permisos
├── services/                     # Servicios API
│   ├── apiClient.ts             # Cliente HTTP con interceptores
│   ├── authService.ts           # Autenticación
│   ├── printerService.ts        # Impresoras
│   ├── servicioUsuarios.ts      # Usuarios impresoras
│   ├── counterService.ts        # Contadores
│   ├── closeService.ts          # Cierres
│   ├── exportService.ts         # Exportaciones
│   ├── empresaService.ts        # Empresas
│   ├── adminUserService.ts      # Usuarios admin
│   └── discoveryService.ts      # Descubrimiento
├── store/                        # Estado Zustand
│   ├── usePrinterStore.ts       # Store impresoras
│   └── useUsuarioStore.ts       # Store usuarios
├── types/                        # Tipos TypeScript
│   ├── index.ts                 # Tipos generales
│   ├── printer.ts               # Tipos impresoras
│   ├── usuario.ts               # Tipos usuarios
│   └── counter.ts               # Tipos contadores
├── utils/                        # Utilidades
│   ├── errorHandler.ts          # Manejo errores
│   ├── printerTransform.ts      # Transformaciones
│   └── columnFiltering.ts       # Filtrado columnas
├── App.tsx                       # Componente raíz
└── main.tsx                      # Entry point
```

### Componentes Principales

#### Dashboard
Layout principal con sidebar de navegación y rutas internas.

**Rutas:**
- `/descubrimiento` - Descubrir impresoras
- `/aprovisionamiento` - Crear usuarios
- `/administracion` - Administrar usuarios
- `/contadores` - Contadores y cierres
- `/empresas` - Gestión empresas (superadmin)
- `/admin-users` - Usuarios admin (superadmin)

#### ProvisioningPanel
Panel de aprovisionamiento con dos modos:
- **Modo Descubrimiento**: Solo descubrir y registrar impresoras
- **Modo Aprovisionamiento**: Crear usuarios y asignar a impresoras

#### AdministracionUsuarios
Gestión completa de usuarios de impresoras:
- Listar usuarios con búsqueda y filtros
- Sincronizar usuarios desde impresora
- Editar usuarios existentes
- Actualizar asignaciones (permisos por impresora)

#### ContadoresModule
Módulo completo de contadores con 3 tabs:
- **Lectura Manual**: Leer contadores de impresora
- **Cierres**: Crear y gestionar cierres periódicos
- **Comparación**: Comparar dos cierres

### Servicios Frontend

#### apiClient
Cliente HTTP centralizado con interceptores automáticos:
- Agrega token JWT a todas las peticiones
- Renueva token automáticamente si expira (401/403)
- Maneja errores de forma consistente
- Guarda CSRF tokens automáticamente

```typescript
// Interceptor de request
config.headers.Authorization = `Bearer ${token}`;
config.headers['X-CSRF-Token'] = csrfToken;

// Interceptor de response
if (error.status === 401 && !originalRequest._retry) {
  // Renovar token automáticamente
  const newToken = await refreshToken();
  // Reintentar request original
  return apiClient(originalRequest);
}
```

#### authService
Gestión de autenticación:
- `login()` - Autenticar usuario
- `logout()` - Cerrar sesión
- `refreshToken()` - Renovar token
- `getCurrentUser()` - Usuario actual
- `changePassword()` - Cambiar contraseña

#### closeService
Gestión de cierres:
- `createClose()` - Crear cierre
- `getCloses()` - Listar cierres
- `getCloseDetail()` - Detalle cierre
- `getCloseUsers()` - Usuarios del cierre
- `compareCloses()` - Comparar cierres

#### exportService
Exportaciones:
- `exportComparison()` - Exportar comparación Excel
- `exportClose()` - Exportar cierre Excel
- `exportUsersCSV()` - Exportar usuarios CSV

**Nota**: Usa `fetch()` nativo en lugar de `axios` para evitar problemas CORS con `responseType: 'blob'`.

### Estado Global

#### AuthContext
Contexto de autenticación con hook `useAuth()`:
- `user` - Usuario actual
- `isAuthenticated` - Estado autenticación
- `loading` - Cargando
- `login()` - Función login
- `logout()` - Función logout
- `refreshToken()` - Renovar token

**Renovación automática**: Cada 25 minutos renueva el token automáticamente.

#### usePrinterStore (Zustand)
Store de impresoras:
- `printers` - Lista impresoras
- `selectedPrinters` - Impresoras seleccionadas
- `setPrinters()` - Actualizar lista
- `togglePrinter()` - Seleccionar/deseleccionar
- `clearSelection()` - Limpiar selección

#### useUsuarioStore (Zustand)
Store de usuarios:
- `usuarios` - Lista usuarios
- `setUsuarios()` - Actualizar lista
- `addUsuario()` - Agregar usuario
- `updateUsuario()` - Actualizar usuario

### Patrones de Diseño

#### Protected Routes
Rutas protegidas con validación de autenticación y roles:

```typescript
<ProtectedRoute requiredRole={['superadmin']}>
  <EmpresasPage />
</ProtectedRoute>
```

#### Error Handling
Manejo consistente de errores con utilidad `parseApiError()`:

```typescript
try {
  await apiCall();
} catch (error) {
  const message = parseApiError(error);
  setError(message);
}
```

#### Loading States
Estados de carga en todos los componentes:

```typescript
const [loading, setLoading] = useState(false);

<Button loading={loading} disabled={loading}>
  {loading ? 'Procesando...' : 'Guardar'}
</Button>
```

---


## 📦 Módulos del Sistema

### 1. Módulo de Autenticación y Multi-Tenancy

**Estado**: ✅ COMPLETADO

**Funcionalidades:**
- Login con JWT (access token 30 min + refresh token 7 días)
- Logout con invalidación de sesión
- Renovación automática de token
- Cambio de contraseña
- Bloqueo de cuenta (5 intentos = 15 min bloqueado)
- Gestión de empresas (CRUD completo)
- Gestión de usuarios admin (CRUD completo)
- Filtrado automático por empresa
- Auditoría completa de acciones

**Roles:**
- `superadmin` - Acceso total, gestiona empresas y usuarios admin
- `admin` - Gestiona su empresa, ve solo sus datos
- `viewer` - Solo lectura
- `operator` - Operaciones básicas

**Archivos clave:**
- Backend: `api/auth.py`, `services/auth_service.py`, `middleware/auth_middleware.py`
- Frontend: `contexts/AuthContext.tsx`, `services/authService.ts`, `pages/LoginPage.tsx`

---

### 2. Módulo de Governance (Aprovisionamiento)

**Estado**: ✅ COMPLETADO

**Funcionalidades:**
- Descubrimiento automático de impresoras en red
- Registro de impresoras descubiertas
- Creación de usuarios de impresoras
- Aprovisionamiento masivo (usuario → múltiples impresoras)
- Configuración de permisos por función:
  - Copiadora (B/N y Color)
  - Impresora (B/N y Color)
  - Escáner
  - Fax
  - Document Server
  - Navegador

**Flujo de trabajo:**
1. Escanear red (rango IP)
2. Seleccionar impresoras descubiertas
3. Registrar impresoras en sistema
4. Crear usuario con permisos
5. Seleccionar impresoras destino
6. Aprovisionar usuario

**Archivos clave:**
- Backend: `api/provisioning.py`, `services/ricoh_web_client.py`
- Frontend: `components/governance/ProvisioningPanel.tsx`

---

### 3. Módulo de Administración de Usuarios

**Estado**: ✅ COMPLETADO

**Funcionalidades:**
- Listar usuarios con búsqueda y filtros
- Sincronizar usuarios desde impresora (todos o específico)
- Editar usuarios existentes
- Actualizar asignaciones (permisos por impresora)
- Agregar/quitar dispositivos
- Configuración de carpeta SMB
- Gestión de contraseña de carpeta

**Sincronización:**
- **Todos los usuarios**: Lee todos los usuarios de la impresora
- **Usuario específico**: Lee solo el usuario con código especificado
- **Actualización automática**: Actualiza la vista después de sincronizar

**Archivos clave:**
- Backend: `api/users.py`, `services/ricoh_web_client.py`
- Frontend: `components/usuarios/AdministracionUsuarios.tsx`

---

### 4. Módulo de Contadores

**Estado**: ✅ COMPLETADO

**Funcionalidades:**
- Lectura manual de contadores totales
- Lectura de contadores por usuario
- Historial de lecturas
- Soporte para múltiples formatos:
  - Estándar (18 columnas)
  - Simplificado (13 columnas)
  - Ecológico (getEcoCounter.cgi)
- Detección automática de formato
- Visualización de contadores en tiempo real

**Tipos de contadores:**
- **Totales**: Copiadora, Impresora, Escáner, Fax
- **Por usuario**: Desglose completo por función y color
- **Ecológicos**: Uso 2 caras, combinar, reducción papel

**Archivos clave:**
- Backend: `api/counters.py`, `services/counter_service.py`
- Frontend: `components/contadores/ContadoresModule.tsx`

---

### 5. Módulo de Cierres Periódicos

**Estado**: ✅ COMPLETADO

**Funcionalidades:**
- Crear cierres (diario, semanal, mensual, personalizado)
- Snapshot inmutable de contadores
- Listar cierres con filtros
- Detalle completo de cierre
- Comparación entre dos cierres
- Exportación a Excel (formato Ricoh oficial)
- Cálculo automático de consumo
- Validación de integridad (hash)

**Tipos de cierre:**
- **Diario**: Snapshot de un día
- **Semanal**: Período de 7 días
- **Mensual**: Mes completo
- **Personalizado**: Rango de fechas libre

**Comparación:**
- Diferencias por usuario
- Consumo del período
- Totales por función
- Exportación a Excel con formato oficial

**Archivos clave:**
- Backend: `api/counters.py`, `services/close_service.py`, `services/export_ricoh.py`
- Frontend: `components/contadores/cierres/`

---

### 6. Módulo de Exportación

**Estado**: ✅ COMPLETADO

**Funcionalidades:**
- Exportar comparación a Excel (formato Ricoh)
- Exportar cierre individual a Excel
- Exportar usuarios a CSV
- Formato oficial con:
  - Encabezados corporativos
  - Totales por función
  - Desglose por usuario
  - Fórmulas automáticas
  - Estilos y colores

**Formatos soportados:**
- **Excel (.xlsx)**: Comparaciones y cierres
- **CSV (.csv)**: Usuarios

**Archivos clave:**
- Backend: `api/export.py`, `services/export_ricoh.py`
- Frontend: `services/exportService.ts`

---

### 7. Módulo de Gestión de Empresas

**Estado**: ✅ COMPLETADO (Solo Superadmin)

**Funcionalidades:**
- Crear empresas (tenants)
- Editar información de empresa
- Desactivar empresas
- Búsqueda por razón social o nombre comercial
- Validaciones:
  - Nombre comercial en kebab-case
  - Email válido
  - Unicidad de razón social y NIT

**Campos:**
- Razón social
- Nombre comercial
- NIT
- Dirección, teléfono, email
- Contacto (nombre y cargo)
- Logo URL
- Configuración JSON

**Archivos clave:**
- Backend: `api/empresas.py`
- Frontend: `pages/EmpresasPage.tsx`, `components/EmpresaModal.tsx`

---

### 8. Módulo de Usuarios Admin

**Estado**: ✅ COMPLETADO (Solo Superadmin)

**Funcionalidades:**
- Crear usuarios administradores
- Editar usuarios existentes
- Desactivar usuarios
- Búsqueda por username, nombre o email
- Filtros por rol y empresa
- Validación de contraseña con medidor visual
- Asignación de empresa según rol

**Validaciones:**
- Username único
- Email válido y único
- Contraseña fuerte (8+ chars, mayúscula, minúscula, número, especial)
- Superadmin no requiere empresa
- Admin/Viewer/Operator requieren empresa

**Archivos clave:**
- Backend: `api/admin_users.py`
- Frontend: `pages/AdminUsersPage.tsx`, `components/AdminUserModal.tsx`

---


## 🔄 Flujos de Datos Principales

### Flujo de Autenticación

```
1. Usuario ingresa credenciales
   ↓
2. Frontend: authService.login(username, password)
   ↓
3. POST /auth/login
   ↓
4. Backend: Validar credenciales
   ↓
5. Backend: Generar access_token (30 min) + refresh_token (7 días)
   ↓
6. Backend: Crear sesión en admin_sessions
   ↓
7. Backend: Registrar en audit_log
   ↓
8. Response: {access_token, refresh_token, user}
   ↓
9. Frontend: Guardar tokens en sessionStorage
   ↓
10. Frontend: Actualizar AuthContext con usuario
   ↓
11. Frontend: Redirigir a /descubrimiento
```

### Flujo de Renovación Automática de Token

```
1. Usuario hace petición API
   ↓
2. apiClient interceptor: Agregar Authorization header
   ↓
3. Backend: Validar token
   ↓
4. Si token expirado → Response 401
   ↓
5. apiClient interceptor: Detectar 401
   ↓
6. apiClient: POST /auth/refresh {refresh_token}
   ↓
7. Backend: Validar refresh_token
   ↓
8. Backend: Generar nuevo access_token
   ↓
9. Response: {access_token}
   ↓
10. apiClient: Guardar nuevo token
   ↓
11. apiClient: Reintentar petición original con nuevo token
   ↓
12. Response exitosa
```

### Flujo de Aprovisionamiento

```
1. Usuario crea usuario de impresora
   ↓
2. Frontend: POST /users/ {name, codigo, smb_path, permisos}
   ↓
3. Backend: Validar datos
   ↓
4. Backend: Encriptar network_password
   ↓
5. Backend: Crear registro en tabla users
   ↓
6. Response: {user_id}
   ↓
7. Usuario selecciona impresoras destino
   ↓
8. Frontend: POST /provisioning/provision {user_id, printer_ids[]}
   ↓
9. Backend: Para cada impresora:
   ↓
10. Backend: ricoh_web_client.provision_user()
    - Login a web impresora
    - Crear usuario en impresora
    - Configurar permisos (COPY_BW, PRT_BW, SCAN, etc.)
    - Configurar carpeta SMB
    - Establecer contraseña "Temporal2021"
   ↓
11. Backend: Crear user_printer_assignment
   ↓
12. Backend: Registrar en audit_log
   ↓
13. Response: {success, assignments[]}
   ↓
14. Frontend: Mostrar mensaje éxito
```

### Flujo de Lectura de Contadores

```
1. Usuario selecciona impresora
   ↓
2. Usuario hace clic en "Lectura Manual"
   ↓
3. Frontend: POST /counters/read/{printer_id}
   ↓
4. Backend: ricoh_web_client.read_counters()
   - Login a web impresora
   - Acceder a getUnificationCounter.cgi
   - Parsear HTML
   - Extraer contadores totales
   ↓
5. Backend: Guardar en contadores_impresora
   ↓
6. Backend: ricoh_web_client.read_user_counters()
   - Acceder a getUserCounter.cgi o getEcoCounter.cgi
   - Parsear HTML (detectar formato automáticamente)
   - Extraer contadores por usuario
   ↓
7. Backend: Guardar en contadores_usuario
   ↓
8. Response: {printer_counters, user_counters[]}
   ↓
9. Frontend: Actualizar vista con contadores
```

### Flujo de Creación de Cierre

```
1. Usuario selecciona impresora
   ↓
2. Usuario hace clic en "Crear Cierre"
   ↓
3. Usuario ingresa: tipo_periodo, fecha_inicio, fecha_fin, notas
   ↓
4. Frontend: POST /counters/close
   ↓
5. Backend: Leer contadores actuales (snapshot)
   ↓
6. Backend: Buscar cierre anterior del mismo tipo
   ↓
7. Backend: Calcular diferencias (consumo del período)
   ↓
8. Backend: Crear registro en cierres_mensuales
   ↓
9. Backend: Para cada usuario:
   - Calcular consumo individual
   - Crear registro en cierres_mensuales_usuarios
   ↓
10. Backend: Generar hash de verificación
   ↓
11. Backend: Registrar en audit_log
   ↓
12. Response: {close_id, totals, users[]}
   ↓
13. Frontend: Mostrar mensaje éxito
   ↓
14. Frontend: Actualizar lista de cierres
```

### Flujo de Comparación de Cierres

```
1. Usuario selecciona dos cierres
   ↓
2. Usuario hace clic en "Comparar"
   ↓
3. Frontend: POST /counters/compare {close_id_1, close_id_2}
   ↓
4. Backend: Obtener datos de ambos cierres
   ↓
5. Backend: Para cada usuario:
   - Buscar en cierre 1
   - Buscar en cierre 2
   - Calcular diferencias
   ↓
6. Backend: Calcular totales
   ↓
7. Response: {comparison_data, users[], totals}
   ↓
8. Frontend: Mostrar tabla comparativa
   ↓
9. Usuario hace clic en "Exportar"
   ↓
10. Frontend: POST /export/comparison
   ↓
11. Backend: Generar Excel con formato Ricoh
   ↓
12. Response: Archivo .xlsx
   ↓
13. Frontend: Descargar archivo
```

### Flujo de Sincronización de Usuarios

```
1. Usuario selecciona impresora
   ↓
2. Usuario hace clic en "Sincronizar Usuarios"
   ↓
3. Usuario elige: "Todos" o "Específico"
   ↓
4. Si específico: Ingresa código de usuario
   ↓
5. Frontend: POST /discovery/sync-users {printer_id, user_code?}
   ↓
6. Backend: ricoh_web_client.get_user_list()
   - Login a web impresora
   - Acceder a lista de usuarios
   - Parsear HTML
   - Extraer usuarios (filtrar por código si aplica)
   ↓
7. Backend: Para cada usuario:
   - Buscar en base de datos
   - Si existe: Actualizar
   - Si no existe: Crear
   - Actualizar user_printer_assignment
   ↓
8. Response: {users[], created, updated}
   ↓
9. Frontend: Actualizar lista de usuarios
   ↓
10. Frontend: Mostrar mensaje con estadísticas
```

---


## 🔒 Seguridad

### Autenticación y Autorización

#### JWT (JSON Web Tokens)
- **Access Token**: 30 minutos de validez
- **Refresh Token**: 7 días de validez
- **Algoritmo**: HS256
- **Claims**: user_id, username, rol, empresa_id, exp, iat
- **Almacenamiento**: sessionStorage (no localStorage)

#### Hashing de Contraseñas
- **Algoritmo**: bcrypt
- **Rounds**: 12 (balance seguridad/performance)
- **Validación**: Mínimo 8 caracteres, mayúscula, minúscula, número, especial

#### Bloqueo de Cuenta
- **Intentos permitidos**: 5
- **Duración bloqueo**: 15 minutos
- **Reset**: Automático después del tiempo

#### Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **superadmin** | Acceso total, gestiona empresas y usuarios admin |
| **admin** | Gestiona su empresa, CRUD completo de recursos |
| **viewer** | Solo lectura de recursos de su empresa |
| **operator** | Operaciones básicas (lecturas, cierres) |

### Multi-Tenancy

#### Filtrado Automático
- Todos los endpoints filtran por `empresa_id` automáticamente
- Superadmin ve todos los datos
- Admin/Viewer/Operator solo ven datos de su empresa
- Validación en backend (no confiar en frontend)

#### Aislamiento de Datos
- Cada empresa tiene sus propios:
  - Impresoras
  - Usuarios de impresoras
  - Contadores
  - Cierres
- No hay acceso cruzado entre empresas

### Protección CORS

```python
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)
```

### Headers de Seguridad

```python
# HSTS (solo producción)
Strict-Transport-Security: max-age=31536000; includeSubDomains

# Prevenir MIME sniffing
X-Content-Type-Options: nosniff

# Prevenir clickjacking
X-Frame-Options: DENY

# XSS Protection
X-XSS-Protection: 1; mode=block
```

### Rate Limiting

#### DDoS Protection
- **Login**: 5 intentos por minuto por IP
- **Refresh**: 10 intentos por minuto por IP
- **API General**: 100 peticiones por minuto por IP

#### Implementación
```python
@app.middleware("http")
async def ddos_protection(request: Request, call_next):
    client_ip = request.client.host
    
    if is_rate_limited(client_ip, request.url.path):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )
    
    return await call_next(request)
```

### CSRF Protection

#### Tokens CSRF
- Generados automáticamente en cada respuesta
- Validados en peticiones mutables (POST, PUT, DELETE, PATCH)
- Almacenados en sessionStorage
- Enviados en header `X-CSRF-Token`

#### Configuración
```python
# Deshabilitado por defecto, habilitar con:
ENABLE_CSRF=true
```

### Encriptación de Datos Sensibles

#### Contraseñas de Red
- Encriptadas con Fernet (symmetric encryption)
- Clave derivada de SECRET_KEY
- Almacenadas en `network_password_encrypted`

```python
from services.encryption_service import EncryptionService

# Encriptar
encrypted = EncryptionService.encrypt("password123")

# Desencriptar
decrypted = EncryptionService.decrypt(encrypted)
```

### Auditoría

#### Registro de Acciones
Todas las acciones administrativas se registran en `admin_audit_log`:
- Usuario que ejecutó la acción
- Acción realizada (crear, actualizar, eliminar)
- Módulo afectado
- Entidad y ID
- Detalles JSON
- Resultado (success, error)
- IP y User Agent
- Timestamp

#### Consultas de Auditoría
```python
# Historial de usuario
GET /audit/user/{user_id}

# Historial de entidad
GET /audit/entity/{entity_type}/{entity_id}
```

### Validación de Entrada

#### Pydantic Schemas
Todos los endpoints validan entrada con Pydantic:
- Tipos de datos
- Longitudes mínimas/máximas
- Formatos (email, URL, etc.)
- Valores permitidos (enums)
- Campos requeridos vs opcionales

#### Sanitización
- Escape de HTML en inputs de texto
- Validación de IPs y rangos de red
- Validación de rutas SMB
- Prevención de SQL injection (ORM)

### Sesiones

#### Gestión de Sesiones
- Almacenadas en tabla `admin_sessions`
- Limpieza automática cada hora (job background)
- Invalidación en logout
- Expiración automática

#### Cleanup Job
```python
# Ejecuta cada hora
async def cleanup_expired_sessions():
    db.query(AdminSession).filter(
        AdminSession.expires_at < datetime.now()
    ).delete()
```

### HTTPS/TLS

#### Producción
- Forzar HTTPS con middleware
- Certificados SSL/TLS
- Redirigir HTTP → HTTPS automáticamente

```python
# Habilitar con:
FORCE_HTTPS=true
ENVIRONMENT=production
```

### Logging Seguro

#### Filtrado de Datos Sensibles
- Contraseñas enmascaradas en logs
- Tokens JWT truncados (solo primeros y últimos 4 chars)
- Datos sensibles reemplazados con `[REDACTED]`

```python
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if 'password' in str(record.msg).lower():
            record.msg = '[REDACTED]'
        return True
```

---


## 🚀 Deployment

### Requisitos del Sistema

#### Hardware Mínimo
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 20 GB
- **Red**: 100 Mbps

#### Hardware Recomendado
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disco**: 50+ GB SSD
- **Red**: 1 Gbps

#### Software
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Sistema Operativo**: Linux (Ubuntu 20.04+), Windows 10+, macOS 11+

### Configuración de Entorno

#### Variables de Entorno Backend

```bash
# Base de datos
DATABASE_URL=postgresql://ricoh_admin:ricoh_secure_2024@postgres:5432/ricoh_fleet

# Seguridad
SECRET_KEY=ricoh-jwt-secret-key-change-in-production-min-32-chars
ENVIRONMENT=production

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Features
DEMO_MODE=false
DEBUG=false
ENABLE_CSRF=true
FORCE_HTTPS=true
ENABLE_SESSION_CLEANUP=true

# Logging
LOG_LEVEL=INFO
```

#### Variables de Entorno Frontend

```bash
# API URL
VITE_API_URL=http://localhost:8000
```

### Docker Compose

#### Desarrollo

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reiniciar servicio específico
docker-compose restart backend
```

#### Producción

```bash
# Build con optimizaciones
docker-compose -f docker-compose.prod.yml build

# Iniciar en modo producción
docker-compose -f docker-compose.prod.yml up -d

# Escalar backend (múltiples instancias)
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Inicialización

#### Primera Vez

```bash
# 1. Levantar base de datos
docker-compose up -d postgres

# 2. Esperar a que esté lista
docker-compose logs -f postgres

# 3. Ejecutar migraciones
docker exec -it ricoh-backend python scripts/run_migrations.py

# 4. Crear superadmin
docker exec -it ricoh-backend python scripts/init_superadmin.py

# 5. Levantar todos los servicios
docker-compose up -d
```

#### Credenciales Iniciales

```
Usuario: superadmin
Contraseña: {:Z75M!=x>9PiPp2
```

**IMPORTANTE**: Cambiar contraseña inmediatamente después del primer login.

### Migraciones de Base de Datos

#### Ejecutar Migraciones

```bash
# Dentro del contenedor
docker exec -it ricoh-backend python scripts/run_migrations.py

# O localmente
cd backend
python scripts/run_migrations.py
```

#### Crear Nueva Migración

```sql
-- backend/migrations/012_nueva_migracion.sql
-- Descripción de la migración

ALTER TABLE tabla ADD COLUMN nueva_columna VARCHAR(255);

-- Rollback (opcional)
-- ALTER TABLE tabla DROP COLUMN nueva_columna;
```

### Respaldos

#### Base de Datos

```bash
# Crear respaldo
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > backup_$(date +%Y%m%d_%H%M%S).sql

# O usar script
./backup-db.bat  # Windows
./backup-db.sh   # Linux/Mac

# Restaurar respaldo
docker exec -i ricoh-postgres psql -U ricoh_admin ricoh_fleet < backup_20260326_120000.sql

# O usar script
./restore-db.bat backup_20260326_120000.sql  # Windows
./restore-db.sh backup_20260326_120000.sql   # Linux/Mac
```

#### Archivos

```bash
# Respaldo completo
tar -czf ricoh_backup_$(date +%Y%m%d).tar.gz \
  backend/ \
  src/ \
  docker-compose.yml \
  .env

# Restaurar
tar -xzf ricoh_backup_20260326.tar.gz
```

### Monitoreo

#### Logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f backend
docker-compose logs -f postgres

# Últimas 100 líneas
docker-compose logs --tail 100 backend

# Logs de aplicación
tail -f backend/logs/ricoh_api.log
```

#### Health Checks

```bash
# Backend
curl http://localhost:8000/

# Base de datos
docker exec ricoh-postgres pg_isready -U ricoh_admin

# Frontend
curl http://localhost:5173/
```

#### Métricas

```bash
# Uso de recursos
docker stats

# Espacio en disco
docker system df

# Logs de contenedor
docker logs ricoh-backend --tail 50
```

### Actualización

#### Actualizar Código

```bash
# 1. Detener servicios
docker-compose down

# 2. Actualizar código (git pull, etc.)
git pull origin main

# 3. Rebuild imágenes
docker-compose build

# 4. Ejecutar migraciones
docker-compose up -d postgres
docker exec -it ricoh-backend python scripts/run_migrations.py

# 5. Iniciar servicios
docker-compose up -d
```

#### Actualizar Dependencias

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
npm install

# Rebuild Docker
docker-compose build
```

### Troubleshooting

#### Backend no inicia

```bash
# Ver logs
docker-compose logs backend

# Verificar base de datos
docker-compose logs postgres

# Reiniciar
docker-compose restart backend
```

#### Error de conexión a base de datos

```bash
# Verificar que postgres esté corriendo
docker-compose ps

# Verificar health check
docker exec ricoh-postgres pg_isready -U ricoh_admin

# Verificar variables de entorno
docker exec ricoh-backend env | grep DATABASE_URL
```

#### Frontend no carga

```bash
# Verificar que backend esté corriendo
curl http://localhost:8000/

# Ver logs frontend
docker-compose logs frontend

# Verificar VITE_API_URL
docker exec ricoh-frontend env | grep VITE_API_URL
```

#### Error 403 en API

```bash
# Verificar token
# En DevTools → Application → Session Storage → access_token

# Verificar CORS
# En DevTools → Network → Ver headers de respuesta

# Verificar logs backend
docker-compose logs backend | grep CORS
```

### URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:5173 | Aplicación web |
| Backend API | http://localhost:8000 | API REST |
| Swagger Docs | http://localhost:8000/docs | Documentación interactiva |
| ReDoc | http://localhost:8000/redoc | Documentación alternativa |
| Adminer | http://localhost:8080 | Admin base de datos |
| PostgreSQL | localhost:5432 | Base de datos (interno) |

### Comandos Útiles

```bash
# Ver estado de servicios
docker-compose ps

# Reiniciar todo
docker-compose restart

# Limpiar todo (CUIDADO: borra datos)
docker-compose down -v

# Ver uso de recursos
docker stats

# Entrar a contenedor
docker exec -it ricoh-backend bash
docker exec -it ricoh-postgres psql -U ricoh_admin ricoh_fleet

# Ver redes
docker network ls
docker network inspect ricoh-network

# Ver volúmenes
docker volume ls
docker volume inspect ricoh-postgres-data
```

---

## 📚 Documentación Adicional

### Documentos Técnicos
- `docs/ARCHITECTURE.md` - Arquitectura detallada
- `docs/ESTADO_ACTUAL_PROYECTO.md` - Estado del proyecto
- `docs/API_CONTADORES.md` - API de contadores
- `docs/API_CIERRES_MENSUALES.md` - API de cierres
- `docs/SISTEMA_AUTENTICACION_COMPLETADO.md` - Sistema de autenticación

### Guías de Usuario
- `docs/GUIA_USUARIO.md` - Guía completa de usuario
- `docs/GUIA_RAPIDA.md` - Inicio rápido
- `docs/INICIO_RAPIDO.md` - Primeros pasos

### Deployment
- `docs/DEPLOYMENT_GUIDE.md` - Guía de deployment
- `docs/TROUBLESHOOTING_DOCKER.md` - Solución de problemas Docker
- `docs/GUIA_RESPALDO_BASE_DATOS.md` - Respaldos

### Fixes y Mejoras
- `docs/RESUMEN_FIXES_RECIENTES_25_MARZO.md` - Últimos fixes
- `docs/FIX_LOGICA_PERMISOS_COLOR.md` - Fix permisos color
- `docs/FIX_ERROR_ASIGNAR_EMPRESA_IMPRESORA.md` - Fix asignación empresa
- `docs/MEJORA_CAMPO_CERRADO_POR_AUTOMATICO.md` - Mejora campo cerrado por

---

## 🎯 Estado del Proyecto

### Completado (100%)

✅ **Autenticación y Multi-Tenancy**
- Login/Logout con JWT
- Gestión de empresas
- Gestión de usuarios admin
- Filtrado automático por empresa
- Auditoría completa

✅ **Módulo de Governance**
- Descubrimiento de red
- Registro de impresoras
- Aprovisionamiento de usuarios
- Configuración de permisos

✅ **Módulo de Usuarios**
- CRUD completo
- Sincronización desde impresoras
- Actualización de asignaciones
- Gestión de permisos por dispositivo

✅ **Módulo de Contadores**
- Lectura manual
- Historial de lecturas
- Soporte múltiples formatos
- Detección automática

✅ **Módulo de Cierres**
- Cierres periódicos (diario, semanal, mensual, personalizado)
- Comparación de cierres
- Exportación Excel formato Ricoh
- Validación de integridad

✅ **Seguridad**
- JWT con renovación automática
- Hashing bcrypt
- Rate limiting
- CORS configurado
- Headers de seguridad
- Encriptación de datos sensibles

✅ **Testing**
- 48+ tests implementados
- Cobertura ~80% código crítico
- Tests unitarios e integración

✅ **Documentación**
- Arquitectura completa
- Guías de usuario
- API documentation
- Troubleshooting

### Métricas Finales

| Métrica | Valor |
|---------|-------|
| **Líneas de Código** | ~15,000 |
| **Endpoints API** | 35+ |
| **Componentes React** | 25+ |
| **Tablas BD** | 11 |
| **Tests** | 48+ |
| **Documentos** | 100+ |
| **Tiempo Desarrollo** | 6 meses |
| **Estado** | ✅ PRODUCCIÓN |

---

**Última Actualización**: 26 de Marzo de 2026  
**Versión del Documento**: 1.0  
**Mantenido por**: Equipo de Desarrollo Ricoh Suite

