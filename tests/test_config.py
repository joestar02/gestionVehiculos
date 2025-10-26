"""
Test de configuración de seguridad y aplicación
"""
import os
import pytest
import importlib
from app.core import config


class TestConfiguration:
    """Test configuration classes"""

    def test_base_config(self):
        """Test base configuration"""
        # Import fresh config to get current environment variables
        importlib.reload(config)
        from app.core.config import Config

        config_instance = Config()

        # Test secret key generation
        assert config_instance.SECRET_KEY is not None
        assert len(config_instance.SECRET_KEY) >= 32  # Should be at least 32 chars for security

        # Test database configuration
        assert hasattr(config_instance, 'SQLALCHEMY_DATABASE_URI')
        assert config_instance.USE_SQLITE is True  # Default should be SQLite

    def test_development_config(self):
        """Test development configuration"""
        importlib.reload(config)
        from app.core.config import DevelopmentConfig

        config_instance = DevelopmentConfig()

        assert config_instance.DEBUG is True
        assert config_instance.TESTING is False

    def test_production_config(self):
        """Test production configuration"""
        importlib.reload(config)
        from app.core.config import ProductionConfig

        config_instance = ProductionConfig()

        assert config_instance.DEBUG is False
        assert config_instance.TESTING is False

    def test_testing_config(self):
        """Test testing configuration"""
        importlib.reload(config)
        from app.core.config import TestingConfig

        config_instance = TestingConfig()

        assert config_instance.DEBUG is True
        assert config_instance.TESTING is True
        # Testing config uses SQLite with a specific path, not memory
        assert 'sqlite:///' in config_instance.SQLALCHEMY_DATABASE_URI

    def test_environment_variable_override(self):
        """Test environment variable overrides"""
        # Set environment variables BEFORE importing
        original_secret = os.environ.get('SECRET_KEY')
        original_sqlite = os.environ.get('USE_SQLITE')

        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['USE_SQLITE'] = 'True'  # Keep SQLite to avoid PostgreSQL issues

        try:
            # Need to reload the module to pick up new environment variables
            importlib.reload(config)
            from app.core.config import Config

            config_instance = Config()
            # The secret key should be overridden by environment variable
            assert config_instance.SECRET_KEY == 'test-secret-key'
            assert config_instance.USE_SQLITE is True

        finally:
            # Clean up environment variables
            if original_secret is not None:
                os.environ['SECRET_KEY'] = original_secret
            else:
                os.environ.pop('SECRET_KEY', None)

            if original_sqlite is not None:
                os.environ['USE_SQLITE'] = original_sqlite
            else:
                os.environ.pop('USE_SQLITE', None)

    def test_postgresql_config_validation(self):
        """Test PostgreSQL configuration validation"""
        # Set environment variables BEFORE importing
        original_sqlite = os.environ.get('USE_SQLITE')
        original_password = os.environ.get('POSTGRES_PASSWORD')

        os.environ['USE_SQLITE'] = 'False'
        os.environ['POSTGRES_PASSWORD'] = 'test-password'

        try:
            # Need to reload the module to pick up new environment variables
            importlib.reload(config)
            from app.core.config import Config

            # Should work now with POSTGRES_PASSWORD set
            config_instance = Config()
            assert config_instance.USE_SQLITE is False
            assert 'postgresql://' in config_instance.SQLALCHEMY_DATABASE_URI

        finally:
            if original_sqlite is not None:
                os.environ['USE_SQLITE'] = original_sqlite
            else:
                os.environ.pop('USE_SQLITE', None)

            if original_password is not None:
                os.environ['POSTGRES_PASSWORD'] = original_password
            else:
                os.environ.pop('POSTGRES_PASSWORD', None)
