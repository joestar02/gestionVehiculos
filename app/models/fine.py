from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class FineStatus(str, enum.Enum):
    PENDING = "pendiente"
    PAID = "pagado"
    APPEALED = "reclamado"
    DISMISSED = "rechazado"
    OVERDUE = "con_retraso"

class FineType(str, enum.Enum):
    SPEEDING = "exceso_velocidad"
    PARKING = "aparcamiento"
    RED_LIGHT = "carril_no_permitido"
    DOCUMENTATION = "documentación"
    OTHER = "otro"

class Fine(db.Model):
    __tablename__ = "fines"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    fine_number = Column(String(50), unique=True, nullable=False)
    fine_type = Column(Enum(FineType), nullable=False)
    fine_date = Column(DateTime, nullable=False)
    notification_date = Column(DateTime)
    location = Column(String(200))
    description = Column(Text, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    reduced_amount = Column(Numeric(10, 2))
    payment_deadline = Column(DateTime)
    reduced_payment_deadline = Column(DateTime)
    payment_date = Column(DateTime)
    payment_amount = Column(Numeric(10, 2))
    status = Column(Enum(FineStatus), default=FineStatus.PENDING)
    responsible_driver = Column(String(100))
    appeal_filed = Column(Boolean, default=False)
    appeal_date = Column(DateTime)
    appeal_reason = Column(Text)
    appeal_result = Column(String(100))
    document_path = Column(String(500))  # Fine document file path
    payment_receipt_path = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="fines")
    driver = relationship("Driver")

    def __repr__(self):
        return f"<Fine {self.fine_number} - Vehicle:{self.vehicle_id} Amount:{self.amount}>"
