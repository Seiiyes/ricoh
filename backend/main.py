"""
Ricoh Equipment Management Suite - Backend API
FastAPI server with PostgreSQL, WebSockets, and network discovery
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, status, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from contextlib import asynccontextmanager
import os
import secrets
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import asyncio
from collections import defaultdict
from sqlalchemy.exc import OperationalError

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
            # Mask password values (but keep error messages)
            if 'password' in msg.lower() and 'error' not in msg.lower() and 'traceback' not in msg.lower():
                import re
                # Only mask actual password values, not the word "password"
                msg = re.sub(r'(password["\']?\s*[:=]\s*["\']?)([^"\'}\s,]+)', r'\1[REDACTED]', msg, flags=re.IGNORECASE)
                record.msg = msg
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
from api.sync import router as sync_router  # ← NUEVO

# Import middleware
from middleware.ddos_protection import DDoSProtectionMiddleware
from middleware.https_redirect import HTTPSRedirectMiddleware
from middleware.csrf_protection import CSRFProtectionMiddleware


# ============================================================================
# WebSocket Security — Secure Connection Manager
# ============================================================================

# WebSocket security constants
WS_MAX_CONNECTIONS_PER_IP = 3        # Max simultaneous WS connections per IP
WS_RATE_LIMIT_CONNECTIONS = 5        # Max new connections per IP per minute
WS_RATE_LIMIT_WINDOW_SECONDS = 60    # Rate limit window (1 minute)
WS_MAX_MESSAGE_SIZE_BYTES = 4096     # Max inbound message size (4 KB)
WS_MAX_MESSAGES_PER_MINUTE = 60      # Max messages per session per minute


class ConnectionManager:
    """
    Secure WebSocket connection manager.

    Security features:
    - JWT authentication required before accepting connections
    - Per-IP rate limiting for new connections (prevents flood)
    - Max concurrent connections per IP (prevents resource exhaustion)
    - Per-session message rate limiting (prevents message flood)
    - Max inbound message size (prevents large payload attacks)
    - Safe disconnect with no KeyError on double-remove
    - Audit logging on connect and disconnect
    """

    def __init__(self):
        # {websocket: {user_id, username, rol, ip, connected_at, msg_count, msg_window_start}}
        self._connections: Dict[WebSocket, dict] = {}

        # {ip: [timestamp, ...]}  — sliding window for connection rate limiting
        self._conn_attempts: Dict[str, List[datetime]] = defaultdict(list)

        # {ip: count}  — current open connections per IP
        self._connections_by_ip: Dict[str, int] = defaultdict(int)

    # ------------------------------------------------------------------
    # Rate limiting helpers
    # ------------------------------------------------------------------

    def _check_connection_rate(self, ip: str) -> bool:
        """Return True if the IP is allowed to open a new connection."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=WS_RATE_LIMIT_WINDOW_SECONDS)

        # Prune old timestamps
        self._conn_attempts[ip] = [
            ts for ts in self._conn_attempts[ip] if ts > window_start
        ]

        if len(self._conn_attempts[ip]) >= WS_RATE_LIMIT_CONNECTIONS:
            return False

        self._conn_attempts[ip].append(now)
        return True

    def _check_concurrent_limit(self, ip: str) -> bool:
        """Return True if the IP has not exceeded the concurrent connection limit."""
        return self._connections_by_ip.get(ip, 0) < WS_MAX_CONNECTIONS_PER_IP

    def _check_message_rate(self, websocket: WebSocket) -> bool:
        """Return True if the session is within the message rate limit."""
        meta = self._connections.get(websocket)
        if not meta:
            return False

        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=60)

        if meta["msg_window_start"] < window_start:
            # Reset window
            meta["msg_count"] = 0
            meta["msg_window_start"] = now

        meta["msg_count"] += 1
        return meta["msg_count"] <= WS_MAX_MESSAGES_PER_MINUTE

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self, websocket: WebSocket, user_id: int, username: str, rol: str, ip: str):
        """Accept a pre-authenticated WebSocket connection."""
        await websocket.accept()
        self._connections[websocket] = {
            "user_id": user_id,
            "username": username,
            "rol": rol,
            "ip": ip,
            "connected_at": datetime.now(timezone.utc),
            "msg_count": 0,
            "msg_window_start": datetime.now(timezone.utc),
        }
        self._connections_by_ip[ip] = self._connections_by_ip.get(ip, 0) + 1
        logger.info(f"[WS] CONNECTED — user={username} ip={ip} total={len(self._connections)}")

    def disconnect(self, websocket: WebSocket):
        """Safely remove a connection without raising if already gone."""
        meta = self._connections.pop(websocket, None)
        if meta:
            ip = meta["ip"]
            self._connections_by_ip[ip] = max(0, self._connections_by_ip.get(ip, 1) - 1)
            logger.info(
                f"[WS] DISCONNECTED — user={meta['username']} ip={ip} "
                f"duration={(datetime.now(timezone.utc) - meta['connected_at']).seconds}s "
                f"remaining={len(self._connections)}"
            )

    # ------------------------------------------------------------------
    # Broadcast (role-aware)
    # ------------------------------------------------------------------

    async def broadcast(self, message: dict, allowed_roles: Optional[List[str]] = None):
        """
        Broadcast to connected clients.

        Args:
            message: JSON-serializable dict
            allowed_roles: If set, only clients with one of these roles receive the message.
                           None = send to all authenticated connections.
        """
        stale: List[WebSocket] = []
        for ws, meta in list(self._connections.items()):
            # Role filter: skip if this client's role is not in allowed_roles
            if allowed_roles and meta.get("rol") not in allowed_roles:
                continue
            try:
                await ws.send_json(message)
            except Exception as exc:
                logger.warning(f"[WS] Failed to send to {meta.get('username')}: {exc}")
                stale.append(ws)

        # Clean up stale connections
        for ws in stale:
            self.disconnect(ws)

    @property
    def active_count(self) -> int:
        return len(self._connections)


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
    
    # Create tables (con reintentos) - evita fallos cuando Postgres aún está iniciando
    max_attempts = int(os.getenv("DB_STARTUP_MAX_ATTEMPTS", "15"))
    delay_seconds = float(os.getenv("DB_STARTUP_RETRY_DELAY", "2"))
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)
            last_error = None
            break
        except OperationalError as e:
            last_error = e
            print(f"⏳ DB aún no disponible (intento {attempt}/{max_attempts}). Reintentando en {delay_seconds}s...")
            await asyncio.sleep(delay_seconds)
    
    if last_error is not None:
        # Dejar el traceback en logs para diagnóstico
        logger.exception("❌ No se pudo inicializar la base de datos tras múltiples intentos", exc_info=last_error)
        raise last_error
    
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


