"""Authentication service"""
from datetime import datetime
from app.extensions import db, bcrypt
from app.models.user import User, UserRole

class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return bcrypt.check_password_hash(hashed_password, plain_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> User | None:
        """Authenticate a user by username and password"""
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        if not user.is_active:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return user
    
    @staticmethod
    def create_user(username: str, email: str, password: str, 
                   first_name: str = None, last_name: str = None,
                   role: UserRole = UserRole.VIEWER) -> User:
        """Create a new user"""
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
        
        return user
    
    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        """Get user by email"""
        return User.query.filter_by(email=email).first()
