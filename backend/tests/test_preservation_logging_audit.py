"""
Preservation Tests for Logging and Auditing Functionality
Task 7: Escribir tests de preservación para logging y auditoría

**Property 2: Preservation** - Logging y Auditoría de Eventos

IMPORTANTE: Estos tests DEBEN PASAR en código sin corregir para confirmar el comportamiento base a preservar.

Preservation Requirements being tested:
- 3.15: Eventos de auditoría se registran con información contextual necesaria
- 3.16: Logs de auditoría proporcionan trazabilidad completa
- 3.17: Inicialización de base de datos funciona correctamente
- 3.18: Creación de usuarios administrativos funciona correctamente
"""
import pytest
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from services.audit_service import AuditService
from db.models_auth import AdminAuditLog, AdminUser, Empresa
from db.database import Base


# ============================================================================
# Property-Based Tests for Audit Logging Preservation
# ============================================================================

@pytest.mark.preservation
class TestAuditLoggingPreservation:
    """
    Property-based tests to verify audit logging functionality is preserved
    
    **Validates: Requirements 3.15, 3.16**
    """
    
    @given(
        accion=st.sampled_from(['login', 'logout', 'crear', 'editar', 'eliminar', 'consultar']),
        modulo=st.sampled_from(['auth', 'empresas', 'admin_users', 'printers', 'users']),
        resultado=st.sampled_from(['exito', 'error', 'denegado']),
        entidad_tipo=st.one_of(st.none(), st.sampled_from(['empresa', 'admin_user', 'printer', 'user'])),
        entidad_id=st.one_of(st.none(), st.integers(min_value=1, max_value=10000)),
        ip_address=st.one_of(
            st.none(),
            st.sampled_from(['192.168.1.1', '10.0.0.1', '172.16.0.1', '127.0.0.1'])
        ),
        user_agent=st.one_of(
            st.none(),
            st.sampled_from([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'PostmanRuntime/7.29.0'
            ])
        )
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_audit_events_logged_with_contextual_information(
        self, db_session, test_admin_user, accion, modulo, resultado, 
        entidad_tipo, entidad_id, ip_address, user_agent
    ):
        """
        **Validates: Requirements 3.15**
        
        Property: For all critical events (login, logout, CRUD operations),
        audit logs contain necessary contextual information:
        - User ID
        - Action type
        - Module
        - Result (success/error/denied)
        - Entity type and ID (when applicable)
        - IP address
        - User agent
        - Timestamp
        
        This test verifies that audit logging captures all necessary context
        and should continue working after security fixes.
        """
        # Property: Audit service logs events with complete contextual information
        audit_log = AuditService.log_action(
            db=db_session,
            user=test_admin_user,
            accion=accion,
            modulo=modulo,
            resultado=resultado,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Verify all contextual information is preserved
        assert audit_log.admin_user_id == test_admin_user.id, \
            "Audit log should contain user ID"
        assert audit_log.accion == accion, \
            "Audit log should contain action type"
        assert audit_log.modulo == modulo, \
            "Audit log should contain module name"
        assert audit_log.resultado == resultado, \
            "Audit log should contain result"
        assert audit_log.entidad_tipo == entidad_tipo, \
            "Audit log should preserve entity type"
        assert audit_log.entidad_id == entidad_id, \
            "Audit log should preserve entity ID"
        assert audit_log.ip_address == ip_address, \
            "Audit log should contain IP address"
        assert audit_log.user_agent == user_agent, \
            "Audit log should contain user agent"
        assert audit_log.created_at is not None, \
            "Audit log should have timestamp"
        assert isinstance(audit_log.created_at, datetime), \
            "Timestamp should be datetime object"
    
    @given(
        detalles=st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_')),
            values=st.one_of(
                st.text(min_size=0, max_size=100),
                st.integers(min_value=0, max_value=1000),
                st.booleans()
            ),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_audit_logs_preserve_additional_details(
        self, db_session, test_admin_user, detalles
    ):
        """
        **Validates: Requirements 3.15**
        
        Property: For all audit events with additional details,
        the details are preserved as JSON and can be retrieved.
        """
        # Property: Additional details are preserved in audit logs
        audit_log = AuditService.log_action(
            db=db_session,
            user=test_admin_user,
            accion="editar",
            modulo="printers",
            resultado="exito",
            detalles=detalles
        )
        
        # Verify details are preserved
        assert audit_log.detalles == detalles, \
            "Audit log should preserve additional details as JSON"
    
    @given(
        num_actions=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_audit_logs_provide_complete_traceability(
        self, db_session, test_admin_user, num_actions
    ):
        """
        **Validates: Requirements 3.16**
        
        Property: For all sequences of user actions,
        audit logs provide complete traceability with chronological ordering.
        
        This test verifies that all actions are logged and can be retrieved
        in the correct order for audit trail purposes.
        """
        # Generate a sequence of actions
        actions = []
        for i in range(num_actions):
            audit_log = AuditService.log_action(
                db=db_session,
                user=test_admin_user,
                accion=f"action_{i}",
                modulo="test_module",
                resultado="exito",
                detalles={"sequence": i}
            )
            actions.append(audit_log)
        
        # Property: All actions are retrievable and ordered chronologically
        user_activity = AuditService.get_user_activity(
            db=db_session,
            user_id=test_admin_user.id,
            limit=num_actions + 10  # Get more than we created
        )
        
        # Filter to only our test actions
        test_actions = [
            log for log in user_activity 
            if log.modulo == "test_module" and log.accion.startswith("action_")
        ]
        
        # Verify complete traceability
        assert len(test_actions) >= num_actions, \
            f"All {num_actions} actions should be logged and retrievable"
        
        # Verify chronological ordering (most recent first)
        for i in range(len(test_actions) - 1):
            assert test_actions[i].created_at >= test_actions[i + 1].created_at, \
                "Audit logs should be ordered chronologically (most recent first)"
    
    @given(
        entidad_tipo=st.sampled_from(['empresa', 'printer', 'user']),
        entidad_id=st.integers(min_value=1, max_value=1000),
        num_operations=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_audit_logs_track_entity_history(
        self, db_session, test_admin_user, entidad_tipo, entidad_id, num_operations
    ):
        """
        **Validates: Requirements 3.16**
        
        Property: For all entities (empresas, printers, users),
        audit logs track complete history of operations on that entity.
        """
        # Perform multiple operations on the same entity
        operations = ['crear', 'editar', 'consultar', 'eliminar']
        
        for i in range(num_operations):
            AuditService.log_action(
                db=db_session,
                user=test_admin_user,
                accion=operations[i % len(operations)],
                modulo=f"{entidad_tipo}s",
                resultado="exito",
                entidad_tipo=entidad_tipo,
                entidad_id=entidad_id,
                detalles={"operation_number": i}
            )
        
        # Property: Entity history is complete and retrievable
        entity_history = AuditService.get_entity_history(
            db=db_session,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
            limit=num_operations + 10
        )
        
        # Verify all operations are tracked
        assert len(entity_history) >= num_operations, \
            f"All {num_operations} operations on entity should be tracked"
        
        # Verify all logs are for the correct entity
        for log in entity_history:
            assert log.entidad_tipo == entidad_tipo, \
                "All logs should be for the correct entity type"
            assert log.entidad_id == entidad_id, \
                "All logs should be for the correct entity ID"
    
    def test_audit_logs_handle_system_actions_without_user(self, db_session):
        """
        **Validates: Requirements 3.15**
        
        Property: System actions (without a user) are logged correctly
        
        This handles cases like automated cleanup, scheduled tasks, etc.
        """
        # Property: System actions can be logged without a user
        audit_log = AuditService.log_action(
            db=db_session,
            user=None,  # System action
            accion="cleanup",
            modulo="system",
            resultado="exito",
            detalles={"type": "automated_cleanup"}
        )
        
        assert audit_log.admin_user_id is None, \
            "System actions should have NULL user_id"
        assert audit_log.accion == "cleanup", \
            "System action should be logged"
        assert audit_log.modulo == "system", \
            "System module should be recorded"
    
    @given(
        modulo=st.sampled_from(['auth', 'empresas', 'printers']),
        resultado=st.sampled_from(['exito', 'error', 'denegado'])
    )
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_audit_logs_filterable_by_module_and_result(
        self, db_session, test_admin_user, modulo, resultado
    ):
        """
        **Validates: Requirements 3.16**
        
        Property: For all modules and results,
        audit logs can be filtered to find specific events.
        """
        # Create some test logs
        AuditService.log_action(
            db=db_session,
            user=test_admin_user,
            accion="test_action",
            modulo=modulo,
            resultado=resultado
        )
        
        # Property: Logs are filterable by module and result
        filtered_logs = AuditService.get_recent_logs(
            db=db_session,
            modulo=modulo,
            resultado=resultado,
            limit=100
        )
        
        # Verify filtering works
        matching_logs = [
            log for log in filtered_logs
            if log.modulo == modulo and log.resultado == resultado
        ]
        
        assert len(matching_logs) > 0, \
            "Should find at least the log we just created"
        
        # Verify all returned logs match the filter
        for log in filtered_logs:
            assert log.modulo == modulo, \
                "All logs should match module filter"
            assert log.resultado == resultado, \
                "All logs should match result filter"


# ============================================================================
# Property-Based Tests for Database Initialization Preservation
# ============================================================================

@pytest.mark.preservation
class TestDatabaseInitializationPreservation:
    """
    Property-based tests to verify database initialization functionality is preserved
    
    **Validates: Requirements 3.17, 3.18**
    """
    
    def test_database_initialization_creates_tables(self, monkeypatch):
        """
        **Validates: Requirements 3.17**
        
        Property: Database initialization creates all required tables
        
        This test verifies that the database schema is correctly initialized.
        """
        # Setup: Use a temporary in-memory SQLite database
        test_db_url = "sqlite:///:memory:"
        monkeypatch.setenv("DATABASE_URL", test_db_url)
        
        # Create engine and initialize database
        engine = create_engine(test_db_url)
        Base.metadata.create_all(bind=engine)
        
        # Property: All required tables are created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        # Verify critical tables exist
        required_tables = [
            'empresas',
            'admin_users',
            'admin_sessions',
            'admin_audit_log',
            'printers',
            'users'
        ]
        
        for table in required_tables:
            assert table in table_names, \
                f"Table '{table}' should be created during initialization"
    
    def test_database_initialization_with_valid_url(self, monkeypatch):
        """
        **Validates: Requirements 3.17**
        
        Property: Database initialization succeeds with valid DATABASE_URL
        """
        # Setup: Use valid SQLite URL
        test_db_url = "sqlite:///:memory:"
        monkeypatch.setenv("DATABASE_URL", test_db_url)
        
        # Property: Initialization succeeds without errors
        try:
            engine = create_engine(test_db_url)
            Base.metadata.create_all(bind=engine)
            
            # Verify connection works
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1
        except Exception as e:
            pytest.fail(f"Database initialization should succeed with valid URL: {e}")
    
    @given(
        username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-')),
        nombre_completo=st.text(min_size=3, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters=' ')),
        email=st.emails(),
        rol=st.sampled_from(['superadmin', 'admin', 'user'])
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_user_creation_with_valid_data(
        self, db_session, username, nombre_completo, email, rol
    ):
        """
        **Validates: Requirements 3.18**
        
        Property: For all valid user data,
        user creation succeeds and stores data correctly.
        
        This test verifies that the user creation functionality works
        with various valid inputs and should continue working after fixes.
        """
        # Ensure unique username and email for this test
        import time
        unique_suffix = f"{hash(username) % 10000}_{int(time.time() * 1000000) % 1000000}"
        username = f"test_{username[:20]}_{unique_suffix}"
        email = f"test_{unique_suffix}_{email}"
        
        # Property: User creation succeeds with valid data
        try:
            user = AdminUser(
                username=username,
                password_hash="$2b$12$dummy_hash_for_testing",
                nombre_completo=nombre_completo,
                email=email,
                rol=rol,
                is_active=True
            )
            
            db_session.add(user)
            db_session.commit()
            db_session.refresh(user)
            
            # Verify user was created correctly
            assert user.id is not None, "User should have an ID after creation"
            assert user.username == username, "Username should be preserved"
            assert user.nombre_completo == nombre_completo, "Full name should be preserved"
            assert user.email == email, "Email should be preserved"
            assert user.rol == rol, "Role should be preserved"
            assert user.is_active is True, "User should be active by default"
            assert user.created_at is not None, "User should have creation timestamp"
        except Exception as e:
            # Rollback on error to keep session clean
            db_session.rollback()
            pytest.fail(f"User creation should succeed with valid data: {e}")
    
    def test_superadmin_creation_with_secure_password(self, db_session):
        """
        **Validates: Requirements 3.18**
        
        Property: Superadmin users can be created with secure password hashes
        
        This simulates the init_superadmin.py script functionality.
        """
        import bcrypt
        
        # Generate a secure password hash (like init_superadmin.py does)
        password = "SecurePassword123!@#"
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        # Property: Superadmin creation succeeds
        superadmin = AdminUser(
            username="test_superadmin",
            password_hash=password_hash,
            nombre_completo="Test Superadmin",
            email="test_superadmin@example.com",
            rol="superadmin",
            is_active=True
        )
        
        db_session.add(superadmin)
        db_session.commit()
        db_session.refresh(superadmin)
        
        # Verify superadmin was created
        assert superadmin.id is not None
        assert superadmin.rol == "superadmin"
        assert superadmin.is_superadmin() is True
        
        # Verify password hash is valid bcrypt format
        assert password_hash.startswith('$2b$'), \
            "Password hash should be bcrypt format"
        
        # Verify password can be verified
        assert bcrypt.checkpw(password_bytes, password_hash.encode('utf-8')), \
            "Password should be verifiable with bcrypt"
    
    def test_user_creation_with_empresa_association(self, db_session, test_empresa):
        """
        **Validates: Requirements 3.18**
        
        Property: Admin users can be associated with empresas (multi-tenancy)
        """
        # Property: User creation with empresa association succeeds
        user = AdminUser(
            username="test_empresa_admin",
            password_hash="$2b$12$dummy_hash",
            nombre_completo="Empresa Admin",
            email="empresa_admin@example.com",
            rol="admin",
            empresa_id=test_empresa.id,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify empresa association
        assert user.empresa_id == test_empresa.id, \
            "User should be associated with empresa"
        assert user.empresa is not None, \
            "User should have empresa relationship"
        assert user.empresa.id == test_empresa.id, \
            "Empresa relationship should be correct"
    
    def test_user_password_update_preserves_other_fields(self, db_session):
        """
        **Validates: Requirements 3.18**
        
        Property: Updating user password preserves all other user fields
        
        This simulates the password update functionality.
        """
        import bcrypt
        
        # Create initial user
        old_password_hash = bcrypt.hashpw(b"OldPassword123!", bcrypt.gensalt(12)).decode('utf-8')
        user = AdminUser(
            username="test_password_update",
            password_hash=old_password_hash,
            nombre_completo="Test User",
            email="test_password_update@example.com",
            rol="admin",
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Store original values
        original_id = user.id
        original_username = user.username
        original_email = user.email
        original_rol = user.rol
        
        # Update password
        new_password_hash = bcrypt.hashpw(b"NewPassword456!", bcrypt.gensalt(12)).decode('utf-8')
        user.password_hash = new_password_hash
        db_session.commit()
        db_session.refresh(user)
        
        # Property: Password update preserves other fields
        assert user.id == original_id, "User ID should not change"
        assert user.username == original_username, "Username should not change"
        assert user.email == original_email, "Email should not change"
        assert user.rol == original_rol, "Role should not change"
        assert user.password_hash == new_password_hash, "Password hash should be updated"
        assert user.password_hash != old_password_hash, "Password hash should be different"


# ============================================================================
# Integration Tests for Preservation
# ============================================================================

@pytest.mark.preservation
class TestLoggingAuditIntegration:
    """
    Integration tests to verify logging and audit work together with database
    
    **Validates: Requirements 3.15, 3.16, 3.17, 3.18**
    """
    
    def test_user_creation_generates_audit_log(self, db_session, test_admin_user):
        """
        **Validates: Requirements 3.15, 3.16, 3.18**
        
        Integration test: User creation generates audit log entry
        
        This simulates the real-world scenario where administrative actions
        are automatically logged for audit trail.
        """
        # Create a new user
        new_user = AdminUser(
            username="integration_test_user",
            password_hash="$2b$12$dummy_hash",
            nombre_completo="Integration Test User",
            email="integration_test@example.com",
            rol="user",
            is_active=True
        )
        
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
        
        # Log the user creation action
        audit_log = AuditService.log_action(
            db=db_session,
            user=test_admin_user,
            accion="crear",
            modulo="admin_users",
            resultado="exito",
            entidad_tipo="admin_user",
            entidad_id=new_user.id,
            detalles={
                "username": new_user.username,
                "rol": new_user.rol
            }
        )
        
        # Integration property: User creation and audit logging work together
        assert audit_log.entidad_id == new_user.id, \
            "Audit log should reference the created user"
        assert audit_log.detalles["username"] == new_user.username, \
            "Audit log should contain user details"
        
        # Verify we can retrieve the audit trail for this user
        entity_history = AuditService.get_entity_history(
            db=db_session,
            entidad_tipo="admin_user",
            entidad_id=new_user.id
        )
        
        assert len(entity_history) > 0, \
            "Should have audit trail for newly created user"
        assert entity_history[0].accion == "crear", \
            "First audit entry should be creation"
    
    def test_complete_user_lifecycle_audit_trail(self, db_session, test_admin_user):
        """
        **Validates: Requirements 3.15, 3.16, 3.18**
        
        Integration test: Complete user lifecycle generates complete audit trail
        
        This tests the full CRUD cycle: Create -> Read -> Update -> Delete
        """
        # 1. Create user
        user = AdminUser(
            username="lifecycle_test_user",
            password_hash="$2b$12$dummy_hash",
            nombre_completo="Lifecycle Test User",
            email="lifecycle_test@example.com",
            rol="user",
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        AuditService.log_action(
            db=db_session,
            user=test_admin_user,
            accion="crear",
            modulo="admin_users",
            resultado="exito",
            entidad_tipo="admin_user",
            entidad_id=user.id
        )
        
        # 2. Read/Consult user
        AuditService.log_action(
            db=db_session,
            user=test_admin_user,
            accion="consultar",
            modulo="admin_users",
            resultado="exito",
            entidad_tipo="admin_user",
            entidad_id=user.id
        )
        
        # 3. Update user
        user.nombre_completo = "Updated Name"
        db_session.commit()
        
        AuditService.log_action(
            db=db_session,
            user=test_admin_user,
            accion="editar",
            modulo="admin_users",
            resultado="exito",
            entidad_tipo="admin_user",
            entidad_id=user.id,
            detalles={"field": "nombre_completo", "new_value": "Updated Name"}
        )
        
        # 4. Delete user
        user_id = user.id
        db_session.delete(user)
        db_session.commit()
        
        AuditService.log_action(
            db=db_session,
            user=test_admin_user,
            accion="eliminar",
            modulo="admin_users",
            resultado="exito",
            entidad_tipo="admin_user",
            entidad_id=user_id
        )
        
        # Integration property: Complete lifecycle is audited
        entity_history = AuditService.get_entity_history(
            db=db_session,
            entidad_tipo="admin_user",
            entidad_id=user_id
        )
        
        # Verify complete audit trail
        assert len(entity_history) >= 4, \
            "Should have audit entries for all lifecycle operations"
        
        actions = [log.accion for log in entity_history]
        assert "crear" in actions, "Should have creation audit"
        assert "consultar" in actions, "Should have read audit"
        assert "editar" in actions, "Should have update audit"
        assert "eliminar" in actions, "Should have deletion audit"
        
        # Verify chronological ordering
        for i in range(len(entity_history) - 1):
            assert entity_history[i].created_at >= entity_history[i + 1].created_at, \
                "Audit trail should be in chronological order"
