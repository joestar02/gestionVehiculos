from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import Optional
from ..models.driver import DriverType, DriverStatus

class DriverBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    document_type: str = Field(..., max_length=20)
    document_number: str = Field(..., min_length=5, max_length=20)
    driver_license_number: str = Field(..., min_length=5, max_length=20)
    driver_license_expiry: datetime
    driver_type: DriverType
    status: DriverStatus = DriverStatus.ACTIVE
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    organization_unit_id: Optional[int] = None
    notes: Optional[str] = None

    @validator('driver_license_expiry')
    def license_not_expired(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Driver license is expired')
        return v

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    driver_license_expiry: Optional[datetime] = None
    status: Optional[DriverStatus] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    organization_unit_id: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class DriverInDBBase(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

class Driver(DriverInDBBase):
    pass

class DriverInDB(DriverInDBBase):
    pass
