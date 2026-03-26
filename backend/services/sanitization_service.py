"""
Sanitization Service
Servicio para sanitizar inputs y prevenir ataques XSS
"""
import html
import re
from typing import Any, Dict, List, Union
import logging

logger = logging.getLogger(__name__)


class SanitizationService:
    """
    Servicio para sanitizar inputs y prevenir XSS (Cross-Site Scripting)
    """
    
    # Patrones peligrosos que deben ser removidos
    DANGEROUS_PATTERNS = [
        # Scripts
        (r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        (r'javascript:', re.IGNORECASE),
        
        # Event handlers
        (r'\bon\w+\s*=', re.IGNORECASE),  # onclick, onload, onerror, etc.
        
        # Iframes y objetos embebidos
        (r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
        (r'<object[^>]*>.*?</object>', re.IGNORECASE | re.DOTALL),
        (r'<embed[^>]*>', re.IGNORECASE),
        (r'<applet[^>]*>.*?</applet>', re.IGNORECASE | re.DOTALL),
        
        # Meta refresh y base
        (r'<meta[^>]*http-equiv[^>]*>', re.IGNORECASE),
        (r'<base[^>]*>', re.IGNORECASE),
        
        # Links con javascript
        (r'<link[^>]*javascript:', re.IGNORECASE),
        
        # Imports
        (r'<import[^>]*>', re.IGNORECASE),
        
        # Data URIs peligrosos
        (r'data:text/html', re.IGNORECASE),
        
        # VBScript
        (r'vbscript:', re.IGNORECASE),
    ]
    
    # Caracteres HTML que deben ser escapados
    HTML_ESCAPE_TABLE = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    
    @classmethod
    def sanitize_string(cls, text: str, escape_html: bool = True) -> str:
        """
        Sanitizar string para prevenir XSS
        
        Args:
            text: String a sanitizar
            escape_html: Si True, escapa caracteres HTML
            
        Returns:
            String sanitizado
            
        Example:
            >>> SanitizationService.sanitize_string('<script>alert("XSS")</script>')
            '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
        """
        if not text or not isinstance(text, str):
            return text
        
        sanitized = text
        
        # 1. Remover patrones peligrosos
        for pattern, flags in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=flags)
        
        # 2. Escapar HTML si se solicita
        if escape_html:
            sanitized = html.escape(sanitized, quote=True)
        
        # 3. Remover caracteres de control (excepto espacios, tabs, newlines)
        sanitized = ''.join(
            char for char in sanitized
            if char.isprintable() or char in ['\n', '\r', '\t', ' ']
        )
        
        return sanitized
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], 
                     fields_to_sanitize: List[str] = None,
                     escape_html: bool = True) -> Dict[str, Any]:
        """
        Sanitizar campos específicos de un diccionario
        
        Args:
            data: Diccionario con datos
            fields_to_sanitize: Lista de campos a sanitizar (None = todos los strings)
            escape_html: Si True, escapa caracteres HTML
            
        Returns:
            Diccionario con campos sanitizados
            
        Example:
            >>> data = {"name": "<script>alert('XSS')</script>", "age": 25}
            >>> SanitizationService.sanitize_dict(data)
            {"name": "&lt;script&gt;alert('XSS')&lt;/script&gt;", "age": 25}
        """
        sanitized_data = {}
        
        for key, value in data.items():
            # Decidir si sanitizar este campo
            should_sanitize = (
                fields_to_sanitize is None or 
                key in fields_to_sanitize
            )
            
            if should_sanitize and isinstance(value, str):
                sanitized_data[key] = cls.sanitize_string(value, escape_html)
            elif isinstance(value, dict):
                sanitized_data[key] = cls.sanitize_dict(value, fields_to_sanitize, escape_html)
            elif isinstance(value, list):
                sanitized_data[key] = cls.sanitize_list(value, escape_html)
            else:
                sanitized_data[key] = value
        
        return sanitized_data
    
    @classmethod
    def sanitize_list(cls, data: List[Any], escape_html: bool = True) -> List[Any]:
        """
        Sanitizar elementos de una lista
        
        Args:
            data: Lista con datos
            escape_html: Si True, escapa caracteres HTML
            
        Returns:
            Lista con elementos sanitizados
        """
        sanitized_list = []
        
        for item in data:
            if isinstance(item, str):
                sanitized_list.append(cls.sanitize_string(item, escape_html))
            elif isinstance(item, dict):
                sanitized_list.append(cls.sanitize_dict(item, None, escape_html))
            elif isinstance(item, list):
                sanitized_list.append(cls.sanitize_list(item, escape_html))
            else:
                sanitized_list.append(item)
        
        return sanitized_list
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitizar nombre de archivo
        
        Args:
            filename: Nombre de archivo
            
        Returns:
            Nombre de archivo sanitizado
            
        Example:
            >>> SanitizationService.sanitize_filename('../../../etc/passwd')
            'etc_passwd'
        """
        if not filename:
            return filename
        
        # Remover path traversal
        sanitized = filename.replace('..', '')
        sanitized = sanitized.replace('/', '_')
        sanitized = sanitized.replace('\\', '_')
        
        # Remover caracteres peligrosos
        sanitized = re.sub(r'[^\w\s\-\.]', '_', sanitized)
        
        # Limitar longitud
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:250] + ('.' + ext if ext else '')
        
        return sanitized
    
    @classmethod
    def sanitize_sql_like_pattern(cls, pattern: str) -> str:
        """
        Sanitizar patrón para SQL LIKE
        Escapa caracteres especiales: % _ [ ]
        
        Args:
            pattern: Patrón de búsqueda
            
        Returns:
            Patrón sanitizado
            
        Example:
            >>> SanitizationService.sanitize_sql_like_pattern('test%')
            'test\\%'
        """
        if not pattern:
            return pattern
        
        # Escapar caracteres especiales de LIKE
        sanitized = pattern.replace('\\', '\\\\')
        sanitized = sanitized.replace('%', '\\%')
        sanitized = sanitized.replace('_', '\\_')
        sanitized = sanitized.replace('[', '\\[')
        sanitized = sanitized.replace(']', '\\]')
        
        return sanitized
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        Validar formato de email
        
        Args:
            email: Email a validar
            
        Returns:
            True si es válido, False si no
        """
        if not email:
            return False
        
        # Patrón básico de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        return bool(re.match(pattern, email))
    
    @classmethod
    def validate_url(cls, url: str, allowed_schemes: List[str] = None) -> bool:
        """
        Validar URL
        
        Args:
            url: URL a validar
            allowed_schemes: Esquemas permitidos (default: ['http', 'https'])
            
        Returns:
            True si es válida, False si no
        """
        if not url:
            return False
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        # Verificar esquema
        scheme = url.split('://')[0].lower() if '://' in url else ''
        
        if scheme not in allowed_schemes:
            return False
        
        # Verificar que no contenga javascript u otros esquemas peligrosos
        dangerous_schemes = ['javascript', 'data', 'vbscript', 'file']
        for dangerous in dangerous_schemes:
            if dangerous in url.lower():
                return False
        
        return True
    
    @classmethod
    def strip_html_tags(cls, text: str) -> str:
        """
        Remover todas las etiquetas HTML
        
        Args:
            text: Texto con HTML
            
        Returns:
            Texto sin etiquetas HTML
            
        Example:
            >>> SanitizationService.strip_html_tags('<p>Hello <b>World</b></p>')
            'Hello World'
        """
        if not text:
            return text
        
        # Remover etiquetas HTML
        clean = re.sub(r'<[^>]+>', '', text)
        
        # Decodificar entidades HTML
        clean = html.unescape(clean)
        
        return clean
    
    @classmethod
    def sanitize_json_string(cls, json_str: str) -> str:
        """
        Sanitizar string que será usado en JSON
        
        Args:
            json_str: String para JSON
            
        Returns:
            String sanitizado para JSON
        """
        if not json_str:
            return json_str
        
        # Escapar caracteres especiales de JSON
        sanitized = json_str.replace('\\', '\\\\')
        sanitized = sanitized.replace('"', '\\"')
        sanitized = sanitized.replace('\n', '\\n')
        sanitized = sanitized.replace('\r', '\\r')
        sanitized = sanitized.replace('\t', '\\t')
        
        return sanitized
    
    @classmethod
    def is_safe_string(cls, text: str) -> bool:
        """
        Verificar si un string es seguro (no contiene patrones peligrosos)
        
        Args:
            text: String a verificar
            
        Returns:
            True si es seguro, False si contiene patrones peligrosos
        """
        if not text:
            return True
        
        # Verificar patrones peligrosos
        for pattern, flags in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, flags=flags):
                logger.warning(f"⚠️ Patrón peligroso detectado: {pattern}")
                return False
        
        return True


# Función de utilidad para uso rápido
def sanitize(data: Union[str, dict, list], escape_html: bool = True) -> Union[str, dict, list]:
    """
    Función de utilidad para sanitizar datos
    
    Args:
        data: Datos a sanitizar (string, dict o list)
        escape_html: Si True, escapa caracteres HTML
        
    Returns:
        Datos sanitizados
        
    Example:
        >>> from services.sanitization_service import sanitize
        >>> sanitize('<script>alert("XSS")</script>')
        '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
    """
    if isinstance(data, str):
        return SanitizationService.sanitize_string(data, escape_html)
    elif isinstance(data, dict):
        return SanitizationService.sanitize_dict(data, None, escape_html)
    elif isinstance(data, list):
        return SanitizationService.sanitize_list(data, escape_html)
    else:
        return data
