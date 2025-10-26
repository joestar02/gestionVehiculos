"""ITV (Inspección Técnica de Vehículos) model"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class ITVStatus(str, enum.Enum):
    PENDING = "pendiente"
    PASSED = "pasado"
    FAILED = "rechazado"
    EXPIRED = "fin_plazo"

class ITVResult(str, enum.Enum):
    FAVORABLE = "favorable"
    DESFAVORABLE = "desfavorable"
    NEGATIVA = "negativa"

class ITVRecord(db.Model):
    __tablename__ = "itv_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    # Información de la inspección
    inspection_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    next_inspection_date = Column(DateTime)
    
    # Resultado
    result = Column(Enum(ITVResult), nullable=False)
    status = Column(Enum(ITVStatus), default=ITVStatus.PENDING)
    
    # Detalles
    inspection_center = Column(String(200))
    inspector_name = Column(String(100))
    certificate_number = Column(String(100), unique=True)
    
    # Defectos encontrados
    defects_found = Column(Text)
    defects_severity = Column(String(50))  # leve, grave, muy_grave
    
    # Costos
    cost = Column(Numeric(10, 2))
    
    # Kilometraje en el momento de la inspección
    mileage_at_inspection = Column(Integer)
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="itv_records")

    def __repr__(self):
        return f"<ITVRecord {self.id} - Vehicle:{self.vehicle_id} Result:{self.result}>"
    
    @property
    def is_expired(self):
        """Check if ITV is expired"""
        return self.expiry_date < datetime.now() if self.expiry_date else True
    
    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            delta = self.expiry_date - datetime.now()
            return delta.days
        return None
