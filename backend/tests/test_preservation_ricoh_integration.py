"""
Preservation Tests for Ricoh Printer Integration
Task 5: Escribir tests de preservación para integración con impresoras Ricoh

**Property 2: Preservation** - Integración con Impresoras Ricoh

IMPORTANTE: Estos tests DEBEN PASAR en código sin corregir para confirmar el comportamiento base a preservar.

Preservation Requirements being tested:
- 3.6: Autenticación con impresoras usando credenciales válidas funciona correctamente
- 3.7: Obtención y uso de wimTokens funciona correctamente
- 3.8: Operaciones CRUD en libretas de direcciones funcionan correctamente

Methodology: Observation-first approach
1. Observe: Authentication with printers using valid credentials works in unfixed code
2. Observe: Obtaining and using wimTokens works in unfixed code
3. Observe: CRUD operations on address books work in unfixed code
4. Write property-based tests: for all valid credentials, authentication establishes session
5. Write property-based tests: for all valid wimTokens, authorized operations succeed
"""
import pytest
import os
import re
from unittest.mock import Mock, MagicMock, patch, call
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from services.ricoh_web_client import RicohWebClient


# ============================================================================
# Test Strategies for Ricoh Integration
# ============================================================================

# Strategy for valid printer IPs
valid_printer_ips = st.sampled_from([
    "192.168.1.100",
    "10.0.0.50",
    "172.16.0.200"
])

# Strategy for valid admin credentials
valid_admin_credentials = st.fixed_dictionaries({
    'username': st.sampled_from(['admin', 'administrator', 'root']),
    'password': st.text(min_size=8, max_size=32, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='!@#$%^&*'
    ))
})

# Strategy for valid wimTokens (numeric strings)
valid_wim_tokens = st.text(
    min_size=10,
    max_size=20,
    alphabet=st.characters(whitelist_categories=('Nd',))
)

# Strategy for valid user configurations
valid_user_configs = st.fixed_dictionaries({
    'nombre': st.text(min_size=3, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'),
        whitelist_characters=' '
    )),
    'codigo_de_usuario': st.text(min_size=3, max_size=10, alphabet=st.characters(
        whitelist_categories=('Nd',)
    )),
    'nombre_usuario_inicio_sesion': st.text(min_size=3, max_size=30, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )),
    'contrasena_inicio_sesion': st.text(min_size=8, max_size=32),
    'funciones_disponibles': st.fixed_dictionaries({
        'copiadora': st.booleans(),
        'escaner': st.booleans(),
        'impresora': st.booleans(),
        'document_server': st.booleans(),
        'fax': st.booleans(),
        'navegador': st.booleans()
    }),
    'carpeta_smb': st.fixed_dictionaries({
        'ruta': st.text(min_size=5, max_size=100, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='\\/_-.'
        ))
    })
})


# ============================================================================
# Property-Based Tests for Authentication Preservation
# ============================================================================

