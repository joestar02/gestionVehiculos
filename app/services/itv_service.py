"""ITV service"""
from typing import List, Optional
from datetime import datetime, timedelta
from app.extensions import db
from app.models.itv import ITVRecord, ITVStatus, ITVResult

class ITVService:
    @staticmethod
    def get_all_itv_records() -> List[ITVRecord]:
        """Get all ITV records"""
        return ITVRecord.query.order_by(ITVRecord.inspection_date.desc()).all()
    
    @staticmethod
    def get_itv_by_id(record_id: int) -> Optional[ITVRecord]:
        """Get ITV record by ID"""
        return ITVRecord.query.get(record_id)
    
    @staticmethod
    def get_itv_by_vehicle(vehicle_id: int) -> List[ITVRecord]:
        """Get all ITV records for a vehicle"""
        return ITVRecord.query.filter_by(vehicle_id=vehicle_id).order_by(ITVRecord.inspection_date.desc()).all()
    
    @staticmethod
    def get_latest_itv(vehicle_id: int) -> Optional[ITVRecord]:
        """Get the latest ITV record for a vehicle"""
        return ITVRecord.query.filter_by(vehicle_id=vehicle_id).order_by(ITVRecord.inspection_date.desc()).first()
    
    @staticmethod
    def get_expired_itvs() -> List[ITVRecord]:
        """Get all expired ITV records"""
        return ITVRecord.query.filter(ITVRecord.expiry_date < datetime.now()).all()
    
    @staticmethod
    def get_expiring_soon(days: int = 30) -> List[ITVRecord]:
        """Get ITV records expiring soon"""
        expiry_threshold = datetime.now() + timedelta(days=days)
        return ITVRecord.query.filter(
            ITVRecord.expiry_date <= expiry_threshold,
            ITVRecord.expiry_date >= datetime.now()
        ).all()
    
    @staticmethod
    def create_itv(
        vehicle_id: int,
        inspection_date: datetime,
        expiry_date: datetime,
        result: ITVResult,
        **kwargs
    ) -> ITVRecord:
        """Create new ITV record"""
        itv = ITVRecord(
            vehicle_id=vehicle_id,
            inspection_date=inspection_date,
            expiry_date=expiry_date,
            result=result,
            status=ITVStatus.PASSED if result == ITVResult.FAVORABLE else ITVStatus.FAILED,
            **kwargs
        )
        db.session.add(itv)
        db.session.commit()
        return itv
    
    @staticmethod
    def update_itv(record_id: int, **kwargs) -> Optional[ITVRecord]:
        """Update ITV record"""
        itv = ITVRecord.query.get(record_id)
        if itv:
            for key, value in kwargs.items():
                if hasattr(itv, key):
                    setattr(itv, key, value)
            db.session.commit()
        return itv
    
    @staticmethod
    def delete_itv(record_id: int) -> bool:
        """Delete ITV record"""
        itv = ITVRecord.query.get(record_id)
        if itv:
            db.session.delete(itv)
            db.session.commit()
            return True
        return False
