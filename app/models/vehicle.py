from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class VehicleType(str, enum.Enum):
    CAR = "coche"
    VAN = "furgoneta"
    TRUCK = "camión"
    MOTORCYCLE = "motocicleta"
    OTHER = "otro"

class OwnershipType(str, enum.Enum):
    OWNED = "propiedad"
    RENTING = "renting"
    LEASING = "leasing"

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "disponible"
    IN_USE = "en_uso"
    MAINTENANCE = "mantenimiento"
    OUT_OF_SERVICE = "fuera_de_servicio"

class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), unique=True, index=True, nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String(30))
    vin = Column(String(17), unique=True, nullable=True)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE)
    ownership_type = Column(Enum(OwnershipType), nullable=False)
    organization_unit_id = Column(Integer, ForeignKey("organization_units.id"))
    current_mileage = Column(Integer, default=0)
    fuel_type = Column(String(20))
    fuel_capacity = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    organization_unit = relationship("OrganizationUnit", back_populates="vehicles")
    renting_contracts = relationship("RentingContract", back_populates="vehicle")
    reservations = relationship("Reservation", back_populates="vehicle")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle")
    itv_records = relationship("ITVRecord", back_populates="vehicle")
    accidents = relationship("Accident", back_populates="vehicle")
    taxes = relationship("VehicleTax", back_populates="vehicle")
    insurances = relationship("VehicleInsurance", back_populates="vehicle")
    fines = relationship("Fine", back_populates="vehicle")
    urban_authorizations = relationship("UrbanAccessAuthorization", back_populates="vehicle")
    driver_associations = relationship("VehicleDriverAssociation", back_populates="vehicle")
    assignments = relationship("VehicleAssignment", back_populates="vehicle")
    pickups = relationship("VehiclePickup", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle {self.license_plate} - {self.make} {self.model}>"
