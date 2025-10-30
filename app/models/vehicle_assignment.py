from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class AssignmentType(str, enum.Enum):
    TEMPORAL = "temporal"  # Asignación temporal
    PERMANENTE = "permanente"  # Asignación permanente
    PROYECTO = "proyecto"  # Asignación por proyecto
    MANTENIMIENTO = "mantenimiento"  # Asignación para mantenimiento

class PaymentStatus(str, enum.Enum):
    PENDING = "pendiente"
    PAID = "pagado"
    OVERDUE = "con_retraso"
    EXEMPTED = "exento"

class VehicleAssignment(db.Model):
    __tablename__ = "vehicle_assignments"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    organization_unit_id = Column(Integer, ForeignKey("organization_units.id"), nullable=True)  # Made nullable

    # Assignment details
    assignment_type = Column(Enum(AssignmentType), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Payment information
    assignment_fee = Column(Numeric(10, 2), nullable=False)  # Costo de la cesión
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime)
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    document_path = Column(String(500))  # Assignment contract document

    # Additional details
    purpose = Column(Text, nullable=False)
    destination = Column(String(200))
    notes = Column(Text)

    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    vehicle = relationship("Vehicle", back_populates="assignments")
    driver = relationship("Driver", back_populates="assignments")
    organization_unit = relationship("OrganizationUnit", back_populates="assignments", foreign_keys=[organization_unit_id])
    creator = relationship("User", back_populates="created_assignments")

    def __repr__(self):
        return f"<VehicleAssignment {self.id} - Vehicle:{self.vehicle_id} Driver:{self.driver_id} Type:{self.assignment_type}>"

    @property
    def is_due_soon(self):
        if self.payment_status == PaymentStatus.PENDING and self.end_date:
            days_until_due = (self.end_date - datetime.utcnow()).days
            return days_until_due <= 15
        return False

    @property
    def is_overdue(self):
        if self.payment_status == PaymentStatus.PENDING and self.end_date:
            return datetime.utcnow() > self.end_date
        return False