# Create FastAPI app (disabling default unauthenticated docs endpoints to secure them)
app = FastAPI(
    title="Ricoh Equipment Management API",
    description="Backend API for Ricoh printer equipment discovery and management with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# CORS Configuration
_default_cors = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_cors).split(",") if o.strip()]

# En desarrollo, permite Vite en red local (192.168.x.x, 10.x, 172.16–31.x) sin listar cada IP.
_environment = os.getenv("ENVIRONMENT", "development")
_default_private_cors = "true" if _environment == "development" else "false"
_cors_allow_private = os.getenv("CORS_ALLOW_PRIVATE_NETWORK", _default_private_cors).lower() == "true"
# Solo HTTP en orígenes privados habituales (puerto típico de Vite u otro dev server)
CORS_ORIGIN_REGEX = (
    r"^http://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?$"
    if _cors_allow_private
    else None
)

if _cors_allow_private:
    logger.info(
        "CORS: orígenes explícitos + regex para red privada (desarrollo). "
        "Desactive con CORS_ALLOW_PRIVATE_NETWORK=false en producción."
    )

# Define explicit allowed methods and headers for CORS
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
ALLOWED_HEADERS = [
    "Content-Type",
    "Authorization",
    "X-CSRF-Token",
    "X-Request-ID"
]

_cors_mw_kwargs = dict(
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "Content-Disposition"],
    max_age=3600,  # Cache preflight requests for 1 hour
)
if CORS_ORIGIN_REGEX:
    _cors_mw_kwargs["allow_origin_regex"] = CORS_ORIGIN_REGEX

app.add_middleware(CORSMiddleware, **_cors_mw_kwargs)

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
    print(f"DEBUG: Adding CSRF Protection! environment={environment}, enable_csrf_env={enable_csrf_env}")
    app.add_middleware(CSRFProtectionMiddleware)
else:
    print(f"DEBUG: Skipping CSRF Protection! environment={environment}, enable_csrf_env={enable_csrf_env}")
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
app.include_router(sync_router)  # ← NUEVO
from api.dashboard import router as dashboard_router
from api.analytics import router as analytics_router
app.include_router(dashboard_router)
app.include_router(analytics_router)


# Authenticated Documentation Endpoints (Docs & OpenAPI protection)
security = HTTPBasic()

def authenticate_docs(credentials: HTTPBasicCredentials = Depends(security)):
    docs_user = os.getenv("DOCS_USERNAME", "admin")
    docs_pass = os.getenv("DOCS_PASSWORD", "ricoh_docs_2026")
    
    is_user_ok = secrets.compare_digest(credentials.username, docs_user)
    is_pass_ok = secrets.compare_digest(credentials.password, docs_pass)
    
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(authenticate_docs)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Ricoh Equipment Management API - Swagger UI")

