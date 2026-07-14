# 🏗️ Arquitectura de Software Detallada y Patrones de Diseño

Este documento describe en detalle la arquitectura lógica de software y los patrones de diseño utilizados en **Ricoh Equipment Manager** para garantizar la modularidad, facilidad de pruebas, thread-safety y aislamiento en producción.

---

## 🧭 1. Arquitectura de Capas Inversas (Clean/Layered Architecture)

El sistema backend (FastAPI) y frontend (React) están estructurados bajo el principio de **separación de responsabilidades** (Separation of Concerns). Las dependencias lógicas siempre apuntan hacia adentro, aislando el dominio y las reglas de negocio de los frameworks o bases de datos físicas.

```
                  ┌─────────────────────────────────────────┐
                  │          Capas de la Aplicación          │
                  │                                         │
                  │     ┌─────────────────────────────┐     │
                  │     │       1. Dominio (Core)     │     │
                  │     │   - Reglas de Negocio Puras │     │
                  │     └──────────────▲──────────────┘     │
                  │                    │                    │
                  │     ┌──────────────┴──────────────┐     │
                  │     │   2. Aplicación (Servicios)  │     │
                  │     │   - Flujos e Integraciones  │     │
                  │     └──────────────▲──────────────┘     │
                  │                    │                    │
                  │     ┌──────────────┴──────────────┐     │
                  │     │ 3. Infraestructura (BD/WIM) │     │
                  │     │   - SQLAlchemy, Selenium    │     │
                  │     └──────────────▲──────────────┘     │
                  │                    │                    │
                  │     ┌──────────────┴──────────────┐     │
                  │     │   4. Presentación (API/UI)  │     │
                  │     │   - Endpoints, WebSockets   │     │
                  │     └─────────────────────────────┘     │
                  │                                         │
                  └─────────────────────────────────────────┘
```

### 1.1 Estructura Lógica en el Backend (FastAPI)
1.  **Dominio (Core/Models)**: Define las entidades básicas del negocio (Usuarios, Impresoras, Cierres) mediante declaraciones puras de SQLAlchemy e interfaces de validación (Pydantic).
2.  **Aplicación (Services)**: Contiene los servicios que orquestan las acciones. Por ejemplo, `auth_service.py` procesa los logins y bloqueos, mientras que `ricoh_web_client.py` ejecuta el scraping y aprovisionamiento.
3.  **Infraestructura (Data Access)**: Implementa la conexión física a base de datos (PostgreSQL), la persistencia física del microservicio de auditoría (SQLite) y las consultas clave-valor en caché (Redis).
4.  **Presentación (API Layer)**: FastAPI routers que exponen los endpoints REST y controlan la comunicación de WebSockets en tiempo real (`ws/logs`).

### 1.2 Estructura Lógica en el Frontend (React)
*   **Capa UI**: Componentes declarativos responsivos (páginas y widgets estilizados con Tailwind CSS). Los componentes son mayormente "pasivos" y no contienen lógica pesada.
*   **Capa de Estado (Zustand / Context)**: Stores globales centralizados (`useUsuarioStore`, `AuthContext`) que guardan la sesión y datos, aislando a los componentes del ciclo de vida de los datos de red.
*   **Capa de Infraestructura (Services)**: Clientes HTTP configurados con Axios (`apiClient.ts`) que incluyen interceptores automáticos de rotación de JWT para recargar tokens transparentemente ante errores 401.

---

## 🗃️ 2. Patrón Repositorio (Repository Pattern)

Para evitar que los controladores de la API realicen consultas directas (`SQLAlchemy queries`) de forma desorganizada, se implementa el **Patrón Repositorio** en la capa de datos.

### Beneficios obtenidos:
*   **Aislamiento de la BD**: Si la estructura de la base de datos cambia, solo se modifica el repositorio específico, no las rutas de la API.
*   **Facilidad de Testing (Mocking)**: Permite inyectar repositorios falsos (mock) en las pruebas unitarias sin tocar la base de datos real.
*   **Reutilización**: Consultas complejas de joins (por ejemplo, buscar cierres activos por empresa y dispositivo) se escriben una sola vez.

### Ejemplo de Implementación:
Las rutas de la API utilizan la inyección de dependencias de FastAPI (`Depends`) para recibir la sesión de la base de datos y delegar el acceso al repositorio:

```python
# Capa de Datos: UserRepository en backend/db/repository.py
class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()

# Capa de Presentación: backend/api/users.py
@router.get("/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
```

---

## 🔄 3. Patrón Adaptador e Integración Multihilo (Scraper & Adapter)

Una de las características más críticas del proyecto es la comunicación bidireccional con impresoras físicas Ricoh que carecen de una API REST formal. Para esto se implementaron dos patrones principales:

### 3.1 Patrón Adaptador (Adapter Pattern)
El sistema expone una interfaz homogénea de gestión de usuarios (`provision`, `deprovision`, `get_permissions`) y el módulo `RicohWebClient` actúa como un **Adaptador**, traduciendo estas llamadas a peticiones HTTP nativas emulando la interfaz web Web Image Monitor (WIM) de las impresoras.

*   **Flujo dual de contraseña SMB**: Permite inyectar credenciales tanto en campos antiguos (`wkpasswordIn`) como modernos (`passwordIn`) de forma transparente.
*   **Orquestación en dos pasos**: Modifica el flujo nativo de WIM para eliminar trabajos de impresión bloqueada enviando una pre-solicitud de selección seguida de una confirmación de tipo formulario (`mode=3`).

### 3.2 Sincronización Paralela y Aislamiento de Hilos (Thread-Safety)
Para aprovisionar y recopilar contadores de múltiples impresoras a la vez sin bloquear el hilo principal del servidor, se utiliza `ThreadPoolExecutor` en el backend. 

Para evitar conflictos de estado entre hilos concurrentes:
*   Se implementó **aislamiento de sesión HTTP (WIM Session Isolation)**. Cada worker que interactúa con una impresora instancia su propio objeto de conexión y cookies mediante `requests.Session()` aislado.
*   Esto previene que las cookies de autenticación de una impresora contaminen las peticiones destinadas a otra de modelo idéntico, evitando bloqueos por colisión de sesión.

---

## 🧩 4. Patrón Sidecar de Microservicios (Audit Portal)

La suite de gobernanza incluye un microservicio de auditoría de seguridad aislado que se ejecuta de manera autónoma en el puerto `8088`.

```
                    ┌─────────────────────────┐
                    │     RICOH-BACKEND       │
                    │                         │
                    │  ┌───────────────────┐  │
                    │  │   FastAPI (8000)  │  │
                    │  └─────────┬─────────┘  │
                    │            │            │
                    │  ┌─────────▼─────────┐  │
                    │  │ AuditPortal (8088)│  │
                    │  └───────────────────┘  │
                    └─────────────────────────┘
```

Este diseño simula un **patrón Sidecar**:
*   **Independencia de Proceso**: Se ejecuta en su propio bucle de eventos Uvicorn dentro del mismo contenedor, evitando que caídas de la API principal comprometan el registro de eventos de seguridad.
*   **Persistencia Dedicada**: Utiliza un motor de base de datosSQLite local de lectura y escritura ultrarrápida. Esto previene cuellos de botella en la base de datos principal PostgreSQL al escribir grandes ráfagas de logs en auditorías intensivas.

---

## ⚛️ 5. Arquitectura del Estado en el Frontend (React + Zustand Store)

El frontend de la aplicación sigue una arquitectura de flujo unidireccional de datos controlada por Zustand, eliminando el "prop-drilling" y manteniendo los componentes limpios de llamadas directas a APIs.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ React Component │ ───>  │ Zustand Action  │ ───>  │  apiClient.ts   │
└─────────────────┘       └─────────────────┘       └─────────────────┘
         ▲                         │                         │
         │                         ▼                         ▼
         │                 ┌─────────────────┐       ┌─────────────────┐
         └──────────────── │  Zustand State  │ <───  │ Servidor Web API│
                           └─────────────────┘       └─────────────────┘
```

1.  **Componente UI**: El usuario interactúa (por ejemplo, hace clic en "Desactivar usuario"). El componente solo despacha una acción del Store.
2.  **Zustand Action**: Realiza la petición asíncrona llamando a la capa de servicios (`apiClient.ts`).
3.  **Axios Client**: Procesa la petición REST, maneja cabeceras CSRF y rota el JWT si es necesario.
4.  **Zustand State**: Al retornar éxito, actualiza el estado interno de React. El componente se vuelve a renderizar automáticamente al detectar el cambio de estado limpio.
