from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class DriverType(str, enum.Enum):
    OFFICIAL = "oficial"
    AUTHORIZED = "autorizado"

class DriverStatus(str, enum.Enum):
    ACTIVE = "activo"
    INACTIVE = "inactivo"
    SUSPENDED = "suspendido"

class Driver(db.Model):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    document_type = Column(String(20), nullable=False)  # DNI, NIE, Passport
    document_number = Column(String(20), unique=True, nullable=False, index=True)
    driver_license_number = Column(String(20), unique=True, nullable=False)
    driver_license_expiry = Column(DateTime, nullable=False)
    driver_type = Column(Enum(DriverType), nullable=False)
    status = Column(Enum(DriverStatus), default=DriverStatus.ACTIVE)
    email = Column(String(100), unique=True, nullable=False, default='')
    phone = Column(String(20))
    address = Column(Text)
    organization_unit_id = Column(Integer, ForeignKey("organization_units.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    organization_unit = relationship("OrganizationUnit", back_populates="drivers")
    vehicle_associations = relationship("VehicleDriverAssociation", back_populates="driver")
    assignments = relationship("VehicleAssignment", back_populates="driver")
    reservations = relationship("Reservation", back_populates="driver")
    pickups = relationship("VehiclePickup", back_populates="driver")
    user = relationship("User", back_populates="driver", foreign_keys=[user_id], uselist=False)

    def __repr__(self):
        return f"<Driver {self.first_name} {self.last_name} - {self.document_number}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
