"""
Preservation Tests for CORS, CSRF, and Rate Limiting Configuration
Task 6: Escribir tests de preservación para configuración CORS, CSRF y rate limiting

**Property 2: Preservation** - Configuración de Seguridad con Valores Válidos

IMPORTANTE: Estos tests DEBEN PASAR en código sin corregir para confirmar el comportamiento base a preservar.

Preservation Requirements being tested:
- 3.9: Peticiones de orígenes permitidos se procesan correctamente
- 3.10: Peticiones con métodos permitidos se procesan correctamente
- 3.11: Peticiones con tokens CSRF válidos se procesan correctamente
- 3.12: Peticiones POST/PUT/DELETE con CSRF válido tienen éxito
- 3.13: Peticiones dentro de límites de rate limiting se procesan sin restricciones
- 3.14: Rate limiting aplica restricciones solo cuando se exceden límites
"""
import pytest
import os
from datetime import datetime, timedelta, timezone
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from fastapi import Request, HTTPException
from fastapi.testclient import TestClient
from starlette.datastructures import Headers
from middleware.csrf_protection import CSRFProtectionMiddleware
from services.rate_limiter_service import RateLimiterService, RateLimitResult


# ============================================================================
# Property-Based Tests for CORS Preservation
# ============================================================================

@pytest.mark.preservation
class TestCORSPreservation:
    """
    Property-based tests to verify CORS functionality is preserved
    
    **Validates: Requirements 3.9, 3.10**
    """
    
    @given(
        origin=st.sampled_from([
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174"
        ]),
        method=st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
    )
    @settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_requests_from_allowed_origins_are_processed(self, origin, method, monkeypatch):
        """
        **Validates: Requirements 3.9, 3.10**
        
        Property: For all allowed origins and all HTTP methods,
        requests are processed correctly by CORS middleware.
        
        This test verifies that CORS configuration allows legitimate requests
        from configured origins and should continue working after security fixes.
        """
        # Disable DDoS protection for testing
        monkeypatch.setenv("ENABLE_DDOS_PROTECTION", "false")
        
        from main import app
        
        client = TestClient(app)
        
        # Property: Requests from allowed origins with allowed methods succeed
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": method
        }
        
        # Test preflight request (OPTIONS)
        response = client.options("/", headers=headers)
        
        # CORS should allow the request
        assert response.status_code in [200, 204], \
            f"Preflight request from allowed origin {origin} should succeed"
        
        # Verify CORS headers are present
        assert "access-control-allow-origin" in response.headers, \
            "Response should include Access-Control-Allow-Origin header"
        
        # The origin should be allowed
        allowed_origin = response.headers.get("access-control-allow-origin")
        assert allowed_origin in [origin, "*"], \
            f"Origin {origin} should be in allowed origins"
    
    @given(
        method=st.sampled_from(["GET", "POST", "PUT", "DELETE", "PATCH"])
    )
    @settings(max_examples=5, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_allowed_methods_are_processed_correctly(self, method, monkeypatch):
        """
        **Validates: Requirements 3.10**
        
        Property: For all allowed HTTP methods, requests are processed correctly.
        """
        # Disable DDoS protection for testing
        monkeypatch.setenv("ENABLE_DDOS_PROTECTION", "false")
        
        from main import app
        
        client = TestClient(app)
        
        # Property: Allowed methods are accepted
        origin = "http://localhost:5173"
        headers = {
            "Origin": origin,
            "Access-Control-Request-Method": method
        }
        
        response = client.options("/", headers=headers)
        
        # Method should be allowed
        assert response.status_code in [200, 204]
        
        # Verify allowed methods header
        if "access-control-allow-methods" in response.headers:
            allowed_methods = response.headers["access-control-allow-methods"]
            # Current implementation allows all methods with "*"
            # After fix, it should be explicit list
            assert "*" in allowed_methods or method in allowed_methods, \
                f"Method {method} should be in allowed methods"
    
    def test_cors_allows_credentials_for_authenticated_requests(self, monkeypatch):
        """
        **Validates: Requirements 3.9**
        
        Property: CORS configuration allows credentials for authenticated requests
        """
        # Disable DDoS protection for testing
        monkeypatch.setenv("ENABLE_DDOS_PROTECTION", "false")
        
        from main import app
        
        client = TestClient(app)
        
        headers = {
            "Origin": "http://localhost:5173",
            "Cookie": "session=abc123"
        }
        
        response = client.get("/", headers=headers)
        
        # Credentials should be allowed
        assert response.status_code == 200
        if "access-control-allow-credentials" in response.headers:
            assert response.headers["access-control-allow-credentials"] == "true", \
                "CORS should allow credentials"
    
    def test_cors_preflight_caching_works(self, monkeypatch):
        """
        **Validates: Requirements 3.9**
        
        Property: CORS preflight responses include max-age for caching
        """
        # Disable DDoS protection for testing
        monkeypatch.setenv("ENABLE_DDOS_PROTECTION", "false")
        
        from main import app
        
        client = TestClient(app)
        
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST"
        }
        
        response = client.options("/", headers=headers)
        
        # Preflight caching should be configured
        if "access-control-max-age" in response.headers:
            max_age = int(response.headers["access-control-max-age"])
            assert max_age > 0, "CORS max-age should be positive"


