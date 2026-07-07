"""
Security Audit Log Portal Microservice
Runs independently on port 8088
"""
import os
import sys
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone, time
import jwt
import bcrypt
from sqlalchemy import func

# Asegurar que las rutas de backend estén en el sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.audit_db import SessionLocal, SecurityAuditLog, init_audit_db

# Inicializar Base de Datos SQLite de logs
init_audit_db()

app = FastAPI(
    title="Security Audit Portal",
    description="Portal de auditoría independiente de logs de accesos y tokens",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir conexiones libres ya que es un puerto independiente controlado por token
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "default-security-audit-secret-key-entropy-123!")
ALGORITHM = "HS256"

# Parsear usuarios de AUDIT_USERS
# Formato esperado: "user1:hash1,user2:hash2"
AUDIT_USERS = {}
raw_env = os.getenv("AUDIT_USERS", "")
audit_users_env = raw_env.strip().strip('"').strip("'")
print(f"[AUDIT] raw env AUDIT_USERS: '{raw_env}'")
print(f"[AUDIT] cleaned env AUDIT_USERS: '{audit_users_env}'")
if audit_users_env:
    for entry in audit_users_env.split(","):
        entry_clean = entry.strip().strip('"').strip("'")
        if ":" in entry_clean:
            u_name, u_hash = entry_clean.split(":", 1)
            AUDIT_USERS[u_name.strip()] = u_hash.strip()
print(f"[AUDIT] parsed AUDIT_USERS keys: {list(AUDIT_USERS.keys())}")


class LoginRequest(BaseModel):
    username: str
    password: str


async def get_current_audit_user(authorization: Optional[str] = Header(None)) -> str:
    """Verifica el token JWT en las peticiones API del portal de logs"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta el token de autorización o formato inválido (debe ser Bearer)."
        )
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("type")
        if not username or token_type != "audit_access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso no válido para auditoría."
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha expirado. Por favor, inicie sesión de nuevo."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de seguridad inválido."
        )


@app.post("/api/login")
async def login(credentials: LoginRequest):
    """Realiza el mini-login contra los hashes configurados en el .env"""
    username = credentials.username.strip()
    password = credentials.password
    
    # Validar si el usuario existe en memoria
    if username not in AUDIT_USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de acceso de auditoría incorrectas."
        )
        
    # Verificar contraseña encriptada con bcrypt
    hashed_pwd = AUDIT_USERS[username]
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_pwd.encode('utf-8')
        if not bcrypt.checkpw(password_bytes, hashed_bytes):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de acceso de auditoría incorrectas."
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de acceso de auditoría incorrectas."
        )
        
    # Generar JWT temporal de 30 minutos
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=30)
    payload = {
        "sub": username,
        "exp": expires_at,
        "iat": now,
        "type": "audit_access"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 1800,  # 30 minutos en segundos
        "username": username
    }


@app.get("/api/fechas", response_model=List[str])
async def get_fechas(current_user: str = Depends(get_current_audit_user)):
    """Retorna las fechas agrupadas con logs de auditoría en SQLite"""
    db = SessionLocal()
    try:
        # SQLite strftime('%Y-%m-%d', timestamp) extrae la fecha
        fechas = db.query(func.strftime('%Y-%m-%d', SecurityAuditLog.timestamp))\
            .distinct()\
            .order_by(func.strftime('%Y-%m-%d', SecurityAuditLog.timestamp).desc())\
            .all()
        return [f[0] for f in fechas if f[0] is not None]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer fechas de auditoría: {str(e)}"
        )
    finally:
        db.close()


@app.get("/api/logs")
async def get_logs(
    fecha: str,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    current_user: str = Depends(get_current_audit_user)
):
    """
    Retorna los registros de auditoría de un día específico filtrados por querys SQLite.
    Paginación server-side.
    """
    db = SessionLocal()
    try:
        # Validar formato de fecha YYYY-MM-DD
        try:
            target_date = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha inválido. Debe ser YYYY-MM-DD."
            )
            
        # Rango del día completo: 00:00:00.000000 a 23:59:59.999999
        start_datetime = datetime.combine(target_date, time.min)
        end_datetime = datetime.combine(target_date, time.max)
        
        query = db.query(SecurityAuditLog).filter(
            SecurityAuditLog.timestamp >= start_datetime,
            SecurityAuditLog.timestamp <= end_datetime
        )
        
        # Filtro de búsqueda rápida
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (SecurityAuditLog.usuario.like(search_pattern)) |
                (SecurityAuditLog.accion.like(search_pattern)) |
                (SecurityAuditLog.resultado.like(search_pattern)) |
                (SecurityAuditLog.ip_address.like(search_pattern))
            )
            
        # Conteo total de registros (para la paginación de la UI)
        total_records = query.count()
        
        # Aplicar límites de página y offset
        offset = (page - 1) * limit
        logs = query.order_by(SecurityAuditLog.timestamp.desc()).offset(offset).limit(limit).all()
        
        # Formatear la respuesta
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "usuario": log.usuario or "Acción del Sistema / Anónimo",
                "accion": log.accion,
                "detalles": log.detalles or {},
                "ip_address": log.ip_address or "N/A",
                "resultado": log.resultado
            })
            
        total_pages = max(1, (total_records + limit - 1) // limit)
        
        return {
            "total_records": total_records,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit,
            "logs": formatted_logs
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar logs en SQLite: {str(e)}"
        )
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def get_portal_ui():
    """Sirve la interfaz web HTML embebida"""
    template_path = "/app/templates/audit_portal.html"
    
    # Fallback local para desarrollo si no está en la carpeta de plantillas de docker
    if not os.path.exists(template_path):
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "templates",
            "audit_portal.html"
        )
        
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Audit Portal Template Not Found</h1><p>Por favor, verifique que templates/audit_portal.html exista.</p>",
            status_code=404
        )
