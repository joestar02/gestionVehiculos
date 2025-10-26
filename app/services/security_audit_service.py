"""Security audit service"""
import logging
from datetime import datetime
from flask import request
from flask_login import current_user
from app.extensions import db
from app.models.user import User

# Configure security logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)
handler = logging.FileHandler('security.log')
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
security_logger.addHandler(handler)

class SecurityAudit:
    """Security audit service"""

    @staticmethod
    def log_authentication_attempt(username: str, success: bool, ip_address: str = None):
        """Log authentication attempts"""
        if not ip_address:
            ip_address = request.remote_addr if request else 'unknown'

        status = "SUCCESS" if success else "FAILED"
        security_logger.info(
            f"Authentication attempt: {status} - User: {username} - IP: {ip_address}"
        )

    @staticmethod
    def log_user_registration(username: str, email: str, ip_address: str = None):
        """Log user registration"""
        if not ip_address:
            ip_address = request.remote_addr if request else 'unknown'

        security_logger.info(
            f"User registration: {username} ({email}) - IP: {ip_address}"
        )

    @staticmethod
    def log_suspicious_activity(activity: str, details: dict = None, ip_address: str = None):
        """Log suspicious activities"""
        if not ip_address:
            ip_address = request.remote_addr if request else 'unknown'

        details_str = f" - Details: {details}" if details else ""
        security_logger.warning(
            f"Suspicious activity: {activity} - IP: {ip_address}{details_str}"
        )

    @staticmethod
    def log_admin_action(action: str, target_user: str = None, details: dict = None):
        """Log administrative actions"""
        if current_user:
            user_id = current_user.id
            username = current_user.username
        else:
            user_id = 'system'
            username = 'system'

        target_str = f" - Target: {target_user}" if target_user else ""
        details_str = f" - Details: {details}" if details else ""

        security_logger.info(
            f"Admin action: {action} - User: {username} (ID: {user_id}){target_str}{details_str}"
        )

    @staticmethod
    def log_security_event(event: str, severity: str = "INFO", details: dict = None):
        """Log general security events"""
        if details:
            details_str = f" - Details: {details}"
        else:
            details_str = ""

        security_logger.info(
            f"Security event ({severity}): {event}{details_str}"
        )
