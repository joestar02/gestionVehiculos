from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app import models, schemas

router = APIRouter()

@router.post("/", response_model=schemas.provider.Provider)
def create_provider(
    provider: schemas.provider.ProviderCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create new provider"""
    # Check if name already exists
    db_provider = db.query(models.Provider).filter(
        models.Provider.name == provider.name
    ).first()
    if db_provider:
        raise HTTPException(status_code=400, detail="Provider name already exists")
    
    # Create new provider
    db_provider = models.Provider(**provider.dict())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

@router.get("/", response_model=List[schemas.provider.Provider])
def read_providers(
    skip: int = 0,
    limit: int = 100,
    provider_type: Optional[str] = None,
    organization_unit_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get all providers with optional filters"""
    query = db.query(models.Provider).filter(models.Provider.is_active == True)
    
    if provider_type:
        query = query.filter(models.Provider.provider_type == provider_type)
    if organization_unit_id:
        query = query.filter(models.Provider.organization_unit_id == organization_unit_id)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{provider_id}", response_model=schemas.provider.Provider)
def read_provider(
    provider_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get provider by ID"""
    db_provider = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if db_provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return db_provider

@router.put("/{provider_id}", response_model=schemas.provider.Provider)
def update_provider(
    provider_id: int,
    provider: schemas.provider.ProviderUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Update provider"""
    db_provider = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if db_provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    update_data = provider.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_provider, field, value)
    
    db_provider.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_provider)
    return db_provider

@router.delete("/{provider_id}", response_model=schemas.provider.Provider)
def delete_provider(
    provider_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Soft delete provider"""
    db_provider = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if db_provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    db_provider.is_active = False
    db_provider.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_provider)
    return db_provider
