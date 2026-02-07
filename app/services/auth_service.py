"""Servicio de autenticación para operaciones de login y gestión de usuarios."""

from datetime import datetime
from app.extensions import db, bcrypt
from app.models.user import User, UserRole

class AuthService:
    """Servicio para operaciones de autenticación y gestión de usuarios."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña en texto plano contra un hash.
        
        Args:
            plain_password: La contraseña en texto plano a verificar.
            hashed_password: El hash de la contraseña almacenado.
            
        Returns:
            True si la contraseña coincide con el hash, False en caso contrario.
        """
        return bcrypt.check_password_hash(hashed_password, plain_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera un hash para una contraseña.
        
        Args:
            password: La contraseña en texto plano.
            
        Returns:
            El hash de la contraseña como string.
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
"""Servicio de autenticación para operaciones de login y gestión de usuarios."""

from datetime import datetime
from app.extensions import db, bcrypt
from app.models.user import User, UserRole
from app.services.security_audit_service import SecurityAudit

class AuthService:
    """Servicio para operaciones de autenticación y gestión de usuarios."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña en texto plano contra un hash.
        
        Args:
            plain_password: La contraseña en texto plano a verificar.
            hashed_password: El hash de la contraseña almacenado.
            
        Returns:
            True si la contraseña coincide con el hash, False en caso contrario.
        """
        return bcrypt.check_password_hash(hashed_password, plain_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera un hash para una contraseña.
        
        Args:
            password: La contraseña en texto plano.
            
        Returns:
            El hash de la contraseña como string.
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> User | None:
        """Autentica a un usuario por nombre de usuario/email y contraseña.
        
        Args:
            username: Nombre de usuario o email.
            password: Contraseña en texto plano.
            
        Returns:
            El objeto User si la autenticación es exitosa, None en caso contrario.
        """
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            # Log failed authentication attempt - user not found
            SecurityAudit.log_security_event(
                event_type='authentication_failed',
                severity='medium',
                details={
                    'action': 'login_attempt',
                    'username_or_email': username,
                    'reason': 'user_not_found',
                    'attempted_by_service': 'AuthService.authenticate_user'
                }
            )
            return None
            
        if not user.is_active:
            # Log failed authentication attempt - user inactive
            SecurityAudit.log_security_event(
                event_type='authentication_failed',
                severity='medium',
                details={
                    'action': 'login_attempt',
                    'username': user.username,
                    'user_id': str(user.id),
                    'reason': 'user_inactive',
                    'attempted_by_service': 'AuthService.authenticate_user'
                }
            )
            return None
            
        if not AuthService.verify_password(password, user.hashed_password):
            # Log failed authentication attempt - wrong password
            SecurityAudit.log_security_event(
                event_type='authentication_failed',
                severity='medium',
                details={
                    'action': 'login_attempt',
                    'username': user.username,
                    'user_id': str(user.id),
                    'reason': 'wrong_password',
                    'attempted_by_service': 'AuthService.authenticate_user'
                }
            )
            return None
        
        # Capture old last_login for logging
        old_last_login = user.last_login
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log successful authentication
        SecurityAudit.log_model_change(
            model_class='User',
            operation='UPDATE',
            instance_id=str(user.id),
            old_data={'last_login': old_last_login.isoformat() if old_last_login else None},
            new_data={'last_login': user.last_login.isoformat()},
            details={
                'action': 'user_login',
                'username': user.username,
                'user_id': str(user.id),
                'updated_by_service': 'AuthService.authenticate_user'
            }
        )
        
        return user
    
    @staticmethod
    def create_user(username: str, email: str, password: str, 
                   first_name: str = None, last_name: str = None,
                   role: UserRole = UserRole.VIEWER) -> User:
        """Crea un nuevo usuario.
        
        Args:
            username: Nombre de usuario único.
            email: Email único del usuario.
            password: Contraseña en texto plano.
            first_name: Nombre del usuario (opcional).
            last_name: Apellido del usuario (opcional).
            role: Rol del usuario (por defecto VIEWER).
            
        Returns:
            El objeto User creado.
            
        Raises:
            ValueError: Si el username o email ya existen.
        """
        # Verificar si ya existe
        if User.query.filter_by(username=username).first():
            raise ValueError("Username already exists")
        if User.query.filter_by(email=email).first():
            raise ValueError("Email already exists")
            
        hashed_password = AuthService.get_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        
        # Log user creation
        SecurityAudit.log_model_change(
            model_class='User',
            operation='CREATE',
            instance_id=str(user.id),
            new_data={
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.value if user.role else None,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            details={
                'action': 'user_created',
                'created_by_service': 'AuthService.create_user'
            }
        )
        
        return user
    
    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        """Obtiene un usuario por nombre de usuario.
        
        Args:
            username: El nombre de usuario.
            
        Returns:
            El objeto User si existe, None en caso contrario.
        """
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        """Obtiene un usuario por email.
        
        Args:
            email: El email del usuario.
            
        Returns:
            El objeto User si existe, None en caso contrario.
        """
        return User.query.filter_by(email=email).first()
