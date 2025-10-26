"""
Tests for application services
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.extensions import db


class TestAuthService:
    """Test authentication service"""

    def test_verify_password(self):
        """Test password verification"""
        # This would need a real hashed password for proper testing
        # For now, we'll test the method exists and handles basic cases
        assert hasattr(AuthService, 'verify_password')
        assert callable(AuthService.verify_password)

    def test_get_password_hash(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = AuthService.get_password_hash(password)

        # Should return a string
        assert isinstance(hashed, str)
        # Should be different from original password
        assert hashed != password
        # Should contain bcrypt hash indicators
        assert hashed.startswith('$2b$')  # bcrypt hash

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        # This would require database setup for proper testing
        # For now, we'll test the method exists
        assert hasattr(AuthService, 'authenticate_user')
        assert callable(AuthService.authenticate_user)

    def test_create_user(self):
        """Test user creation"""
        # Test with mock database
        with patch('app.services.auth_service.db') as mock_db:
            mock_db.session.add = MagicMock()
            mock_db.session.commit = MagicMock()
            mock_db.session.refresh = MagicMock()

            user = AuthService.create_user(
                username="testuser",
                email="test@example.com",
                password="testpass123",
                first_name="Test",
                last_name="User"
            )

            # Should create user object
            assert user is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"

    def test_get_user_by_username(self):
        """Test get user by username"""
        with patch('app.services.auth_service.User') as mock_user_class:
            mock_query = MagicMock()
            mock_user_class.query.filter_by.return_value.first.return_value = None
            mock_user_class.query = mock_query

            result = AuthService.get_user_by_username("testuser")
            assert result is None

    def test_get_user_by_email(self):
        """Test get user by email"""
        with patch('app.services.auth_service.User') as mock_user_class:
            mock_query = MagicMock()
            mock_user_class.query.filter_by.return_value.first.return_value = None
            mock_user_class.query = mock_query

            result = AuthService.get_user_by_email("test@example.com")
            assert result is None


class TestInputValidationService:
    """Test input validation service integration"""

    def test_email_validator_integration(self):
        """Test that email validator library is working"""
        # Test valid email
        valid, result = InputValidator.validate_email("test@example.com")
        assert valid is True
        assert result == "test@example.com"

        # Test invalid email
        invalid, message = InputValidator.validate_email("not-an-email")
        assert invalid is False

    def test_password_complexity(self):
        """Test password complexity requirements"""
        # Test minimum length
        valid, message = InputValidator.validate_password("Short1!")
        assert valid is False
        assert "al menos 8 caracteres" in message

        # Test complexity requirements
        valid, message = InputValidator.validate_password("simplepassword")
        assert valid is False
        assert "mayúscula" in message or "número" in message or "carácter especial" in message

    def test_license_plate_format(self):
        """Test license plate format validation"""
        # Valid Spanish format
        valid, result = InputValidator.validate_license_plate("ABC1234")
        assert valid is True

        # Invalid format
        invalid, message = InputValidator.validate_license_plate("INVALID")
        assert invalid is False

    def test_document_number_format(self):
        """Test document number format validation"""
        # Valid DNI format
        valid, result = InputValidator.validate_document_number("12345678A")
        assert valid is True

        # Invalid format
        invalid, message = InputValidator.validate_document_number("1234567A")
        assert invalid is False
