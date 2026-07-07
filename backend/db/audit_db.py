"""
SQLite database configuration for security audit logs
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

# Asegurar que el directorio de logs exista
LOGS_DIR = "/app/logs"
if not os.path.exists(LOGS_DIR):
    # En desarrollo local puede no existir la carpeta de logs de docker, la creamos
    os.makedirs(LOGS_DIR, exist_ok=True)

AUDIT_DB_PATH = os.path.join(LOGS_DIR, "security_audit.db")
AUDIT_DATABASE_URL = f"sqlite:///{AUDIT_DB_PATH}"

# SQLite requiere check_same_thread=False para multihilos en FastAPI
engine = create_engine(
    AUDIT_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SecurityAuditLog(Base):
    """
    Modelo de logs de auditoría de seguridad
    Se almacena de forma aislada en SQLite
    """
    __tablename__ = "security_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    usuario = Column(String(150), nullable=True, index=True)
    accion = Column(String(100), nullable=False, index=True)
    detalles = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    resultado = Column(String(20), nullable=False, index=True)

    def __repr__(self):
        return f"<SecurityAuditLog(id={self.id}, usuario='{self.usuario}', accion='{self.accion}', resultado='{self.resultado}')>"


def init_audit_db():
    """Crea las tablas de auditoría si no existen"""
    Base.metadata.create_all(bind=engine)


def get_audit_db():
    """Generador de sesiones de base de datos de auditoría"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
