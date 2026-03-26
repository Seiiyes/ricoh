"""
Property-based tests for Multi-Tenancy Data Isolation
Tests universal properties that should hold for all multi-tenant operations
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from services.company_filter_service import CompanyFilterService
from db.models import Printer, User
from db.models_auth import AdminUser, Empresa
from sqlalchemy.orm import Query


@pytest.mark.property
class TestMultiTenancyProperties:
    """Property-based test suite for Multi-Tenancy"""
    
    @given(
        st.integers(min_value=1, max_value=100),
        st.integers(min_value=1, max_value=100),
        st.sampled_from(['admin', 'viewer', 'operator'])
    )
    @settings(max_examples=100)
    def test_property_data_isolation_for_admin(self, empresa_id_1, empresa_id_2, rol):
        """
        Property 11: Multi-Tenancy Data Isolation
        
        For any admin user with empresa_id:
        - Should only see resources with matching empresa_id
        - Should NOT see resources with different empresa_id
        - Superadmin should see ALL resources
        """
        # Skip if empresa IDs are the same
        assume(empresa_id_1 != empresa_id_2)
        
        # Create mock admin user
        admin_user = AdminUser(
            id=1,
            username='admin_test',
            rol=rol,
            empresa_id=empresa_id_1
        )
        
        # Create mock query (we'll test the filter logic)
        # In real scenario, this would be applied to actual database queries
        
        # Property 1: Admin should only access their empresa_id
        assert CompanyFilterService.validate_company_access(admin_user, empresa_id_1) is True, \
            "Admin should have access to their own empresa"
        
        # Property 2: Admin should NOT access different empresa_id
        assert CompanyFilterService.validate_company_access(admin_user, empresa_id_2) is False, \
            "Admin should NOT have access to different empresa"
        
        # Property 3: Superadmin should access ANY empresa_id
        superadmin = AdminUser(
            id=2,
            username='superadmin_test',
            rol='superadmin',
            empresa_id=None
        )
        
        assert CompanyFilterService.validate_company_access(superadmin, empresa_id_1) is True, \
            "Superadmin should have access to any empresa"
        assert CompanyFilterService.validate_company_access(superadmin, empresa_id_2) is True, \
            "Superadmin should have access to any empresa"
    
    @given(
        st.integers(min_value=1, max_value=100),
        st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50)
    def test_property_empresa_id_enforcement_on_create(self, user_empresa_id, provided_empresa_id):
        """
        Property 12: Empresa ID Enforcement on Resource Creation
        
        For any admin user creating a resource:
        - System should automatically set empresa_id to admin's empresa_id
        - Even if different empresa_id is provided in request
        - Superadmin can create resources for any empresa
        """
        # Skip if IDs are the same
        assume(user_empresa_id != provided_empresa_id)
        
        # Create mock admin user
        admin_user = AdminUser(
            id=1,
            username='admin_test',
            rol='admin',
            empresa_id=user_empresa_id
        )
        
        # Mock resource data with different empresa_id
        resource_data = {
            'name': 'Test Resource',
            'empresa_id': provided_empresa_id  # Admin tries to set different empresa
        }
        
        # Apply enforcement
        enforced_data = CompanyFilterService.enforce_company_on_create(admin_user, resource_data)
        
        # Property: empresa_id should be forced to admin's empresa_id
        assert enforced_data['empresa_id'] == user_empresa_id, \
            f"Admin's empresa_id ({user_empresa_id}) should override provided empresa_id ({provided_empresa_id})"
        
        # Property: Superadmin should NOT have empresa_id enforced
        superadmin = AdminUser(
            id=2,
            username='superadmin_test',
            rol='superadmin',
            empresa_id=None
        )
        
        superadmin_data = {
            'name': 'Test Resource',
            'empresa_id': provided_empresa_id
        }
        
        enforced_superadmin_data = CompanyFilterService.enforce_company_on_create(
            superadmin, 
            superadmin_data
        )
        
        # Superadmin's provided empresa_id should be preserved
        assert enforced_superadmin_data['empresa_id'] == provided_empresa_id, \
            "Superadmin should be able to set any empresa_id"
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=50)
    def test_property_superadmin_sees_all_data(self, empresa_id):
        """
        Property: Superadmin should see data from all empresas
        
        For any empresa_id, superadmin should have access
        """
        superadmin = AdminUser(
            id=1,
            username='superadmin_test',
            rol='superadmin',
            empresa_id=None
        )
        
        # Superadmin should have access to any empresa
        assert CompanyFilterService.validate_company_access(superadmin, empresa_id) is True, \
            f"Superadmin should have access to empresa {empresa_id}"
        
        # Superadmin should have empresa_id = None
        assert superadmin.empresa_id is None, \
            "Superadmin should not have empresa_id"
    
    @given(
        st.integers(min_value=1, max_value=100),
        st.lists(st.integers(min_value=1, max_value=100), min_size=2, max_size=10, unique=True)
    )
    @settings(max_examples=30)
    def test_property_admin_cannot_access_other_empresas(self, admin_empresa_id, other_empresa_ids):
        """
        Property: Admin should NEVER access resources from other empresas
        
        For any admin with empresa_id, they should NOT access any other empresa_id
        """
        # Remove admin's empresa_id from the list if present
        other_empresa_ids = [eid for eid in other_empresa_ids if eid != admin_empresa_id]
        
        # Skip if no other empresas
        assume(len(other_empresa_ids) > 0)
        
        admin_user = AdminUser(
            id=1,
            username='admin_test',
            rol='admin',
            empresa_id=admin_empresa_id
        )
        
        # Admin should NOT have access to any other empresa
        for other_empresa_id in other_empresa_ids:
            assert CompanyFilterService.validate_company_access(admin_user, other_empresa_id) is False, \
                f"Admin with empresa {admin_empresa_id} should NOT access empresa {other_empresa_id}"


@pytest.mark.property
class TestFormatValidationProperties:
    """Property-based tests for format validation"""
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_property_nombre_comercial_format(self, text):
        """
        Property 1: Format Validation Consistency for nombre_comercial
        
        nombre_comercial should:
        - Accept lowercase letters, numbers, and hyphens
        - Reject uppercase letters
        - Reject spaces
        - Reject special characters (except hyphen)
        """
        import re
        
        # Valid pattern: lowercase alphanumeric with hyphens (kebab-case)
        valid_pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
        
        is_valid = bool(re.match(valid_pattern, text))
        
        # Check properties
        has_uppercase = any(c.isupper() for c in text)
        has_space = ' ' in text
        has_invalid_special = any(c in '!@#$%^&*()_+=[]{}|;:,.<>?/' for c in text)
        
        if has_uppercase or has_space or has_invalid_special:
            assert is_valid is False, \
                f"Should reject invalid nombre_comercial: {text}"
        
        # Valid examples should pass
        valid_examples = ['empresa-uno', 'test-123', 'mi-empresa']
        for example in valid_examples:
            assert bool(re.match(valid_pattern, example)) is True, \
                f"Should accept valid nombre_comercial: {example}"
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_property_username_format(self, text):
        """
        Property 1: Format Validation Consistency for username
        
        username should:
        - Accept lowercase letters, numbers, underscores, and hyphens
        - Reject uppercase letters
        - Reject spaces
        - Reject special characters (except underscore and hyphen)
        """
        import re
        
        # Valid pattern: lowercase alphanumeric with underscores/hyphens
        valid_pattern = r'^[a-z0-9_-]+$'
        
        is_valid = bool(re.match(valid_pattern, text))
        
        # Check properties
        has_uppercase = any(c.isupper() for c in text)
        has_space = ' ' in text
        has_invalid_special = any(c in '!@#$%^&*()+=[]{}|;:,.<>?/' for c in text)
        
        if has_uppercase or has_space or has_invalid_special:
            assert is_valid is False, \
                f"Should reject invalid username: {text}"
        
        # Valid examples should pass
        valid_examples = ['user_name', 'test-user', 'admin123', 'user_123']
        for example in valid_examples:
            assert bool(re.match(valid_pattern, example)) is True, \
                f"Should accept valid username: {example}"
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_property_email_format(self, text):
        """
        Property 1: Format Validation Consistency for email
        
        email should follow standard email format
        """
        import re
        
        # Simple email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        is_valid = bool(re.match(email_pattern, text))
        
        # Valid examples should pass
        valid_examples = [
            'user@example.com',
            'test.user@company.co',
            'admin+tag@domain.org'
        ]
        for example in valid_examples:
            assert bool(re.match(email_pattern, example)) is True, \
                f"Should accept valid email: {example}"
        
        # Invalid examples should fail
        invalid_examples = [
            'notanemail',
            '@example.com',
            'user@',
            'user @example.com'
        ]
        for example in invalid_examples:
            assert bool(re.match(email_pattern, example)) is False, \
                f"Should reject invalid email: {example}"
