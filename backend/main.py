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

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import database
from db.database import init_db, engine
from db import Base

# Import API routers
from api import users_router, printers_router, provisioning_router, discovery_router, counters_router


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
    print("🌐 Server ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Ricoh Equipment Management API...")


# Create FastAPI app
app = FastAPI(
    title="Ricoh Equipment Management API",
    description="Backend API for Ricoh printer equipment discovery and management with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(users_router)
app.include_router(printers_router)
app.include_router(provisioning_router)
app.include_router(discovery_router)
app.include_router(counters_router)


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

