"""Input validation and sanitization service"""
import re
import bleach
from email_validator import validate_email, EmailNotValidError
from flask import request

class InputValidator:
    """Input validation and sanitization service"""

    # Allowed HTML tags for rich text (if needed)
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u']
    ALLOWED_ATTRIBUTES = {}

    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_PATTERN = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
    )

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not value:
            return ""

        # Remove leading/trailing whitespace
        value = value.strip()

        # Check length
        if len(value) > max_length:
            value = value[:max_length]

        # Basic HTML escaping (bleach handles this)
        return bleach.clean(value, tags=[], attributes={}, strip=True)

    @staticmethod
    def sanitize_html(value: str, max_length: int = 1000) -> str:
        """Sanitize HTML input with allowed tags"""
        if not value:
            return ""

        # Remove leading/trailing whitespace
        value = value.strip()

        # Check length
        if len(value) > max_length:
            value = value[:max_length]

        return bleach.clean(value, tags=InputValidator.ALLOWED_TAGS,
                          attributes=InputValidator.ALLOWED_ATTRIBUTES, strip=True)

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email address"""
        if not email:
            return False, "Email es requerido"

        email = email.strip().lower()

        try:
            validate_email(email, check_deliverability=False)
            return True, email
        except EmailNotValidError as e:
            return False, f"Email no válido: {str(e)}"

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username"""
        if not username:
            return False, "Nombre de usuario es requerido"

        username = username.strip()

        if len(username) < 3:
            return False, "Nombre de usuario debe tener al menos 3 caracteres"

        if len(username) > 50:
            return False, "Nombre de usuario no puede exceder 50 caracteres"

        # Username pattern: letters, numbers, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Nombre de usuario solo puede contener letras, números, guiones y guiones bajos"

        return True, username

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if not password:
            return False, "Contraseña es requerida"

        if len(password) < InputValidator.MIN_PASSWORD_LENGTH:
            return False, f"Contraseña debe tener al menos {InputValidator.MIN_PASSWORD_LENGTH} caracteres"

        if len(password) > 128:
            return False, "Contraseña no puede exceder 128 caracteres"

        # Check for complexity requirements
        if not re.search(r'[a-z]', password):
            return False, "Contraseña debe contener al menos una letra minúscula"

        if not re.search(r'[A-Z]', password):
            return False, "Contraseña debe contener al menos una letra mayúscula"

        if not re.search(r'\d', password):
            return False, "Contraseña debe contener al menos un número"

        if not re.search(r'[@$!%*?&]', password):
            return False, "Contraseña debe contener al menos un carácter especial (@$!%*?&)"

        return True, "Contraseña válida"

    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """Validate phone number (basic validation)"""
        if not phone:
            return True, ""  # Phone is optional

        phone = phone.strip()

        # Remove all non-digit characters
        phone_digits = re.sub(r'\D', '', phone)

        if len(phone_digits) < 10:
            return False, "Número de teléfono debe tener al menos 10 dígitos"

        if len(phone_digits) > 15:
            return False, "Número de teléfono no puede exceder 15 dígitos"

        return True, phone_digits

    @staticmethod
    def validate_license_plate(plate: str) -> tuple[bool, str]:
        """Validate vehicle license plate"""
        if not plate:
            return False, "Placa de vehículo es requerida"

        plate = plate.strip().upper()

        # Spanish license plate pattern (example)
        if not re.match(r'^([A-Z]{1,3}\d{4}|\d{4}[A-Z]{1,3})$', plate):
            return False, "Formato de placa no válido (ej: ABC1234 o 1234ABC)"

        return True, plate

    @staticmethod
    def validate_document_number(doc_number: str) -> tuple[bool, str]:
        """Validate document number (DNI/NIF)"""
        if not doc_number:
            return False, "Número de documento es requerido"

        doc_number = doc_number.strip().upper()

        # Spanish DNI pattern (8 digits + letter)
        if not re.match(r'^\d{8}[A-Z]$', doc_number):
            return False, "Formato de documento no válido (8 dígitos + letra)"

        return True, doc_number

    @staticmethod
    def get_client_ip() -> str:
        """Get real client IP address"""
        # Check for proxy headers
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP').strip()
        else:
            return request.remote_addr or 'unknown'

    @staticmethod
    def is_safe_url(target):
        """Check if URL is safe (same domain)"""
        from flask import url_for
        from urllib.parse import urlparse, urljoin

        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))

        return test_url.scheme in ('http', 'https') and \
               ref_url.netloc == test_url.netloc
