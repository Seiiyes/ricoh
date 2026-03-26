"""
Integration tests for multi-tenancy data isolation
"""
import pytest
from services.company_filter_service import CompanyFilterService


@pytest.mark.integration
class TestMultiTenancy:
    """Test suite for multi-tenancy data isolation"""
    
    def test_superadmin_sees_all_data(self, db_session, superadmin_user, test_empresa):
        """Test that superadmin can see all data without filtering"""
        from db.models import Printer
        from sqlalchemy import select
        
        # Create printers for different empresas
        printer1 = Printer(
            hostname="printer1.test.com",
            ip_address="192.168.1.100",
            empresa_id=test_empresa.id
        )
        db_session.add(printer1)
        db_session.commit()
        
        # Query without filter
        query = select(Printer)
        
        # Apply filter for superadmin
        filtered_query = CompanyFilterService.apply_filter(query, superadmin_user)
        
        # Superadmin should see all printers
        result = db_session.execute(filtered_query).scalars().all()
        assert len(result) >= 1
    
    def test_admin_sees_only_own_empresa_data(self, db_session, admin_user, test_empresa):
        """Test that admin only sees data from their empresa"""
        from db.models import Printer
        from db.models_auth import Empresa
        from sqlalchemy import select
        
        # Create another empresa
        otra_empresa = Empresa(
            razon_social="Otra Empresa S.A.S.",
            nombre_comercial="otra-empresa",
            nit="900777888-9",
            email="otra@empresa.com",
            is_active=True
        )
        db_session.add(otra_empresa)
        db_session.commit()
        
        # Create printers for both empresas
        printer1 = Printer(
            hostname="printer1.test.com",
            ip_address="192.168.1.100",
            empresa_id=test_empresa.id
        )
        printer2 = Printer(
            hostname="printer2.test.com",
            ip_address="192.168.1.101",
            empresa_id=otra_empresa.id
        )
        db_session.add_all([printer1, printer2])
        db_session.commit()
        
        # Query with filter for admin
        query = select(Printer)
        filtered_query = CompanyFilterService.apply_filter(query, admin_user)
        
        # Admin should only see printers from their empresa
        result = db_session.execute(filtered_query).scalars().all()
        assert len(result) == 1
        assert result[0].empresa_id == test_empresa.id
    
    def test_admin_cannot_access_other_empresa_resource(self, db_session, admin_user, test_empresa):
        """Test that admin cannot access resources from another empresa"""
        from db.models_auth import Empresa
        
        # Create another empresa
        otra_empresa = Empresa(
            razon_social="Otra Empresa S.A.S.",
            nombre_comercial="otra-empresa",
            nit="900777888-9",
            email="otra@empresa.com",
            is_active=True
        )
        db_session.add(otra_empresa)
        db_session.commit()
        
        # Admin should not have access to otra_empresa
        has_access = CompanyFilterService.validate_company_access(admin_user, otra_empresa.id)
        assert has_access is False
    
    def test_admin_can_access_own_empresa_resource(self, db_session, admin_user, test_empresa):
        """Test that admin can access resources from their own empresa"""
        has_access = CompanyFilterService.validate_company_access(admin_user, test_empresa.id)
        assert has_access is True
    
    def test_enforce_company_on_create_for_admin(self, db_session, admin_user, test_empresa):
        """Test that empresa_id is enforced when admin creates resource"""
        data = {
            "hostname": "new-printer.test.com",
            "empresa_id": 999  # Try to set different empresa_id
        }
        
        # Enforce company
        enforced_data = CompanyFilterService.enforce_company_on_create(admin_user, data)
        
        # Should be forced to admin's empresa_id
        assert enforced_data["empresa_id"] == test_empresa.id
    
    def test_enforce_company_on_create_for_superadmin(self, db_session, superadmin_user):
        """Test that empresa_id is not enforced for superadmin"""
        data = {
            "hostname": "new-printer.test.com",
            "empresa_id": 999
        }
        
        # Enforce company
        enforced_data = CompanyFilterService.enforce_company_on_create(superadmin_user, data)
        
        # Should keep original empresa_id for superadmin
        assert enforced_data["empresa_id"] == 999
