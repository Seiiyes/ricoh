import json
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, MagicMock

# Excepciones simuladas
class InvalidTokenError(Exception): pass
class ExpiredTokenError(Exception): pass
class AccountDisabledError(Exception): pass

# Mock del Modelo AdminSession
class MockAdminSession:
    def __init__(self, token, user_id, ip, ua, expires_at):
        self.token = token
        self.admin_user_id = user_id
        self.ip_address = ip
        self.user_agent = ua
        self.expires_at = expires_at

# Mock del Modelo AdminUser
class MockAdminUser:
    def __init__(self, user_id, username, is_active=True):
        self.id = user_id
        self.username = username
        self.is_active = is_active

# Simulación de Redis local para pruebas
class MockRedis:
    def __init__(self):
        self.store = {}
    
    def get(self, key):
        return self.store.get(key)
        
    def set(self, key, value, ttl=None):
        self.store[key] = value
        
    def delete(self, key):
        self.store.pop(key, None)

# IMPLEMENTACIÓN PROPUESTA PARA LA MIGRACIÓN SEGURA
def validate_token_secure(db, redis_client, token: str, client_ip: str, client_ua: str) -> MockAdminUser:
    """
    Función de validación segura propuesta para migración.
    Realiza Cache HIT en Redis, Device Binding en IP/UserAgent y revoca ante desajustes.
    """
    # 1. Intentar Cache HIT en Redis
    session_data = redis_client.get(f"session:{token}")
    
    if session_data:
        session_dict = json.loads(session_data)
        user_id = session_dict["user_id"]
        saved_ip = session_dict["ip_address"]
        saved_ua = session_dict["user_agent"]
    else:
        # Cache MISS - Fallback a PostgreSQL
        session = db.query(MockAdminSession).filter(token=token).first()
        if not session:
            raise InvalidTokenError("Session not found")
            
        if session.expires_at < datetime.now(timezone.utc):
            raise ExpiredTokenError("Session expired")
            
        user_id = session.admin_user_id
        saved_ip = session.ip_address
        saved_ua = session.user_agent
        
        # Cachear en Redis
        redis_client.set(f"session:{token}", json.dumps({
            "user_id": user_id,
            "ip_address": saved_ip,
            "user_agent": saved_ua
        }))

    # 2. Control de Huella Digital (Device Binding)
    if saved_ip != client_ip:
        # Revocación proactiva e inmediata ante posible hijacking
        redis_client.delete(f"session:{token}")
        db.delete_session(token)
        raise InvalidTokenError("Device binding violation: IP mismatch")
        
    if saved_ua != client_ua:
        redis_client.delete(f"session:{token}")
        db.delete_session(token)
        raise InvalidTokenError("Device binding violation: User-Agent mismatch")

    # 3. Obtener Usuario
    user = db.query(MockAdminUser).filter(user_id=user_id).first()
    if not user or not user.is_active:
        raise AccountDisabledError("User disabled or not found")
        
    return user


def setup_mocks():
    db = MagicMock()
    redis_client = MockRedis()
    
    token = "jwt_valid_token_123"
    user_id = 42
    ip = "192.168.10.5"
    ua = "Mozilla/5.0 (Windows NT 10.0)"
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    
    session = MockAdminSession(token, user_id, ip, ua, expiry)
    user = MockAdminUser(user_id, "admin_test")
    
    db.query.return_value.filter.return_value.first.side_effect = lambda: (
        session if db.query.call_args[0][0] == MockAdminSession else user
    )
    
    db.deleted_tokens = []
    db.delete_session = lambda t: db.deleted_tokens.append(t)
    
    return db, redis_client, token, user_id, ip, ua, session, user


# Ejecución de pruebas
def test_validate_session_cache_miss_populates_redis():
    db, redis_client, token, user_id, ip, ua, session, user = setup_mocks()
    assert redis_client.get(f"session:{token}") is None
    valid_user = validate_token_secure(db, redis_client, token, ip, ua)
    assert valid_user.id == user_id
    assert redis_client.get(f"session:{token}") is not None
    print("[OK] test_validate_session_cache_miss_populates_redis")

def test_validate_session_cache_hit_skips_db():
    db, redis_client, token, user_id, ip, ua, session, user = setup_mocks()
    redis_client.set(f"session:{token}", json.dumps({
        "user_id": user_id,
        "ip_address": ip,
        "user_agent": ua
    }))
    db.reset_mock()
    valid_user = validate_token_secure(db, redis_client, token, ip, ua)
    assert valid_user.id == user_id
    for call in db.query.call_args_list:
        assert call[0][0] != MockAdminSession
    print("[OK] test_validate_session_cache_hit_skips_db")

def test_device_binding_ip_mismatch_revokes_session():
    db, redis_client, token, user_id, ip, ua, session, user = setup_mocks()
    redis_client.set(f"session:{token}", json.dumps({
        "user_id": user_id,
        "ip_address": ip,
        "user_agent": ua
    }))
    hacker_ip = "200.15.88.99"
    try:
        validate_token_secure(db, redis_client, token, hacker_ip, ua)
        assert False, "Should have raised InvalidTokenError"
    except InvalidTokenError:
        pass
    assert redis_client.get(f"session:{token}") is None
    assert token in db.deleted_tokens
    print("[OK] test_device_binding_ip_mismatch_revokes_session")

def test_device_binding_ua_mismatch_revokes_session():
    db, redis_client, token, user_id, ip, ua, session, user = setup_mocks()
    redis_client.set(f"session:{token}", json.dumps({
        "user_id": user_id,
        "ip_address": ip,
        "user_agent": ua
    }))
    hacker_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)"
    try:
        validate_token_secure(db, redis_client, token, ip, hacker_ua)
        assert False, "Should have raised InvalidTokenError"
    except InvalidTokenError:
        pass
    assert redis_client.get(f"session:{token}") is None
    assert token in db.deleted_tokens
    print("[OK] test_device_binding_ua_mismatch_revokes_session")

if __name__ == "__main__":
    print("=== STARTING SESSION VALIDATION TESTS (STANDALONE) ===")
    test_validate_session_cache_miss_populates_redis()
    test_validate_session_cache_hit_skips_db()
    test_device_binding_ip_mismatch_revokes_session()
    test_device_binding_ua_mismatch_revokes_session()
    print("=== ALL TESTS PASSED SUCCESSFULLY ===")
