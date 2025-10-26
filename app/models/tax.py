from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class TaxType(str, enum.Enum):
    IVTM = "ivtm"  # Impuesto sobre Vehículos de Tracción Mecánica
    OTHER = "otro"

class PaymentStatus(str, enum.Enum):
    PENDING = "pendiente"
    PAID = "pagado"
    OVERDUE = "con_retraso"
    EXEMPTED = "exento"

class VehicleTax(db.Model):
    __tablename__ = "vehicle_taxes"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    tax_type = Column(Enum(TaxType), nullable=False)
    tax_year = Column(Integer, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    due_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    document_path = Column(String(500))  # Receipt file path
    alert_days_before = Column(Integer, default=15)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="taxes")

    def __repr__(self):
        return f"<VehicleTax {self.id} - {self.tax_type} Vehicle:{self.vehicle_id} Year:{self.tax_year}>"

    @property
    def is_due_soon(self):
        if self.due_date and self.alert_days_before and self.payment_status == PaymentStatus.PENDING:
            days_until_due = (self.due_date - datetime.utcnow()).days
            return days_until_due <= self.alert_days_before
        return False
