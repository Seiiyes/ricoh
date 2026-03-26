"""
Integration tests for empresa endpoints
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestEmpresaEndpoints:
    """Test suite for empresa endpoints"""
    
    def test_get_empresas_as_superadmin(self, client, db_session, test_empresa, superadmin_token):
        """Test GET /empresas as superadmin returns 200 and list of empresas"""
        response = client.get(
            "/empresas",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0
    
    def test_get_empresas_as_admin(self, client, db_session, admin_user, admin_token):
        """Test GET /empresas as admin returns 403"""
        response = client.get(
            "/empresas",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 403
    
    def test_create_empresa_as_superadmin(self, client, db_session, superadmin_token):
        """Test POST /empresas as superadmin with valid data returns 201"""
        response = client.post(
            "/empresas",
            headers={"Authorization": f"Bearer {superadmin_token}"},
            json={
                "razon_social": "Nueva Empresa S.A.S.",
                "nombre_comercial": "nueva-empresa",
                "nit": "900987654-3",
                "email": "info@nuevaempresa.com"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["razon_social"] == "Nueva Empresa S.A.S."
        assert data["nombre_comercial"] == "nueva-empresa"
    
    def test_create_empresa_with_duplicate_razon_social(self, client, db_session, test_empresa, superadmin_token):
        """Test POST /empresas with duplicate razon_social returns 409"""
        response = client.post(
            "/empresas",
            headers={"Authorization": f"Bearer {superadmin_token}"},
            json={
                "razon_social": "Test Empresa S.A.S.",  # Duplicate
                "nombre_comercial": "otra-empresa",
                "nit": "900111222-3",
                "email": "info@otra.com"
            }
        )
        
        assert response.status_code == 409
    
    def test_create_empresa_with_duplicate_nombre_comercial(self, client, db_session, test_empresa, superadmin_token):
        """Test POST /empresas with duplicate nombre_comercial returns 409"""
        response = client.post(
            "/empresas",
            headers={"Authorization": f"Bearer {superadmin_token}"},
            json={
                "razon_social": "Otra Empresa S.A.S.",
                "nombre_comercial": "test-empresa",  # Duplicate
                "nit": "900111222-3",
                "email": "info@otra.com"
            }
        )
        
        assert response.status_code == 409
    
    def test_get_empresa_by_id_as_superadmin(self, client, db_session, test_empresa, superadmin_token):
        """Test GET /empresas/{id} as superadmin returns 200"""
        response = client.get(
            f"/empresas/{test_empresa.id}",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_empresa.id
        assert data["razon_social"] == test_empresa.razon_social
    
    def test_update_empresa_as_superadmin(self, client, db_session, test_empresa, superadmin_token):
        """Test PUT /empresas/{id} as superadmin updates empresa correctly"""
        response = client.put(
            f"/empresas/{test_empresa.id}",
            headers={"Authorization": f"Bearer {superadmin_token}"},
            json={
                "razon_social": "Test Empresa Actualizada S.A.S.",
                "email": "nuevo@empresa.com"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["razon_social"] == "Test Empresa Actualizada S.A.S."
        assert data["email"] == "nuevo@empresa.com"
    
    def test_delete_empresa_without_resources(self, client, db_session, superadmin_token):
        """Test DELETE /empresas/{id} without resources sets is_active=False"""
        # Create a new empresa without resources
        from db.models_auth import Empresa
        empresa = Empresa(
            razon_social="Empresa Para Eliminar S.A.S.",
            nombre_comercial="empresa-eliminar",
            nit="900555666-7",
            email="eliminar@empresa.com",
            is_active=True
        )
        db_session.add(empresa)
        db_session.commit()
        db_session.refresh(empresa)
        
        response = client.delete(
            f"/empresas/{empresa.id}",
            headers={"Authorization": f"Bearer {superadmin_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify empresa is deactivated
        db_session.refresh(empresa)
        assert empresa.is_active is False
