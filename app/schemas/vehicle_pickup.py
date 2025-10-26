from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from ..models.vehicle_pickup import PickupStatus

class VehiclePickupBase(BaseModel):
    reservation_id: int
    driver_id: int
    vehicle_id: int
    pickup_status: PickupStatus
    pickup_time: Optional[datetime] = None
    return_time: Optional[datetime] = None
    start_mileage: Optional[int] = Field(None, ge=0)
    end_mileage: Optional[int] = Field(None, ge=0)
    fuel_level_start: Optional[int] = Field(None, ge=0, le=100)
    fuel_level_end: Optional[int] = Field(None, ge=0, le=100)
    vehicle_condition_start: Optional[str] = None
    vehicle_condition_end: Optional[str] = None
    not_taken_reason: Optional[str] = None
    not_taken_attachment: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None

    @validator('end_mileage')
    def end_mileage_greater(cls, v, values):
        if v is not None and 'start_mileage' in values and values['start_mileage'] is not None:
            if v < values['start_mileage']:
                raise ValueError('End mileage must be greater than or equal to start mileage')
        return v

    @validator('not_taken_reason')
    def reason_required_if_not_taken(cls, v, values):
        if 'pickup_status' in values and values['pickup_status'] == PickupStatus.NOT_TAKEN:
            if not v:
                raise ValueError('Reason is required when vehicle is not taken')
        return v

class VehiclePickupCreate(VehiclePickupBase):
    pass

class VehiclePickupUpdate(BaseModel):
    return_time: Optional[datetime] = None
    end_mileage: Optional[int] = Field(None, ge=0)
    fuel_level_end: Optional[int] = Field(None, ge=0, le=100)
    vehicle_condition_end: Optional[str] = None
    notes: Optional[str] = None

class VehiclePickupInDBBase(VehiclePickupBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VehiclePickup(VehiclePickupInDBBase):
    pass

class VehiclePickupInDB(VehiclePickupInDBBase):
    pass
