"""Flask application factory"""
from flask import Flask, g, request, jsonify
from app.core.config import get_config
from app.extensions import init_extensions
from app.services.security_audit_service import SecurityAudit
import time

def create_app(config_name=None):
    """Create and configure Flask application"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Request logging middleware
    @app.before_request
    def log_request_start():
        """Log the start of each request"""
        g.request_start_time = time.time()
        g.session_id = f"{time.time()}_{id(g)}"  # Simple session ID for tracking

    @app.after_request
    def log_request_end(response):
        """Log the completion of each request"""
        if hasattr(g, 'request_start_time'):
            duration_ms = (time.time() - g.request_start_time) * 1000

            # Skip logging for static files and health checks
            if not request.path.startswith('/static') and request.path not in ['/favicon.ico']:
                SecurityAudit.log_api_access(
                    endpoint=request.endpoint or 'unknown',
                    method=request.method,
                    response_code=response.status_code,
                    duration_ms=duration_ms,
                    details={
                        'path': request.path,
                        'query_string': request.query_string.decode('utf-8') if request.query_string else '',
                        'content_length': response.content_length,
                        'response_content_type': response.content_type
                    }
                )

        return response

    # Add CSP headers to allow source maps
    @app.after_request
    def add_security_headers(response):
        # Add CSP header allowing source maps from jsdelivr and web workers
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net blob:; "
            "worker-src 'self' blob:; "
            "child-src 'self' blob:; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data: cdn.jsdelivr.net; "
            "font-src 'self' cdn.jsdelivr.net; "
            "connect-src 'self' cdn.jsdelivr.net; "
            "frame-src 'self'; "
            "object-src 'none';"
        )
        response.headers['Content-Security-Policy'] = csp_policy
        return response

    # Load configuration
    if config_name is None:
        config_class = get_config()
    else:
        from app.core.config import config
        config_class = config[config_name]

    # Instantiate config and load into app
    config_instance = config_class()
    app.config.from_object(config_instance)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register context processors
    register_context_processors(app)

    return app

def register_blueprints(app):
    """Register Flask blueprints"""
    from app.controllers.auth_controller import auth_bp
    from app.controllers.vehicle_controller import vehicle_bp
    from app.controllers.driver_controller import driver_bp
    from app.controllers.reservation_controller import reservation_bp
    from app.controllers.organization_controller import organization_bp
    from app.controllers.maintenance_controller import maintenance_bp
    from app.controllers.compliance_controller import compliance_bp
    from app.controllers.pickup_controller import pickup_bp
    from app.controllers.provider_controller import provider_bp
    from app.controllers.assignment_controller import assignment_bp
    from app.controllers.main_controller import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(vehicle_bp, url_prefix='/vehicles')
    app.register_blueprint(driver_bp, url_prefix='/drivers')
    app.register_blueprint(reservation_bp, url_prefix='/reservations')
    app.register_blueprint(organization_bp, url_prefix='/organizations')
    app.register_blueprint(maintenance_bp, url_prefix='/maintenance')
    app.register_blueprint(compliance_bp, url_prefix='/compliance')
    app.register_blueprint(pickup_bp, url_prefix='/pickups')
    app.register_blueprint(provider_bp, url_prefix='/providers')
    app.register_blueprint(assignment_bp, url_prefix='/assignments')

def register_error_handlers(app):
    """Register error handlers"""
    from flask import render_template
    from app.utils.error_helpers import log_exception

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from app.extensions import db
        db.session.rollback()
        # Log and generate error id
        err_id = log_exception(error, __name__)
        return render_template('errors/500.html', error_id=err_id), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(429)
    def too_many_requests_error(error):
        return render_template('errors/429.html'), 429

    @app.errorhandler(400)
    def forbidden_error(error):
        return render_template('errors/400.html'), 400    

def register_context_processors(app):
    """Register context processors"""
    from datetime import datetime
    # Register template filters (i18n)
    try:
        from app.utils.i18n import translate
        app.jinja_env.filters['t'] = translate
    except Exception:
        # If the module isn't available, ignore — templates will show raw values
        pass

    @app.context_processor
    def inject_config():
        return {
            'app_name': app.config.get('PROJECT_NAME', 'Gestión de Vehículos'),
            'app_version': app.config.get('VERSION', '1.0.0'),
            'now': datetime.now(),
            'datetime': datetime
        }
