from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from ..models.accident import AccidentSeverity, AccidentStatus

class AccidentBase(BaseModel):
    vehicle_id: int
    driver_id: Optional[int] = None
    accident_date: datetime
    location: str = Field(..., min_length=5, max_length=200)
    severity: AccidentSeverity
    status: AccidentStatus = AccidentStatus.REPORTED
    description: str = Field(..., min_length=10)
    weather_conditions: Optional[str] = Field(None, max_length=100)
    road_conditions: Optional[str] = Field(None, max_length=100)
    other_parties_involved: Optional[str] = None
    witnesses: Optional[str] = None
    police_report_number: Optional[str] = Field(None, max_length=50)
    insurance_claim_number: Optional[str] = Field(None, max_length=50)
    damage_description: Optional[str] = None
    estimated_repair_cost: Optional[Decimal] = Field(None, ge=0)
    actual_repair_cost: Optional[Decimal] = Field(None, ge=0)
    repair_provider: Optional[str] = Field(None, max_length=100)
    repair_start_date: Optional[datetime] = None
    repair_completion_date: Optional[datetime] = None
    responsible_party: Optional[str] = Field(None, max_length=100)
    document_paths: Optional[str] = None
    photos_paths: Optional[str] = None
    notes: Optional[str] = None

class AccidentCreate(AccidentBase):
    pass

class AccidentUpdate(BaseModel):
    status: Optional[AccidentStatus] = None
    insurance_claim_number: Optional[str] = Field(None, max_length=50)
    damage_description: Optional[str] = None
    estimated_repair_cost: Optional[Decimal] = Field(None, ge=0)
    actual_repair_cost: Optional[Decimal] = Field(None, ge=0)
    repair_provider: Optional[str] = Field(None, max_length=100)
    repair_start_date: Optional[datetime] = None
    repair_completion_date: Optional[datetime] = None
    document_paths: Optional[str] = None
    photos_paths: Optional[str] = None
    notes: Optional[str] = None

class AccidentInDBBase(AccidentBase):
    id: int
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class Accident(AccidentInDBBase):
    pass

class AccidentInDB(AccidentInDBBase):
    pass