@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(authenticate_docs)):
    return get_redoc_html(openapi_url="/openapi.json", title="Ricoh Equipment Management API - ReDoc")

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint(username: str = Depends(authenticate_docs)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)


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


# ============================================================================
# WebSocket endpoint — /ws/logs  (authenticated, rate-limited)
# ============================================================================

@app.websocket("/ws/logs")
async def websocket_logs(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token for authentication"),
):
    """
    Secure WebSocket endpoint for real-time log streaming.

    Security measures applied before accepting the connection:
      1. JWT validation  — token must be a valid, non-expired access token.
      2. Session check   — token must have an active DB session (not logged out).
      3. Account check   — user must be active.
      4. Connection rate — max 5 new connections per IP per minute.
      5. Concurrent cap  — max 3 simultaneous connections per IP.

    While connected:
      6. Message size    — inbound messages exceeding 4 KB are silently dropped.
      7. Message rate    — max 60 inbound messages per minute per session.
    """
    from db.database import SessionLocal
    from services.auth_service import AuthService
    from services.jwt_service import InvalidTokenError, ExpiredTokenError

    # ----------------------------------------------------------------
    # Resolve client IP (support reverse-proxy headers)
    # ----------------------------------------------------------------
    client_ip = "unknown"
    forwarded_for = websocket.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    elif websocket.client:
        client_ip = websocket.client.host

    # ----------------------------------------------------------------
    # 1-3: Authenticate BEFORE accepting the WebSocket handshake
    # ----------------------------------------------------------------
    db = SessionLocal()
    try:
        client_ua = websocket.headers.get("user-agent", "unknown")
        authenticated_user = AuthService.validate_token(db, token, client_ip, client_ua)
        user_id = authenticated_user.id
        username = authenticated_user.username
        rol = authenticated_user.rol
    except (InvalidTokenError, ExpiredTokenError) as exc:
        logger.warning(f"[WS] AUTH FAILED from {client_ip}: {exc}")
        # Reject before handshake — send 403 via plain HTTP upgrade rejection
        await websocket.close(code=4001, reason="Unauthorized: invalid or expired token")
        return
    except Exception as exc:
        logger.error(f"[WS] AUTH ERROR from {client_ip}: {exc}")
        await websocket.close(code=4001, reason="Unauthorized: authentication error")
        return
    finally:
        db.close()

    # ----------------------------------------------------------------
    # 4: Connection rate limit
    # ----------------------------------------------------------------
    if not manager._check_connection_rate(client_ip):
        logger.warning(
            f"[WS] RATE LIMIT exceeded for {client_ip} (user={username}). "
            f"Max {WS_RATE_LIMIT_CONNECTIONS} connections/{WS_RATE_LIMIT_WINDOW_SECONDS}s."
        )
        await websocket.close(code=4029, reason="Too many connection attempts. Try again later.")
        return

    # ----------------------------------------------------------------
    # 5: Concurrent connection limit
    # ----------------------------------------------------------------
    if not manager._check_concurrent_limit(client_ip):
        logger.warning(
            f"[WS] CONCURRENT LIMIT exceeded for {client_ip} (user={username}). "
            f"Max {WS_MAX_CONNECTIONS_PER_IP} simultaneous connections."
        )
        await websocket.close(code=4008, reason="Too many simultaneous connections from this IP.")
        return

    # ----------------------------------------------------------------
    # All checks passed — accept the connection
    # ----------------------------------------------------------------
    await manager.connect(websocket, user_id=user_id, username=username, rol=rol, ip=client_ip)

    try:
        # Send authenticated welcome message
        await websocket.send_json({
            "id": "system",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": f"Connected to Ricoh Equipment Management Console — {username}",
            "type": "info"
        })

        # Keep-alive loop — listen for inbound messages (ping/pong or commands)
        while True:
            try:
                # 6: Enforce max message size — receive raw bytes first
                raw = await websocket.receive_bytes()
                if len(raw) > WS_MAX_MESSAGE_SIZE_BYTES:
                    logger.warning(
                        f"[WS] Message too large ({len(raw)} bytes) from "
                        f"{username}@{client_ip} — dropped"
                    )
                    continue

                # 7: Message rate limiting
                if not manager._check_message_rate(websocket):
                    logger.warning(
                        f"[WS] Message rate limit exceeded for {username}@{client_ip} — dropped"
                    )
                    continue

                # (messages from client are informational — no action needed)

            except WebSocketDisconnect:
                break
            except RuntimeError:
                # Connection already closed
                break
            except Exception as exc:
                logger.debug(f"[WS] Receive error for {username}: {exc}")
                break

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.error(f"[WS] Unexpected error for {username}@{client_ip}: {exc}")
    finally:
        manager.disconnect(websocket)


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

