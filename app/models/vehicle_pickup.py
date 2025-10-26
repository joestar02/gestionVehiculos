from sqlalchemy import Column, Integer, Enum, DateTime, ForeignKey, Boolean, Text, String
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class PickupStatus(str, enum.Enum):
    TAKEN = "prestado"
    NOT_TAKEN = "no_prestado"

class VehiclePickup(db.Model):
    __tablename__ = "vehicle_pickups"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False, unique=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    pickup_status = Column(Enum(PickupStatus), nullable=False)
    pickup_time = Column(DateTime)
    return_time = Column(DateTime)
    start_mileage = Column(Integer)
    end_mileage = Column(Integer)
    fuel_level_start = Column(Integer)  # Percentage
    fuel_level_end = Column(Integer)  # Percentage
    vehicle_condition_start = Column(Text)
    vehicle_condition_end = Column(Text)
    not_taken_reason = Column(Text)
    not_taken_attachment = Column(String(500))  # File path
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reservation = relationship("Reservation", back_populates="pickup")
    driver = relationship("Driver", back_populates="pickups")
    vehicle = relationship("Vehicle", back_populates="pickups")

    def __repr__(self):
        return f"<VehiclePickup {self.id} - Reservation:{self.reservation_id} Status:{self.pickup_status}>"

    @property
    def total_km(self):
        if self.start_mileage and self.end_mileage:
            return self.end_mileage - self.start_mileage
        return None
