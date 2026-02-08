"""Audit decorators for automatic logging of model changes and security events"""
import functools
import json
from typing import Any, Callable, Optional, Dict
from datetime import datetime
from flask_login import current_user
from flask import request

from app.extensions import db
from app.services.security_audit_service import SecurityAudit


def audit_model_change(model_class: str, operation: str):
    """
    Decorator to automatically log model changes (CREATE, UPDATE, DELETE).
    Works with both static methods and instance methods.
    
    Args:
        model_class: Name of the model class being modified
        operation: Operation type (CREATE, UPDATE, DELETE)
    
    Example:
        @audit_model_change('Provider', 'CREATE')
        @staticmethod
        def create_provider(name: str, ...):
            provider = Provider(...)
            db.session.add(provider)
            db.session.commit()
            return provider
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # If operation is CREATE, log the new entity
                if operation == 'CREATE' and result:
                    _log_create(model_class, result)
                
                # If operation is UPDATE, log the changes
                elif operation == 'UPDATE' and result:
                    _log_update(model_class, result, args, kwargs)
                
                # If operation is DELETE, log the deletion
                elif operation == 'DELETE' and result:
                    _log_delete(model_class, args, kwargs)
                
                return result
            
            except Exception as e:
                SecurityAudit.log_operation(
                    operation=operation,
                    resource=f"{model_class.lower()}",
                    success=False,
                    details={
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'function': func.__name__
                    }
                )
                raise
        
        return wrapper
    return decorator


def audit_operation(operation: str, resource: str, include_params: bool = False):
    """
    Decorator to log general security operations.
    
    Args:
        operation: Operation type (CREATE, READ, UPDATE, DELETE, etc.)
        resource: Resource type being operated on
        include_params: Whether to include function parameters in logs
    
    Example:
        @audit_operation('CREATE', 'vehicle')
        def create_vehicle(self, license_plate, make, model):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                result = func(self, *args, **kwargs)
                
                details = {
                    'function': func.__name__,
                    'success': True
                }
                
                if include_params:
                    details['params'] = _sanitize_params(args, kwargs)
                
                if result and hasattr(result, 'id'):
                    details['id'] = result.id
                
                SecurityAudit.log_operation(
                    operation=operation,
                    resource=resource,
                    success=True,
                    details=details
                )
                
                return result
            
            except Exception as e:
                SecurityAudit.log_operation(
                    operation=operation,
                    resource=resource,
                    success=False,
                    details={
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'function': func.__name__
                    }
                )
                raise
        
        return wrapper
    return decorator


