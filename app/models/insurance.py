from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class InsuranceType(str, enum.Enum):
    RESPONSABILIDAD_CIVIL = "responsabilidad_civil"
    TODO_RIESGO = "todo_riesgo"
    TERCEROS_AMPLIADO = "terceros_ampliado"
    ROBO_INCIDIO = "robo_incendio"
    CRISTALES = "cristales"
    OTHER = "otro"

class InsurancePaymentStatus(str, enum.Enum):
    PENDING = "pendiente"
    PAID = "pagado"
    OVERDUE = "con_retraso"
    CANCELLED = "cancelado"

class VehicleInsurance(db.Model):
    __tablename__ = "vehicle_insurances"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    insurance_type = Column(Enum(InsuranceType), nullable=False)
    insurance_company = Column(String(100), nullable=False)
    policy_number = Column(String(100), nullable=False, unique=True)
    premium_amount = Column(Numeric(10, 2), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    payment_date = Column(DateTime)
    payment_status = Column(Enum(InsurancePaymentStatus), default=InsurancePaymentStatus.PENDING)
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    document_path = Column(String(500))  # Insurance policy document file path
    coverage_details = Column(Text)
    alert_days_before = Column(Integer, default=30)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="insurances")

    def __repr__(self):
        return f"<VehicleInsurance {self.id} - {self.insurance_type} Vehicle:{self.vehicle_id} Company:{self.insurance_company}>"

    @property
    def is_expiring_soon(self):
        if self.end_date and self.alert_days_before and self.payment_status == InsurancePaymentStatus.PENDING:
            days_until_expiry = (self.end_date - datetime.utcnow()).days
            return days_until_expiry <= self.alert_days_before
        return False

    @property
    def is_expired(self):
        if self.end_date:
            return datetime.utcnow() > self.end_date
        return False
