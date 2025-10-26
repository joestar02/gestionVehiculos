from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from decimal import Decimal
from ..models.maintenance import MaintenanceType, MaintenanceStatus

class MaintenanceRecordBase(BaseModel):
    vehicle_id: int
    maintenance_type: MaintenanceType
    status: MaintenanceStatus = MaintenanceStatus.SCHEDULED
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    mileage_at_service: Optional[int] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    provider_name: Optional[str] = Field(None, max_length=100)
    provider_contact: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    work_performed: Optional[str] = None
    parts_replaced: Optional[str] = None
    next_service_date: Optional[datetime] = None
    next_service_mileage: Optional[int] = Field(None, ge=0)
    invoice_number: Optional[str] = Field(None, max_length=50)
    document_path: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None

class MaintenanceRecordCreate(MaintenanceRecordBase):
    pass

class MaintenanceRecordUpdate(BaseModel):
    status: Optional[MaintenanceStatus] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    mileage_at_service: Optional[int] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    provider_name: Optional[str] = Field(None, max_length=100)
    work_performed: Optional[str] = None
    parts_replaced: Optional[str] = None
    next_service_date: Optional[datetime] = None
    next_service_mileage: Optional[int] = Field(None, ge=0)
    invoice_number: Optional[str] = Field(None, max_length=50)
    document_path: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None

class MaintenanceRecordInDBBase(MaintenanceRecordBase):
    id: int
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class MaintenanceRecord(MaintenanceRecordInDBBase):
    pass

class MaintenanceRecordInDB(MaintenanceRecordInDBBase):
    pass


# ITV Schemas
class ITVRecordBase(BaseModel):
    vehicle_id: int
    inspection_date: datetime
    next_inspection_date: datetime
    result: str = Field(..., max_length=50)
    station_name: Optional[str] = Field(None, max_length=100)
    station_code: Optional[str] = Field(None, max_length=20)
    certificate_number: Optional[str] = Field(None, max_length=50)
    defects_found: Optional[str] = None
    document_path: Optional[str] = Field(None, max_length=500)
    alert_days_before: int = Field(30, ge=1, le=365)
    notes: Optional[str] = None

    @validator('next_inspection_date')
    def next_after_current(cls, v, values):
        if 'inspection_date' in values and v <= values['inspection_date']:
            raise ValueError('Next inspection date must be after current inspection date')
        return v

class ITVRecordCreate(ITVRecordBase):
    pass

class ITVRecordUpdate(BaseModel):
    next_inspection_date: Optional[datetime] = None
    defects_found: Optional[str] = None
    document_path: Optional[str] = Field(None, max_length=500)
    alert_days_before: Optional[int] = Field(None, ge=1, le=365)
    notes: Optional[str] = None

class ITVRecordInDBBase(ITVRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ITVRecord(ITVRecordInDBBase):
    pass

class ITVRecordInDB(ITVRecordInDBBase):
    pass
