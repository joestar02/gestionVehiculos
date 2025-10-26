from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class OrganizationUnitBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manager_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)

class OrganizationUnitCreate(OrganizationUnitBase):
    pass

class OrganizationUnitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    manager_name: Optional[str] = Field(None, max_length=100)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

class OrganizationUnitInDBBase(OrganizationUnitBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrganizationUnit(OrganizationUnitInDBBase):
    pass

class OrganizationUnitInDB(OrganizationUnitInDBBase):
    pass
