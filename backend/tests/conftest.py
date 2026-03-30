"""
Pytest configuration and fixtures
"""
import pytest
from sqlalchemy import create_engine, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

# Set test environment BEFORE any imports
os.environ["ENVIRONMENT"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-minimum-32-characters-long"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Monkey-patch JSONB to use JSON for SQLite BEFORE importing models
from sqlalchemy.dialects import postgresql
postgresql.JSONB = JSON


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine"""
    # Import Base from db.database to use the same Base as models
    from db.database import Base
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Import all models to register them with Base.metadata
    # This must be done before create_all
    from db.models import User, Printer, UserPrinterAssignment
    from db.models_auth import (
        Empresa, AdminUser, AdminSession, AdminAuditLog
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


@pytest.fixture
def superadmin_user(db_session):
    """Create a superadmin user for testing"""
    from db.models_auth import AdminUser
    from services.password_service import PasswordService
    
    user = AdminUser(
        username="test_superadmin",
        password_hash=PasswordService.hash_password("TestPass123!"),
        nombre_completo="Test Superadmin",
        email="superadmin@test.com",
        rol="superadmin",
        empresa_id=None,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_empresa(db_session):
    """Create a test empresa"""
    from db.models_auth import Empresa
    
    empresa = Empresa(
        razon_social="Test Empresa S.A.S.",
        nombre_comercial="test-empresa",
        nit="900123456-7",
        email="test@empresa.com",
        is_active=True
    )
    db_session.add(empresa)
    db_session.commit()
    db_session.refresh(empresa)
    return empresa


@pytest.fixture
def admin_user(db_session, test_empresa):
    """Create an admin user for testing"""
    from db.models_auth import AdminUser
    from services.password_service import PasswordService
    
    user = AdminUser(
        username="test_admin",
        password_hash=PasswordService.hash_password("TestPass123!"),
        nombre_completo="Test Admin",
        email="admin@test.com",
        rol="admin",
        empresa_id=test_empresa.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def superadmin_token(superadmin_user):
    """Generate a JWT token for superadmin"""
    from services.jwt_service import JWTService
    return JWTService.create_access_token(superadmin_user)


@pytest.fixture
def admin_token(admin_user):
    """Generate a JWT token for admin"""
    from services.jwt_service import JWTService
    return JWTService.create_access_token(admin_user)


@pytest.fixture
def test_admin_user(db_session, test_empresa):
    """Alias for admin_user fixture"""
    from db.models_auth import AdminUser
    from services.password_service import PasswordService
    
    user = AdminUser(
        username="test_admin",
        password_hash=PasswordService.hash_password("TestPass123!"),
        nombre_completo="Test Admin",
        email="admin@test.com",
        rol="admin",
        empresa_id=test_empresa.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_superadmin(db_session):
    """Alias for superadmin_user fixture"""
    from db.models_auth import AdminUser
    from services.password_service import PasswordService
    
    user = AdminUser(
        username="test_superadmin",
        password_hash=PasswordService.hash_password("TestPass123!"),
        nombre_completo="Test Superadmin",
        email="superadmin@test.com",
        rol="superadmin",
        empresa_id=None,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_session(db_session, test_admin_user):
    """Create a test admin session"""
    from db.models_auth import AdminSession
    from services.jwt_service import JWTService
    from datetime import datetime, timedelta
    
    token = JWTService.create_access_token(test_admin_user)
    
    session = AdminSession(
        admin_user_id=test_admin_user.id,
        token=token,
        ip_address="127.0.0.1",
        user_agent="test-agent",
        expires_at=datetime.utcnow() + timedelta(minutes=30),
        last_activity=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session
