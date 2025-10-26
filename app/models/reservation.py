from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class ReservationStatus(str, enum.Enum):
    PENDING = "pendiente"
    CONFIRMED = "confirmado"
    IN_PROGRESS = "en_progreso"
    COMPLETED = "completado"
    CANCELLED = "cancelado"

class Reservation(db.Model):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_unit_id = Column(Integer, ForeignKey("organization_units.id"), nullable=False)
    
    # Fechas planificadas
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Fechas reales
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    actual_start_mileage = Column(Integer)
    actual_end_mileage = Column(Integer)
    
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING)
    purpose = Column(Text, nullable=False)
    destination = Column(String(200))
    notes = Column(Text)
    
    cancellation_reason = Column(Text)
    cancelled_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="reservations")
    driver = relationship("Driver", back_populates="reservations")
    user = relationship("User")
    organization_unit = relationship("OrganizationUnit", back_populates="reservations")
    pickup = relationship("VehiclePickup", back_populates="reservation", uselist=False)

    def __repr__(self):
        return f"<Reservation {self.id} - Vehicle:{self.vehicle_id} Driver:{self.driver_id}>"
