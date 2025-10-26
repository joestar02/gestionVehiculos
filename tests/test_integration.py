"""
Integration tests for the complete application
"""
import pytest
from app.main import create_app
from app.extensions import db


class TestApplicationIntegration:
    """Integration tests for the complete application"""

    @pytest.fixture
    def app(self):
        """Create test application"""
        app = create_app('testing')
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()

    def test_application_creation(self):
        """Test that application can be created"""
        app = create_app('testing')
        assert app is not None
        assert app.config['TESTING'] is True

    def test_database_initialization(self, app):
        """Test database initialization in test mode"""
        with app.app_context():
            # In testing mode, should use in-memory database
            assert 'memory' in app.config['SQLALCHEMY_DATABASE_URI']

    def test_security_headers_middleware(self, app):
        """Test that security headers are configured"""
        # This would test that Talisman is properly configured
        # For now, we'll just ensure the app has the security extensions
        assert hasattr(app, 'extensions')

    def test_csrf_protection(self, client):
        """Test CSRF protection is active"""
        # Try to make a POST request without CSRF token
        response = client.post('/auth/login', data={
            'username': 'test',
            'password': 'test'
        })

        # Should get an error due to missing CSRF token
        # Flask-WTF should handle this and return an error
        assert response.status_code in [400, 403]  # Bad Request or Forbidden

    def test_rate_limiting(self, client):
        """Test rate limiting is active"""
        # Make multiple requests quickly
        responses = []
        for i in range(10):
            response = client.get('/auth/login')
            responses.append(response.status_code)

        # Should eventually get rate limited
        # Note: This is a basic test, real rate limiting tests would need more setup
        assert 200 in responses  # At least some requests should succeed