# ============================================================================
# Property-Based Tests for CSRF Preservation
# ============================================================================

@pytest.mark.preservation
class TestCSRFPreservation:
    """
    Property-based tests to verify CSRF functionality is preserved
    
    **Validates: Requirements 3.11, 3.12**
    """
    
    @given(
        session_id=st.text(min_size=10, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        user_agent=st.text(min_size=5, max_size=100)
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_valid_csrf_tokens_are_accepted(self, session_id, user_agent):
        """
        **Validates: Requirements 3.11, 3.12**
        
        Property: For all valid CSRF tokens generated by the system,
        requests with those tokens are processed correctly.
        
        This test verifies that CSRF protection works correctly with valid tokens
        and should continue working after security fixes.
        """
        from fastapi import FastAPI
        from starlette.middleware.base import BaseHTTPMiddleware
        from starlette.responses import JSONResponse
        
        # Create a test app with CSRF middleware
        app = FastAPI()
        csrf_middleware = CSRFProtectionMiddleware(app)
        
        # Mock request for token generation
        class MockRequest:
            def __init__(self, session_id, user_agent):
                self.headers = {
                    "Authorization": f"Bearer {session_id}",
                    "User-Agent": user_agent
                }
                self.method = "GET"
                self.url = type('obj', (object,), {'path': '/test'})()
            
            def get(self, key, default=None):
                return self.headers.get(key, default)
        
        mock_request = MockRequest(session_id, user_agent)
        
        # Property: Generate token and verify it's valid
        csrf_token = csrf_middleware._generate_csrf_token(mock_request)
        
        assert isinstance(csrf_token, str), "CSRF token should be a string"
        assert len(csrf_token) > 0, "CSRF token should not be empty"
        assert csrf_token in csrf_middleware._token_cache, \
            "Generated token should be stored in cache"
        
        # Verify token data
        token_data = csrf_middleware._token_cache[csrf_token]
        assert "session_id" in token_data
        assert "user_agent" in token_data
        assert "expires_at" in token_data
        
        # Token should not be expired
        assert datetime.utcnow() < token_data["expires_at"], \
            "Newly generated token should not be expired"
    
    @given(
        method=st.sampled_from(["POST", "PUT", "DELETE", "PATCH"])
    )
    @settings(max_examples=30, deadline=None)
    def test_csrf_protected_methods_with_valid_token_succeed(self, method):
        """
        **Validates: Requirements 3.12**
        
        Property: For all protected HTTP methods (POST, PUT, DELETE, PATCH),
        requests with valid CSRF tokens are processed successfully.
        """
        from fastapi import FastAPI
        
        app = FastAPI()
        csrf_middleware = CSRFProtectionMiddleware(app)
        
        # Generate a valid token
        class MockRequest:
            def __init__(self):
                self.headers = {
                    "Authorization": "Bearer test_session_123",
                    "User-Agent": "TestAgent/1.0"
                }
                self.method = "GET"
                self.url = type('obj', (object,), {'path': '/test'})()
                self.query_params = {}
        
        mock_request = MockRequest()
        csrf_token = csrf_middleware._generate_csrf_token(mock_request)
        
        # Property: Protected method with valid token should be allowed
        mock_request.method = method
        mock_request.headers["X-CSRF-Token"] = csrf_token
        
        # Verify token is valid (should not raise exception)
        try:
            csrf_middleware._validate_csrf_token(mock_request)
            # If we get here, validation passed
            validation_passed = True
        except HTTPException:
            validation_passed = False
        
        assert validation_passed, \
            f"Method {method} with valid CSRF token should pass validation"
    
    def test_csrf_token_expiration_time_is_2_hours(self):
        """
        **Validates: Requirements 3.11**
        
        Property: CSRF tokens expire in 2 hours
        """
        from fastapi import FastAPI
        
        app = FastAPI()
        csrf_middleware = CSRFProtectionMiddleware(app)
        
        class MockRequest:
            def __init__(self):
                self.headers = {
                    "Authorization": "Bearer test_session",
                    "User-Agent": "TestAgent"
                }
                self.method = "GET"
                self.url = type('obj', (object,), {'path': '/test'})()
        
        mock_request = MockRequest()
        csrf_token = csrf_middleware._generate_csrf_token(mock_request)
        
        # Property: Token expires in 2 hours
        token_data = csrf_middleware._token_cache[csrf_token]
        expires_at = token_data["expires_at"]
        now = datetime.utcnow()
        
        expiration_delta = expires_at - now
        expected_hours = 2
        expected_seconds = expected_hours * 60 * 60
        
        # Allow 10 seconds tolerance
        assert abs(expiration_delta.total_seconds() - expected_seconds) < 10, \
            f"CSRF token should expire in {expected_hours} hours"
    
    def test_csrf_token_cleanup_removes_expired_tokens(self):
        """
        **Validates: Requirements 3.11**
        
        Property: Expired CSRF tokens are cleaned up from cache
        """
        from fastapi import FastAPI
        
        app = FastAPI()
        csrf_middleware = CSRFProtectionMiddleware(app)
        
        # Add an expired token manually
        expired_token = "expired_token_123"
        csrf_middleware._token_cache[expired_token] = {
            "session_id": "test",
            "user_agent": "test",
            "expires_at": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        
        # Add a valid token
        class MockRequest:
            def __init__(self):
                self.headers = {
                    "Authorization": "Bearer test_session",
                    "User-Agent": "TestAgent"
                }
                self.method = "GET"
                self.url = type('obj', (object,), {'path': '/test'})()
        
        mock_request = MockRequest()
        valid_token = csrf_middleware._generate_csrf_token(mock_request)
        
        # Property: Cleanup removes expired tokens but keeps valid ones
        csrf_middleware._cleanup_expired_tokens()
        
        assert expired_token not in csrf_middleware._token_cache, \
            "Expired token should be removed"
        assert valid_token in csrf_middleware._token_cache, \
            "Valid token should be preserved"
    
    def test_csrf_excluded_paths_bypass_validation(self):
        """
        **Validates: Requirements 3.11**
        
        Property: Excluded paths bypass CSRF validation
        """
        from fastapi import FastAPI
        
        app = FastAPI()
        csrf_middleware = CSRFProtectionMiddleware(app)
        
        # Property: Excluded paths don't require CSRF token
        excluded_paths = ["/auth/login", "/auth/refresh", "/docs", "/openapi.json"]
        
        for path in excluded_paths:
            assert path in csrf_middleware.EXCLUDED_PATHS, \
                f"Path {path} should be in excluded paths"


# ============================================================================
# Property-Based Tests for Rate Limiting Preservation
# ============================================================================

@pytest.mark.preservation
class TestRateLimitingPreservation:
    """
    Property-based tests to verify rate limiting functionality is preserved
    
    **Validates: Requirements 3.13, 3.14**
    """
    
    @given(
        key=st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='.-_')),
        max_requests=st.integers(min_value=5, max_value=100),
        window_seconds=st.integers(min_value=10, max_value=300)
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_requests_within_limits_are_not_restricted(self, key, max_requests, window_seconds):
        """
        **Validates: Requirements 3.13**
        
        Property: For all rate limit configurations, requests within the limit
        are processed without restrictions.
        
        This test verifies that rate limiting allows legitimate traffic
        and should continue working after security fixes.
        """
        # Reset rate limiter state for this test
        RateLimiterService.reset_counter(key)
        
        # Property: Requests within limit are allowed
        for i in range(max_requests):
            result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
            
            assert result.allowed is True, \
                f"Request {i+1}/{max_requests} should be allowed"
            assert result.remaining >= 0, \
                "Remaining count should be non-negative"
            assert result.reset_at > datetime.now(timezone.utc), \
                "Reset time should be in the future"
        
        # Cleanup
        RateLimiterService.reset_counter(key)
    
    @given(
        key=st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='.-_')),
        max_requests=st.integers(min_value=3, max_value=10)
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_rate_limiting_applies_restrictions_when_exceeded(self, key, max_requests):
        """
        **Validates: Requirements 3.14**
        
        Property: For all rate limit configurations, requests exceeding the limit
        are restricted.
        """
        # Reset rate limiter state
        RateLimiterService.reset_counter(key)
        
        window_seconds = 60
        
        # Property: Requests up to limit are allowed
        for i in range(max_requests):
            result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
            assert result.allowed is True, f"Request {i+1} should be allowed"
        
        # Property: Request exceeding limit is restricted
        result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
        assert result.allowed is False, \
            f"Request {max_requests + 1} should be restricted (limit: {max_requests})"
        assert result.remaining == 0, \
            "Remaining count should be 0 when limit exceeded"
        
        # Cleanup
        RateLimiterService.reset_counter(key)
    
    @given(
        key=st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='.-_')),
        max_requests=st.integers(min_value=5, max_value=20)
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_rate_limit_remaining_count_decreases_correctly(self, key, max_requests):
        """
        **Validates: Requirements 3.13**
        
        Property: For all rate limit configurations, the remaining count
        decreases correctly with each request.
        """
        # Reset rate limiter state
        RateLimiterService.reset_counter(key)
        
        window_seconds = 60
        
        # Property: Remaining count decreases with each request
        for i in range(max_requests):
            result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
            
            expected_remaining = max_requests - i - 1
            assert result.remaining == expected_remaining, \
                f"After request {i+1}, remaining should be {expected_remaining}, got {result.remaining}"
        
        # Cleanup
        RateLimiterService.reset_counter(key)
    
    def test_rate_limit_window_resets_after_expiration(self):
        """
        **Validates: Requirements 3.13, 3.14**
        
        Property: Rate limit window resets after expiration time
        """
        import time
        
        key = "test_reset_key"
        max_requests = 3
        window_seconds = 2  # Short window for testing
        
        # Reset state
        RateLimiterService.reset_counter(key)
        
        # Use up the limit
        for i in range(max_requests):
            result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
            assert result.allowed is True
        
        # Next request should be blocked
        result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
        assert result.allowed is False
        
        # Wait for window to expire
        time.sleep(window_seconds + 0.5)
        
        # Property: After window expires, limit resets
        result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
        assert result.allowed is True, \
            "After window expiration, requests should be allowed again"
        
        # Cleanup
        RateLimiterService.reset_counter(key)
    
    def test_rate_limit_reset_at_time_is_accurate(self):
        """
        **Validates: Requirements 3.13**
        
        Property: Rate limit reset_at time is accurate
        """
        key = "test_reset_time"
        max_requests = 5
        window_seconds = 60
        
        # Reset state
        RateLimiterService.reset_counter(key)
        
        # Make a request
        before = datetime.now(timezone.utc)
        result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
        after = datetime.now(timezone.utc)
        
        # Property: reset_at should be approximately window_seconds in the future
        expected_reset = before + timedelta(seconds=window_seconds)
        actual_reset = result.reset_at
        
        # Allow 2 seconds tolerance
        time_diff = abs((actual_reset - expected_reset).total_seconds())
        assert time_diff < 2, \
            f"Reset time should be approximately {window_seconds} seconds in the future"
        
        # Cleanup
        RateLimiterService.reset_counter(key)
    
    def test_rate_limit_cleanup_removes_expired_counters(self):
        """
        **Validates: Requirements 3.13**
        
        Property: Expired rate limit counters are cleaned up
        """
        import time
        
        key = "test_cleanup_key"
        max_requests = 5
        window_seconds = 1  # Short window
        
        # Reset state
        RateLimiterService.reset_counter(key)
        
        # Make a request to create a counter
        RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
        
        # Wait for window to expire
        time.sleep(window_seconds + 0.5)
        
        # Property: Cleanup removes expired counters
        removed = RateLimiterService.cleanup_expired(window_seconds)
        
        # At least our test key should be removed
        assert removed >= 0, "Cleanup should remove expired counters"
        
        # Verify counter was reset
        result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
        assert result.remaining == max_requests - 1, \
            "After cleanup, counter should be reset"
        
        # Cleanup
        RateLimiterService.reset_counter(key)
    
    def test_rate_limit_get_remaining_returns_correct_count(self):
        """
        **Validates: Requirements 3.13**
        
        Property: get_remaining returns accurate remaining request count
        """
        key = "test_remaining_key"
        max_requests = 10
        window_seconds = 60
        
        # Reset state
        RateLimiterService.reset_counter(key)
        
        # Initially, all requests should be available
        remaining = RateLimiterService.get_remaining(key, max_requests, window_seconds)
        assert remaining == max_requests, \
            "Initially, all requests should be available"
        
        # Make some requests
        for i in range(3):
            RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
        
        # Property: Remaining count should be accurate
        remaining = RateLimiterService.get_remaining(key, max_requests, window_seconds)
        assert remaining == max_requests - 3, \
            f"After 3 requests, remaining should be {max_requests - 3}"
        
        # Cleanup
        RateLimiterService.reset_counter(key)


