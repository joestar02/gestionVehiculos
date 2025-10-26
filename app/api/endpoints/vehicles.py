from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.vehicle.Vehicle)
def create_vehicle(
    vehicle: schemas.vehicle.VehicleCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create new vehicle"""
    # Check if license plate already exists
    db_vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.license_plate == vehicle.license_plate
    ).first()
    if db_vehicle:
        raise HTTPException(status_code=400, detail="License plate already registered")
    
    # Check if VIN already exists
    if vehicle.vin:
        db_vin = db.query(models.Vehicle).filter(
            models.Vehicle.vin == vehicle.vin
        ).first()
        if db_vin:
            raise HTTPException(status_code=400, detail="VIN already registered")
    
    # Create new vehicle
    db_vehicle = models.Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@router.get("/", response_model=List[schemas.vehicle.Vehicle])
def read_vehicles(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    organization_unit_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all vehicles with optional filters"""
    query = db.query(models.Vehicle).filter(models.Vehicle.is_active == True)
    
    if status:
        query = query.filter(models.Vehicle.status == status)
    if vehicle_type:
        query = query.filter(models.Vehicle.vehicle_type == vehicle_type)
    if organization_unit_id:
        query = query.filter(models.Vehicle.organization_unit_id == organization_unit_id)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{vehicle_id}", response_model=schemas.vehicle.Vehicle)
def read_vehicle(
    vehicle_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get vehicle by ID"""
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return db_vehicle

@router.put("/{vehicle_id}", response_model=schemas.vehicle.Vehicle)
def update_vehicle(
    vehicle_id: int,
    vehicle: schemas.vehicle.VehicleUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Update vehicle"""
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    update_data = vehicle.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    
    db_vehicle.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@router.delete("/{vehicle_id}", response_model=schemas.vehicle.Vehicle)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Soft delete vehicle"""
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if db_vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_vehicle.is_active = False
    db_vehicle.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle
