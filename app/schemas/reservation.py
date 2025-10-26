from pydantic import BaseModel, Field, validator
from datetime import datetime, time
from typing import Optional
from ..models.reservation import ReservationStatus

class ReservationBase(BaseModel):
    vehicle_id: int
    driver_id: int
    organization_unit_id: int
    reservation_date: datetime
    start_time: time
    end_time: time
    purpose: Optional[str] = None
    destination: Optional[str] = Field(None, max_length=200)
    estimated_km: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

    @validator('end_time')
    def end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class ReservationCreate(ReservationBase):
    pass

class ReservationUpdate(BaseModel):
    reservation_date: Optional[datetime] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    status: Optional[ReservationStatus] = None
    purpose: Optional[str] = None
    destination: Optional[str] = Field(None, max_length=200)
    estimated_km: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class ReservationCancel(BaseModel):
    cancellation_reason: str = Field(..., min_length=10)

class ReservationInDBBase(ReservationBase):
    id: int
    status: ReservationStatus
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: datetime
    reminder_sent: bool

    class Config:
        from_attributes = True

class Reservation(ReservationInDBBase):
    pass

class ReservationInDB(ReservationInDBBase):
    pass
