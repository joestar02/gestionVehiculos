from functools import wraps
from flask import abort, flash, request
from flask_login import current_user
from app.models.user import UserRole
from app.models.permission import Permission, RolePermission
from app.extensions import db
from app.services.security_audit_service import SecurityAudit
import time

def audit_operation(operation_type: str, resource_type: str):
    """Decorator to log CRUD operations with detailed information"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            # Extract resource ID from kwargs or args if possible
            resource_id = kwargs.get('id') or kwargs.get('vehicle_id') or kwargs.get('reservation_id') or str(args[0] if args else 'unknown')

            # Get old values for updates/deletes if possible
            old_values = None
            if operation_type.upper() in ['UPDATE', 'DELETE']:
                try:
                    # This would need to be customized per model/service
                    # For now, we'll log that we attempted to get old values
                    old_values = {'attempted_capture': True}
                except:
                    pass

            try:
                result = f(*args, **kwargs)

                # Log successful operation
                SecurityAudit.log_data_operation(
                    operation=operation_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    old_values=old_values,
                    details={
                        'operation_duration_ms': round((time.time() - start_time) * 1000, 2),
                        'endpoint': request.endpoint if request else 'unknown',
                        'method': request.method if request else 'unknown'
                    }
                )

                return result

            except Exception as e:
                # Log failed operation
                SecurityAudit.log_data_operation(
                    operation=operation_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details={
                        'operation_duration_ms': round((time.time() - start_time) * 1000, 2),
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'endpoint': request.endpoint if request else 'unknown',
                        'method': request.method if request else 'unknown'
                    }
                )
                raise

        return decorated_function
    return decorator

def has_permission(permission_name):
    """Decorator to check if current user has a specific permission with audit logging"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            if not current_user.is_authenticated:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=permission_name,
                    granted=False,
                    details={'reason': 'not_authenticated'}
                )
                abort(401)

            # Superuser has all permissions
            if current_user.is_superuser:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=permission_name,
                    granted=True,
                    details={'reason': 'superuser_access', 'user_role': 'superuser'}
                )
                return f(*args, **kwargs)

            # Check role-based permissions
            role_permissions = db.session.query(Permission.name).join(RolePermission).filter(
                RolePermission.role == current_user.role.value
            ).all()

            user_permissions = [p[0] for p in role_permissions]

            if permission_name not in user_permissions:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=permission_name,
                    granted=False,
                    details={
                        'reason': 'insufficient_permissions',
                        'user_role': current_user.role.value,
                        'required_permission': permission_name,
                        'user_permissions': user_permissions
                    }
                )
                flash('No tienes permisos para realizar esta acción', 'error')
                abort(403)

            # Log successful permission check
            SecurityAudit.log_permission_check(
                resource=f.__name__,
                permission=permission_name,
                granted=True,
                details={
                    'user_role': current_user.role.value,
                    'permission_check_duration_ms': round((time.time() - start_time) * 1000, 2)
                }
            )

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_role(*roles):
    """Decorator to check if current user has one of the specified roles with audit logging"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            if not current_user.is_authenticated:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=f"role:{','.join(r.value for r in roles)}",
                    granted=False,
                    details={'reason': 'not_authenticated'}
                )
                abort(401)

            if current_user.is_superuser or current_user.role in roles:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=f"role:{','.join(r.value for r in roles)}",
                    granted=True,
                    details={
                        'user_role': current_user.role.value,
                        'required_roles': [r.value for r in roles],
                        'access_reason': 'superuser' if current_user.is_superuser else 'role_match',
                        'permission_check_duration_ms': round((time.time() - start_time) * 1000, 2)
                    }
                )
                return f(*args, **kwargs)

            SecurityAudit.log_permission_check(
                resource=f.__name__,
                permission=f"role:{','.join(r.value for r in roles)}",
                granted=False,
                details={
                    'reason': 'insufficient_role',
                    'user_role': current_user.role.value,
                    'required_roles': [r.value for r in roles]
                }
            )

            flash('No tienes permisos para acceder a esta página', 'error')
            abort(403)

        return decorated_function
    return decorator
    """Decorator to check if current user has a specific permission with audit logging"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            if not current_user.is_authenticated:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=permission_name,
                    granted=False,
                    details={'reason': 'not_authenticated'}
                )
                abort(401)

            # Superuser has all permissions
            if current_user.is_superuser:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=permission_name,
                    granted=True,
                    details={'reason': 'superuser_access', 'user_role': 'superuser'}
                )
                return f(*args, **kwargs)

            # Check role-based permissions
            role_permissions = db.session.query(Permission.name).join(RolePermission).filter(
                RolePermission.role == current_user.role.value
            ).all()

            user_permissions = [p[0] for p in role_permissions]

            if permission_name not in user_permissions:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=permission_name,
                    granted=False,
                    details={
                        'reason': 'insufficient_permissions',
                        'user_role': current_user.role.value,
                        'required_permission': permission_name,
                        'user_permissions': user_permissions
                    }
                )
                flash('No tienes permisos para realizar esta acción', 'error')
                abort(403)

            # Log successful permission check
            SecurityAudit.log_permission_check(
                resource=f.__name__,
                permission=permission_name,
                granted=True,
                details={
                    'user_role': current_user.role.value,
                    'permission_check_duration_ms': round((time.time() - start_time) * 1000, 2)
                }
            )

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def has_role(*roles):
    """Decorator to check if current user has one of the specified roles with audit logging"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            if not current_user.is_authenticated:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=f"role:{','.join(r.value for r in roles)}",
                    granted=False,
                    details={'reason': 'not_authenticated'}
                )
                abort(401)

            if current_user.is_superuser or current_user.role in roles:
                SecurityAudit.log_permission_check(
                    resource=f.__name__,
                    permission=f"role:{','.join(r.value for r in roles)}",
                    granted=True,
                    details={
                        'user_role': current_user.role.value,
                        'required_roles': [r.value for r in roles],
                        'access_reason': 'superuser' if current_user.is_superuser else 'role_match',
                        'permission_check_duration_ms': round((time.time() - start_time) * 1000, 2)
                    }
                )
                return f(*args, **kwargs)

            SecurityAudit.log_permission_check(
                resource=f.__name__,
                permission=f"role:{','.join(r.value for r in roles)}",
                granted=False,
                details={
                    'reason': 'insufficient_role',
                    'user_role': current_user.role.value,
                    'required_roles': [r.value for r in roles]
                }
            )

            flash('No tienes permisos para acceder a esta página', 'error')
            abort(403)

        return decorated_function
    return decorator