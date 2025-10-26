from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from decimal import Decimal
from ..models.tax import TaxType, PaymentStatus

class VehicleTaxBase(BaseModel):
    vehicle_id: int
    tax_type: TaxType
    tax_year: int = Field(..., ge=2000, le=2100)
    amount: Decimal = Field(..., ge=0)
    due_date: datetime
    payment_date: Optional[datetime] = None
    payment_status: PaymentStatus = PaymentStatus.PENDING
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=100)
    document_path: Optional[str] = Field(None, max_length=500)
    alert_days_before: int = Field(15, ge=1, le=365)
    notes: Optional[str] = None

    @validator('tax_year')
    def valid_year(cls, v):
        current_year = datetime.now().year
        if v > current_year + 1:
            raise ValueError(f'Tax year cannot be more than {current_year + 1}')
        return v

class VehicleTaxCreate(VehicleTaxBase):
    pass

class VehicleTaxUpdate(BaseModel):
    payment_date: Optional[datetime] = None
    payment_status: Optional[PaymentStatus] = None
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_reference: Optional[str] = Field(None, max_length=100)
    document_path: Optional[str] = Field(None, max_length=500)
    alert_days_before: Optional[int] = Field(None, ge=1, le=365)
    notes: Optional[str] = None

class VehicleTaxInDBBase(VehicleTaxBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VehicleTax(VehicleTaxInDBBase):
    pass

class VehicleTaxInDB(VehicleTaxInDBBase):
    pass
