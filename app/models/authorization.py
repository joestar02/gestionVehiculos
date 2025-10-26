from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.extensions import db

class UrbanAccessAuthorization(db.Model):
    __tablename__ = "urban_access_authorizations"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    authorization_type = Column(String(100), nullable=False)  # ZBE, LEZ, etc.
    issuing_authority = Column(String(100), nullable=False)
    authorization_number = Column(String(50), unique=True, nullable=False)
    zone_description = Column(String(200))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    conditions = Column(Text)
    document_path = Column(String(500))  # Authorization document file path
    alert_days_before_expiry = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="urban_authorizations")

    def __repr__(self):
        return f"<UrbanAccessAuthorization {self.authorization_number} - Vehicle:{self.vehicle_id}>"

    @property
    def is_expiring_soon(self):
        if self.end_date and self.alert_days_before_expiry:
            days_until_expiry = (self.end_date - datetime.utcnow()).days
            return days_until_expiry <= self.alert_days_before_expiry
        return False
