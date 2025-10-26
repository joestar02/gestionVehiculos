"""Maintenance service"""
from typing import List, Optional
from datetime import datetime
from app.extensions import db
from app.models.maintenance import MaintenanceRecord, MaintenanceType, MaintenanceStatus
from app.services.provider_service import ProviderService

class MaintenanceService:
    """Service for maintenance operations"""
    
    @staticmethod
    def get_all_maintenance_records() -> List[MaintenanceRecord]:
        """Get all maintenance records"""
        return MaintenanceRecord.query.order_by(MaintenanceRecord.scheduled_date.desc()).all()
    
    @staticmethod
    def get_maintenance_by_id(maintenance_id: int) -> Optional[MaintenanceRecord]:
        """Get maintenance record by ID"""
        return MaintenanceRecord.query.get(maintenance_id)
    
    @staticmethod
    def get_maintenance_by_vehicle(vehicle_id: int) -> List[MaintenanceRecord]:
        """Get maintenance records for a specific vehicle"""
        return MaintenanceRecord.query.filter_by(vehicle_id=vehicle_id).order_by(
            MaintenanceRecord.scheduled_date.desc()
        ).all()
    
    @staticmethod
    def get_pending_maintenance() -> List[MaintenanceRecord]:
        """Get pending maintenance records"""
        return MaintenanceRecord.query.filter_by(
            status=MaintenanceStatus.SCHEDULED
        ).order_by(MaintenanceRecord.scheduled_date).all()
    
    @staticmethod
    def create_maintenance(vehicle_id: int, maintenance_type: MaintenanceType,
                          scheduled_date, description: str,
                          estimated_cost: Optional[float] = None,
                          provider_id: Optional[int] = None,
                          notes: Optional[str] = None) -> MaintenanceRecord:
        """Create a new maintenance record"""
        provider_name = None
        if provider_id:
            prov = ProviderService.get_provider_by_id(provider_id)
            if prov:
                provider_name = prov.name

        maintenance = MaintenanceRecord(
            vehicle_id=vehicle_id,
            maintenance_type=maintenance_type,
            scheduled_date=scheduled_date,
            description=description,
            cost=estimated_cost,
            provider_id=provider_id,
            provider_name=provider_name,
            notes=notes,
            status=MaintenanceStatus.SCHEDULED
        )
        
        db.session.add(maintenance)
        db.session.commit()
        db.session.refresh(maintenance)
        
        return maintenance
    
    @staticmethod
    def update_maintenance(maintenance_id: int, **kwargs) -> Optional[MaintenanceRecord]:
        """Update maintenance record"""
        maintenance = MaintenanceService.get_maintenance_by_id(maintenance_id)
        if not maintenance:
            return None
        
        # If provider_id provided, resolve provider_name
        if 'provider_id' in kwargs and kwargs.get('provider_id') is not None:
            prov = ProviderService.get_provider_by_id(kwargs.get('provider_id'))
            if prov:
                maintenance.provider_name = prov.name
            maintenance.provider_id = kwargs.get('provider_id')

        for key, value in kwargs.items():
            # skip provider_id since already handled
            if key == 'provider_id':
                continue
            if hasattr(maintenance, key) and value is not None:
                setattr(maintenance, key, value)
        
        db.session.commit()
        db.session.refresh(maintenance)
        
        return maintenance
    
    @staticmethod
    def complete_maintenance(maintenance_id: int, actual_cost: float,
                           completion_notes: Optional[str] = None) -> Optional[MaintenanceRecord]:
        """Mark maintenance as completed"""
        maintenance = MaintenanceService.get_maintenance_by_id(maintenance_id)
        if not maintenance:
            return None
        
        maintenance.status = MaintenanceStatus.COMPLETED
        maintenance.completed_date = datetime.utcnow()
        maintenance.actual_cost = actual_cost
        if completion_notes:
            maintenance.notes = (maintenance.notes or '') + '\n' + completion_notes
        
        db.session.commit()
        db.session.refresh(maintenance)
        
        return maintenance
    
    @staticmethod
    def get_active_maintenances() -> List[MaintenanceRecord]:
        """Get all active maintenances (scheduled date hasn't passed)"""
        return MaintenanceRecord.query.filter(
            MaintenanceRecord.scheduled_date >= datetime.utcnow(),
            MaintenanceRecord.status != MaintenanceStatus.COMPLETED,
            MaintenanceRecord.status != MaintenanceStatus.CANCELLED
        ).order_by(MaintenanceRecord.scheduled_date).all()
    
    @staticmethod
    def cancel_maintenance(maintenance_id: int, reason: str) -> Optional[MaintenanceRecord]:
        """Cancel a maintenance record"""
        maintenance = MaintenanceService.get_maintenance_by_id(maintenance_id)
        if not maintenance:
            return None
        
        maintenance.status = MaintenanceStatus.CANCELLED
        maintenance.notes = (maintenance.notes or '') + f'\nCancelado: {reason}'
        
        db.session.commit()
        db.session.refresh(maintenance)
        
        return maintenance
