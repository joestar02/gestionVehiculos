"""Flask extensions initialization"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
csrf = CSRFProtect()

def init_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # Initialize database auditing
    from app.services.database_audit_service import init_database_logging
    init_database_logging(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))

    # Configure security headers with Talisman
    # Only force HTTPS in production, allow HTTP in development
    # Configure cookie and Talisman behavior depending on debug/production
    # Ensure session cookies are not marked 'Secure' when running without HTTPS (development)
    # This prevents browsers from refusing to send the session cookie over plain HTTP which
    # would cause server-side CSRF validation to fail (token missing on POST).
    app.config.setdefault('SESSION_COOKIE_SECURE', not app.debug)
    app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config.setdefault('REMEMBER_COOKIE_SECURE', not app.debug)
    app.config.setdefault('REMEMBER_COOKIE_SAMESITE', 'Lax')

    # Only force HTTPS in production; explicitly pass force_https/session_cookie_secure to Talisman
    talisman = Talisman(app, force_https=not app.debug, session_cookie_secure=not app.debug)

    # Configure Content Security Policy and other security headers
    talisman.content_security_policy = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            'https://cdn.jsdelivr.net',
            "'unsafe-inline'"  # Required for Bootstrap JS
        ],
        'style-src': [
            "'self'",
            'https://cdn.jsdelivr.net',
            'https://fonts.googleapis.com',
            "'unsafe-inline'"
        ],
        'font-src': [
            "'self'",
            'https://cdn.jsdelivr.net',
            'https://fonts.gstatic.com',
            'data:'  # Required for some icon fonts
        ],
        'img-src': [
            "'self'",
            'data:',
            'https:'
        ],
        'connect-src': "'self'"
    }

    # Configure other security headers
    talisman.frame_options = 'DENY'
    talisman.xss_protection = {'mode': 'block'}
    talisman.referrer_policy = 'strict-origin-when-cross-origin'
    talisman.feature_policy = {
        'camera': "'none'",
        'microphone': "'none'",
        'geolocation': "'none'",
        'payment': "'none'"
    }
