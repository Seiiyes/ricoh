"""
Tests para UserSyncService y normalización de códigos de usuario
"""
import pytest
from services.user_sync_service import normalize_user_code, UserSyncService
from db.models import User
from sqlalchemy.orm import Session


class TestNormalizeUserCode:
    """Tests para la función normalize_user_code"""
    
    def test_normalize_code_with_leading_zeros(self):
        """Debe eliminar ceros a la izquierda"""
        assert normalize_user_code("0547") == "547"
        assert normalize_user_code("00123") == "123"
        assert normalize_user_code("000001") == "1"
    
    def test_normalize_code_without_leading_zeros(self):
        """Debe mantener códigos sin ceros a la izquierda"""
        assert normalize_user_code("8599") == "8599"
        assert normalize_user_code("1234") == "1234"
        assert normalize_user_code("5") == "5"
    
    def test_normalize_code_all_zeros(self):
        """Debe convertir "0000" a "0" """
        assert normalize_user_code("0000") == "0"
        assert normalize_user_code("00") == "0"
        assert normalize_user_code("0") == "0"
    
    def test_normalize_code_empty_string(self):
        """Debe convertir string vacío a "0" """
        assert normalize_user_code("") == "0"
        assert normalize_user_code("   ") == "0"
    
    def test_normalize_code_with_whitespace(self):
        """Debe eliminar espacios y normalizar"""
        assert normalize_user_code("  0547  ") == "547"
        assert normalize_user_code(" 8599 ") == "8599"
    
    def test_normalize_code_none(self):
        """Debe manejar None como "0" """
        assert normalize_user_code(None) == "0"


class TestUserSyncService:
    """Tests para UserSyncService"""
    
    def test_sync_user_from_counter_normalizes_code(self, db_session: Session):
        """Debe normalizar código antes de buscar/crear usuario"""
        # Crear usuario con código normalizado
        user = User(
            name="Test User",
            codigo_de_usuario="547",  # Sin ceros a la izquierda
            network_username="test\\user",
            network_password_encrypted="",
            smb_server="192.168.1.1",
            smb_port=21,
            smb_path="\\\\server\\path",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        # Intentar sincronizar con código con ceros a la izquierda
        user_id = UserSyncService.sync_user_from_counter(
            codigo_usuario="0547",  # Con ceros a la izquierda
            nombre_usuario="Test User",
            db=db_session
        )
        
        # Debe retornar el mismo usuario (no crear duplicado)
        assert user_id == user.id
        
        # Verificar que no se creó duplicado
        total_users = db_session.query(User).filter(
            User.name == "Test User"
        ).count()
        assert total_users == 1
    
    def test_sync_user_from_counter_creates_with_normalized_code(self, db_session: Session):
        """Debe crear usuario con código normalizado"""
        # Sincronizar usuario que no existe con código con ceros
        user_id = UserSyncService.sync_user_from_counter(
            codigo_usuario="0123",  # Con ceros a la izquierda
            nombre_usuario="New User",
            db=db_session
        )
        
        # Verificar que se creó con código normalizado
        user = db_session.query(User).filter(User.id == user_id).first()
        assert user is not None
        assert user.codigo_de_usuario == "123"  # Sin ceros a la izquierda
        assert user.name == "New User"
    
    def test_sync_user_prevents_duplicates(self, db_session: Session):
        """Debe prevenir creación de duplicados con códigos variantes"""
        # Primera sincronización con código sin ceros
        user_id_1 = UserSyncService.sync_user_from_counter(
            codigo_usuario="456",
            nombre_usuario="Duplicate Test",
            db=db_session
        )
        
        # Segunda sincronización con código con ceros (mismo usuario)
        user_id_2 = UserSyncService.sync_user_from_counter(
            codigo_usuario="0456",
            nombre_usuario="Duplicate Test",
            db=db_session
        )
        
        # Deben ser el mismo usuario
        assert user_id_1 == user_id_2
        
        # Verificar que solo hay 1 usuario
        total_users = db_session.query(User).filter(
            User.name == "Duplicate Test"
        ).count()
        assert total_users == 1


@pytest.fixture
def db_session():
    """Fixture para sesión de base de datos de prueba"""
    from db.database import get_db
    session = next(get_db())
    
    # Setup: limpiar datos de prueba
    session.query(User).filter(
        User.name.in_(["Test User", "New User", "Duplicate Test"])
    ).delete(synchronize_session=False)
    session.commit()
    
    yield session
    
    # Teardown: limpiar datos de prueba
    session.query(User).filter(
        User.name.in_(["Test User", "New User", "Duplicate Test"])
    ).delete(synchronize_session=False)
    session.commit()
    session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
