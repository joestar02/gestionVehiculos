from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date, time

from app.api import deps
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.reservation.Reservation)
def create_reservation(
    reservation: schemas.reservation.ReservationCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create new reservation"""
    # Check if vehicle exists
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == reservation.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Check if driver exists
    driver = db.query(models.Driver).filter(models.Driver.id == reservation.driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Check for overlapping reservations
    overlapping = db.query(models.Reservation).filter(
        models.Reservation.vehicle_id == reservation.vehicle_id,
        models.Reservation.reservation_date == reservation.reservation_date,
        models.Reservation.status.in_([
            models.ReservationStatus.PENDING,
            models.ReservationStatus.CONFIRMED
        ]),
        or_(
            and_(
                models.Reservation.start_time <= reservation.start_time,
                models.Reservation.end_time > reservation.start_time
            ),
            and_(
                models.Reservation.start_time < reservation.end_time,
                models.Reservation.end_time >= reservation.end_time
            ),
            and_(
                models.Reservation.start_time >= reservation.start_time,
                models.Reservation.end_time <= reservation.end_time
            )
        )
    ).first()
    
    if overlapping:
        raise HTTPException(
            status_code=400,
            detail="Vehicle is already reserved for this time slot"
        )
    
    # Create reservation
    db_reservation = models.Reservation(
        **reservation.dict(),
        created_by=current_user.id,
        status=models.ReservationStatus.CONFIRMED
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@router.get("/", response_model=List[schemas.reservation.Reservation])
def read_reservations(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all reservations with optional filters"""
    query = db.query(models.Reservation)
    
    if vehicle_id:
        query = query.filter(models.Reservation.vehicle_id == vehicle_id)
    if driver_id:
        query = query.filter(models.Reservation.driver_id == driver_id)
    if status:
        query = query.filter(models.Reservation.status == status)
    if date_from:
        query = query.filter(models.Reservation.reservation_date >= date_from)
    if date_to:
        query = query.filter(models.Reservation.reservation_date <= date_to)
    
    return query.order_by(models.Reservation.reservation_date.desc()).offset(skip).limit(limit).all()

@router.get("/{reservation_id}", response_model=schemas.reservation.Reservation)
def read_reservation(
    reservation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get reservation by ID"""
    db_reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return db_reservation

@router.put("/{reservation_id}", response_model=schemas.reservation.Reservation)
def update_reservation(
    reservation_id: int,
    reservation: schemas.reservation.ReservationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Update reservation"""
    db_reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if db_reservation.status == models.ReservationStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot update cancelled reservation")
    
    update_data = reservation.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reservation, field, value)
    
    db_reservation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@router.post("/{reservation_id}/cancel", response_model=schemas.reservation.Reservation)
def cancel_reservation(
    reservation_id: int,
    cancel_data: schemas.reservation.ReservationCancel,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Cancel reservation"""
    db_reservation = db.query(models.Reservation).filter(
        models.Reservation.id == reservation_id
    ).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if db_reservation.status == models.ReservationStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Reservation already cancelled")
    
    db_reservation.status = models.ReservationStatus.CANCELLED
    db_reservation.cancellation_reason = cancel_data.cancellation_reason
    db_reservation.cancelled_at = datetime.utcnow()
    db_reservation.cancelled_by = current_user.id
    db_reservation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_reservation)
    return db_reservation