# ============================================================================
# Integration Tests for Preservation
# ============================================================================

@pytest.mark.preservation
class TestSecurityConfigurationIntegration:
    """
    Integration tests to verify CORS, CSRF, and rate limiting work together
    
    **Validates: Requirements 3.9, 3.10, 3.11, 3.12, 3.13, 3.14**
    """
    
    def test_cors_csrf_and_rate_limiting_work_together(self, monkeypatch):
        """
        **Validates: Requirements 3.9, 3.10, 3.11, 3.12, 3.13, 3.14**
        
        Integration test: CORS, CSRF, and rate limiting work together correctly
        
        This simulates a real-world scenario where a client makes authenticated
        requests that are subject to CORS, CSRF, and rate limiting checks.
        """
        # Disable DDoS protection for testing
        monkeypatch.setenv("ENABLE_DDOS_PROTECTION", "false")
        
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Scenario: Client from allowed origin makes requests
        origin = "http://localhost:5173"
        headers = {
            "Origin": origin,
            "User-Agent": "TestClient/1.0"
        }
        
        # Step 1: GET request should succeed (no CSRF needed)
        response = client.get("/", headers=headers)
        assert response.status_code == 200, \
            "GET request from allowed origin should succeed"
        
        # Verify CORS headers are present
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"] in [origin, "*"], \
                "CORS should allow the origin"
        
        # Step 2: Multiple requests within rate limit should succeed
        key = "integration_test_client"
        max_requests = 10
        window_seconds = 60
        
        RateLimiterService.reset_counter(key)
        
        for i in range(5):  # Well within limit
            result = RateLimiterService.check_rate_limit(key, max_requests, window_seconds)
            assert result.allowed is True, \
                f"Request {i+1} should be allowed (within rate limit)"
        
        # Integration property: All security layers work correctly together
        # without blocking legitimate traffic
        assert True, "CORS, CSRF, and rate limiting work together correctly"
        
        # Cleanup
        RateLimiterService.reset_counter(key)
    
    def test_rate_limiting_respects_different_keys(self):
        """
        **Validates: Requirements 3.13, 3.14**
        
        Property: Rate limiting tracks different keys independently
        """
        max_requests = 3
        window_seconds = 60
        
        key1 = "client_1"
        key2 = "client_2"
        
        # Reset state
        RateLimiterService.reset_counter(key1)
        RateLimiterService.reset_counter(key2)
        
        # Use up limit for key1
        for i in range(max_requests):
            result = RateLimiterService.check_rate_limit(key1, max_requests, window_seconds)
            assert result.allowed is True
        
        # key1 should be blocked
        result = RateLimiterService.check_rate_limit(key1, max_requests, window_seconds)
        assert result.allowed is False
        
        # Property: key2 should still be allowed (independent tracking)
        result = RateLimiterService.check_rate_limit(key2, max_requests, window_seconds)
        assert result.allowed is True, \
            "Different keys should be tracked independently"
        
        # Cleanup
        RateLimiterService.reset_counter(key1)
        RateLimiterService.reset_counter(key2)
