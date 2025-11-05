"""Reservation service"""
from typing import List, Optional
from datetime import datetime
from app.extensions import db
from app.models.reservation import Reservation, ReservationStatus

class ReservationService:
    """Service for reservation operations"""
    
    @staticmethod
    def get_all_reservations() -> List[Reservation]:
        """Get all reservations"""
        return Reservation.query.order_by(Reservation.start_date.desc()).all()

    @staticmethod
    def get_all_reservations_paginated(page: int = 1, per_page: int = 20):
        """Get all reservations with pagination"""
        return Reservation.query.order_by(Reservation.start_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_reservation_by_id(reservation_id: int) -> Optional[Reservation]:
        """Get reservation by ID"""
        return Reservation.query.get(reservation_id)
    
    @staticmethod
    def get_reservations_by_vehicle(vehicle_id: int) -> List[Reservation]:
        """Get reservations for a specific vehicle"""
        return Reservation.query.filter_by(vehicle_id=vehicle_id).order_by(
            Reservation.start_date.desc()
        ).all()
    
    @staticmethod
    def get_reservations_by_driver(driver_id: int) -> List[Reservation]:
        """Get reservations for a specific driver"""
        return Reservation.query.filter_by(driver_id=driver_id).order_by(
            Reservation.start_date.desc()
        ).all()

    @staticmethod
    def get_reservations_by_driver_paginated(driver_id: int, page: int = 1, per_page: int = 20):
        """Get reservations for a specific driver with pagination"""
        return Reservation.query.filter_by(driver_id=driver_id).order_by(Reservation.start_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_reservations_by_driver_and_date_range(driver_id: int, start_date, end_date) -> List[Reservation]:
        """Get reservations for a specific driver within date range"""
        return Reservation.query.filter(
            Reservation.driver_id == driver_id,
            Reservation.start_date >= start_date,
            Reservation.start_date <= end_date
        ).order_by(Reservation.start_date).all()

    @staticmethod
    def get_reservations_by_driver_and_date_range_paginated(driver_id: int, start_date, end_date, page: int = 1, per_page: int = 20):
        """Get reservations for a specific driver within date range with pagination"""
        return Reservation.query.filter(
            Reservation.driver_id == driver_id,
            Reservation.start_date >= start_date,
            Reservation.start_date <= end_date
        ).order_by(Reservation.start_date).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_reservations_by_date_range(start_date, end_date) -> List[Reservation]:
        """Get reservations within a date range"""
        return Reservation.query.filter(
            Reservation.start_date >= start_date,
            Reservation.start_date <= end_date
        ).order_by(Reservation.start_date).all()

    @staticmethod
    def get_reservations_by_date_range_paginated(start_date, end_date, page: int = 1, per_page: int = 20):
        """Get reservations within a date range with pagination"""
        return Reservation.query.filter(
            Reservation.start_date >= start_date,
            Reservation.start_date <= end_date
        ).order_by(Reservation.start_date).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def _check_vehicle_overlap(vehicle_id: int, start_date, end_date, exclude_reservation_id: int = None):
        """Raise ValueError if the vehicle has an existing reservation that overlaps the given range."""
        q = Reservation.query.filter(
            Reservation.vehicle_id == vehicle_id,
            Reservation.status != ReservationStatus.CANCELLED,
            Reservation.start_date < end_date,
            Reservation.end_date > start_date
        )
        if exclude_reservation_id:
            q = q.filter(Reservation.id != exclude_reservation_id)

        conflict = q.first()
        if conflict:
            raise ValueError(f'El vehículo tiene una reserva solapada (id={conflict.id})')
    
    @staticmethod
    def create_reservation(vehicle_id: int, driver_id: int, start_date,
                          end_date, purpose: str, user_id: int,
                          destination: Optional[str] = None,
                          notes: Optional[str] = None,
                          organization_unit_id: Optional[int] = None) -> Reservation:
        """Create a new reservation"""
        # Validate overlap for the selected vehicle
        ReservationService._check_vehicle_overlap(vehicle_id, start_date, end_date)

        reservation = Reservation(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            start_date=start_date,
            end_date=end_date,
            purpose=purpose,
            destination=destination,
            notes=notes,
            user_id=user_id,
            organization_unit_id=organization_unit_id or 0,
            status=ReservationStatus.PENDING
        )
        
        db.session.add(reservation)
        db.session.commit()
        db.session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    def update_reservation(reservation_id: int, **kwargs) -> Optional[Reservation]:
        """Update reservation information"""
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            return None

        # If changing vehicle or dates, ensure no overlap
        new_vehicle = kwargs.get('vehicle_id', reservation.vehicle_id)
        new_start = kwargs.get('start_date', reservation.start_date)
        new_end = kwargs.get('end_date', reservation.end_date)
        ReservationService._check_vehicle_overlap(new_vehicle, new_start, new_end, exclude_reservation_id=reservation_id)

        for key, value in kwargs.items():
            if hasattr(reservation, key) and value is not None:
                setattr(reservation, key, value)

        db.session.commit()
        db.session.refresh(reservation)

        return reservation
    
    @staticmethod
    def cancel_reservation(reservation_id: int, cancellation_reason: str) -> Optional[Reservation]:
        """Cancel a reservation"""
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.CANCELLED
        reservation.cancellation_reason = cancellation_reason
        reservation.cancelled_at = datetime.utcnow()
        
        db.session.commit()
        db.session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    def confirm_reservation(reservation_id: int) -> Optional[Reservation]:
        """Confirm a reservation"""
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.CONFIRMED
        
        db.session.commit()
        db.session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    def start_reservation(reservation_id: int, actual_start_mileage: int) -> Optional[Reservation]:
        """Start a reservation (vehicle pickup)"""
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.IN_PROGRESS
        reservation.actual_start_date = datetime.utcnow()
        reservation.actual_start_mileage = actual_start_mileage
        
        db.session.commit()
        db.session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    def complete_reservation(reservation_id: int, actual_end_mileage: int,
                           notes: Optional[str] = None) -> Optional[Reservation]:
        """Complete a reservation (vehicle return)"""
        reservation = ReservationService.get_reservation_by_id(reservation_id)
        if not reservation:
            return None
        
        reservation.status = ReservationStatus.COMPLETED
        reservation.actual_end_date = datetime.utcnow()
        reservation.actual_end_mileage = actual_end_mileage
        if notes:
            reservation.notes = (reservation.notes or '') + '\n' + notes
        
        db.session.commit()
        db.session.refresh(reservation)
        
        return reservation
