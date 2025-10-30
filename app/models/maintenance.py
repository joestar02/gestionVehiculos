from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.extensions import db

class MaintenanceType(str, enum.Enum):
    ITV = "itv"
    OIL_CHANGE = "cambio_aceite"
    TIRE_CHANGE = "cambio_neumaticos"
    BRAKE_SERVICE = "revision_frenos"
    GENERAL_INSPECTION = "inspeccion_general"
    REPAIR = "reparacion"
    Maintenance = "revision_mantenimiento"
    OTHER = "otro"

class MaintenanceStatus(str, enum.Enum):
    SCHEDULED = "programado"
    IN_PROGRESS = "en_proceso"
    COMPLETED = "completado"
    CANCELLED = "cancelado"

class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED)
    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime)
    mileage_at_service = Column(Integer)
    cost = Column(Numeric(10, 2))
    provider_id = Column(Integer, ForeignKey("providers.id"))
    provider_name = Column(String(100))
    provider_contact = Column(String(100))
    description = Column(Text)
    work_performed = Column(Text)
    parts_replaced = Column(Text)
    next_service_date = Column(DateTime)
    next_service_mileage = Column(Integer)
    invoice_number = Column(String(50))
    document_path = Column(String(500))  # File path
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")
    provider = relationship("Provider", back_populates="maintenance_records")

    def __repr__(self):
        return f"<MaintenanceRecord {self.id} - {self.maintenance_type} Vehicle:{self.vehicle_id}>"
