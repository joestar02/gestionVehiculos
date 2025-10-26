from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from app.extensions import db

class RentingContract(db.Model):
    __tablename__ = "renting_contracts"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    company_name = Column(String(100), nullable=False)
    contract_number = Column(String(50), unique=True, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    monthly_cost = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))
    km_limit = Column(Integer)
    excess_km_cost = Column(Numeric(10, 2))
    contact_person = Column(String(100))
    contact_email = Column(String(100))
    contact_phone = Column(String(20))
    terms_and_conditions = Column(Text)
    document_path = Column(String(500))  # File path
    is_active = Column(Boolean, default=True)
    alert_days_before_expiry = Column(Integer, default=30)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="renting_contracts")

    def __repr__(self):
        return f"<RentingContract {self.contract_number} - {self.company_name}>"

    @property
    def is_expiring_soon(self):
        if self.end_date and self.alert_days_before_expiry:
            days_until_expiry = (self.end_date - datetime.utcnow()).days
            return days_until_expiry <= self.alert_days_before_expiry
        return False
