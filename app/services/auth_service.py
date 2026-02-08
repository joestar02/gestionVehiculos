"""Servicio de autenticación para operaciones de login y gestión de usuarios."""

from datetime import datetime
from app.extensions import db, bcrypt
from app.models.user import User, UserRole
from app.utils.audit_decorators import audit_model_change

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
    @audit_model_change('User', 'UPDATE')
    def authenticate_user(username: str, password: str) -> User | None:
        """Autentica a un usuario por nombre de usuario/email y contraseña.
        
        Args:
            username: Nombre de usuario o email.
            password: Contraseña en texto plano.
            
        Returns:
            El objeto User si la autenticación es exitosa, None en caso contrario.
        """
        from app.services.security_audit_service import SecurityAudit
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            # Log failed authentication attempt - user not found
            SecurityAudit.log_security_event(
                'authentication_failed',
                'WARNING',
                {
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
                'authentication_failed',
                'WARNING',
                {
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
                'authentication_failed',
                'WARNING',
                {
                    'action': 'login_attempt',
                    'username': user.username,
                    'user_id': str(user.id),
                    'reason': 'wrong_password',
                    'attempted_by_service': 'AuthService.authenticate_user'
                }
            )
            return None
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return user
    
    @staticmethod
    @audit_model_change('User', 'CREATE')
    def create_user(username: str, email: str, password: str, 
                   first_name: str = None, last_name: str = None,
                   role: UserRole = UserRole.VIEWER,
                   organization_unit_id: int = None) -> User:
        """Crea un nuevo usuario.
        
        Args:
            username: Nombre de usuario único.
            email: Email único del usuario.
            password: Contraseña en texto plano.
            first_name: Nombre del usuario (opcional).
            last_name: Apellido del usuario (opcional).
            role: Rol del usuario (por defecto VIEWER).
            organization_unit_id: ID del nodo de organización (opcional).
            
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
            role=role,
            organization_unit_id=organization_unit_id
        )
        
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        
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
