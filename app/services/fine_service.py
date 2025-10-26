"""Fine service"""
from typing import List, Optional
from datetime import datetime
from app.extensions import db
from app.models.fine import Fine, FineStatus, FineType

class FineService:
    @staticmethod
    def get_all_fines() -> List[Fine]:
        """Get all fines"""
        return Fine.query.order_by(Fine.fine_date.desc()).all()
    
    @staticmethod
    def get_fine_by_id(fine_id: int) -> Optional[Fine]:
        """Get fine by ID"""
        return Fine.query.get(fine_id)
    
    @staticmethod
    def get_fines_by_vehicle(vehicle_id: int) -> List[Fine]:
        """Get all fines for a vehicle"""
        return Fine.query.filter_by(vehicle_id=vehicle_id).order_by(Fine.fine_date.desc()).all()
    
    @staticmethod
    def get_fines_by_driver(driver_id: int) -> List[Fine]:
        """Get all fines for a driver"""
        return Fine.query.filter_by(driver_id=driver_id).order_by(Fine.fine_date.desc()).all()
    
    @staticmethod
    def get_pending_fines() -> List[Fine]:
        """Get all pending fines"""
        return Fine.query.filter_by(status=FineStatus.PENDING).all()
    
    @staticmethod
    def get_overdue_fines() -> List[Fine]:
        """Get all overdue fines"""
        return Fine.query.filter(
            Fine.status == FineStatus.PENDING,
            Fine.payment_deadline < datetime.now()
        ).all()
    
    @staticmethod
    def create_fine(
        vehicle_id: int,
        fine_number: str,
        fine_type: FineType,
        fine_date: datetime,
        description: str,
        amount: float,
        **kwargs
    ) -> Fine:
        """Create new fine"""
        fine = Fine(
            vehicle_id=vehicle_id,
            fine_number=fine_number,
            fine_type=fine_type,
            fine_date=fine_date,
            description=description,
            amount=amount,
            **kwargs
        )
        db.session.add(fine)
        db.session.commit()
        return fine
    
    @staticmethod
    def mark_as_paid(fine_id: int, payment_date: datetime, payment_amount: float) -> Optional[Fine]:
        """Mark fine as paid"""
        fine = Fine.query.get(fine_id)
        if fine:
            fine.status = FineStatus.PAID
            fine.payment_date = payment_date
            fine.payment_amount = payment_amount
            db.session.commit()
        return fine
    
    @staticmethod
    def file_appeal(fine_id: int, appeal_reason: str) -> Optional[Fine]:
        """File an appeal for a fine"""
        fine = Fine.query.get(fine_id)
        if fine:
            fine.status = FineStatus.APPEALED
            fine.appeal_filed = True
            fine.appeal_date = datetime.now()
            fine.appeal_reason = appeal_reason
            db.session.commit()
        return fine
    
    @staticmethod
    def update_fine(fine_id: int, **kwargs) -> Optional[Fine]:
        """Update fine"""
        fine = Fine.query.get(fine_id)
        if fine:
            for key, value in kwargs.items():
                if hasattr(fine, key):
                    setattr(fine, key, value)
            db.session.commit()
        return fine
    
    @staticmethod
    def delete_fine(fine_id: int) -> bool:
        """Delete fine"""
        fine = Fine.query.get(fine_id)
        if fine:
            db.session.delete(fine)
            db.session.commit()
            return True
        return False
