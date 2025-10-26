"""Controllers layer for handling HTTP requests"""

# Import all controller blueprints for easy registration
from .auth_controller import auth_bp
from .vehicle_controller import vehicle_bp
from .driver_controller import driver_bp
from .reservation_controller import reservation_bp
from .organization_controller import organization_bp
from .maintenance_controller import maintenance_bp
from .compliance_controller import compliance_bp
from .provider_controller import provider_bp
from .assignment_controller import assignment_bp
from .pickup_controller import pickup_bp
from .main_controller import main_bp

__all__ = [
    'auth_bp', 'vehicle_bp', 'driver_bp', 'reservation_bp',
    'organization_bp', 'maintenance_bp', 'compliance_bp',
    'provider_bp', 'assignment_bp', 'pickup_bp', 'main_bp'
]
