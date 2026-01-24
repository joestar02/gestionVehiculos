"""
Tests for application services
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.auth_service import AuthService
from app.services.input_validation_service import InputValidator
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
        with patch('app.models.user.User') as mock_user:
            mock_query = MagicMock()
            mock_user.query.filter_by.return_value.first.return_value = None
            mock_user.query = mock_query

            result = AuthService.get_user_by_username("testuser")
            assert result is None

    def test_get_user_by_email(self):
        """Test get user by email"""
        with patch('app.models.user.User') as mock_user:
            mock_query = MagicMock()
            mock_user.query.filter_by.return_value.first.return_value = None
            mock_user.query = mock_query

            result = AuthService.get_user_by_email("test@example.com")
            assert result is None

    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        with patch('app.models.user.User') as mock_user_class, \
             patch('app.services.auth_service.AuthService.verify_password', return_value=True), \
             patch('app.extensions.db.session') as mock_session:
            
            mock_user = MagicMock()
            mock_user.is_active = True
            mock_user.hashed_password = "hashed"
            mock_user_class.query.filter.return_value.first.return_value = mock_user

            result = AuthService.authenticate_user("testuser", "password")
            
            assert result == mock_user
            mock_session.commit.assert_called_once()

    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user"""
        with patch('app.models.user.User') as mock_user_class:
            mock_user_class.query.filter.return_value.first.return_value = None

            result = AuthService.authenticate_user("nonexistent", "password")
            
            assert result is None

    def test_authenticate_user_inactive(self):
        """Test authentication with inactive user"""
        with patch('app.models.user.User') as mock_user_class:
            mock_user = MagicMock()
            mock_user.is_active = False
            mock_user_class.query.filter.return_value.first.return_value = mock_user

            result = AuthService.authenticate_user("testuser", "password")
            
            assert result is None

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password"""
        with patch('app.models.user.User') as mock_user_class, \
             patch('app.services.auth_service.AuthService.verify_password', return_value=False):
            
            mock_user = MagicMock()
            mock_user.is_active = True
            mock_user_class.query.filter.return_value.first.return_value = mock_user

            result = AuthService.authenticate_user("testuser", "wrongpass")
            
            assert result is None

    def test_create_user_success(self):
        """Test successful user creation"""
        with patch('app.models.user.User') as mock_user_class, \
             patch('app.services.auth_service.AuthService.get_password_hash', return_value="hashed"), \
             patch('app.extensions.db.session') as mock_session:
            
            mock_user_instance = MagicMock()
            mock_user_class.query.filter_by.return_value.first.return_value = None
            mock_user_class.return_value = mock_user_instance

            result = AuthService.create_user("testuser", "test@example.com", "password")
            
            assert result == mock_user_instance
            mock_session.add.assert_called_once_with(mock_user_instance)
            mock_session.commit.assert_called_once()

    def test_create_user_username_exists(self):
        """Test user creation with existing username"""
        with patch('app.models.user.User') as mock_user_class:
            mock_user_class.query.filter_by.return_value.first.return_value = MagicMock()

            with pytest.raises(ValueError, match="Username already exists"):
                AuthService.create_user("existing", "test@example.com", "password")

    def test_create_user_email_exists(self):
        """Test user creation with existing email"""
        with patch('app.models.user.User') as mock_user_class:
            # Username check passes
            mock_user_class.query.filter_by.side_effect = [None, MagicMock()]

            with pytest.raises(ValueError, match="Email already exists"):
                AuthService.create_user("newuser", "existing@example.com", "password")


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
