from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class UrbanAccessAuthorizationBase(BaseModel):
    vehicle_id: int
    authorization_type: str = Field(..., min_length=2, max_length=100)
    issuing_authority: str = Field(..., min_length=2, max_length=100)
    authorization_number: str = Field(..., min_length=2, max_length=50)
    zone_description: Optional[str] = Field(None, max_length=200)
    start_date: datetime
    end_date: datetime
    conditions: Optional[str] = None
    document_path: Optional[str] = Field(None, max_length=500)
    alert_days_before_expiry: int = Field(30, ge=1, le=365)
    notes: Optional[str] = None

    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class UrbanAccessAuthorizationCreate(UrbanAccessAuthorizationBase):
    pass

class UrbanAccessAuthorizationUpdate(BaseModel):
    end_date: Optional[datetime] = None
    conditions: Optional[str] = None
    document_path: Optional[str] = Field(None, max_length=500)
    alert_days_before_expiry: Optional[int] = Field(None, ge=1, le=365)
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class UrbanAccessAuthorizationInDBBase(UrbanAccessAuthorizationBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UrbanAccessAuthorization(UrbanAccessAuthorizationInDBBase):
    pass

class UrbanAccessAuthorizationInDB(UrbanAccessAuthorizationInDBBase):
    pass
