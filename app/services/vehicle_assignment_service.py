"""Vehicle Assignment service"""
from typing import List, Optional
from datetime import datetime, timedelta
from app.extensions import db
from app.models.vehicle_assignment import VehicleAssignment, AssignmentType, PaymentStatus

class VehicleAssignmentService:
    @staticmethod
    def get_all_assignments() -> List[VehicleAssignment]:
        """Get all vehicle assignment records"""
        return VehicleAssignment.query.order_by(VehicleAssignment.end_date.desc()).all()

    @staticmethod
    def get_assignment_by_id(assignment_id: int) -> Optional[VehicleAssignment]:
        """Get vehicle assignment record by ID"""
        return VehicleAssignment.query.get(assignment_id)

    @staticmethod
    def get_assignments_by_vehicle(vehicle_id: int) -> List[VehicleAssignment]:
        """Get all assignment records for a vehicle"""
        return VehicleAssignment.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleAssignment.end_date.desc()).all()

    @staticmethod
    def get_assignments_by_driver(driver_id: int) -> List[VehicleAssignment]:
        """Get all assignment records for a driver"""
        return VehicleAssignment.query.filter_by(driver_id=driver_id).order_by(VehicleAssignment.end_date.desc()).all()

    @staticmethod
    def get_pending_assignments() -> List[VehicleAssignment]:
        """Get all pending assignment payments"""
        return VehicleAssignment.query.filter_by(payment_status=PaymentStatus.PENDING, is_active=True).all()

    @staticmethod
    def get_overdue_assignments() -> List[VehicleAssignment]:
        """Get all overdue assignment payments"""
        return VehicleAssignment.query.filter(
            VehicleAssignment.payment_status == PaymentStatus.PENDING,
            VehicleAssignment.end_date < datetime.utcnow(),
            VehicleAssignment.is_active == True
        ).all()

    @staticmethod
    def get_active_assignments() -> List[VehicleAssignment]:
        """Get all active assignments"""
        return VehicleAssignment.query.filter(
            VehicleAssignment.is_active == True,
            VehicleAssignment.start_date <= datetime.utcnow(),
            VehicleAssignment.end_date >= datetime.utcnow()
        ).all()

    @staticmethod
    def create_assignment(
        vehicle_id: int,
        driver_id: int,
        assignment_type: AssignmentType,
        start_date: datetime,
        end_date: datetime,
        assignment_fee: float,
        purpose: str,
        **kwargs
    ) -> VehicleAssignment:
        """Create new vehicle assignment record"""
        assignment = VehicleAssignment(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            assignment_type=assignment_type,
            start_date=start_date,
            end_date=end_date,
            assignment_fee=assignment_fee,
            purpose=purpose,
            **kwargs
        )
        db.session.add(assignment)
        db.session.commit()
        return assignment

    @staticmethod
    def mark_as_paid(assignment_id: int, payment_date: datetime, payment_method: str = None, payment_reference: str = None) -> Optional[VehicleAssignment]:
        """Mark assignment as paid"""
        assignment = VehicleAssignment.query.get(assignment_id)
        if assignment:
            assignment.payment_status = PaymentStatus.PAID
            assignment.payment_date = payment_date
            if payment_method:
                assignment.payment_method = payment_method
            if payment_reference:
                assignment.payment_reference = payment_reference
            db.session.commit()
        return assignment

    @staticmethod
    def update_assignment(assignment_id: int, **kwargs) -> Optional[VehicleAssignment]:
        """Update assignment record"""
        assignment = VehicleAssignment.query.get(assignment_id)
        if assignment:
            for key, value in kwargs.items():
                if hasattr(assignment, key):
                    setattr(assignment, key, value)
            db.session.commit()
        return assignment

    @staticmethod
    def delete_assignment(assignment_id: int) -> bool:
        """Delete assignment record"""
        assignment = VehicleAssignment.query.get(assignment_id)
        if assignment:
            db.session.delete(assignment)
            db.session.commit()
            return True
        return False

    @staticmethod
    def deactivate_assignment(assignment_id: int) -> Optional[VehicleAssignment]:
        """Deactivate assignment (set is_active to False)"""
        assignment = VehicleAssignment.query.get(assignment_id)
        if assignment:
            assignment.is_active = False
            db.session.commit()
        return assignment
