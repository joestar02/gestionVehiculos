from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db

class Permission(db.Model):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "vehicle:create"
    description = Column(String(255))

    # Relationships
    roles = relationship("RolePermission", back_populates="permission")

class RolePermission(db.Model):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True)
    role = Column(String(50), nullable=False)  # Use UserRole enum values
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    permission = relationship("Permission", back_populates="roles")