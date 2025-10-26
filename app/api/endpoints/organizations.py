from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.api import deps
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.organization.OrganizationUnit)
def create_organization_unit(
    org_unit: schemas.organization.OrganizationUnitCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create new organization unit"""
    # Check if code already exists
    existing = db.query(models.OrganizationUnit).filter(
        models.OrganizationUnit.code == org_unit.code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization unit code already exists")
    
    # Check if name already exists
    existing_name = db.query(models.OrganizationUnit).filter(
        models.OrganizationUnit.name == org_unit.name
    ).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="Organization unit name already exists")
    
    db_org_unit = models.OrganizationUnit(**org_unit.dict())
    db.add(db_org_unit)
    db.commit()
    db.refresh(db_org_unit)
    return db_org_unit

@router.get("/", response_model=List[schemas.organization.OrganizationUnit])
def read_organization_units(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all organization units"""
    return db.query(models.OrganizationUnit).filter(
        models.OrganizationUnit.is_active == True
    ).offset(skip).limit(limit).all()

@router.get("/{org_unit_id}", response_model=schemas.organization.OrganizationUnit)
def read_organization_unit(
    org_unit_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get organization unit by ID"""
    db_org_unit = db.query(models.OrganizationUnit).filter(
        models.OrganizationUnit.id == org_unit_id
    ).first()
    if db_org_unit is None:
        raise HTTPException(status_code=404, detail="Organization unit not found")
    return db_org_unit

@router.put("/{org_unit_id}", response_model=schemas.organization.OrganizationUnit)
def update_organization_unit(
    org_unit_id: int,
    org_unit: schemas.organization.OrganizationUnitUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Update organization unit"""
    db_org_unit = db.query(models.OrganizationUnit).filter(
        models.OrganizationUnit.id == org_unit_id
    ).first()
    if db_org_unit is None:
        raise HTTPException(status_code=404, detail="Organization unit not found")
    
    update_data = org_unit.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_org_unit, field, value)
    
    db_org_unit.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_org_unit)
    return db_org_unit

@router.delete("/{org_unit_id}", response_model=schemas.organization.OrganizationUnit)
def delete_organization_unit(
    org_unit_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Soft delete organization unit"""
    db_org_unit = db.query(models.OrganizationUnit).filter(
        models.OrganizationUnit.id == org_unit_id
    ).first()
    if db_org_unit is None:
        raise HTTPException(status_code=404, detail="Organization unit not found")
    
    db_org_unit.is_active = False
    db_org_unit.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_org_unit)
    return db_org_unit
