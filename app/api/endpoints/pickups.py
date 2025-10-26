from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.vehicle_pickup.VehiclePickup)
def create_pickup(
    pickup: schemas.vehicle_pickup.VehiclePickupCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Register vehicle pickup"""
    # Check if reservation exists
    reservation = db.query(models.Reservation).filter(
        models.Reservation.id == pickup.reservation_id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    # Check if pickup already exists for this reservation
    existing = db.query(models.VehiclePickup).filter(
        models.VehiclePickup.reservation_id == pickup.reservation_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Pickup already registered for this reservation")
    
    # Create pickup
    db_pickup = models.VehiclePickup(**pickup.dict())
    db.add(db_pickup)
    
    # Update reservation status
    if pickup.pickup_status == models.PickupStatus.TAKEN:
        reservation.status = models.ReservationStatus.COMPLETED
    else:
        reservation.status = models.ReservationStatus.NO_SHOW
    
    # Update vehicle mileage if taken
    if pickup.pickup_status == models.PickupStatus.TAKEN and pickup.end_mileage:
        vehicle = db.query(models.Vehicle).filter(
            models.Vehicle.id == pickup.vehicle_id
        ).first()
        if vehicle:
            vehicle.current_mileage = pickup.end_mileage
            vehicle.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_pickup)
    return db_pickup

@router.get("/", response_model=List[schemas.vehicle_pickup.VehiclePickup])
def read_pickups(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    pickup_status: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all pickups with optional filters"""
    query = db.query(models.VehiclePickup)
    
    if vehicle_id:
        query = query.filter(models.VehiclePickup.vehicle_id == vehicle_id)
    if driver_id:
        query = query.filter(models.VehiclePickup.driver_id == driver_id)
    if pickup_status:
        query = query.filter(models.VehiclePickup.pickup_status == pickup_status)
    
    return query.order_by(models.VehiclePickup.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{pickup_id}", response_model=schemas.vehicle_pickup.VehiclePickup)
def read_pickup(
    pickup_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get pickup by ID"""
    db_pickup = db.query(models.VehiclePickup).filter(
        models.VehiclePickup.id == pickup_id
    ).first()
    if db_pickup is None:
        raise HTTPException(status_code=404, detail="Pickup not found")
    return db_pickup

@router.put("/{pickup_id}", response_model=schemas.vehicle_pickup.VehiclePickup)
def update_pickup(
    pickup_id: int,
    pickup: schemas.vehicle_pickup.VehiclePickupUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Update pickup (mainly for return information)"""
    db_pickup = db.query(models.VehiclePickup).filter(
        models.VehiclePickup.id == pickup_id
    ).first()
    if db_pickup is None:
        raise HTTPException(status_code=404, detail="Pickup not found")
    
    update_data = pickup.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pickup, field, value)
    
    # Update vehicle mileage if end_mileage is provided
    if pickup.end_mileage:
        vehicle = db.query(models.Vehicle).filter(
            models.Vehicle.id == db_pickup.vehicle_id
        ).first()
        if vehicle:
            vehicle.current_mileage = pickup.end_mileage
            vehicle.updated_at = datetime.utcnow()
    
    db_pickup.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_pickup)
    return db_pickup

@router.get("/not-taken/report", response_model=List[schemas.vehicle_pickup.VehiclePickup])
def get_not_taken_report(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get report of vehicles not taken"""
    pickups = db.query(models.VehiclePickup).filter(
        models.VehiclePickup.pickup_status == models.PickupStatus.NOT_TAKEN
    ).order_by(models.VehiclePickup.created_at.desc()).offset(skip).limit(limit).all()
    
    return pickups
