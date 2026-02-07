"""Security audit service with enhanced logging"""
import logging
import json
from datetime import datetime
from flask import request, g
from flask_login import current_user
from app.extensions import db
from app.models.user import User

# Configure security logger with enhanced formatting
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Create formatter with more detailed information
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(user_id)s] %(username)s@%(ip_address)s - %(operation)s - %(resource)s - %(details)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler for security logs
handler = logging.FileHandler('security.log')
handler.setFormatter(formatter)
security_logger.addHandler(handler)

# Console handler for development
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
security_logger.addHandler(console_handler)

class SecurityAudit:
    """Enhanced security audit service with detailed operation logging"""

    @staticmethod
    def _get_request_context():
        """Get comprehensive request context information"""
        context = {
            'user_id': getattr(current_user, 'id', 'anonymous') if current_user and current_user.is_authenticated else 'anonymous',
            'username': getattr(current_user, 'username', 'anonymous') if current_user and current_user.is_authenticated else 'anonymous',
            'user_role': getattr(current_user, 'role', None).value if current_user and current_user.is_authenticated and current_user.role else 'none',
            'ip_address': request.remote_addr if request else 'unknown',
            'user_agent': request.headers.get('User-Agent', 'unknown') if request else 'unknown',
            'method': request.method if request else 'unknown',
            'endpoint': request.endpoint if request else 'unknown',
            'url': request.url if request else 'unknown',
            'timestamp': datetime.utcnow().isoformat(),
            'session_id': getattr(g, 'session_id', 'unknown') if hasattr(g, 'session_id') else 'unknown'
        }
        return context

    @staticmethod
    def _format_log_message(operation: str, resource: str, details: dict = None, **extra_fields):
        """Format log message with structured data"""
        context = SecurityAudit._get_request_context()

        # Merge context with extra fields
        log_data = {**context, **extra_fields}

        # Add operation and resource
        log_data['operation'] = operation
        log_data['resource'] = resource

        # Add details if provided
        if details:
            log_data['details'] = json.dumps(details, default=str, ensure_ascii=False)
        else:
            log_data['details'] = '{}'

        # Create structured log message
        message = f"{operation.upper()} - {resource}"

        # Add extra context for specific operations
        if operation in ['CREATE', 'UPDATE', 'DELETE'] and details:
            if 'id' in details:
                message += f" (ID: {details['id']})"
            if 'name' in details:
                message += f" '{details['name']}'"

        return message, log_data

    @staticmethod
    def log_operation(operation: str, resource: str, success: bool = True, details: dict = None, **extra_fields):
        """Log a general operation with full context"""
        message, log_data = SecurityAudit._format_log_message(operation, resource, details, **extra_fields)

        if success:
            security_logger.info(message, extra=log_data)
        else:
            log_data['error'] = True
            security_logger.error(f"FAILED: {message}", extra=log_data)

    @staticmethod
    def log_authentication_attempt(username: str, success: bool, ip_address: str = None, details: dict = None):
        """Log authentication attempts with enhanced details"""
        operation = "LOGIN_SUCCESS" if success else "LOGIN_FAILED"
        resource = "authentication"

        log_details = details or {}
        log_details.update({
            'attempted_username': username,
            'login_method': 'form' if request and request.method == 'POST' else 'unknown'
        })

        SecurityAudit.log_operation(operation, resource, success, log_details)

    @staticmethod
    def log_user_registration(username: str, email: str, ip_address: str = None, details: dict = None):
        """Log user registration with enhanced details"""
        operation = "USER_REGISTER"
        resource = "user_account"

        log_details = details or {}
        log_details.update({
            'new_username': username,
            'email': email,
            'registration_method': 'web_form'
        })

        SecurityAudit.log_operation(operation, resource, True, log_details)

    @staticmethod
    def log_suspicious_activity(activity: str, details: dict = None, severity: str = "WARNING"):
        """Log suspicious activities with enhanced context"""
        operation = f"SUSPICIOUS_{activity.upper().replace(' ', '_')}"
        resource = "security_monitoring"

        log_details = details or {}
        log_details.update({
            'activity_type': activity,
            'severity': severity,
            'requires_investigation': True
        })

        # Use appropriate log level based on severity
        if severity.upper() in ['CRITICAL', 'ERROR']:
            security_logger.error(f"SUSPICIOUS ACTIVITY: {activity}", extra={
                **SecurityAudit._get_request_context(),
                'operation': operation,
                'resource': resource,
                'details': json.dumps(log_details, default=str, ensure_ascii=False)
            })
        else:
            security_logger.warning(f"SUSPICIOUS ACTIVITY: {activity}", extra={
                **SecurityAudit._get_request_context(),
                'operation': operation,
                'resource': resource,
                'details': json.dumps(log_details, default=str, ensure_ascii=False)
            })

    @staticmethod
    def log_admin_action(action: str, target_user: str = None, target_resource: str = None, details: dict = None):
        """Log administrative actions with full context"""
        operation = f"ADMIN_{action.upper()}"
        resource = target_resource or "system_admin"

        log_details = details or {}
        if target_user:
            log_details['target_user'] = target_user

        SecurityAudit.log_operation(operation, resource, True, log_details)

    @staticmethod
    def log_permission_check(resource: str, permission: str, granted: bool, details: dict = None):
        """Log permission checks for audit trail"""
        operation = "PERMISSION_CHECK"
        resource_type = f"{resource}_access"

        log_details = details or {}
        log_details.update({
            'permission_required': permission,
            'access_granted': granted,
            'access_denied': not granted
        })

        SecurityAudit.log_operation(operation, resource_type, granted, log_details)

    @staticmethod
    def log_data_operation(operation: str, resource_type: str, resource_id: str = None,
                          old_values: dict = None, new_values: dict = None, details: dict = None):
        """Log CRUD operations on data with before/after values"""
        operation_upper = operation.upper()
        resource = f"{resource_type}:{resource_id}" if resource_id else resource_type

        log_details = details or {}
        log_details.update({
            'resource_type': resource_type,
            'resource_id': resource_id or 'new'
        })

        if old_values:
            log_details['old_values'] = old_values
        if new_values:
            log_details['new_values'] = new_values

        # Add change summary for updates
        if operation_upper == 'UPDATE' and old_values and new_values:
            changes = {}
            for key in set(old_values.keys()) | set(new_values.keys()):
                old_val = old_values.get(key)
                new_val = new_values.get(key)
                if old_val != new_val:
                    changes[key] = {'from': old_val, 'to': new_val}
            if changes:
                log_details['changes'] = changes

        SecurityAudit.log_operation(operation_upper, resource, True, log_details)

    @staticmethod
    def log_security_event(event: str, severity: str = "INFO", details: dict = None):
        """Log general security events"""
        operation = f"SECURITY_EVENT_{event.upper().replace(' ', '_')}"
        resource = "system_security"

        log_details = details or {}
        log_details.update({
            'event_type': event,
            'severity': severity
        })

        SecurityAudit.log_operation(operation, resource, True, log_details)

    @staticmethod
    def log_api_access(endpoint: str, method: str, response_code: int, duration_ms: float = None, details: dict = None):
        """Log API access for monitoring"""
        operation = f"API_{method.upper()}"
        resource = f"api:{endpoint}"

        log_details = details or {}
        log_details.update({
            'http_method': method,
            'response_code': response_code,
            'response_status': 'success' if 200 <= response_code < 400 else 'error'
        })

        if duration_ms:
            log_details['duration_ms'] = round(duration_ms, 2)

        success = 200 <= response_code < 400
        SecurityAudit.log_operation(operation, resource, success, log_details)

    @staticmethod
    def log_database_operation(operation: str, table: str, record_id: str = None,
                              old_values: dict = None, new_values: dict = None,
                              query: str = None, execution_time: float = None, details: dict = None):
        """Log database operations with detailed information"""
        from app.services.database_audit_service import DatabaseAudit

        # Use the database audit service for detailed DB logging
        db_details = details or {}

        if record_id:
            db_details['record_id'] = record_id
        if old_values:
            db_details['old_values'] = old_values
        if new_values:
            db_details['new_values'] = new_values
        if query:
            db_details['query'] = query
        if execution_time:
            db_details['execution_time'] = execution_time

        # Add change summary for updates
        if operation.upper() == 'UPDATE' and old_values and new_values:
            changes = {}
            for key in set(old_values.keys()) | set(new_values.keys()):
                old_val = old_values.get(key)
                new_val = new_values.get(key)
                if old_val != new_val:
                    changes[key] = {'from': old_val, 'to': new_val}
            if changes:
                db_details['changes'] = changes

        DatabaseAudit._log_database_operation(operation, table, db_details, execution_time)

    @staticmethod
    def log_model_change(model_class: str, operation: str, instance_id: str = None,
                        old_data: dict = None, new_data: dict = None, details: dict = None):
        """Log changes to model instances with automatic field comparison"""
        table_name = model_class.lower()

        # Extract meaningful information for logging
        log_details = details or {}

        if instance_id:
            log_details['instance_id'] = instance_id

        # For updates, compare old vs new data
        if operation.upper() == 'UPDATE' and old_data and new_data:
            changes = {}
            for field in set(old_data.keys()) | set(new_data.keys()):
                old_val = old_data.get(field)
                new_val = new_data.get(field)
                if old_val != new_val:
                    changes[field] = {'from': old_val, 'to': new_val}

            if changes:
                log_details['field_changes'] = changes
                log_details['changed_fields'] = list(changes.keys())
                log_details['change_count'] = len(changes)

        # Add model metadata
        log_details['model_class'] = model_class
        log_details['table_name'] = table_name

        SecurityAudit.log_database_operation(
            operation=operation,
            table=table_name,
            record_id=instance_id,
            old_values=old_data,
            new_values=new_data,
            details=log_details
        )
