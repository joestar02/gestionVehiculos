from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.models.vehicle import VehicleType, OwnershipType, VehicleStatus


class VehicleBase(BaseModel):
    license_plate: str = Field(..., min_length=1, max_length=20, description="License plate of the vehicle")
    make: str = Field(..., min_length=1, max_length=50, description="Vehicle make/brand")
    model: str = Field(..., min_length=1, max_length=50, description="Vehicle model")
    year: int = Field(..., ge=1900, description="Manufacturing year")
    color: Optional[str] = Field(None, max_length=30, description="Vehicle color")
    vin: Optional[str] = Field(None, min_length=17, max_length=17, description="Vehicle Identification Number")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE, description="Current status")
    ownership_type: OwnershipType = Field(..., description="Ownership type")
    organization_unit_id: Optional[int] = Field(None, description="Organization unit ID")
    current_mileage: int = Field(default=0, ge=0, description="Current mileage")
    fuel_type: Optional[str] = Field(None, max_length=20, description="Fuel type")
    fuel_capacity: Optional[int] = Field(None, ge=0, description="Fuel capacity in liters")
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v > datetime.now().year + 1:
            raise ValueError('Year cannot be more than next year')
        return v


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle"""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating an existing vehicle"""
    license_plate: Optional[str] = Field(None, min_length=1, max_length=20)
    make: Optional[str] = Field(None, min_length=1, max_length=50)
    model: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1900)
    color: Optional[str] = Field(None, max_length=30)
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    vehicle_type: Optional[VehicleType] = None
    status: Optional[VehicleStatus] = None
    ownership_type: Optional[OwnershipType] = None
    organization_unit_id: Optional[int] = None
    current_mileage: Optional[int] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, max_length=20)
    fuel_capacity: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class Vehicle(VehicleBase):
    """Schema for vehicle response"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True