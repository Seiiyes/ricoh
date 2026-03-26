"""
Tests for DDoS Protection Middleware
"""
import pytest
from fastapi.testclient import TestClient
from middleware.ddos_protection import (
    IPBlockList,
    BurstDetector,
    DDoSProtectionConfig,
    get_ddos_stats,
    cleanup_ddos_data
)
from datetime import datetime, timedelta, timezone


@pytest.mark.unit
class TestIPBlockList:
    """Test suite for IP blocking functionality"""
    
    def test_block_and_check_ip(self):
        """Test blocking and checking IP"""
        test_ip = "192.168.1.100"
        
        # Block IP
        IPBlockList.block_ip(test_ip, duration_seconds=60)
        
        # Verify it's blocked
        assert IPBlockList.is_blocked(test_ip) is True
        
        # Cleanup
        IPBlockList.unblock_ip(test_ip)
    
    def test_unblock_ip(self):
        """Test unblocking IP"""
        test_ip = "192.168.1.101"
        
        # Block and then unblock
        IPBlockList.block_ip(test_ip, duration_seconds=60)
        IPBlockList.unblock_ip(test_ip)
        
        # Verify it's not blocked
        assert IPBlockList.is_blocked(test_ip) is False
    
    def test_expired_block(self):
        """Test that expired blocks are automatically removed"""
        test_ip = "192.168.1.102"
        
        # Block for 1 second
        IPBlockList.block_ip(test_ip, duration_seconds=1)
        
        # Should be blocked immediately
        assert IPBlockList.is_blocked(test_ip) is True
        
        # Wait for expiration
        import time
        time.sleep(1.1)
        
        # Should be unblocked now
        assert IPBlockList.is_blocked(test_ip) is False
    
    def test_get_blocked_ips(self):
        """Test getting list of blocked IPs"""
        test_ip1 = "192.168.1.103"
        test_ip2 = "192.168.1.104"
        
        # Block two IPs
        IPBlockList.block_ip(test_ip1, duration_seconds=60)
        IPBlockList.block_ip(test_ip2, duration_seconds=60)
        
        # Get blocked IPs
        blocked = IPBlockList.get_blocked_ips()
        
        # Verify both are in the list
        assert test_ip1 in blocked
        assert test_ip2 in blocked
        
        # Cleanup
        IPBlockList.unblock_ip(test_ip1)
        IPBlockList.unblock_ip(test_ip2)
    
    def test_cleanup_expired(self):
        """Test cleanup of expired blocks"""
        test_ip = "192.168.1.105"
        
        # Block for 1 second
        IPBlockList.block_ip(test_ip, duration_seconds=1)
        
        # Wait for expiration
        import time
        time.sleep(1.1)
        
        # Run cleanup
        cleaned = IPBlockList.cleanup_expired()
        
        # Should have cleaned at least 1
        assert cleaned >= 1
        
        # IP should not be in blocked list
        assert IPBlockList.is_blocked(test_ip) is False


@pytest.mark.unit
class TestBurstDetector:
    """Test suite for burst attack detection"""
    
    def test_normal_traffic(self):
        """Test that normal traffic is not flagged"""
        test_ip = "192.168.1.200"
        
        # Simulate normal traffic (below threshold)
        for _ in range(10):
            is_burst = BurstDetector.record_request(test_ip)
            assert is_burst is False
    
    def test_burst_detection(self):
        """Test that burst attacks are detected"""
        test_ip = "192.168.1.201"
        
        # Simulate burst attack (above threshold)
        is_burst = False
        for _ in range(DDoSProtectionConfig.BURST_THRESHOLD + 1):
            is_burst = BurstDetector.record_request(test_ip)
        
        # Should detect burst
        assert is_burst is True
    
    def test_cleanup_old_records(self):
        """Test cleanup of old burst records"""
        test_ip = "192.168.1.202"
        
        # Record some requests
        for _ in range(5):
            BurstDetector.record_request(test_ip)
        
        # Cleanup
        BurstDetector.cleanup_old_records(max_age_seconds=1)
        
        # Wait and cleanup again
        import time
        time.sleep(1.1)
        BurstDetector.cleanup_old_records(max_age_seconds=1)
        
        # Should have cleaned up


@pytest.mark.unit
class TestDDoSStats:
    """Test suite for DDoS statistics"""
    
    def test_get_ddos_stats(self):
        """Test getting DDoS statistics"""
        stats = get_ddos_stats()
        
        # Verify structure
        assert "blocked_ips" in stats
        assert "blocked_count" in stats
        assert "config" in stats
        
        # Verify config
        config = stats["config"]
        assert "global_rate_limit" in config
        assert "burst_threshold" in config
        assert "block_duration" in config
    
    def test_cleanup_ddos_data(self):
        """Test cleanup of DDoS data"""
        result = cleanup_ddos_data()
        
        # Verify structure
        assert "blocked_ips_cleaned" in result
        assert "rate_limit_counters_cleaned" in result
        
        # Values should be non-negative
        assert result["blocked_ips_cleaned"] >= 0
        assert result["rate_limit_counters_cleaned"] >= 0


@pytest.mark.integration
class TestDDoSProtectionIntegration:
    """Integration tests for DDoS protection"""
    
    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are present"""
        response = client.get("/")
        
        # Verify headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    def test_whitelist_bypass(self, client):
        """Test that whitelisted IPs bypass rate limiting"""
        # Localhost should be whitelisted
        # Make many requests quickly
        for _ in range(150):  # More than global limit
            response = client.get("/")
            # Should not get rate limited
            assert response.status_code != 429
    
    def test_payload_size_limit(self, client):
        """Test that large payloads are rejected"""
        # Create a large payload (> 10MB)
        large_data = "x" * (11 * 1024 * 1024)  # 11 MB
        
        response = client.post(
            "/auth/login",
            json={"username": "test", "password": large_data}
        )
        
        # Should be rejected (but might fail at validation first)
        # This test documents expected behavior
        assert response.status_code in [413, 422]


@pytest.mark.unit
class TestDDoSConfiguration:
    """Test suite for DDoS configuration"""
    
    def test_config_values(self):
        """Test that configuration values are reasonable"""
        # Global rate limit should be positive
        assert DDoSProtectionConfig.GLOBAL_RATE_LIMIT > 0
        assert DDoSProtectionConfig.GLOBAL_RATE_WINDOW > 0
        
        # Burst detection should be configured
        assert DDoSProtectionConfig.BURST_THRESHOLD > 0
        assert DDoSProtectionConfig.BURST_WINDOW > 0
        
        # Block duration should be reasonable
        assert DDoSProtectionConfig.BLOCK_DURATION > 0
        
        # Payload size should be reasonable
        assert DDoSProtectionConfig.MAX_PAYLOAD_SIZE > 0
    
    def test_endpoint_limits(self):
        """Test that endpoint limits are configured"""
        # Should have limits for critical endpoints
        assert "/auth/login" in DDoSProtectionConfig.ENDPOINT_LIMITS
        assert "/auth/refresh" in DDoSProtectionConfig.ENDPOINT_LIMITS
        
        # Limits should be tuples of (limit, window)
        for endpoint, (limit, window) in DDoSProtectionConfig.ENDPOINT_LIMITS.items():
            assert limit > 0
            assert window > 0
    
    def test_whitelist_ips(self):
        """Test that whitelist contains localhost"""
        # Should include localhost
        assert "127.0.0.1" in DDoSProtectionConfig.WHITELIST_IPS
        assert "::1" in DDoSProtectionConfig.WHITELIST_IPS
