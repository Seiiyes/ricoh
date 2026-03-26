"""
Tests for Sanitization Service
"""
import pytest
from services.sanitization_service import SanitizationService, sanitize


class TestSanitizationService:
    """Tests para SanitizationService"""
    
    def test_sanitize_script_tag(self):
        """Test remover script tags"""
        malicious = '<script>alert("XSS")</script>'
        sanitized = SanitizationService.sanitize_string(malicious)
        
        # Script debe ser removido
        assert '<script>' not in sanitized
        assert 'alert' not in sanitized
    
    def test_sanitize_event_handlers(self):
        """Test remover event handlers"""
        malicious = '<img src="x" onerror="alert(1)">'
        sanitized = SanitizationService.sanitize_string(malicious)
        
        # Event handler debe ser removido
        assert 'onerror' not in sanitized
    
    def test_sanitize_javascript_protocol(self):
        """Test remover javascript: protocol"""
        malicious = '<a href="javascript:alert(1)">Click</a>'
        sanitized = SanitizationService.sanitize_string(malicious)
        
        # javascript: debe ser removido
        assert 'javascript:' not in sanitized
    
    def test_sanitize_iframe(self):
        """Test remover iframes"""
        malicious = '<iframe src="http://evil.com"></iframe>'
        sanitized = SanitizationService.sanitize_string(malicious)
        
        # iframe debe ser removido
        assert '<iframe' not in sanitized
    
    def test_sanitize_html_escape(self):
        """Test escapar caracteres HTML"""
        text = '<div>Hello & "World"</div>'
        sanitized = SanitizationService.sanitize_string(text, escape_html=True)
        
        # Caracteres HTML deben estar escapados
        assert '&lt;' in sanitized
        assert '&gt;' in sanitized
        assert '&amp;' in sanitized
        assert '&quot;' in sanitized
    
    def test_sanitize_no_escape(self):
        """Test sin escapar HTML"""
        text = '<div>Hello</div>'
        sanitized = SanitizationService.sanitize_string(text, escape_html=False)
        
        # Sin escape, solo remover patrones peligrosos
        assert '<div>' in sanitized
    
    def test_sanitize_dict(self):
        """Test sanitizar diccionario"""
        data = {
            "name": '<script>alert("XSS")</script>',
            "age": 25,
            "bio": '<img src="x" onerror="alert(1)">'
        }
        
        sanitized = SanitizationService.sanitize_dict(data)
        
        # Strings deben estar sanitizados
        assert '<script>' not in sanitized["name"]
        assert 'onerror' not in sanitized["bio"]
        
        # Números no deben cambiar
        assert sanitized["age"] == 25
    
    def test_sanitize_dict_specific_fields(self):
        """Test sanitizar solo campos específicos"""
        data = {
            "name": '<script>alert("XSS")</script>',
            "description": '<b>Bold text</b>'
        }
        
        # Sanitizar solo name
        sanitized = SanitizationService.sanitize_dict(data, fields_to_sanitize=["name"])
        
        # name debe estar sanitizado
        assert '<script>' not in sanitized["name"]
        
        # description no debe cambiar (no está en la lista)
        assert sanitized["description"] == '<b>Bold text</b>'
    
    def test_sanitize_list(self):
        """Test sanitizar lista"""
        data = [
            '<script>alert(1)</script>',
            'Normal text',
            '<img src="x" onerror="alert(1)">'
        ]
        
        sanitized = SanitizationService.sanitize_list(data)
        
        # Elementos deben estar sanitizados
        assert '<script>' not in sanitized[0]
        assert sanitized[1] == 'Normal text'
        assert 'onerror' not in sanitized[2]
    
    def test_sanitize_nested_dict(self):
        """Test sanitizar diccionario anidado"""
        data = {
            "user": {
                "name": '<script>alert("XSS")</script>',
                "email": "test@test.com"
            }
        }
        
        sanitized = SanitizationService.sanitize_dict(data)
        
        # Nested strings deben estar sanitizados
        assert '<script>' not in sanitized["user"]["name"]
        assert sanitized["user"]["email"] == "test@test.com"
    
    def test_sanitize_filename(self):
        """Test sanitizar nombre de archivo"""
        # Path traversal
        filename = '../../../etc/passwd'
        sanitized = SanitizationService.sanitize_filename(filename)
        assert '..' not in sanitized
        assert '/' not in sanitized
        
        # Caracteres peligrosos
        filename = 'file<>:"|?*.txt'
        sanitized = SanitizationService.sanitize_filename(filename)
        assert '<' not in sanitized
        assert '>' not in sanitized
        assert ':' not in sanitized
        assert '"' not in sanitized
        assert '|' not in sanitized
        assert '?' not in sanitized
        assert '*' not in sanitized
    
    def test_sanitize_sql_like_pattern(self):
        """Test sanitizar patrón SQL LIKE"""
        pattern = 'test%_value'
        sanitized = SanitizationService.sanitize_sql_like_pattern(pattern)
        
        # Caracteres especiales deben estar escapados
        assert '\\%' in sanitized
        assert '\\_' in sanitized
    
    def test_validate_email(self):
        """Test validar email"""
        # Emails válidos
        assert SanitizationService.validate_email('test@test.com') is True
        assert SanitizationService.validate_email('user.name@example.co.uk') is True
        
        # Emails inválidos
        assert SanitizationService.validate_email('invalid') is False
        assert SanitizationService.validate_email('test@') is False
        assert SanitizationService.validate_email('@test.com') is False
        assert SanitizationService.validate_email('') is False
        assert SanitizationService.validate_email(None) is False
    
    def test_validate_url(self):
        """Test validar URL"""
        # URLs válidas
        assert SanitizationService.validate_url('http://example.com') is True
        assert SanitizationService.validate_url('https://example.com') is True
        
        # URLs inválidas
        assert SanitizationService.validate_url('javascript:alert(1)') is False
        assert SanitizationService.validate_url('data:text/html,<script>alert(1)</script>') is False
        assert SanitizationService.validate_url('ftp://example.com') is False
        assert SanitizationService.validate_url('') is False
        assert SanitizationService.validate_url(None) is False
    
    def test_strip_html_tags(self):
        """Test remover todas las etiquetas HTML"""
        html = '<p>Hello <b>World</b></p>'
        stripped = SanitizationService.strip_html_tags(html)
        
        # Etiquetas deben ser removidas
        assert '<p>' not in stripped
        assert '<b>' not in stripped
        assert stripped == 'Hello World'
    
    def test_sanitize_json_string(self):
        """Test sanitizar string para JSON"""
        text = 'Line 1\nLine 2\tTabbed\r\nWindows'
        sanitized = SanitizationService.sanitize_json_string(text)
        
        # Caracteres especiales deben estar escapados
        assert '\\n' in sanitized
        assert '\\t' in sanitized
        assert '\\r' in sanitized
    
    def test_is_safe_string(self):
        """Test verificar si string es seguro"""
        # Strings seguros
        assert SanitizationService.is_safe_string('Normal text') is True
        assert SanitizationService.is_safe_string('Text with numbers 123') is True
        
        # Strings peligrosos
        assert SanitizationService.is_safe_string('<script>alert(1)</script>') is False
        assert SanitizationService.is_safe_string('<img onerror="alert(1)">') is False
        assert SanitizationService.is_safe_string('javascript:alert(1)') is False
    
    def test_sanitize_utility_function(self):
        """Test función de utilidad sanitize()"""
        # String
        result = sanitize('<script>alert(1)</script>')
        assert '<script>' not in result
        
        # Dict
        result = sanitize({"name": '<script>alert(1)</script>'})
        assert '<script>' not in result["name"]
        
        # List
        result = sanitize(['<script>alert(1)</script>'])
        assert '<script>' not in result[0]
        
        # Otros tipos
        result = sanitize(123)
        assert result == 123
