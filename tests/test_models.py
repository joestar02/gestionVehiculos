"""
Tests for application models
"""
import pytest
from app.models.user import User, UserRole
from app.models.vehicle import Vehicle
from app.models.driver import Driver


class TestUserModel:
    """Test User model"""

    def test_user_creation(self):
        """Test user object creation"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            first_name="Test",
            last_name="User"
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashedpassword"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.role == UserRole.VIEWER  # Default role
        assert user.is_active is True  # Default active
        assert user.is_superuser is False  # Default not superuser

    def test_user_full_name_property(self):
        """Test full name property"""
        # User with both names
        user1 = User(first_name="John", last_name="Doe")
        assert user1.full_name == "John Doe"

        # User with only first name
        user2 = User(first_name="John", last_name=None)
        assert user2.full_name == "John"

        # User with only last name
        user3 = User(first_name=None, last_name="Doe")
        assert user3.full_name == "Doe"

        # User with no names (fallback to username)
        user4 = User(username="testuser")
        assert user4.full_name == "testuser"

    def test_user_get_id(self):
        """Test get_id method for Flask-Login"""
        user = User(id=123)
        assert user.get_id() == "123"

    def test_user_role_enum(self):
        """Test user role enum"""
        # Test all roles exist
        assert UserRole.ADMIN == "admin"
        assert UserRole.FLEET_MANAGER == "fleet_manager"
        assert UserRole.OPERATIONS_MANAGER == "operations_manager"
        assert UserRole.DRIVER == "driver"
        assert UserRole.VIEWER == "viewer"

    def test_user_repr(self):
        """Test user string representation"""
        user = User(username="testuser", email="test@example.com")
        repr_str = repr(user)
        assert "testuser" in repr_str
        assert "test@example.com" in repr_str


class TestVehicleModel:
    """Test Vehicle model"""

    def test_vehicle_creation(self):
        """Test vehicle object creation"""
        vehicle = Vehicle(
            license_plate="ABC1234",
            make="Toyota",
            model="Corolla",
            year=2020,
            color="White"
        )

        assert vehicle.license_plate == "ABC1234"
        assert vehicle.make == "Toyota"
        assert vehicle.model == "Corolla"
        assert vehicle.year == 2020
        assert vehicle.color == "White"

    def test_vehicle_repr(self):
        """Test vehicle string representation"""
        vehicle = Vehicle(license_plate="ABC1234", make="Toyota", model="Corolla")
        repr_str = repr(vehicle)
        assert "ABC1234" in repr_str
        assert "Toyota" in repr_str


class TestDriverModel:
    """Test Driver model"""

    def test_driver_creation(self):
        """Test driver object creation"""
        driver = Driver(
            document_number="12345678A",
            first_name="John",
            last_name="Doe",
            phone="123456789"
        )

        assert driver.document_number == "12345678A"
        assert driver.first_name == "John"
        assert driver.last_name == "Doe"
        assert driver.phone == "123456789"

    def test_driver_full_name_property(self):
        """Test driver full name property"""
        driver = Driver(first_name="John", last_name="Doe")
        assert driver.full_name == "John Doe"