def audit_auth(operation: str):
    """
    Decorator to automatically log authentication events (LOGIN, LOGOUT, FAILED_LOGIN).
    
    Args:
        operation: AUTH operation (LOGIN, LOGOUT, FAILED_LOGIN)
    
    Example:
        @audit_auth('LOGIN')
        def login(self, username, password):
            user = User.query.filter_by(username=username).first()
            return user
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            try:
                result = func(self, *args, **kwargs)
                
                # Extract username from args or kwargs
                username = _extract_from_args(args, kwargs, 'username')
                
                if operation == 'LOGIN' and result:
                    SecurityAudit.log_authentication_attempt(
                        username=username or 'unknown',
                        success=True,
                        details={
                            'user_agent': request.headers.get('User-Agent') if request else None,
                            'login_method': 'web_form',
                            'function': func.__name__
                        }
                    )
                
                elif operation == 'LOGOUT':
                    SecurityAudit.log_operation(
                        operation='LOGOUT',
                        resource='authentication',
                        success=True,
                        details={'user': username or 'unknown'}
                    )
                
                return result
            
            except Exception as e:
                if operation == 'LOGIN':
                    username = _extract_from_args(args, kwargs, 'username')
                    SecurityAudit.log_authentication_attempt(
                        username=username or 'unknown',
                        success=False,
                        details={
                            'error': str(e),
                            'error_type': type(e).__name__
                        }
                    )
                
                raise
        
        return wrapper
    return decorator


# ============================================================================
# Helper Functions
# ============================================================================

def _log_create(model_class: str, entity: Any) -> None:
    """Log creation of a model instance"""
    try:
        new_data = _serialize_model(entity)
        
        SecurityAudit.log_model_change(
            model_class=model_class,
            operation='CREATE',
            instance_id=str(getattr(entity, 'id', 'unknown')),
            new_data=new_data,
            details={
                'action': f'{model_class.lower()}_created',
                'created_at': datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        # Fail silently to not break the operation
        print(f"Warning: Could not log {model_class} creation: {str(e)}")


def _log_update(model_class: str, entity: Any, args: tuple, kwargs: dict) -> None:
    """Log update of a model instance"""
    try:
        # Data structure for update is typically: old_data, new_data
        new_data = _serialize_model(entity)
        
        # Try to extract old_data from context if available
        old_data = _get_old_values(entity) if hasattr(entity, '__dict__') else {}
        
        updated_fields = list(kwargs.keys()) if kwargs else []
        
        SecurityAudit.log_model_change(
            model_class=model_class,
            operation='UPDATE',
            instance_id=str(getattr(entity, 'id', 'unknown')),
            old_data=old_data,
            new_data=new_data,
            details={
                'action': f'{model_class.lower()}_updated',
                'updated_fields': updated_fields,
                'updated_at': datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        print(f"Warning: Could not log {model_class} update: {str(e)}")


def _log_delete(model_class: str, args: tuple, kwargs: dict) -> None:
    """Log deletion of a model instance"""
    try:
        # Extract id from args or kwargs
        instance_id = _extract_from_args(args, kwargs, 'id') or _extract_from_args(args, kwargs, f'{model_class.lower()}_id')
        
        SecurityAudit.log_model_change(
            model_class=model_class,
            operation='DELETE',
            instance_id=str(instance_id) if instance_id else 'unknown',
            old_data={'is_active': True},
            new_data={'is_active': False},
            details={
                'action': f'{model_class.lower()}_deleted',
                'deleted_at': datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        print(f"Warning: Could not log {model_class} deletion: {str(e)}")


def _serialize_model(entity: Any) -> Dict[str, Any]:
    """Serialize a SQLAlchemy model to a dictionary"""
    data = {}
    
    if not entity:
        return data
    
    # Get all columns from the model
    if hasattr(entity, '__table__'):
        for column in entity.__table__.columns:
            value = getattr(entity, column.name, None)
            
            # Skip certain columns
            if column.name in ['created_at', 'updated_at']:
                continue
            
            # Handle enum types
            if hasattr(value, 'value'):
                data[column.name] = value.value
            else:
                data[column.name] = value
    
    return data


def _get_old_values(entity: Any) -> Dict[str, Any]:
    """Get old values from SQLAlchemy's change tracker"""
    old_values = {}
    
    try:
        if hasattr(entity, '__dict__') and hasattr(db.session, 'identity_map'):
            # Get the history for each attribute
            from sqlalchemy import inspect
            mapper = inspect(entity)
            
            for column in mapper.columns:
                history = inspect(entity).attrs[column.name].history
                if history and history.unchanged:
                    old_values[column.name] = history.unchanged[0]
    except Exception:
        pass
    
    return old_values


def _sanitize_params(args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Sanitize function parameters for logging (remove sensitive data)"""
    sensitive_fields = ['password', 'token', 'secret', 'api_key']
    
    sanitized = {
        'args_count': len(args),
        'kwargs': {}
    }
    
    for key, value in kwargs.items():
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            sanitized['kwargs'][key] = '***REDACTED***'
        else:
            try:
                sanitized['kwargs'][key] = str(value)[:100]  # Limit length
            except Exception:
                sanitized['kwargs'][key] = type(value).__name__
    
    return sanitized


def _extract_from_args(args: tuple, kwargs: dict, field_name: str) -> Optional[Any]:
    """Extract a field value from function arguments or keyword arguments"""
    # Try kwargs first
    if field_name in kwargs:
        return kwargs[field_name]
    
    # Try to find in args (common pattern: self, field1, field2, ...)
    # This is fragile so we only do it for specific fields like 'id'
    if field_name == 'id' and len(args) > 0:
        return args[0]  # Often the first arg after self
    
    if field_name == 'username' and len(args) > 0:
        return args[0]
    
    return None
