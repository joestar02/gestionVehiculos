from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import Optional
from decimal import Decimal

class RentingContractBase(BaseModel):
    vehicle_id: int
    company_name: str = Field(..., min_length=2, max_length=100)
    contract_number: str = Field(..., min_length=2, max_length=50)
    start_date: datetime
    end_date: datetime
    monthly_cost: Optional[Decimal] = Field(None, ge=0)
    total_cost: Optional[Decimal] = Field(None, ge=0)
    km_limit: Optional[int] = Field(None, ge=0)
    excess_km_cost: Optional[Decimal] = Field(None, ge=0)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    terms_and_conditions: Optional[str] = None
    document_path: Optional[str] = Field(None, max_length=500)
    alert_days_before_expiry: int = Field(30, ge=1, le=365)
    notes: Optional[str] = None

    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class RentingContractCreate(RentingContractBase):
    pass

class RentingContractUpdate(BaseModel):
    end_date: Optional[datetime] = None
    monthly_cost: Optional[Decimal] = Field(None, ge=0)
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    terms_and_conditions: Optional[str] = None
    document_path: Optional[str] = Field(None, max_length=500)
    alert_days_before_expiry: Optional[int] = Field(None, ge=1, le=365)
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class RentingContractInDBBase(RentingContractBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RentingContract(RentingContractInDBBase):
    pass

class RentingContractInDB(RentingContractInDBBase):
    pass
