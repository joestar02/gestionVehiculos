# 🧪 Testing Guide - Vehicle Management System

## Overview

This project includes comprehensive tests to ensure code quality, security, and functionality. The test suite covers:

- **Security Tests**: Authentication, authorization, input validation, and security auditing
- **Service Tests**: Business logic and service layer functionality
- **Model Tests**: Database models and relationships
- **Integration Tests**: End-to-end application testing
- **Configuration Tests**: Application configuration and environment setup

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── test_config.py           # Configuration tests
├── test_security.py         # Security and authentication tests
├── test_services.py         # Service layer tests
├── test_models.py           # Database model tests
└── test_integration.py      # Integration tests
```

## Prerequisites

### Install Testing Dependencies

```bash
# Install development and testing dependencies
pip install -r requirements-dev.txt

# Or install individually
pip install pytest pytest-cov pytest-mock coverage faker responses
```

### Environment Setup

Make sure you have the application dependencies installed:

```bash
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```bash
# Directly with pytest (recommended)
pytest tests/ -v --color=yes
```

### Run Specific Test Categories

```bash
# Security tests only
python run_tests.py security

# Integration tests only
python -m pytest tests/test_integration.py -v

# Model tests only
python -m pytest tests/test_models.py -v
```

### Run with Coverage Report

```bash
pytest --cov=app tests/ --cov-report=html --cov-report=term-missing
```

### Run Tests with Verbose Output

```bash
python -m pytest tests/ -v --tb=short
```

## Test Categories

### 1. Configuration Tests (`test_config.py`)

Tests for application configuration:
- Environment variable handling
- Database configuration
- Security settings
- Production vs development configs

### 2. Security Tests (`test_security.py`)

Comprehensive security testing:
- Input validation and sanitization
- Authentication mechanisms
- Rate limiting functionality
- Security audit logging
- CSRF protection

### 3. Service Tests (`test_services.py`)

Business logic testing:
- Authentication service
- Input validation service
- Password hashing and verification
- User management

### 4. Model Tests (`test_models.py`)

Database model testing:
- User model functionality
- Vehicle model relationships
- Driver model properties
- Data validation

### 5. Integration Tests (`test_integration.py`)

End-to-end testing:
- Application initialization
- Database connectivity
- Security middleware
- HTTP request/response handling

## Writing New Tests

### Test File Structure

```python
import pytest
from app.services.example_service import ExampleService

class TestExampleService:
    """Test cases for ExampleService"""

    def test_example_method(self):
        """Test example method functionality"""
        # Arrange
        service = ExampleService()

        # Act
        result = service.example_method()

        # Assert
        assert result is not None

    @pytest.fixture
    def sample_data(self):
        """Fixture providing sample test data"""
        return {"key": "value"}
```

### Using Fixtures

```python
@pytest.fixture
def app():
    """Create test application"""
    from app.main import create_app
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
```

### Mocking External Dependencies

```python
from unittest.mock import patch

@patch('app.services.example_service.external_api')
def test_external_call(mock_api):
    """Test external API calls"""
    mock_api.return_value = {"result": "success"}

    service = ExampleService()
    result = service.call_external_api()

    assert result["result"] == "success"
    mock_api.assert_called_once()
```

## Security Testing Best Practices

### Testing Authentication

```python
def test_login_success(self, client):
    """Test successful login"""
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass',
        'csrf_token': 'valid_token'
    })
    assert response.status_code == 200

def test_login_rate_limiting(self, client):
    """Test rate limiting on login attempts"""
    # Make multiple rapid requests
    for i in range(10):
        response = client.post('/auth/login', data={...})

    # Should eventually be rate limited
    assert response.status_code == 429  # Too Many Requests
```

### Testing Input Validation

```python
def test_input_sanitization(self):
    """Test input sanitization"""
    validator = InputValidator()

    # Test XSS prevention
    malicious_input = "<script>alert('xss')</script>"
    result = validator.sanitize_string(malicious_input)
    assert "<script>" not in result

    # Test SQL injection prevention
    sql_input = "'; DROP TABLE users; --"
    result = validator.sanitize_string(sql_input)
    assert "DROP TABLE" not in result
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
        - name: Install dependencies
            run: |
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                pip install -r requirements-dev.txt
        - name: Run tests
            run: pytest tests/ -v --color=yes
```

## Debugging Tests

### Common Issues and Solutions

1. **Database Connection Errors**
   ```bash
   # Ensure test database is properly configured
   export FLASK_ENV=testing
   ```

2. **Import Errors**
   ```bash
   # Install all dependencies
   pip install -r requirements.txt -r requirements-dev.txt
   ```

3. **CSRF Token Errors**
   ```python
   # Include CSRF token in POST requests
   response = client.post('/auth/login', data={
       'username': 'test',
       'password': 'test',
       'csrf_token': response.csrf_token  # Get from previous request
   })
   ```

## Coverage Goals

Aim for:
- **Overall Coverage**: > 80%
- **Security Code**: > 90%
- **Critical Paths**: > 95%

## Contributing

When adding new features:

1. Write tests for new functionality
2. Ensure security tests cover new endpoints
3. Update this documentation if needed
4. Run full test suite before submitting PR

---

For questions or issues with testing, please check the test files for examples or create an issue in the project repository.
