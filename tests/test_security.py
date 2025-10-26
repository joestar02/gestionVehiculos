"""
Security tests for authentication, authorization, and input validation
"""
import pytest
import re
from unittest.mock import patch, MagicMock
from app.services.input_validation_service import InputValidator
from app.services.security_audit_service import SecurityAudit
from app.controllers.auth_controller import failed_attempts


class TestInputValidation:
    """Test input validation service"""

    def test_sanitize_string(self):
        """Test string sanitization"""
        # Normal string
        result = InputValidator.sanitize_string("  test string  ")
        assert result == "test string"

        # Long string should be truncated
        long_string = "a" * 300
        result = InputValidator.sanitize_string(long_string, 100)
        assert len(result) == 100

        # Empty string
        result = InputValidator.sanitize_string("")
        assert result == ""

        # None value
        result = InputValidator.sanitize_string(None)
        assert result == ""

    def test_validate_email(self):
        """Test email validation"""
        # Valid emails
        valid, result = InputValidator.validate_email("test@example.com")
        assert valid is True
        assert result == "test@example.com"

        # Invalid emails
        invalid, message = InputValidator.validate_email("invalid-email")
        assert invalid is False

        invalid, message = InputValidator.validate_email("")
        assert invalid is False

    def test_validate_username(self):
        """Test username validation"""
        # Valid usernames
        valid, result = InputValidator.validate_username("testuser")
        assert valid is True

        valid, result = InputValidator.validate_username("test_user")
        assert valid is True

        valid, result = InputValidator.validate_username("test-user")
        assert valid is True

        # Invalid usernames
        invalid, message = InputValidator.validate_username("")
        assert invalid is False

        invalid, message = InputValidator.validate_username("ab")  # Too short
        assert invalid is False

        invalid, message = InputValidator.validate_username("a" * 51)  # Too long
        assert invalid is False

        invalid, message = InputValidator.validate_username("test@user!")  # Invalid chars
        assert invalid is False

    def test_validate_password(self):
        """Test password validation"""
        # Valid passwords
        valid, message = InputValidator.validate_password("SecurePass123!")
        assert valid is True

        # Invalid passwords - too short
        invalid, message = InputValidator.validate_password("Short1!")
        assert invalid is False

        # Invalid passwords - no uppercase
        invalid, message = InputValidator.validate_password("lowercase123!")
        assert invalid is False

        # Invalid passwords - no lowercase
        invalid, message = InputValidator.validate_password("UPPERCASE123!")
        assert invalid is False

        # Invalid passwords - no numbers
        invalid, message = InputValidator.validate_password("NoNumbers!")
        assert invalid is False

        # Invalid passwords - no special chars
        invalid, message = InputValidator.validate_password("NoSpecial123")
        assert invalid is False

    def test_validate_phone(self):
        """Test phone validation"""
        # Valid phones
        valid, result = InputValidator.validate_phone("1234567890")
        assert valid is True

        # Empty phone (should be valid as optional)
        valid, result = InputValidator.validate_phone("")
        assert valid is True

        # Invalid phones - too short
        invalid, message = InputValidator.validate_phone("123")
        assert invalid is False

        # Invalid phones - too long
        invalid, message = InputValidator.validate_phone("1" * 20)
        assert invalid is False

    def test_validate_license_plate(self):
        """Test license plate validation"""
        # Valid plates
        valid, result = InputValidator.validate_license_plate("ABC1234")
        assert valid is True

        valid, result = InputValidator.validate_license_plate("1234ABC")
        assert valid is True

        # Invalid plates
        invalid, message = InputValidator.validate_license_plate("")
        assert invalid is False

        invalid, message = InputValidator.validate_license_plate("INVALID")
        assert invalid is False

    def test_validate_document_number(self):
        """Test document number validation"""
        # Valid document numbers
        valid, result = InputValidator.validate_document_number("12345678A")
        assert valid is True

        # Invalid document numbers
        invalid, message = InputValidator.validate_document_number("")
        assert invalid is False

        invalid, message = InputValidator.validate_document_number("1234567A")  # Too short
        assert invalid is False

        invalid, message = InputValidator.validate_document_number("123456789A")  # Too long
        assert invalid is False


class TestSecurityAudit:
    """Test security audit service"""

    def test_log_authentication_attempt(self):
        """Test authentication logging"""
        with patch('app.services.security_audit_service.security_logger') as mock_logger:
            SecurityAudit.log_authentication_attempt("testuser", True, "192.168.1.1")
            mock_logger.info.assert_called_once()
            call_args = mock_logger.info.call_args[0][0]
            assert "SUCCESS" in call_args
            assert "testuser" in call_args
            assert "192.168.1.1" in call_args

    def test_log_suspicious_activity(self):
        """Test suspicious activity logging"""
        with patch('app.services.security_audit_service.security_logger') as mock_logger:
            SecurityAudit.log_suspicious_activity("Suspicious login", {"reason": "too many attempts"})
            mock_logger.warning.assert_called_once()

    def test_log_security_event(self):
        """Test general security event logging"""
        with patch('app.services.security_audit_service.security_logger') as mock_logger:
            SecurityAudit.log_security_event("Test event", "INFO", {"key": "value"})
            mock_logger.info.assert_called_once()


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_failed_attempts_tracking(self):
        """Test failed login attempts tracking"""
        # Clear any existing attempts
        failed_attempts.clear()

        # Simulate failed login attempts
        client_ip = "192.168.1.100"

        # Add some failed attempts
        for i in range(3):
            if client_ip not in failed_attempts:
                failed_attempts[client_ip] = []
            failed_attempts[client_ip].append(1000000000 + i)  # Mock timestamps

        # Check that attempts are tracked
        assert client_ip in failed_attempts
        assert len(failed_attempts[client_ip]) == 3

        # Test cleanup of old attempts (simulated)
        current_time = 1000000100  # After the attempts
        failed_attempts[client_ip] = [
            attempt_time for attempt_time in failed_attempts[client_ip]
            if current_time - attempt_time < 3600  # Keep only recent ones
        ]

        # All attempts should still be there since they're within the hour
        assert len(failed_attempts[client_ip]) == 3
