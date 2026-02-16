# Ricoh Multi-Fleet Governance Suite - Architecture v2.0

## 🏗️ System Architecture

### Overview
Production-ready architecture with PostgreSQL, Docker orchestration, WebSocket real-time updates, and scalable repository pattern.

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │   Adminer    │  │   Backend    │          │
│  │  (Database)  │  │  (DB Admin)  │  │   (FastAPI)  │          │
│  │  Port: 5432  │  │  Port: 8080  │  │  Port: 8000  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                                     │                  │
│         └─────────────────────────────────────┘                  │
│                    ricoh-network (bridge)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React + TS)                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Components                                                │ │
│  │  - ProvisioningPanel (Main UI)                            │ │
│  │  - DiscoveryModal (Network Scan)                          │ │
│  │  - PrinterCard (Device Display)                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Services                                                  │ │
│  │  - printerService (API Client)                            │ │
│  │  - WebSocket Connection (Real-time logs)                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  State Management (Zustand)                               │ │
│  │  - Printers, Users, Logs, Selection                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Backend Architecture

### Layered Structure

```
backend/
├── main.py                 # FastAPI app, WebSocket manager
├── api/                    # API Routes Layer
│   ├── discovery.py        # Network scanning endpoints
│   ├── printers.py         # Printer CRUD endpoints
│   ├── users.py            # User CRUD endpoints
│   ├── provisioning.py     # Bulk provisioning endpoints
│   └── schemas.py          # Pydantic request/response models
├── services/               # Business Logic Layer
│   ├── network_scanner.py  # Async network scanning
│   └── provisioning.py     # Provisioning logic
├── db/                     # Data Access Layer
│   ├── database.py         # SQLAlchemy engine & session
│   ├── models.py           # ORM models (User, Printer, Assignment)
│   ├── repository.py       # Repository pattern (abstraction)
│   └── init.sql            # Database initialization
└── requirements.txt        # Python dependencies
```

### Database Schema

```sql
┌─────────────────────┐
│       users         │
├─────────────────────┤
│ id (PK)             │
│ name                │
│ pin                 │
│ smb_path            │
│ email               │
│ department          │
│ is_active           │
│ created_at          │
│ updated_at          │
└─────────────────────┘
         │
         │ 1:N
         ↓
┌─────────────────────────────┐
│ user_printer_assignments    │
├─────────────────────────────┤
│ id (PK)                     │
│ user_id (FK)                │
│ printer_id (FK)             │
│ provisioned_at              │
│ is_active                   │
│ notes                       │
└─────────────────────────────┘
         │
         │ N:1
         ↓
┌─────────────────────┐
│      printers       │
├─────────────────────┤
│ id (PK)             │
│ hostname            │
│ ip_address (UNIQUE) │
│ location            │
│ status (ENUM)       │
│ detected_model      │
│ serial_number       │
│ has_color           │
│ has_scanner         │
│ has_fax             │
│ toner_cyan          │
│ toner_magenta       │
│ toner_yellow        │
│ toner_black         │
│ last_seen           │
│ notes               │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

## 🔄 Data Flow

### 1. Network Discovery Flow

```
User clicks "Discover Printers"
    ↓
DiscoveryModal opens
    ↓
User enters IP range → Click "Scan Network"
    ↓
POST /discovery/scan {ip_range}
    ↓
NetworkScanner.scan_network() (async)
    ↓
Concurrent IP scanning (asyncio.gather)
    ↓
Port detection (80, 443, 161)
    ↓
Hostname resolution
    ↓
Return discovered devices
    ↓
User selects devices → Click "Register"
    ↓
POST /discovery/register-discovered
    ↓
PrinterRepository.create() for each
    ↓
Devices saved to PostgreSQL
    ↓
Frontend reloads printer list
    ↓
WebSocket broadcasts: "X printers registered"
```

### 2. User Provisioning Flow

```
User fills form (name, PIN, SMB path)
    ↓
User selects printers from grid
    ↓
Click "Push Configuration"
    ↓
POST /users/ {name, pin, smb_path}
    ↓
UserRepository.create()
    ↓
User saved to database
    ↓
POST /provisioning/provision {user_id, printer_ids[]}
    ↓
ProvisioningService.provision_user_to_printers()
    ↓
AssignmentRepository.bulk_create()
    ↓
Assignments saved to database
    ↓
WebSocket broadcasts: "User provisioned to X printers"
    ↓
Frontend shows success message
    ↓
Form cleared, selection reset
```

### 3. Real-time Updates Flow

```
Frontend connects to WebSocket
    ↓
WS: ws://localhost:8000/ws/logs
    ↓
ConnectionManager.connect()
    ↓
Backend operations trigger logs
    ↓
broadcast_log("message", "type")
    ↓
ConnectionManager.broadcast()
    ↓
All connected clients receive event
    ↓
Frontend: addLog() → Zustand store
    ↓
Console component re-renders
    ↓
