import os
import secrets
from datetime import timedelta

class Config:
    """Base configuration"""
    PROJECT_NAME = "Gestión de Flota de Vehículos"
    VERSION = "1.0.0"

    # Flask
    # Generate a secure secret key if not provided via environment
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # Database - SQLite por defecto para desarrollo
    USE_SQLITE = os.environ.get('USE_SQLITE', 'True').lower() == 'true'
    SQLITE_DB_PATH = os.environ.get('SQLITE_DB_PATH', 'gestion_vehiculos.db')

    # PostgreSQL (opcional) - valores por defecto más seguros
    POSTGRES_SERVER = os.environ.get('POSTGRES_SERVER', 'localhost')
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')  # No default password
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'gestion_vehiculos')

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads (default locations and limits)
    INSURANCE_UPLOAD_FOLDER = os.environ.get('INSURANCE_UPLOAD_FOLDER', os.path.join('static', 'uploads', 'insurances'))
    INSURANCE_ALLOWED_EXTENSIONS = {'.pdf'}
    INSURANCE_MAX_BYTES = int(os.environ.get('INSURANCE_MAX_BYTES', 5 * 1024 * 1024))  # 5 MB default

    # Security - valores más seguros
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 1  # 1 day instead of 8 days
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    # Cookie settings can be overridden via environment variables for flexibility
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    REMEMBER_COOKIE_SECURE = os.environ.get('REMEMBER_COOKIE_SECURE', 'False').lower() == 'true'
    REMEMBER_COOKIE_SAMESITE = os.environ.get('REMEMBER_COOKIE_SAMESITE', 'Lax')

    # First superuser - valores más seguros
    FIRST_SUPERUSER = os.environ.get('FIRST_SUPERUSER', 'admin@example.com')
    FIRST_SUPERUSER_USERNAME = os.environ.get('FIRST_SUPERUSER_USERNAME', 'admin')
    FIRST_SUPERUSER_PASSWORD = os.environ.get('FIRST_SUPERUSER_PASSWORD')  # No default password

    def __init__(self):
        # Set SQLALCHEMY_DATABASE_URI based on USE_SQLITE
        if self.USE_SQLITE:
            db_path = os.path.join(os.getcwd(), self.SQLITE_DB_PATH)
            self.SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        else:
            # Validate required environment variables for PostgreSQL
            if not self.POSTGRES_PASSWORD:
                raise ValueError("POSTGRES_PASSWORD environment variable is required when USE_SQLITE is False")
            self.SQLALCHEMY_DATABASE_URI = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
