from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.extensions import db

class OrganizationUnit(db.Model):
    __tablename__ = "organization_units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("organization_units.id"), nullable=True)
    manager_name = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicles = relationship("Vehicle", back_populates="organization_unit")
    drivers = relationship("Driver", back_populates="organization_unit")
    providers = relationship("Provider", back_populates="organization_unit")
    users = relationship("User", back_populates="organization_unit")
    parent = relationship("OrganizationUnit", remote_side=[id])
    child_units = relationship("OrganizationUnit", back_populates="parent")
    reservations = relationship("Reservation", back_populates="organization_unit")
    assignments = relationship("VehicleAssignment", back_populates="organization_unit")

    def __repr__(self):
        return f"<OrganizationUnit {self.code} - {self.name}>"
