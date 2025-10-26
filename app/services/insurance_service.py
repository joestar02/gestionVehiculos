"""Insurance service"""
from typing import List, Optional
from datetime import datetime, timedelta
from app.extensions import db
from app.models.insurance import VehicleInsurance, InsuranceType, PaymentStatus
from sqlalchemy.exc import IntegrityError

class InsuranceService:
    @staticmethod
    def get_all_insurances() -> List[VehicleInsurance]:
        """Get all insurance records"""
        return VehicleInsurance.query.order_by(VehicleInsurance.end_date.desc()).all()

    @staticmethod
    def get_insurance_by_id(insurance_id: int) -> Optional[VehicleInsurance]:
        """Get insurance record by ID"""
        return VehicleInsurance.query.get(insurance_id)

    @staticmethod
    def get_insurances_by_vehicle(vehicle_id: int) -> List[VehicleInsurance]:
        """Get all insurance records for a vehicle"""
        return VehicleInsurance.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleInsurance.end_date.desc()).all()

    @staticmethod
    def get_pending_insurances() -> List[VehicleInsurance]:
        """Get all pending insurance payments"""
        return VehicleInsurance.query.filter_by(payment_status=PaymentStatus.PENDING).all()

    @staticmethod
    def get_expiring_soon_insurances(days: int = 30) -> List[VehicleInsurance]:
        """Get all insurances expiring soon"""
        return VehicleInsurance.query.filter(
            VehicleInsurance.payment_status == PaymentStatus.PENDING,
            VehicleInsurance.end_date <= datetime.utcnow() + timedelta(days=days)
        ).all()

    @staticmethod
    def get_expired_insurances() -> List[VehicleInsurance]:
        """Get all expired insurances"""
        return VehicleInsurance.query.filter(
            VehicleInsurance.end_date < datetime.utcnow()
        ).all()

    @staticmethod
    def create_insurance(
        vehicle_id: int,
        insurance_type: InsuranceType,
        insurance_company: str,
        policy_number: str,
        premium_amount: float,
        start_date: datetime,
        end_date: datetime,
        **kwargs
    ) -> VehicleInsurance:
        """Create new insurance record"""
        # Basic validations
        if start_date > end_date:
            raise ValueError("La fecha de inicio debe ser anterior o igual a la fecha de fin")

        # Ensure policy_number uniqueness
        existing = VehicleInsurance.query.filter_by(policy_number=policy_number).first()
        if existing:
            raise ValueError("Número de póliza duplicado")

        insurance = VehicleInsurance(
            vehicle_id=vehicle_id,
            insurance_type=insurance_type,
            insurance_company=insurance_company,
            policy_number=policy_number,
            premium_amount=premium_amount,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
        db.session.add(insurance)
        db.session.commit()
        return insurance

    @staticmethod
    def mark_as_paid(insurance_id: int, payment_date: datetime, payment_method: str = None, payment_reference: str = None) -> Optional[VehicleInsurance]:
        """Mark insurance as paid"""
        insurance = VehicleInsurance.query.get(insurance_id)
        if insurance:
            insurance.payment_status = PaymentStatus.PAID
            insurance.payment_date = payment_date
            if payment_method:
                insurance.payment_method = payment_method
            if payment_reference:
                insurance.payment_reference = payment_reference
            db.session.commit()
        return insurance

    @staticmethod
    def update_insurance(insurance_id: int, **kwargs) -> Optional[VehicleInsurance]:
        """Update insurance record"""
        insurance = VehicleInsurance.query.get(insurance_id)
        if insurance:
            # If updating dates or policy_number, validate
            if 'start_date' in kwargs and 'end_date' in kwargs:
                if kwargs['start_date'] > kwargs['end_date']:
                    raise ValueError("La fecha de inicio debe ser anterior o igual a la fecha de fin")
            if 'policy_number' in kwargs and kwargs['policy_number'] != insurance.policy_number:
                exists = VehicleInsurance.query.filter_by(policy_number=kwargs['policy_number']).first()
                if exists:
                    raise ValueError("Número de póliza duplicado")

            for key, value in kwargs.items():
                if hasattr(insurance, key):
                    setattr(insurance, key, value)
            db.session.commit()
        return insurance

    @staticmethod
    def delete_insurance(insurance_id: int) -> bool:
        """Delete insurance record"""
        insurance = VehicleInsurance.query.get(insurance_id)
        if insurance:
            db.session.delete(insurance)
            db.session.commit()
            return True
        return False
