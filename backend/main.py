"""
Ricoh Equipment Management Suite - Backend API
FastAPI server with PostgreSQL, WebSockets, and network discovery
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import json
import logging
from datetime import datetime
from typing import List
import asyncio

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/ricoh_api.log') if os.path.exists('logs') or os.makedirs('logs', exist_ok=True) else logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Mask sensitive data in logs
class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive data in logs"""
    
    def filter(self, record):
        # Mask passwords and tokens in log messages
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Mask password fields
            if 'password' in msg.lower():
                record.msg = msg.replace(record.msg, '[REDACTED]')
            # Mask tokens (show only first and last 4 chars)
            if 'token' in msg.lower() and len(msg) > 20:
                if 'eyJ' in msg:  # JWT token
                    import re
                    tokens = re.findall(r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*', msg)
                    for token in tokens:
                        if len(token) > 20:
                            masked = f"{token[:4]}...{token[-4:]}"
                            record.msg = msg.replace(token, masked)
        return True

# Add filter to all handlers
for handler in logging.getLogger().handlers:
    handler.addFilter(SensitiveDataFilter())

# Import database
from db.database import init_db, engine
from db import Base

# Import API routers
from api import users_router, printers_router, provisioning_router, discovery_router, counters_router
from api.export import router as export_router
from api.auth import router as auth_router
from api.empresas import router as empresas_router
from api.admin_users import router as admin_users_router
from api.ddos_admin import router as ddos_admin_router

# Import middleware
from middleware.ddos_protection import DDoSProtectionMiddleware
from middleware.https_redirect import HTTPSRedirectMiddleware
from middleware.csrf_protection import CSRFProtectionMiddleware


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Starting Ricoh Equipment Management API...")
    print("📊 Initializing database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized")
    print(f"🔧 Demo Mode: {os.getenv('DEMO_MODE', 'true')}")
    
    # Start background cleanup job
    cleanup_task = None
    if os.getenv("ENABLE_SESSION_CLEANUP", "true").lower() == "true":
        print("🧹 Starting session cleanup job (runs every hour)...")
        cleanup_task = asyncio.create_task(run_cleanup_job_periodically())
    
    print("🌐 Server ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Ricoh Equipment Management API...")
    
    # Cancel cleanup task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass


async def run_cleanup_job_periodically():
    """Run cleanup job every hour"""
    from jobs.cleanup_sessions import run_cleanup_job
    
    while True:
        try:
            # Wait 1 hour
            await asyncio.sleep(3600)
            
            # Run cleanup in background thread to avoid blocking
            await asyncio.to_thread(run_cleanup_job)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in cleanup job: {e}")
            # Continue running even if there's an error


# Create FastAPI app
app = FastAPI(
    title="Ricoh Equipment Management API",
    description="Backend API for Ricoh printer equipment discovery and management with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174").split(",")

# Define explicit allowed methods and headers for CORS
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "X-CSRF-Token",
    "X-Request-ID"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "Content-Disposition"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add DDoS Protection Middleware
app.add_middleware(DDoSProtectionMiddleware)

# Add HTTPS Redirect Middleware (solo en producción si FORCE_HTTPS=true)
app.add_middleware(HTTPSRedirectMiddleware)

# Add CSRF Protection Middleware
# Habilitar CSRF por defecto en producción y staging, o si ENABLE_CSRF=true
# Permitir deshabilitar explícitamente solo si ENABLE_CSRF=false está configurado
environment = os.getenv("ENVIRONMENT", "development")
enable_csrf_env = os.getenv("ENABLE_CSRF", "").lower()

# Lógica de habilitación:
# - En producción/staging: habilitada por defecto, deshabilitar solo si ENABLE_CSRF=false
# - En desarrollo: deshabilitada por defecto, habilitar solo si ENABLE_CSRF=true
if environment in ["production", "staging"]:
    enable_csrf = enable_csrf_env != "false"
else:
    enable_csrf = enable_csrf_env == "true"

if enable_csrf:
    logger.info(f"🛡️ CSRF Protection enabled (ENVIRONMENT={environment})")
    app.add_middleware(CSRFProtectionMiddleware)
else:
    logger.warning(f"⚠️ CSRF Protection disabled (ENVIRONMENT={environment}, not recommended for production)")


# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    
    # Debug: Print all headers
    if request.url.path not in ["/", "/docs", "/openapi.json"]:
        print(f"[HEADERS] Request a {request.url.path}")
        print(f"[HEADERS] Authorization: {request.headers.get('authorization', 'MISSING')}")
        print(f"[HEADERS] All headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    # Only add HSTS in production
    if os.getenv("ENVIRONMENT", "development") == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # XSS Protection (legacy browsers)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response


# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    body = await request.body()
    logger.error("=" * 80)
    logger.error("❌ VALIDATION ERROR")
    logger.error("=" * 80)
    logger.error(f"URL: {request.url}")
    logger.error(f"Method: {request.method}")
    logger.error(f"Body: {body.decode('utf-8')}")
    logger.error(f"Errors: {json.dumps(exc.errors(), indent=2)}")
    logger.error("=" * 80)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": body.decode('utf-8')
        }
    )


# Include API routers
app.include_router(auth_router)
app.include_router(empresas_router)
app.include_router(admin_users_router)
app.include_router(ddos_admin_router)
app.include_router(users_router)
app.include_router(printers_router)
app.include_router(provisioning_router)
app.include_router(discovery_router)
app.include_router(counters_router)
app.include_router(export_router)


# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Ricoh Equipment Management API",
        "status": "online",
        "version": "2.0.0",
        "demo_mode": os.getenv("DEMO_MODE", "true").lower() == "true",
        "database": "PostgreSQL",
        "features": [
            "User Management",
            "Printer Equipment Management",
            "Network Discovery",
            "Bulk Provisioning",
            "Real-time WebSocket Updates"
        ]
    }


# WebSocket endpoint for real-time logs
@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log streaming
    Clients can connect to receive live updates
    """
    await manager.connect(websocket)
    try:
        # Send welcome message
        await websocket.send_json({
            "id": "system",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": "Connected to Ricoh Equipment Management Console",
            "type": "info"
        })
        
        # Simple loop to keep alive, listening for any message (even if we ignore them)
        while True:
            try:
                # Escuchar pero con un timeout implícito o simplemente esperar
                await websocket.receive_text()
            except Exception:
                # Si hay error en la recepción (como un timeout del cliente), seguimos vivos
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            manager.disconnect(websocket)
        except:
            pass


# Helper function to broadcast logs
async def broadcast_log(message: str, log_type: str = "info", **kwargs):
    """
    Broadcast a log message to all connected WebSocket clients
    
    Args:
        message: Log message
        log_type: Type of log (info, success, error, warning)
        **kwargs: Additional data to include
    """
    log_event = {
        "id": f"log-{datetime.now().timestamp()}",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message": message,
        "type": log_type,
        **kwargs
    }
    await manager.broadcast(log_event)


# Make broadcast_log available to other modules
app.state.broadcast_log = broadcast_log


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

