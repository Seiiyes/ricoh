"""
Integration tests for authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAuthEndpoints:
    """Test suite for authentication endpoints"""
    
    def test_login_with_valid_credentials(self, client, db_session, superadmin_user):
        """Test POST /auth/login with valid credentials returns 200 and tokens"""
        response = client.post(
            "/auth/login",
            json={
                "username": "test_superadmin",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        assert data["user"]["username"] == "test_superadmin"
        assert "password_hash" not in data["user"]
    
    def test_login_with_invalid_credentials(self, client, db_session, superadmin_user):
        """Test POST /auth/login with invalid credentials returns 401"""
        response = client.post(
            "/auth/login",
            json={
                "username": "test_superadmin",
                "password": "WrongPassword!"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_login_with_nonexistent_user(self, client, db_session):
        """Test POST /auth/login with nonexistent user returns 401"""
        response = client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_with_inactive_user(self, client, db_session, superadmin_user):
        """Test POST /auth/login with inactive user returns 403"""
        # Deactivate user
        superadmin_user.is_active = False
        db_session.commit()
        
        response = client.post(
            "/auth/login",
            json={
                "username": "test_superadmin",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == 403
    
    def test_get_me_with_valid_token(self, client, db_session, superadmin_user, superadmin_token):
        """Test GET /auth/me with valid token returns 200 and user info"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test_superadmin"
        assert "password_hash" not in data
    
    def test_get_me_without_token(self, client):
        """Test GET /auth/me without token returns 401"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_get_me_with_invalid_token(self, client):
        """Test GET /auth/me with invalid token returns 401"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_logout_with_valid_token(self, client, db_session, superadmin_user, superadmin_token):
        """Test POST /auth/logout with valid token returns 200"""
        # First create a session
        from db.models_auth import AdminSession
        from datetime import datetime, timedelta
        
        session = AdminSession(
            admin_user_id=superadmin_user.id,
            token=superadmin_token,
            refresh_token="refresh_token_here",
            ip_address="127.0.0.1",
            user_agent="test",
            expires_at=datetime.utcnow() + timedelta(minutes=30),
            refresh_expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_change_password_with_correct_current_password(self, client, db_session, superadmin_user, superadmin_token):
        """Test POST /auth/change-password with correct current password returns 200"""
        response = client.post(
            "/auth/change-password",
            headers={"Authorization": f"Bearer {superadmin_token}"},
            json={
                "current_password": "TestPass123!",
                "new_password": "NewPass456!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_change_password_with_incorrect_current_password(self, client, db_session, superadmin_user, superadmin_token):
        """Test POST /auth/change-password with incorrect current password returns 400"""
        response = client.post(
            "/auth/change-password",
            headers={"Authorization": f"Bearer {superadmin_token}"},
            json={
                "current_password": "WrongPass123!",
                "new_password": "NewPass456!"
            }
        )
        
        assert response.status_code == 400
    
    def test_change_password_with_weak_new_password(self, client, db_session, superadmin_user, superadmin_token):
        """Test POST /auth/change-password with weak new password returns 400"""
        response = client.post(
            "/auth/change-password",
            headers={"Authorization": f"Bearer {superadmin_token}"},
            json={
                "current_password": "TestPass123!",
                "new_password": "weak"
            }
        )
        
        assert response.status_code == 422  # Validation error
