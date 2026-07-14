# ️ Diagrama de Arquitectura - Modelo C4

Este documento detalla la arquitectura de **Ricoh Equipment Manager** estructurada bajo la metodología del **Modelo C4** (Contexto, Contenedores y Componentes) para facilitar el entendimiento técnico a gran escala.

---

##  Nivel 1: Diagrama de Contexto del Sistema

Muestra cómo interactúa el sistema **Ricoh Equipment Manager** con los usuarios y la infraestructura física externa de la organización.

```mermaid
graph LR
    UserAdmin([Administrador TI]) -->|Gestiona usuarios, impresoras y cierres| RicohSuite[Ricoh Equipment Manager Suite]
    Operator([Operario de Flota]) -->|Visualiza lecturas y alertas| RicohSuite
    
    RicohSuite -->|Consulta contadores y aprovisiona usuarios| RicohFleet[Flota de Impresoras Ricoh Físicas]
    RicohFleet -->|Ejecuta escaneos a carpeta de red| NetworkShare[Servidor de Archivos SMB Corporativo]
    RicohSuite -->|Auditoría e historial de accesos| AuditSystem[Audit Portal Log]

    style RicohSuite fill:#f96,stroke:#333,stroke-width:4px
    style RicohFleet fill:#f99,stroke:#333,stroke-width:2px
    style NetworkShare fill:#ccc,stroke:#333,stroke-dasharray: 5 5
```

---

##  Nivel 2: Diagrama de Contenedores

Muestra las tecnologías y fronteras de los contenedores Docker orquestados que conforman el sistema.

```mermaid
graph TD
    UserAdmin([Administrador TI]) -->|Acceso HTTPS:443 / HTTP:80| Nginx[Contenedor: ricoh-nginx\nNginx Alpine]
    
    subgraph ricoh-network
        Nginx -->|Sirve estáticos| ReactApp[Contenedor: ricoh-frontend\nReact 19, TypeScript, Zustand]
        Nginx -->|Proxy Pass /api| FastAPI[Contenedor: ricoh-backend\nFastAPI, Python 3.11]
        
        FastAPI -->|Autenticación y Caché| Redis[(Contenedor: ricoh-redis\nRedis 7 Alpine)]
        FastAPI -->|Persistencia relacional| Postgres[(Contenedor: ricoh-postgres\nPostgreSQL 16)]
        
        FastAPI -->|Audit microservice :8088| SQLite[(Logs SQLite Local\naudit.db)]
    end

    FastAPI -->|HTTP / Scraping WIM| RicohFleet[Impresoras Ricoh Físicas\nProtocolo HTTP / HTTPS]
    
    style Nginx fill:#f9f,stroke:#333,stroke-width:2px
    style ReactApp fill:#9f9,stroke:#333,stroke-width:2px
    style FastAPI fill:#9ff,stroke:#333,stroke-width:2px
    style Postgres fill:#ff9,stroke:#333,stroke-width:2px
    style Redis fill:#ffb,stroke:#333,stroke-width:2px
```

---

## ️ Nivel 3: Diagrama de Componentes (Backend FastAPI)

Detalla cómo interactúan los diferentes módulos de software internos dentro del contenedor `ricoh-backend`.

```mermaid
graph TD
    Request([Petición API desde Nginx]) --> AuthMiddleware[Auth Middleware\nDevice Binding / JWT Validation]
    
    AuthMiddleware --> RouterLayer[Capa de Rutas\nFastAPI Routers]
    
    subgraph Capa de Servicios y Negocio
        RouterLayer --> AuthService[Auth Service\nbcrypt / Token generation]
        RouterLayer --> ProvisioningService[Provisioning Service\nOrquestador de usuarios]
        RouterLayer --> CounterService[Counter Service\nLectura e histórico]
    end

    subgraph Capa de Adaptadores e Integración
        ProvisioningService --> RicohWebClient[Ricoh Web Client\nHTTP Scraping / WIM Adapter]
        CounterService --> RicohWebClient
    end

    subgraph Capa de Acceso a Datos
        AuthService --> RepositoryPattern[Repositories\nUser, Printer, Close Repositories]
        ProvisioningService --> RepositoryPattern
        CounterService --> RepositoryPattern
        
        RepositoryPattern --> SQLAlchemy[SQLAlchemy ORM]
    end

    SQLAlchemy --> PostgreSQL[(Base de Datos\nPostgreSQL)]
    RicohWebClient --> PhysicalPrinters[Flota Ricoh\nWIM HTTP Interface]

    style RouterLayer fill:#dff,stroke:#333
    style RicohWebClient fill:#ffd,stroke:#333,stroke-width:2px
    style RepositoryPattern fill:#fdf,stroke:#333
```
