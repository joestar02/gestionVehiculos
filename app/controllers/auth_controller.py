"""Authentication controller"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_limiter.util import get_remote_address
from flask import current_app
from app.services.auth_service import AuthService
from app.services.security_audit_service import SecurityAudit
from app.services.input_validation_service import InputValidator
from app.extensions import limiter, csrf
import time
import hashlib

auth_bp = Blueprint('auth', __name__)

# Store failed login attempts for rate limiting
failed_attempts = {}

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=get_remote_address)  # Limit login attempts
def login():
    """Login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    # Determine availability of optional endpoints to avoid template errors
    has_forgot_password = 'auth.forgot_password' in current_app.view_functions
    has_register = 'auth.register' in current_app.view_functions

    if request.method == 'POST':
        # Validate CSRF token
        csrf.protect()

        raw_username = request.form.get('username', '')
        raw_password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        ip_address = get_remote_address()

        # Validate and sanitize input
        username = InputValidator.sanitize_string(raw_username, 50)
        password = raw_password  # Don't sanitize password

        if not username or not password:
            SecurityAudit.log_suspicious_activity(
                "Login attempt with missing credentials",
                {"username": username},
                ip_address
            )
            flash('Por favor ingresa usuario y contraseña', 'error')
            return render_template('auth/login.html', has_forgot_password=has_forgot_password, has_register=has_register)

        # Additional validation
        if len(username) < 3:
            SecurityAudit.log_suspicious_activity(
                "Login attempt with invalid username",
                {"username": username},
                ip_address
            )
            flash('Nombre de usuario no válido', 'error')
            return render_template('auth/login.html', has_forgot_password=has_forgot_password, has_register=has_register)

        user = AuthService.authenticate_user(username, password)

        if user:
            # Clear failed attempts on successful login
            client_ip = get_remote_address()
            failed_attempts.pop(client_ip, None)

            # Log successful authentication with enhanced details
            SecurityAudit.log_authentication_attempt(
                username,
                True,
                details={
                    'login_method': 'web_form',
                    'remember_me': remember,
                    'user_agent': request.headers.get('User-Agent'),
                    'next_page': next_page
                }
            )

            login_user(user, remember=remember)
            next_page = request.args.get('next')

            # Validate redirect URL for security
            if next_page and not InputValidator.is_safe_url(next_page):
                SecurityAudit.log_suspicious_activity(
                    "Suspicious redirect URL attempt",
                    {
                        "redirect_url": next_page,
                        "username": username,
                        "validation_failed": True
                    }
                )
                next_page = None

            flash(f'Bienvenido, {user.full_name}!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            # Track failed attempts
            client_ip = get_remote_address()
            if client_ip not in failed_attempts:
                failed_attempts[client_ip] = []
            failed_attempts[client_ip].append(time.time())

            # Clean old attempts (older than 1 hour)
            current_time = time.time()
            failed_attempts[client_ip] = [attempt_time for attempt_time in failed_attempts[client_ip]
                                        if current_time - attempt_time < 3600]

            # Log failed authentication
            SecurityAudit.log_authentication_attempt(username, False, ip_address)

            # Generic error message to prevent user enumeration
            flash('Credenciales incorrectas. Verifica tu usuario y contraseña.', 'error')

    return render_template('auth/login.html', has_forgot_password=has_forgot_password, has_register=has_register)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout handler"""
    # Log logout
    SecurityAudit.log_security_event(
        f"User logout: {current_user.username}",
        "INFO",
        {"user_id": current_user.id}
    )

    logout_user()
    flash('Has cerrado sesión exitosamente', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour", key_func=get_remote_address)  # Limit registration attempts
def register():
    """Registration page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        # Validate CSRF token
        csrf.protect()

        raw_username = request.form.get('username', '')
        raw_email = request.form.get('email', '')
        raw_password = request.form.get('password', '')
        raw_password_confirm = request.form.get('password_confirm', '')
        raw_first_name = request.form.get('first_name', '')
        raw_last_name = request.form.get('last_name', '')
        ip_address = get_remote_address()

        # Validate and sanitize input
        username = InputValidator.sanitize_string(raw_username, 50)
        email = InputValidator.sanitize_string(raw_email, 100).lower()
        password = raw_password  # Don't sanitize password
        password_confirm = raw_password_confirm  # Don't sanitize password
        first_name = InputValidator.sanitize_string(raw_first_name, 50)
        last_name = InputValidator.sanitize_string(raw_last_name, 50)

        # Validate email
        email_valid, email_result = InputValidator.validate_email(raw_email)
        if not email_valid:
            SecurityAudit.log_suspicious_activity(
                "Registration attempt with invalid email",
                {"email": raw_email},
                ip_address
            )
            flash(email_result, 'error')
            return render_template('auth/register.html')
        email = email_result

        # Validate username
        username_valid, username_result = InputValidator.validate_username(raw_username)
        if not username_valid:
            SecurityAudit.log_suspicious_activity(
                "Registration attempt with invalid username",
                {"username": raw_username},
                ip_address
            )
            flash(username_result, 'error')
            return render_template('auth/register.html')
        username = username_result

        # Validate password
        password_valid, password_message = InputValidator.validate_password(raw_password)
        if not password_valid:
            SecurityAudit.log_suspicious_activity(
                "Registration attempt with weak password",
                {"username": username, "password_length": len(raw_password)},
                ip_address
            )
            flash(password_message, 'error')
            return render_template('auth/register.html')

        # Validate password confirmation
        if password != password_confirm:
            SecurityAudit.log_suspicious_activity(
                "Registration attempt with mismatched passwords",
                {"username": username},
                ip_address
            )
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/register.html')

        # Check if user exists
        if AuthService.get_user_by_username(username):
            SecurityAudit.log_suspicious_activity(
                "Registration attempt with existing username",
                {"username": username},
                ip_address
            )
            flash('El nombre de usuario ya está en uso', 'error')
            return render_template('auth/register.html')

        if AuthService.get_user_by_email(email):
            SecurityAudit.log_suspicious_activity(
                "Registration attempt with existing email",
                {"email": email},
                ip_address
            )
            flash('El correo electrónico ya está registrado', 'error')
            return render_template('auth/register.html')

        try:
            user = AuthService.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Log successful registration
            SecurityAudit.log_user_registration(username, email, ip_address)

            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            # Log registration error
            SecurityAudit.log_security_event(
                f"Registration error for {username}",
                "ERROR",
                {"error": str(e), "email": email}
            )
            flash(f'Error al registrar usuario: {str(e)}', 'error')

    return render_template('auth/register.html')
