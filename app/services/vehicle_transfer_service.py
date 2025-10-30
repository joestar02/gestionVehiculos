from datetime import datetime
from app.extensions import db
from app.models.vehicle_assignment import VehicleAssignment, AssignmentType, PaymentStatus

class VehicleTransferService:
    """Service for handling vehicle transfer operations"""
    
    @staticmethod
    def get_all_transfers():
        """Get all vehicle transfers"""
        return VehicleAssignment.query.order_by(VehicleAssignment.start_date.desc()).all()
    
    @staticmethod
    def get_transfer_by_id(transfer_id):
        """Get a single transfer by ID"""
        return VehicleAssignment.query.get(transfer_id)
    
    @staticmethod
    def create_transfer(
        vehicle_id, 
        driver_id, 
        assignment_type, 
        start_date, 
        end_date, 
        assignment_fee=0, 
        purpose=None, 
        destination=None, 
        notes=None, 
        created_by=None
    ):
        """Create a new vehicle transfer"""
        transfer = VehicleAssignment(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            assignment_type=assignment_type,
            start_date=start_date,
            end_date=end_date,
            assignment_fee=assignment_fee,
            purpose=purpose,
            destination=destination,
            notes=notes,
            payment_status=PaymentStatus.PENDING,
            created_by=created_by,
            is_active=True
        )
        
        db.session.add(transfer)
        db.session.commit()
        return transfer
    
    @staticmethod
    def update_transfer(
        transfer_id, 
        vehicle_id, 
        driver_id, 
        assignment_type, 
        start_date, 
        end_date, 
        assignment_fee=0, 
        purpose=None, 
        destination=None, 
        notes=None
    ):
        """Update an existing vehicle transfer"""
        transfer = VehicleAssignment.query.get(transfer_id)
        if not transfer:
            raise ValueError("Transfer not found")
            
        transfer.vehicle_id = vehicle_id
        transfer.driver_id = driver_id
        transfer.assignment_type = assignment_type
        transfer.start_date = start_date
        transfer.end_date = end_date
        transfer.assignment_fee = assignment_fee
        transfer.purpose = purpose
        transfer.destination = destination
        transfer.notes = notes
        
        db.session.commit()
        return transfer
    
    @staticmethod
    def delete_transfer(transfer_id):
        """Delete a vehicle transfer"""
        transfer = VehicleAssignment.query.get(transfer_id)
        if not transfer:
            raise ValueError("Transfer not found")
            
        db.session.delete(transfer)
        db.session.commit()
    
    @staticmethod
    def mark_as_paid(transfer_id, payment_date=None, payment_method=None, payment_reference=None):
        """Mark a transfer as paid"""
        transfer = VehicleAssignment.query.get(transfer_id)
        if not transfer:
            raise ValueError("Transfer not found")
            
        transfer.payment_status = PaymentStatus.PAID
        transfer.payment_date = payment_date or datetime.utcnow()
        transfer.payment_method = payment_method
        transfer.payment_reference = payment_reference
        
        db.session.commit()
        return transfer
