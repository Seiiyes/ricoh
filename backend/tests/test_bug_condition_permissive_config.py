"""
Bug Condition Exploration Tests - Configuración de Seguridad Permisiva

**CRÍTICO**: Estos tests DEBEN FALLAR en código sin corregir.
El fallo confirma que los bugs de configuración permisiva existen.

**NO intentar corregir los tests o el código cuando fallen.**

**OBJETIVO**: Descubrir contraejemplos que demuestren que los bugs existen.

Estos tests codifican el comportamiento esperado y validarán las correcciones
cuando pasen después de la implementación.

**Validates: Requirements 2.8, 2.9, 2.10, 2.11**
"""
import pytest
import os
import sys
from hypothesis import given, strategies as st, settings, Phase
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


class TestBugCondition_PermissiveConfig:
    """
    Property 1: Bug Condition - Configuración de Seguridad Permisiva
    
    Estos tests verifican que el código actual acepta configuraciones
    de seguridad permisivas que deberían ser rechazadas.
    """
    
    def test_cors_origins_permisivo_permite_wildcard_methods(self):
        """
        **Validates: Requirements 2.8**
        
        Test para CORS origins permisivo (permite "*" en métodos)
        
        Bug Condition: CORS configurado con allow_methods=["*"]
        Expected Behavior: CORS debe usar lista explícita de métodos
        
        RESULTADO ESPERADO: Test FALLA (confirma que bug existe)
        Contraejemplo esperado: allow_methods contiene "*"
        """
        # Leer el archivo main.py directamente para verificar la configuración
        import re
        from pathlib import Path
        
        main_file = Path(__file__).parent.parent / "main.py"
        main_content = main_file.read_text(encoding="utf-8")
        
        # Buscar la configuración de allow_methods en CORS
        # Puede estar inline: allow_methods=["*"] o usando constante: allow_methods=ALLOWED_METHODS
        allow_methods_match = re.search(r'allow_methods\s*=\s*\[(.*?)\]', main_content, re.DOTALL)
        
        # Si no encuentra inline, buscar la constante ALLOWED_METHODS
        if not allow_methods_match:
            allow_methods_match = re.search(r'ALLOWED_METHODS\s*=\s*\[(.*?)\]', main_content, re.DOTALL)
        
        assert allow_methods_match is not None, "Configuración allow_methods no encontrada"
        
        allow_methods_str = allow_methods_match.group(1).strip()
        
        # Bug Condition: Verificar que NO permite wildcard "*"
        # Este test DEBE FALLAR en código sin corregir porque actualmente permite "*"
        assert '"*"' not in allow_methods_str and "'*'" not in allow_methods_str, (
            f"CORS permite wildcard '*' en métodos. "
            f"Contraejemplo encontrado: allow_methods=[{allow_methods_str}]. "
            f"Comportamiento esperado: Lista explícita como ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']"
        )
        
        # Verificar que usa lista explícita de métodos HTTP
        expected_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        for method in expected_methods:
            assert f'"{method}"' in allow_methods_str or f"'{method}'" in allow_methods_str, (
                f"CORS no incluye método {method} en lista explícita. "
                f"Configuración actual: allow_methods=[{allow_methods_str}]"
            )
    
    def test_cors_origins_permisivo_permite_wildcard_headers(self):
        """
        **Validates: Requirements 2.8**
        
        Test para CORS origins permisivo (permite "*" en headers)
        
        Bug Condition: CORS configurado con allow_headers=["*"]
        Expected Behavior: CORS debe usar lista explícita de headers
        
        RESULTADO ESPERADO: Test FALLA (confirma que bug existe)
        Contraejemplo esperado: allow_headers contiene "*"
        """
        # Leer el archivo main.py directamente para verificar la configuración
        import re
        from pathlib import Path
        
        main_file = Path(__file__).parent.parent / "main.py"
        main_content = main_file.read_text(encoding="utf-8")
        
        # Buscar la configuración de allow_headers en CORS
        # Puede estar inline: allow_headers=["*"] o usando constante: allow_headers=ALLOWED_HEADERS
        allow_headers_match = re.search(r'allow_headers\s*=\s*\[(.*?)\]', main_content, re.DOTALL)
        
        # Si no encuentra inline, buscar la constante ALLOWED_HEADERS
        if not allow_headers_match:
            allow_headers_match = re.search(r'ALLOWED_HEADERS\s*=\s*\[(.*?)\]', main_content, re.DOTALL)
        
        assert allow_headers_match is not None, "Configuración allow_headers no encontrada"
        
        allow_headers_str = allow_headers_match.group(1).strip()
        
        # Bug Condition: Verificar que NO permite wildcard "*"
        # Este test DEBE FALLAR en código sin corregir porque actualmente permite "*"
        assert '"*"' not in allow_headers_str and "'*'" not in allow_headers_str, (
            f"CORS permite wildcard '*' en headers. "
            f"Contraejemplo encontrado: allow_headers=[{allow_headers_str}]. "
            f"Comportamiento esperado: Lista explícita como ['Content-Type', 'Authorization', 'X-CSRF-Token', 'X-Request-ID']"
        )
        
        # Verificar que usa lista explícita de headers
        expected_headers = ["Content-Type", "Authorization", "X-CSRF-Token", "X-Request-ID"]
        for header in expected_headers:
            assert f'"{header}"' in allow_headers_str or f"'{header}'" in allow_headers_str, (
                f"CORS no incluye header {header} en lista explícita. "
                f"Configuración actual: allow_headers=[{allow_headers_str}]"
            )
    
    def test_csrf_deshabilitada_por_defecto_en_produccion(self):
        """
        **Validates: Requirements 2.9**
        
        Test para CSRF deshabilitada por defecto en producción
        
        Bug Condition: CSRF deshabilitada cuando ENVIRONMENT=production
        Expected Behavior: CSRF debe estar habilitada por defecto en producción
        
        RESULTADO ESPERADO: Test FALLA (confirma que bug existe)
        Contraejemplo esperado: CSRF no está habilitada en producción
        """
        # Guardar valor original de ENVIRONMENT
        original_env = os.getenv("ENVIRONMENT")
        original_csrf = os.getenv("ENABLE_CSRF")
        
        try:
            # Simular entorno de producción sin ENABLE_CSRF explícito
            os.environ["ENVIRONMENT"] = "production"
            if "ENABLE_CSRF" in os.environ:
                del os.environ["ENABLE_CSRF"]
            
            # Reimportar main para aplicar nueva configuración
            import importlib
            import main
            importlib.reload(main)
            
            # Buscar el middleware CSRF en la aplicación
            csrf_middleware = None
            for middleware in main.app.user_middleware:
                if middleware.cls.__name__ == "CSRFProtectionMiddleware":
                    csrf_middleware = middleware
                    break
            
            # Bug Condition: Verificar que CSRF está habilitada en producción
            # Este test DEBE FALLAR en código sin corregir porque CSRF está deshabilitada por defecto
            assert csrf_middleware is not None, (
                f"CSRF deshabilitada en producción. "
                f"Contraejemplo encontrado: ENVIRONMENT=production, ENABLE_CSRF no configurado, CSRF middleware ausente. "
                f"Comportamiento esperado: CSRF habilitada por defecto en producción"
            )
            
        finally:
            # Restaurar valores originales
            if original_env:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            
            if original_csrf:
                os.environ["ENABLE_CSRF"] = original_csrf
            elif "ENABLE_CSRF" in os.environ:
                del os.environ["ENABLE_CSRF"]
    
    def test_csrf_usa_almacenamiento_en_memoria(self):
        """
        **Validates: Requirements 2.10**
        
        Test para CSRF usando almacenamiento en memoria
        
        Bug Condition: CSRF usa self._token_cache = {} (memoria)
        Expected Behavior: CSRF debe usar Redis cuando REDIS_URL está configurada
        
        RESULTADO ESPERADO: Test FALLA (confirma que bug existe)
        Contraejemplo esperado: CSRF usa diccionario en memoria
        """
        from middleware.csrf_protection import CSRFProtectionMiddleware
        
        # Crear instancia de middleware
        csrf = CSRFProtectionMiddleware(app=None)
        
        # Bug Condition: Verificar que NO usa almacenamiento en memoria
        # Este test DEBE FALLAR en código sin corregir porque usa _token_cache
        assert not hasattr(csrf, "_token_cache"), (
            f"CSRF usa almacenamiento en memoria. "
            f"Contraejemplo encontrado: CSRFProtectionMiddleware tiene atributo _token_cache. "
            f"Comportamiento esperado: Usar Redis cuando REDIS_URL está configurada"
        )
        
        # Verificar que tiene soporte para Redis
        assert hasattr(csrf, "redis_client") or hasattr(csrf, "storage_backend"), (
            f"CSRF no tiene soporte para Redis. "
            f"Comportamiento esperado: Atributo redis_client o storage_backend"
        )
    
    def test_rate_limiter_usa_almacenamiento_en_memoria(self):
        """
        **Validates: Requirements 2.11**
        
        Test para rate limiter usando almacenamiento en memoria
        
        Bug Condition: Rate limiter usa _storage = defaultdict(dict) (memoria)
        Expected Behavior: Rate limiter debe usar Redis cuando REDIS_URL está configurada
        
        RESULTADO ESPERADO: Test FALLA (confirma que bug existe)
        Contraejemplo esperado: Rate limiter usa diccionario en memoria
        """
        from services.rate_limiter_service import RateLimiterService
        
        # Bug Condition: Verificar que NO usa almacenamiento en memoria
        # Este test DEBE FALLAR en código sin corregir porque usa _storage
        assert not hasattr(RateLimiterService, "_storage"), (
            f"Rate limiter usa almacenamiento en memoria. "
            f"Contraejemplo encontrado: RateLimiterService tiene atributo _storage. "
            f"Comportamiento esperado: Usar Redis cuando REDIS_URL está configurada"
        )
        
        # Verificar que tiene soporte para Redis
        assert hasattr(RateLimiterService, "_redis_client") or hasattr(RateLimiterService, "_storage_backend"), (
            f"Rate limiter no tiene soporte para Redis. "
            f"Comportamiento esperado: Atributo _redis_client o _storage_backend"
        )