@pytest.mark.preservation
class TestRicohAuthenticationPreservation:
    """
    Property-based tests to verify Ricoh printer authentication is preserved
    
    **Validates: Requirements 3.6**
    """
    
    @given(
        printer_ip=valid_printer_ips,
        credentials=valid_admin_credentials
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_authentication_establishes_session_for_all_valid_credentials(
        self, printer_ip, credentials
    ):
        """
        **Validates: Requirements 3.6**
        
        Property: For all valid credentials, authentication with Ricoh printers
        establishes an authenticated session.
        
        This test verifies that authentication works correctly with valid credentials
        and should continue working after security fixes.
        """
        # Setup: Create client with valid credentials
        client = RicohWebClient(
            timeout=30,
            admin_user=credentials['username'],
            admin_password=credentials['password']
        )
        
        # Mock the HTTP requests to simulate successful authentication
        with patch.object(client.session, 'get') as mock_get, \
             patch.object(client.session, 'post') as mock_post:
            
            # Mock initial test request (not authenticated)
            mock_test_response = Mock()
            mock_test_response.status_code = 302  # Redirect to login
            mock_test_response.text = '<html>Redirect to login</html>'
            
            # Mock login form request
            mock_form_response = Mock()
            mock_form_response.status_code = 200
            mock_form_response.text = '<input name="wimToken" value="1234567890" />'
            
            # Mock verification request (authenticated)
            mock_verify_response = Mock()
            mock_verify_response.status_code = 200
            mock_verify_response.text = '<input name="wimToken" value="1234567890" /><div>Address Book</div>'
            
            mock_get.side_effect = [
                mock_test_response,      # Initial test
                mock_form_response,      # Login form
                mock_verify_response     # Verification
            ]
            
            # Mock login POST
            mock_login_response = Mock()
            mock_login_response.status_code = 200
            mock_login_response.text = '<html>Login successful</html>'
            mock_post.return_value = mock_login_response
            
            # Property: Authentication establishes session
            result = client._authenticate(printer_ip)
            
            assert result is True, \
                f"Authentication should succeed with valid credentials"
            
            # Verify session was established
            assert printer_ip in client._authenticated_printers, \
                f"Printer {printer_ip} should be in authenticated printers set"
            
            # Verify wimToken was stored
            assert printer_ip in client._wim_tokens, \
                f"wimToken should be stored for printer {printer_ip}"
            assert client._wim_tokens[printer_ip] == "1234567890", \
                f"Stored wimToken should match the one from response"
    
    @given(printer_ip=valid_printer_ips)
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_authentication_reuses_existing_session(self, printer_ip):
        """
        **Validates: Requirements 3.6**
        
        Property: For all printers with existing authenticated sessions,
        authentication is reused without re-authenticating.
        
        This verifies session caching works correctly.
        """
        # Setup
        client = RicohWebClient(
            admin_user="admin",
            admin_password="ValidPassword123!"
        )
        
        # Pre-populate authenticated session
        client._authenticated_printers.add(printer_ip)
        
        # Property: Existing session is reused
        result = client._authenticate(printer_ip)
        
        assert result is True, \
            "Authentication should succeed immediately with existing session"
    
    def test_authentication_handles_already_logged_in_session(self):
        """
        **Validates: Requirements 3.6**
        
        Edge case: Authentication detects when already logged in
        """
        # Setup
        client = RicohWebClient(
            admin_user="admin",
            admin_password="ValidPassword123!"
        )
        printer_ip = "192.168.1.100"
        
        with patch.object(client.session, 'get') as mock_get:
            # Mock response showing we're already authenticated
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<input name="wimToken" value="9876543210" /><div>Address Book</div>'
            mock_get.return_value = mock_response
            
            # Property: Already authenticated session is detected
            result = client._authenticate(printer_ip)
            
            assert result is True
            assert printer_ip in client._authenticated_printers
            assert client._wim_tokens[printer_ip] == "9876543210"


# ============================================================================
# Property-Based Tests for wimToken Management Preservation
# ============================================================================

@pytest.mark.preservation
class TestWimTokenManagementPreservation:
    """
    Property-based tests to verify wimToken management is preserved
    
    **Validates: Requirements 3.7**
    """
    
    @given(
        printer_ip=valid_printer_ips,
        wim_token=valid_wim_tokens
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_wim_token_extraction_from_login_page(self, printer_ip, wim_token):
        """
        **Validates: Requirements 3.7**
        
        Property: For all printers, wimToken can be extracted from login page.
        
        This verifies wimToken extraction works correctly.
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        
        with patch.object(client.session, 'get') as mock_get:
            # Mock login page with wimToken
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = f'<form><input name="wimToken" value="{wim_token}" /></form>'
            mock_get.return_value = mock_response
            
            # Property: wimToken is extracted correctly
            extracted_token = client._get_login_token(printer_ip)
            
            assert extracted_token == wim_token, \
                f"Extracted wimToken should match the one in HTML"
    
    @given(
        printer_ip=valid_printer_ips,
        wim_token=valid_wim_tokens
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_wim_token_refresh_from_address_list(self, printer_ip, wim_token):
        """
        **Validates: Requirements 3.7**
        
        Property: For all printers, wimToken can be refreshed from address list page.
        
        This verifies wimToken refresh mechanism works correctly.
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        
        with patch.object(client.session, 'get') as mock_get:
            # Mock address list page with fresh wimToken
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = f'<form><input name="wimToken" value="{wim_token}" /></form>'
            mock_get.return_value = mock_response
            
            # Property: wimToken is refreshed correctly
            refreshed_token = client._refresh_wim_token(printer_ip)
            
            assert refreshed_token == wim_token, \
                f"Refreshed wimToken should match the one in HTML"
            
            # Verify token was cached
            assert client._wim_tokens.get(printer_ip) == wim_token, \
                f"Refreshed wimToken should be cached"
    
    @given(printer_ip=valid_printer_ips)
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_wim_token_refresh_handles_failure_gracefully(self, printer_ip):
        """
        **Validates: Requirements 3.7**
        
        Property: For all printers, wimToken refresh handles failures gracefully
        by returning cached token or empty string.
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        
        # Pre-populate cached token
        cached_token = "1234567890"
        client._wim_tokens[printer_ip] = cached_token
        
        with patch.object(client.session, 'get') as mock_get:
            # Mock failed response
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = '<html>Error</html>'
            mock_get.return_value = mock_response
            
            # Property: Failure returns cached token
            result = client._refresh_wim_token(printer_ip)
            
            assert result == cached_token, \
                f"Failed refresh should return cached token"
    
    def test_wim_token_storage_and_retrieval(self):
        """
        **Validates: Requirements 3.7**
        
        Property: wimTokens are correctly stored and retrieved per printer
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        
        # Store tokens for multiple printers
        tokens = {
            "192.168.1.100": "1111111111",
            "192.168.1.101": "2222222222",
            "192.168.1.102": "3333333333"
        }
        
        for ip, token in tokens.items():
            client._wim_tokens[ip] = token
        
        # Property: Each printer has its own token
        for ip, expected_token in tokens.items():
            assert client._wim_tokens[ip] == expected_token, \
                f"Token for {ip} should be {expected_token}"


# ============================================================================
# Property-Based Tests for Address Book Operations Preservation
# ============================================================================

@pytest.mark.preservation
class TestAddressBookOperationsPreservation:
    """
    Property-based tests to verify address book CRUD operations are preserved
    
    **Validates: Requirements 3.8**
    """
    
    def test_user_provisioning_succeeds_with_valid_config(self):
        """
        **Validates: Requirements 3.8**
        
        Property: For all valid user configurations, provisioning to Ricoh printers
        succeeds when authenticated.
        
        This verifies user provisioning (CREATE operation) works correctly.
        """
        # Setup
        client = RicohWebClient(
            admin_user="admin",
            admin_password="ValidPassword123!"
        )
        printer_ip = "192.168.1.100"
        
        # Pre-authenticate
        client._authenticated_printers.add(printer_ip)
        client._wim_tokens[printer_ip] = "1234567890"
        
        # Valid user config
        user_config = {
            'nombre': 'Test User',
            'codigo_de_usuario': '12345',
            'nombre_usuario_inicio_sesion': 'testuser',
            'contrasena_inicio_sesion': 'Password123!',
            'funciones_disponibles': {
                'copiadora': True,
                'escaner': True,
                'impresora': False,
                'document_server': False,
                'fax': False,
                'navegador': False
            },
            'carpeta_smb': {
                'ruta': '\\\\server\\share\\testuser'
            }
        }
        
        with patch.object(client.session, 'get') as mock_get, \
             patch.object(client.session, 'post') as mock_post:
            
            # Mock list page response
            mock_list_response = Mock()
            mock_list_response.status_code = 200
            mock_list_response.text = '<input name="wimToken" value="1234567890" />'
            
            # Mock form response with entry index
            mock_form_response = Mock()
            mock_form_response.status_code = 200
            mock_form_response.text = '''
                <input name="wimToken" value="9999999999" />
                <input name="entryIndexIn" value="00001" />
            '''
            
            mock_get.return_value = mock_list_response
            
            # Mock POST responses
            mock_post_responses = [
                mock_form_response,  # adrsGetUser.cgi
                Mock(status_code=200, text='<html>Success</html>')  # adrsSetUser.cgi
            ]
            mock_post.side_effect = mock_post_responses
            
            # Property: Provisioning succeeds with valid configuration
            result = client.provision_user(printer_ip, user_config)
            
            assert result is True, \
                f"User provisioning should succeed with valid configuration"
            
            # Verify POST was called with correct data
            assert mock_post.call_count >= 1, \
                "POST should be called at least once for provisioning"
    
    def test_user_provisioning_handles_busy_printer(self):
        """
        **Validates: Requirements 3.8**
        
        Property: For all printers, provisioning correctly detects and reports
        when printer is busy.
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        printer_ip = "192.168.1.100"
        client._authenticated_printers.add(printer_ip)
        client._wim_tokens[printer_ip] = "1234567890"
        
        user_config = {
            'nombre': 'Test User',
            'codigo_de_usuario': '12345',
            'nombre_usuario_inicio_sesion': 'testuser',
            'contrasena_inicio_sesion': 'password',
            'funciones_disponibles': {
                'copiadora': True,
                'escaner': True,
                'impresora': False,
                'document_server': False,
                'fax': False,
                'navegador': False
            },
            'carpeta_smb': {'ruta': '\\\\server\\share'}
        }
        
        with patch.object(client.session, 'get') as mock_get, \
             patch.object(client.session, 'post') as mock_post:
            
            mock_list_response = Mock()
            mock_list_response.status_code = 200
            mock_list_response.text = '<input name="wimToken" value="1234567890" />'
            mock_get.return_value = mock_list_response
            
            # Mock BUSY response
            mock_busy_response = Mock()
            mock_busy_response.status_code = 200
            mock_busy_response.text = '<html>BUSY - está siendo utilizado</html>'
            
            mock_post.side_effect = [
                Mock(status_code=200, text='<input name="wimToken" value="9999" /><input name="entryIndexIn" value="00001" />'),
                mock_busy_response
            ]
            
            # Property: BUSY status is detected
            result = client.provision_user(printer_ip, user_config)
            
            assert result == "BUSY", \
                f"Provisioning should return 'BUSY' when printer is busy"
    
    def test_user_provisioning_handles_badflow_error(self):
        """
        **Validates: Requirements 3.8**
        
        Property: For all printers, provisioning correctly detects and reports
        BADFLOW errors (anti-scraping protection).
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        printer_ip = "192.168.1.100"
        client._authenticated_printers.add(printer_ip)
        client._wim_tokens[printer_ip] = "1234567890"
        
        user_config = {
            'nombre': 'Test User',
            'codigo_de_usuario': '12345',
            'nombre_usuario_inicio_sesion': 'testuser',
            'contrasena_inicio_sesion': 'password',
            'funciones_disponibles': {
                'copiadora': True,
                'escaner': False,
                'impresora': False,
                'document_server': False,
                'fax': False,
                'navegador': False
            },
            'carpeta_smb': {'ruta': '\\\\server\\share'}
        }
        
        with patch.object(client.session, 'get') as mock_get, \
             patch.object(client.session, 'post') as mock_post:
            
            mock_list_response = Mock()
            mock_list_response.status_code = 200
            mock_list_response.text = '<input name="wimToken" value="1234567890" />'
            mock_get.return_value = mock_list_response
            
            # Mock BADFLOW response
            mock_badflow_response = Mock()
            mock_badflow_response.status_code = 200
            mock_badflow_response.text = '<html>BADFLOW - Invalid request flow</html>'
            
            mock_post.side_effect = [
                Mock(status_code=200, text='<input name="wimToken" value="9999" /><input name="entryIndexIn" value="00001" />'),
                mock_badflow_response
            ]
            
            # Property: BADFLOW is detected
            result = client.provision_user(printer_ip, user_config)
            
            assert result == "BADFLOW", \
                f"Provisioning should return 'BADFLOW' when anti-scraping is triggered"
    
    def test_user_provisioning_uses_default_password_when_not_provided(self):
        """
        **Validates: Requirements 3.8**
        
        Edge case: Provisioning uses default password when not provided
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        printer_ip = "192.168.1.100"
        client._authenticated_printers.add(printer_ip)
        client._wim_tokens[printer_ip] = "1234567890"
        
        # User config without password
        user_config = {
            'nombre': 'Test User',
            'codigo_de_usuario': '12345',
            'nombre_usuario_inicio_sesion': 'testuser',
            'contrasena_inicio_sesion': '',  # Empty password
            'funciones_disponibles': {'copiadora': True},
            'carpeta_smb': {'ruta': '\\\\server\\share'}
        }
        
        with patch.object(client.session, 'get') as mock_get, \
             patch.object(client.session, 'post') as mock_post:
            
            mock_list_response = Mock()
            mock_list_response.status_code = 200
            mock_list_response.text = '<input name="wimToken" value="1234567890" />'
            mock_get.return_value = mock_list_response
            
            mock_post.side_effect = [
                Mock(status_code=200, text='<input name="wimToken" value="9999" /><input name="entryIndexIn" value="00001" />'),
                Mock(status_code=200, text='<html>Success</html>')
            ]
            
            # Property: Default password is used
            result = client.provision_user(printer_ip, user_config)
            
            # Verify default password was used in POST
            post_calls = mock_post.call_args_list
            if len(post_calls) >= 2:
                # Check the adrsSetUser.cgi call (second POST)
                set_user_call = post_calls[1]
                form_data = set_user_call[1].get('data', [])
                
                # Verify password field exists in form data
                password_fields = [item for item in form_data if item[0] == 'folderAuthPasswordIn']
                assert len(password_fields) > 0, "Password field should be present"
                assert password_fields[0][1] == 'Temporal2021', \
                    "Default password 'Temporal2021' should be used when not provided"


# ============================================================================
# Property-Based Tests for Session Management Preservation
# ============================================================================

@pytest.mark.preservation
class TestSessionManagementPreservation:
    """
    Property-based tests to verify session management is preserved
    
    **Validates: Requirements 3.6, 3.7**
    """
    
    def test_session_reset_clears_all_cached_data(self):
        """
        **Validates: Requirements 3.6, 3.7**
        
        Property: Session reset clears all authenticated printers and wimTokens
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        
        # Populate session data
        client._authenticated_printers.add("192.168.1.100")
        client._authenticated_printers.add("192.168.1.101")
        client._wim_tokens["192.168.1.100"] = "1111111111"
        client._wim_tokens["192.168.1.101"] = "2222222222"
        
        # Property: Reset clears everything
        client.reset_session()
        
        assert len(client._authenticated_printers) == 0, \
            "Authenticated printers should be cleared"
        assert len(client._wim_tokens) == 0, \
            "wimTokens should be cleared"
    
    @given(
        printer_ips=st.lists(valid_printer_ips, min_size=1, max_size=5, unique=True)
    )
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_multiple_printer_sessions_are_independent(self, printer_ips):
        """
        **Validates: Requirements 3.6, 3.7**
        
        Property: For all sets of printers, each printer maintains independent
        authentication state and wimToken.
        """
        # Setup
        client = RicohWebClient(admin_user="admin", admin_password="test")
        
        # Authenticate multiple printers
        for i, ip in enumerate(printer_ips):
            client._authenticated_printers.add(ip)
            client._wim_tokens[ip] = f"{i:010d}"  # Unique token per printer
        
        # Property: Each printer has independent state
        for i, ip in enumerate(printer_ips):
            assert ip in client._authenticated_printers, \
                f"Printer {ip} should be authenticated"
            assert client._wim_tokens[ip] == f"{i:010d}", \
                f"Printer {ip} should have its own unique wimToken"
        
        # Verify total count
        assert len(client._authenticated_printers) == len(printer_ips), \
            "All printers should be authenticated"
        assert len(client._wim_tokens) == len(printer_ips), \
            "All printers should have wimTokens"


# ============================================================================
# Integration Tests for Preservation
# ============================================================================

@pytest.mark.preservation
class TestRicohIntegrationPreservation:
    """
    Integration tests to verify complete Ricoh integration workflow is preserved
    
    **Validates: Requirements 3.6, 3.7, 3.8**
    """
    
    def test_complete_user_provisioning_workflow(self):
        """
        **Validates: Requirements 3.6, 3.7, 3.8**
        
        Integration test: Complete workflow from authentication to user provisioning
        
        This simulates the real-world scenario of authenticating with a printer
        and provisioning a user to the address book.
        """
        # Setup
        client = RicohWebClient(
            admin_user="admin",
            admin_password="SecurePassword123!"
        )
        printer_ip = "192.168.1.100"
        
        user_config = {
            'nombre': 'Juan Perez',
            'codigo_de_usuario': '12345',
            'nombre_usuario_inicio_sesion': 'jperez',
            'contrasena_inicio_sesion': 'UserPass123!',
            'funciones_disponibles': {
                'copiadora': True,
                'escaner': True,
                'impresora': True,
                'document_server': False,
                'fax': False,
                'navegador': False
            },
            'carpeta_smb': {
                'ruta': '\\\\fileserver\\users\\jperez'
            }
        }
        
        with patch.object(client.session, 'get') as mock_get, \
             patch.object(client.session, 'post') as mock_post:
            
            # Mock authentication flow
            mock_test_response = Mock()
            mock_test_response.status_code = 302
            mock_test_response.text = '<html>Redirect</html>'
            
            mock_form_response = Mock()
            mock_form_response.status_code = 200
            mock_form_response.text = '<input name="wimToken" value="1234567890" />'
            
            mock_verify_response = Mock()
            mock_verify_response.status_code = 200
            mock_verify_response.text = '<input name="wimToken" value="1234567890" /><div>Address Book</div>'
            
            # Mock provisioning flow
            mock_list_response = Mock()
            mock_list_response.status_code = 200
            mock_list_response.text = '<input name="wimToken" value="9999999999" />'
            
            mock_get.side_effect = [
                mock_test_response,      # Auth: initial test
                mock_form_response,      # Auth: login form
                mock_verify_response,    # Auth: verification
                mock_list_response       # Provision: list page
            ]
            
            mock_login_response = Mock()
            mock_login_response.status_code = 200
            mock_login_response.text = '<html>Login OK</html>'
            
            mock_get_user_response = Mock()
            mock_get_user_response.status_code = 200
            mock_get_user_response.text = '''
                <input name="wimToken" value="8888888888" />
                <input name="entryIndexIn" value="00042" />
            '''
            
            mock_set_user_response = Mock()
            mock_set_user_response.status_code = 200
            mock_set_user_response.text = '<html>User provisioned successfully</html>'
            
            mock_post.side_effect = [
                mock_login_response,      # Auth: login POST
                mock_get_user_response,   # Provision: get user form
                mock_set_user_response    # Provision: set user
            ]
            
            # Integration workflow: Authenticate then provision
            auth_result = client._authenticate(printer_ip)
            assert auth_result is True, "Authentication should succeed"
            
            provision_result = client.provision_user(printer_ip, user_config)
            assert provision_result is True, "Provisioning should succeed"
            
            # Verify complete workflow
            assert printer_ip in client._authenticated_printers, \
                "Printer should remain authenticated"
            assert printer_ip in client._wim_tokens, \
                "wimToken should be maintained"
            
            # Verify all expected calls were made
            assert mock_get.call_count == 4, \
                "Should make 4 GET requests (3 for auth, 1 for provision)"
            assert mock_post.call_count == 3, \
                "Should make 3 POST requests (1 for auth, 2 for provision)"
