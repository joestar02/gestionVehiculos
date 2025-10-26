from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app import models, schemas

router = APIRouter()

# Maintenance Records
@router.post("/", response_model=schemas.maintenance.MaintenanceRecord)
def create_maintenance_record(
    maintenance: schemas.maintenance.MaintenanceRecordCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create new maintenance record"""
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == maintenance.vehicle_id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_maintenance = models.MaintenanceRecord(
        **maintenance.dict(),
        created_by=current_user.id
    )
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance

@router.get("/", response_model=List[schemas.maintenance.MaintenanceRecord])
def read_maintenance_records(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    maintenance_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all maintenance records with optional filters"""
    query = db.query(models.MaintenanceRecord)
    
    if vehicle_id:
        query = query.filter(models.MaintenanceRecord.vehicle_id == vehicle_id)
    if maintenance_type:
        query = query.filter(models.MaintenanceRecord.maintenance_type == maintenance_type)
    if status:
        query = query.filter(models.MaintenanceRecord.status == status)
    
    return query.order_by(models.MaintenanceRecord.scheduled_date.desc()).offset(skip).limit(limit).all()

@router.get("/{maintenance_id}", response_model=schemas.maintenance.MaintenanceRecord)
def read_maintenance_record(
    maintenance_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get maintenance record by ID"""
    db_maintenance = db.query(models.MaintenanceRecord).filter(
        models.MaintenanceRecord.id == maintenance_id
    ).first()
    if db_maintenance is None:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return db_maintenance

@router.put("/{maintenance_id}", response_model=schemas.maintenance.MaintenanceRecord)
def update_maintenance_record(
    maintenance_id: int,
    maintenance: schemas.maintenance.MaintenanceRecordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Update maintenance record"""
    db_maintenance = db.query(models.MaintenanceRecord).filter(
        models.MaintenanceRecord.id == maintenance_id
    ).first()
    if db_maintenance is None:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    
    update_data = maintenance.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_maintenance, field, value)
    
    db_maintenance.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance

# ITV Records
@router.post("/itv", response_model=schemas.maintenance.ITVRecord)
def create_itv_record(
    itv: schemas.maintenance.ITVRecordCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create new ITV record"""
    vehicle = db.query(models.Vehicle).filter(
        models.Vehicle.id == itv.vehicle_id
    ).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_itv = models.ITVRecord(**itv.dict())
    db.add(db_itv)
    db.commit()
    db.refresh(db_itv)
    return db_itv

@router.get("/itv", response_model=List[schemas.maintenance.ITVRecord])
def read_itv_records(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all ITV records with optional filters"""
    query = db.query(models.ITVRecord)
    
    if vehicle_id:
        query = query.filter(models.ITVRecord.vehicle_id == vehicle_id)
    
    return query.order_by(models.ITVRecord.inspection_date.desc()).offset(skip).limit(limit).all()

@router.get("/itv/{itv_id}", response_model=schemas.maintenance.ITVRecord)
def read_itv_record(
    itv_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get ITV record by ID"""
    db_itv = db.query(models.ITVRecord).filter(
        models.ITVRecord.id == itv_id
    ).first()
    if db_itv is None:
        raise HTTPException(status_code=404, detail="ITV record not found")
    return db_itv

@router.put("/itv/{itv_id}", response_model=schemas.maintenance.ITVRecord)
def update_itv_record(
    itv_id: int,
    itv: schemas.maintenance.ITVRecordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Update ITV record"""
    db_itv = db.query(models.ITVRecord).filter(
        models.ITVRecord.id == itv_id
    ).first()
    if db_itv is None:
        raise HTTPException(status_code=404, detail="ITV record not found")
    
    update_data = itv.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_itv, field, value)
    
    db_itv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_itv)
    return db_itv

@router.get("/itv/expiring-soon/list", response_model=List[schemas.maintenance.ITVRecord])
def get_expiring_itv_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get ITV records expiring soon"""
    from datetime import timedelta
    
    # Get records where next_inspection_date is within alert_days_before
    records = db.query(models.ITVRecord).all()
    expiring = [r for r in records if r.is_expiring_soon]
    
    return expiring[skip:skip+limit]