class TestBugCondition_PermissiveConfig_PropertyBased:
    """
    Property-Based Tests para configuración permisiva
    
    Estos tests usan Hypothesis para generar casos de prueba automáticamente
    y verificar propiedades universales sobre la configuración de seguridad.
    """
    
    @given(
        environment=st.sampled_from(["production", "staging"])
    )
    @settings(
        max_examples=5,
        phases=[Phase.generate, Phase.target],
        deadline=None
    )
    def test_property_csrf_habilitada_en_entornos_productivos(self, environment):
        """
        **Validates: Requirements 2.9**
        
        Property: Para cualquier entorno productivo (production, staging),
        CSRF debe estar habilitada por defecto.
        
        RESULTADO ESPERADO: Test FALLA (confirma que bug existe)
        """
        # Guardar valor original
        original_env = os.getenv("ENVIRONMENT")
        original_csrf = os.getenv("ENABLE_CSRF")
        
        try:
            # Configurar entorno
            os.environ["ENVIRONMENT"] = environment
            if "ENABLE_CSRF" in os.environ:
                del os.environ["ENABLE_CSRF"]
            
            # Reimportar main
            import importlib
            import main
            importlib.reload(main)
            
            # Verificar que CSRF está habilitada
            csrf_middleware = None
            for middleware in main.app.user_middleware:
                if middleware.cls.__name__ == "CSRFProtectionMiddleware":
                    csrf_middleware = middleware
                    break
            
            # Property: CSRF debe estar habilitada en entornos productivos
            assert csrf_middleware is not None, (
                f"Property violation: CSRF deshabilitada en {environment}. "
                f"Para cualquier entorno productivo, CSRF debe estar habilitada por defecto."
            )
            
        finally:
            # Restaurar valores originales
            if original_env:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]
            
            if original_csrf:
                os.environ["ENABLE_CSRF"] = original_csrf
            elif "ENABLE_CSRF" in os.environ:
                del os.environ["ENABLE_CSRF"]
    
    @given(
        method=st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    )
    @settings(
        max_examples=7,
        phases=[Phase.generate, Phase.target],
        deadline=None
    )
    def test_property_cors_metodos_explicitos(self, method):
        """
        **Validates: Requirements 2.8**
        
        Property: Para cualquier método HTTP válido, CORS debe tener
        una lista explícita de métodos permitidos (no wildcard "*").
        
        RESULTADO ESPERADO: Test FALLA (confirma que bug existe)
        """
        # Leer el archivo main.py directamente
        import re
        from pathlib import Path
        
        main_file = Path(__file__).parent.parent / "main.py"
        main_content = main_file.read_text(encoding="utf-8")
        
        # Buscar la configuración de allow_methods
        allow_methods_match = re.search(r'allow_methods\s*=\s*\[(.*?)\]', main_content, re.DOTALL)
        assert allow_methods_match is not None
        
        allow_methods_str = allow_methods_match.group(1).strip()
        
        # Property: No debe usar wildcard
        assert '"*"' not in allow_methods_str and "'*'" not in allow_methods_str, (
            f"Property violation: CORS usa wildcard '*' para métodos. "
            f"Debe usar lista explícita de métodos permitidos."
        )
        
        # Property: Si el método es necesario, debe estar en la lista explícita
        if method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            assert f'"{method}"' in allow_methods_str or f"'{method}'" in allow_methods_str, (
                f"Property violation: Método {method} no está en lista explícita. "
                f"Configuración actual: allow_methods=[{allow_methods_str}]"
            )
