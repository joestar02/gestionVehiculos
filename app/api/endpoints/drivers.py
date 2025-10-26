from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.driver.Driver)
def create_driver(
    driver: schemas.driver.DriverCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create new driver"""
    # Check if document number already exists
    db_driver = db.query(models.Driver).filter(
        models.Driver.document_number == driver.document_number
    ).first()
    if db_driver:
        raise HTTPException(status_code=400, detail="Document number already registered")
    
    # Check if email already exists
    db_email = db.query(models.Driver).filter(
        models.Driver.email == driver.email
    ).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if license number already exists
    db_license = db.query(models.Driver).filter(
        models.Driver.driver_license_number == driver.driver_license_number
    ).first()
    if db_license:
        raise HTTPException(status_code=400, detail="Driver license number already registered")
    
    # Create new driver
    db_driver = models.Driver(**driver.dict(), created_by=current_user.id)
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

@router.get("/", response_model=List[schemas.driver.Driver])
def read_drivers(
    skip: int = 0,
    limit: int = 100,
    driver_type: Optional[str] = None,
    status: Optional[str] = None,
    organization_unit_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all drivers with optional filters"""
    query = db.query(models.Driver).filter(models.Driver.is_active == True)
    
    if driver_type:
        query = query.filter(models.Driver.driver_type == driver_type)
    if status:
        query = query.filter(models.Driver.status == status)
    if organization_unit_id:
        query = query.filter(models.Driver.organization_unit_id == organization_unit_id)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{driver_id}", response_model=schemas.driver.Driver)
def read_driver(
    driver_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get driver by ID"""
    db_driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return db_driver

@router.put("/{driver_id}", response_model=schemas.driver.Driver)
def update_driver(
    driver_id: int,
    driver: schemas.driver.DriverUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Update driver"""
    db_driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    update_data = driver.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_driver, field, value)
    
    db_driver.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_driver)
    return db_driver

@router.delete("/{driver_id}", response_model=schemas.driver.Driver)
def delete_driver(
    driver_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Soft delete driver"""
    db_driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    db_driver.is_active = False
    db_driver.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_driver)
    return db_driver

@router.post("/{driver_id}/vehicles/{vehicle_id}", response_model=dict)
def associate_driver_to_vehicle(
    driver_id: int,
    vehicle_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Associate driver to vehicle"""
    # Check if driver exists
    driver = db.query(models.Driver).filter(models.Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Check if vehicle exists
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Check if association already exists
    existing = db.query(models.VehicleDriverAssociation).filter(
        models.VehicleDriverAssociation.driver_id == driver_id,
        models.VehicleDriverAssociation.vehicle_id == vehicle_id,
        models.VehicleDriverAssociation.is_active == True
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Association already exists")
    
    # Create association
    association = models.VehicleDriverAssociation(
        driver_id=driver_id,
        vehicle_id=vehicle_id,
        created_by=current_user.id
    )
    db.add(association)
    db.commit()
    
    return {"message": "Driver associated to vehicle successfully"}

@router.delete("/{driver_id}/vehicles/{vehicle_id}", response_model=dict)
def remove_driver_from_vehicle(
    driver_id: int,
    vehicle_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Remove driver from vehicle"""
    association = db.query(models.VehicleDriverAssociation).filter(
        models.VehicleDriverAssociation.driver_id == driver_id,
        models.VehicleDriverAssociation.vehicle_id == vehicle_id,
        models.VehicleDriverAssociation.is_active == True
    ).first()
    
    if not association:
        raise HTTPException(status_code=404, detail="Association not found")
    
    association.is_active = False
    association.end_date = datetime.utcnow()
    association.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Driver removed from vehicle successfully"}