User sees real-time log
```

## 🎯 API Endpoints

### Discovery
- `POST /discovery/scan` - Scan network for printers
- `POST /discovery/register-discovered` - Register discovered devices

### Printers
- `GET /printers/` - List all printers
- `POST /printers/` - Create printer manually
- `GET /printers/{id}` - Get printer by ID
- `PUT /printers/{id}` - Update printer
- `DELETE /printers/{id}` - Delete printer
- `GET /printers/search/{query}` - Search printers

### Users
- `GET /users/` - List all users
- `POST /users/` - Create user
- `GET /users/{id}` - Get user by ID
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user (soft)
- `GET /users/search/{query}` - Search users

### Provisioning
- `POST /provisioning/provision` - Provision user to printers
- `GET /provisioning/user/{id}` - Get user provisioning status
- `GET /provisioning/printer/{id}` - Get printer users
- `DELETE /provisioning/remove` - Remove assignments

### WebSocket
- `WS /ws/logs` - Real-time log streaming

## 🔒 Security Features

### Implemented
- ✅ CORS configuration
- ✅ Input validation (Pydantic)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Connection pooling
- ✅ Health checks
- ✅ Error handling

### Production Recommendations
- 🔐 JWT authentication
- 🔐 Password hashing (bcrypt)
- 🔐 Rate limiting
- 🔐 HTTPS/TLS
- 🔐 API keys
- 🔐 Audit logging
- 🔐 Role-based access control (RBAC)

## 📊 Scalability

### Horizontal Scaling
- Multiple backend instances behind load balancer
- Shared PostgreSQL database
- Redis for session management
- WebSocket sticky sessions

### Vertical Scaling
- Increase container resources
- Optimize database queries
- Add database indexes
- Connection pooling tuning

### Performance Optimizations
- Database query optimization
- Caching layer (Redis)
- CDN for static assets
- Async operations
- Batch processing

## 🐳 Docker Services

### PostgreSQL
- Image: `postgres:16-alpine`
- Port: 5432
- Volume: `postgres_data`
- Health check: `pg_isready`

### Adminer
- Image: `adminer:latest`
- Port: 8080
- Theme: Dracula
- Access: http://localhost:8080

### Backend
- Build: `./backend/Dockerfile`
- Port: 8000
- Depends on: PostgreSQL
- Auto-reload: Enabled

### Frontend
- Image: `node:20-alpine`
- Port: 5173
- Depends on: Backend
- Hot reload: Enabled

## 🔄 Repository Pattern

### Benefits
- Abstraction from database implementation
- Easy to test (mock repositories)
- Centralized data access logic
- Easy to switch databases
- Consistent API across entities

### Example Usage

```python
# In API route
from db.repository import PrinterRepository

@router.get("/printers/")
async def get_printers(db: Session = Depends(get_db)):
    printers = PrinterRepository.get_all(db)
    return printers

# Repository handles all database logic
class PrinterRepository:
    @staticmethod
    def get_all(db: Session) -> List[Printer]:
        return db.query(Printer).all()
```

## 🎨 Frontend Architecture

### Component Hierarchy

```
App
└── ProvisioningPanel
    ├── User Form (Left Panel)
    │   ├── Name Input
    │   ├── PIN Input
    │   ├── SMB Path Input
    │   └── Push Configuration Button
    ├── Fleet Grid (Right Panel)
    │   ├── Discover Button
    │   └── PrinterCard[] (Grid)
    ├── Live Console (Bottom)
    │   └── Log Events (WebSocket)
    └── DiscoveryModal (Overlay)
        ├── IP Range Input
        ├── Scan Button
        ├── Device List (Checkboxes)
        └── Register Button
```

### State Management (Zustand)

```typescript
interface PrinterStore {
  printers: PrinterDevice[]
  selectedPrinters: string[]
  logs: Log[]
  isLoading: boolean
  
  setPrinters: (printers) => void
  togglePrinter: (id) => void
  addLog: (message, type) => void
  setLoading: (loading) => void
  clearSelection: () => void
}
```

## 🚀 Deployment Options

### Development
```bash
docker-compose up --build
```

### Production
- Use production Dockerfile
- Set environment variables
- Configure reverse proxy (Nginx)
- Enable HTTPS
- Set up monitoring
- Configure backups

## 📈 Monitoring & Observability

### Logs
- Application logs: `docker-compose logs -f backend`
- Database logs: `docker-compose logs -f postgres`
- Frontend logs: Browser console

### Metrics (Future)
- Prometheus + Grafana
- Request rate, latency, errors
- Database connection pool
- WebSocket connections

### Health Checks
- Backend: `GET /`
- Database: `pg_isready`
- Frontend: HTTP 200

## 🔧 Configuration

### Environment Variables

**Backend:**
- `DATABASE_URL` - PostgreSQL connection string
- `DEMO_MODE` - Enable/disable demo data
- `CORS_ORIGINS` - Allowed origins
- `SECRET_KEY` - JWT secret (production)

**Frontend:**
- `VITE_API_URL` - Backend API URL

### Database Configuration
- Connection pool: 10-20 connections
- Timeout: 30 seconds
- Auto-reconnect: Enabled

## 📝 Development Workflow

1. Start services: `docker-compose up`
2. Access Adminer: http://localhost:8080
3. View API docs: http://localhost:8000/docs
4. Develop frontend: http://localhost:5173
5. View logs: `docker-compose logs -f`
6. Stop services: `docker-compose down`

## 🎯 Key Features

- ✅ Network discovery with async scanning
- ✅ PostgreSQL persistence
- ✅ Repository pattern for data access
- ✅ WebSocket real-time updates
- ✅ Bulk user provisioning
- ✅ Professional discovery modal
- ✅ Docker orchestration
- ✅ Database admin UI
- ✅ Comprehensive API documentation
- ✅ Industrial Clarity design system
