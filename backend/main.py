"""
Ricoh Multi-Fleet Governance Suite - Backend API
FastAPI server with PostgreSQL, WebSockets, and network discovery
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import json
from datetime import datetime
from typing import List

# Import database
from db.database import init_db, engine
from db import Base

# Import API routers
from api import users_router, printers_router, provisioning_router, discovery_router


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
    print("🚀 Starting Ricoh Fleet Governance API...")
    print("📊 Initializing database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized")
    print(f"🔧 Demo Mode: {os.getenv('DEMO_MODE', 'true')}")
    print("🌐 Server ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Ricoh Fleet Governance API...")


# Create FastAPI app
app = FastAPI(
    title="Ricoh Fleet Governance API",
    description="Backend API for Ricoh printer fleet discovery and management with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(users_router)
app.include_router(printers_router)
app.include_router(provisioning_router)
app.include_router(discovery_router)


# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Ricoh Fleet Governance API",
        "status": "online",
        "version": "2.0.0",
        "demo_mode": os.getenv("DEMO_MODE", "true").lower() == "true",
        "database": "PostgreSQL",
        "features": [
            "User Management",
            "Printer Fleet Management",
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
            "message": "Connected to Ricoh Fleet Governance Console",
            "type": "info"
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Echo back or process if needed
            
    except WebSocketDisconnect:
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
