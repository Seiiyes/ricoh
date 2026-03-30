# Guía de Archivos de Entorno (.env)

## Estructura de Archivos

```
proyecto/
├── .env                              # Frontend - Desarrollo (git ignored)
├── .env.example                      # Frontend - Plantilla
├── backend/
│   ├── .env                          # Backend - Docker (git ignored)
│   ├── .env.example                  # Backend - Plantilla
│   └── .env.local                    # Backend - Sin Docker (git ignored)
└── deployment/
    └── .env.production.example       # Producción - Plantilla
```

## Cuándo Usar Cada Archivo

### Desarrollo con Docker (Recomendado)

**Frontend:**
- Copiar `.env.example` → `.env`
- Usar: `VITE_API_URL=http://localhost:8000`

**Backend:**
- Copiar `backend/.env.example` → `backend/.env`
- Usar: `DATABASE_URL=postgresql://...@postgres:5432/...`
- El host es `postgres` (nombre del contenedor Docker)

**Comandos:**
```bash
# Iniciar todo con Docker
docker-compose up -d
```

### Desarrollo sin Docker (Python directo)

**Frontend:**
- Igual que con Docker: `.env` con `VITE_API_URL=http://localhost:8000`

**Backend:**
- Copiar `backend/.env.example` → `backend/.env.local`
- Usar: `DATABASE_URL=postgresql://...@localhost:5432/...`
- El host es `localhost` (PostgreSQL instalado localmente)

**Comandos:**
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend
cd backend
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate   # Windows
uvicorn app.main:app --reload
```

### Producción (Servidor Rack 24/7)

**Configuración:**
- Copiar `deployment/.env.production.example` → `deployment/.env.production`
- Generar NUEVAS claves de seguridad:
  ```bash
  # ENCRYPTION_KEY
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  
  # SECRET_KEY
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- Configurar dominio, SSL, contraseñas fuertes

**Deployment:**
```bash
cd deployment
./setup-ubuntu-server.sh
./deploy-production.sh
```

## Variables Críticas de Seguridad

### Desarrollo
- `ENCRYPTION_KEY`: Puede usar valor de ejemplo
- `SECRET_KEY`: Puede usar valor de ejemplo
- `RICOH_ADMIN_PASSWORD`: Configurar si usas impresoras reales

### Producción (OBLIGATORIO)
- `ENCRYPTION_KEY`: DEBE ser única y generada
- `SECRET_KEY`: DEBE ser única y generada
- `RICOH_ADMIN_PASSWORD`: DEBE estar configurada
- `POSTGRES_PASSWORD`: DEBE ser fuerte (16+ caracteres)
- `REDIS_PASSWORD`: DEBE ser fuerte (16+ caracteres)

## Archivos Ignorados por Git

Los siguientes archivos NO se suben a GitHub (están en `.gitignore`):
- `.env`
- `.env.local`
- `backend/.env`
- `backend/.env.local`
- `deployment/.env.production`

Los archivos `.example` SÍ se suben como plantillas.

## Diferencias Clave

| Archivo | Propósito | DATABASE_URL Host | Git |
|---------|-----------|-------------------|-----|
| `.env` | Frontend desarrollo | N/A | ❌ Ignored |
| `.env.example` | Frontend plantilla | N/A | ✅ Tracked |
| `backend/.env` | Backend Docker | `postgres:5432` | ❌ Ignored |
| `backend/.env.example` | Backend plantilla | `localhost:5432` | ✅ Tracked |
| `backend/.env.local` | Backend sin Docker | `localhost:5432` | ❌ Ignored |
| `deployment/.env.production.example` | Producción plantilla | `postgres:5432` | ✅ Tracked |

## Troubleshooting

**Error: "Connection refused" en backend**
- Con Docker: Verifica que uses `postgres:5432` en `backend/.env`
- Sin Docker: Verifica que uses `localhost:5432` en `backend/.env.local`

**Error: "ENCRYPTION_KEY not set"**
- Genera una clave: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- Agrégala a tu archivo `.env` correspondiente

**Frontend no conecta con backend**
- Verifica que `VITE_API_URL` apunte a `http://localhost:8000`
- Verifica que el backend esté corriendo en el puerto 8000
