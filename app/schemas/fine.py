from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from ..models.fine import FineStatus, FineType

class FineBase(BaseModel):
    vehicle_id: int
    driver_id: Optional[int] = None
    fine_number: str = Field(..., min_length=5, max_length=50)
    fine_type: FineType
    fine_date: datetime
    notification_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    description: str = Field(..., min_length=10)
    amount: Decimal = Field(..., ge=0)
    reduced_amount: Optional[Decimal] = Field(None, ge=0)
    payment_deadline: Optional[datetime] = None
    reduced_payment_deadline: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    payment_amount: Optional[Decimal] = Field(None, ge=0)
    status: FineStatus = FineStatus.PENDING
    responsible_driver: Optional[str] = Field(None, max_length=100)
    appeal_filed: bool = False
    appeal_date: Optional[datetime] = None
    appeal_reason: Optional[str] = None
    appeal_result: Optional[str] = Field(None, max_length=100)
    document_path: Optional[str] = Field(None, max_length=500)
    payment_receipt_path: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None

class FineCreate(FineBase):
    pass

class FineUpdate(BaseModel):
    status: Optional[FineStatus] = None
    payment_date: Optional[datetime] = None
    payment_amount: Optional[Decimal] = Field(None, ge=0)
    responsible_driver: Optional[str] = Field(None, max_length=100)
    appeal_filed: Optional[bool] = None
    appeal_date: Optional[datetime] = None
    appeal_reason: Optional[str] = None
    appeal_result: Optional[str] = Field(None, max_length=100)
    payment_receipt_path: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None

class FineInDBBase(FineBase):
    id: int
    created_at: datetime
    created_by: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class Fine(FineInDBBase):
    pass

class FineInDB(FineInDBBase):
    pass
