"""Tax service"""
from typing import List, Optional
from datetime import datetime
from app.extensions import db
from app.models.tax import VehicleTax, TaxType, PaymentStatus

class TaxService:
    @staticmethod
    def get_all_taxes() -> List[VehicleTax]:
        """Get all tax records"""
        return VehicleTax.query.order_by(VehicleTax.tax_year.desc()).all()
    
    @staticmethod
    def get_tax_by_id(tax_id: int) -> Optional[VehicleTax]:
        """Get tax record by ID"""
        return VehicleTax.query.get(tax_id)
    
    @staticmethod
    def get_taxes_by_vehicle(vehicle_id: int) -> List[VehicleTax]:
        """Get all tax records for a vehicle"""
        return VehicleTax.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleTax.tax_year.desc()).all()
    
    @staticmethod
    def get_pending_taxes() -> List[VehicleTax]:
        """Get all pending tax payments"""
        return VehicleTax.query.filter_by(payment_status=PaymentStatus.PENDING).all()
    
    @staticmethod
    def get_overdue_taxes() -> List[VehicleTax]:
        """Get all overdue tax payments"""
        return VehicleTax.query.filter(
            VehicleTax.payment_status == PaymentStatus.PENDING,
            VehicleTax.due_date < datetime.now()
        ).all()
    
    @staticmethod
    def create_tax(
        vehicle_id: int,
        tax_type: TaxType,
        tax_year: int,
        amount: float,
        due_date: datetime,
        **kwargs
    ) -> VehicleTax:
        """Create new tax record"""
        tax = VehicleTax(
            vehicle_id=vehicle_id,
            tax_type=tax_type,
            tax_year=tax_year,
            amount=amount,
            due_date=due_date,
            **kwargs
        )
        db.session.add(tax)
        db.session.commit()
        return tax
    
    @staticmethod
    def mark_as_paid(tax_id: int, payment_date: datetime, payment_method: str = None, payment_reference: str = None) -> Optional[VehicleTax]:
        """Mark tax as paid"""
        tax = VehicleTax.query.get(tax_id)
        if tax:
            tax.payment_status = PaymentStatus.PAID
            tax.payment_date = payment_date
            if payment_method:
                tax.payment_method = payment_method
            if payment_reference:
                tax.payment_reference = payment_reference
            db.session.commit()
        return tax
    
    @staticmethod
    def update_tax(tax_id: int, **kwargs) -> Optional[VehicleTax]:
        """Update tax record"""
        tax = VehicleTax.query.get(tax_id)
        if tax:
            for key, value in kwargs.items():
                if hasattr(tax, key):
                    setattr(tax, key, value)
            db.session.commit()
        return tax
    
    @staticmethod
    def delete_tax(tax_id: int) -> bool:
        """Delete tax record"""
        tax = VehicleTax.query.get(tax_id)
        if tax:
            db.session.delete(tax)
            db.session.commit()
            return True
        return False
