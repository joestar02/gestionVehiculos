from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app import models, schemas

router = APIRouter()

# Accidents
@router.post("/accidents", response_model=schemas.accident.Accident)
def create_accident(
    accident: schemas.accident.AccidentCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == accident.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_accident = models.Accident(**accident.dict(), created_by=current_user.id)
    db.add(db_accident)
    db.commit()
    db.refresh(db_accident)
    return db_accident

@router.get("/accidents", response_model=List[schemas.accident.Accident])
def read_accidents(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    query = db.query(models.Accident)
    if vehicle_id:
        query = query.filter(models.Accident.vehicle_id == vehicle_id)
    return query.order_by(models.Accident.accident_date.desc()).offset(skip).limit(limit).all()

# Taxes
@router.post("/taxes", response_model=schemas.tax.VehicleTax)
def create_tax(
    tax: schemas.tax.VehicleTaxCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == tax.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_tax = models.VehicleTax(**tax.dict())
    db.add(db_tax)
    db.commit()
    db.refresh(db_tax)
    return db_tax

@router.get("/taxes", response_model=List[schemas.tax.VehicleTax])
def read_taxes(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    query = db.query(models.VehicleTax)
    if vehicle_id:
        query = query.filter(models.VehicleTax.vehicle_id == vehicle_id)
    return query.order_by(models.VehicleTax.due_date.desc()).offset(skip).limit(limit).all()

# Fines
@router.post("/fines", response_model=schemas.fine.Fine)
def create_fine(
    fine: schemas.fine.FineCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == fine.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_fine = models.Fine(**fine.dict(), created_by=current_user.id)
    db.add(db_fine)
    db.commit()
    db.refresh(db_fine)
    return db_fine

@router.get("/fines", response_model=List[schemas.fine.Fine])
def read_fines(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    query = db.query(models.Fine)
    if vehicle_id:
        query = query.filter(models.Fine.vehicle_id == vehicle_id)
    return query.order_by(models.Fine.fine_date.desc()).offset(skip).limit(limit).all()

# Authorizations
@router.post("/authorizations", response_model=schemas.authorization.UrbanAccessAuthorization)
def create_authorization(
    authorization: schemas.authorization.UrbanAccessAuthorizationCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == authorization.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_auth = models.UrbanAccessAuthorization(**authorization.dict())
    db.add(db_auth)
    db.commit()
    db.refresh(db_auth)
    return db_auth

@router.get("/authorizations", response_model=List[schemas.authorization.UrbanAccessAuthorization])
def read_authorizations(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    query = db.query(models.UrbanAccessAuthorization)
    if vehicle_id:
        query = query.filter(models.UrbanAccessAuthorization.vehicle_id == vehicle_id)
    return query.offset(skip).limit(limit).all()

# Renting
@router.post("/renting", response_model=schemas.renting.RentingContract)
def create_renting(
    contract: schemas.renting.RentingContractCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == contract.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db_contract = models.RentingContract(**contract.dict())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

@router.get("/renting", response_model=List[schemas.renting.RentingContract])
def read_renting_contracts(
    skip: int = 0,
    limit: int = 100,
    vehicle_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    query = db.query(models.RentingContract)
    if vehicle_id:
        query = query.filter(models.RentingContract.vehicle_id == vehicle_id)
    return query.offset(skip).limit(limit).all()
