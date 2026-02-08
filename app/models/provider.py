from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class ProviderType(str, enum.Enum):
    WORKSHOP = "taller"
    CAR_WASH = "lavadero"
    PARTS_STORE = "tienda_recambios"
    OTHER = "otro"

class Provider(db.Model):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    provider_type = Column(Enum(ProviderType), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    website = Column(String(200))
    notes = Column(Text)
    organization_unit_id = Column(Integer, ForeignKey("organization_units.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization_unit = relationship("OrganizationUnit", back_populates="providers")
    maintenance_records = relationship("MaintenanceRecord", back_populates="provider")

    def __repr__(self):
        return f"<Provider {self.name} - {self.provider_type.value.title()}>"

    @property
    def provider_type_display(self):
        return self.provider_type.value.replace('_', ' ').title()
