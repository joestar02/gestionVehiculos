from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from flask_login import UserMixin

from app.extensions import db

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    FLEET_MANAGER = "fleet_manager"
    OPERATIONS_MANAGER = "operations_manager"
    DRIVER = "driver"
    VIEWER = "viewer"

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    organization_unit_id = Column(Integer, ForeignKey("organization_units.id"), nullable=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    driver = relationship("Driver", back_populates="user", foreign_keys="Driver.user_id", uselist=False)
    organization_unit = relationship("OrganizationUnit", back_populates="users")
    created_assignments = relationship("VehicleAssignment", back_populates="creator")

    def __repr__(self):
        return f"<User {self.username} - {self.email}>"

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username
    
    def get_id(self):
        """Override Flask-Login's get_id method"""
        return str(self.id)
