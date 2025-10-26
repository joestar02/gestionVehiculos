from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class AccidentSeverity(str, enum.Enum):
    MINOR = "pequeño"
    MODERATE = "moderado"
    SEVERE = "importante"

class AccidentStatus(str, enum.Enum):
    REPORTED = "avisado"
    UNDER_REPAIR = "en_reparacion"
    REPAIRED = "reparado"
    INSURANCE_CLAIM = "reclamo_seguro"
    CLOSED = "cerrado"

class Accident(db.Model):
    __tablename__ = "accidents"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"))
    accident_date = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=False)
    severity = Column(Enum(AccidentSeverity), nullable=False)
    status = Column(Enum(AccidentStatus), default=AccidentStatus.REPORTED)
    description = Column(Text, nullable=False)
    weather_conditions = Column(String(100))
    road_conditions = Column(String(100))
    other_parties_involved = Column(Text)
    witnesses = Column(Text)
    police_report_number = Column(String(50))
    insurance_claim_number = Column(String(50))
    damage_description = Column(Text)
    estimated_repair_cost = Column(Numeric(10, 2))
    actual_repair_cost = Column(Numeric(10, 2))
    repair_provider = Column(String(100))
    repair_start_date = Column(DateTime)
    repair_completion_date = Column(DateTime)
    responsible_party = Column(String(100))
    document_paths = Column(Text)  # JSON array of file paths
    photos_paths = Column(Text)  # JSON array of photo paths
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="accidents")
    driver = relationship("Driver")

    def __repr__(self):
        return f"<Accident {self.id} - Vehicle:{self.vehicle_id} Date:{self.accident_date}>"
