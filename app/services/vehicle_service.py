"""Vehicle service"""
from typing import List, Optional
from sqlalchemy import or_
from app.extensions import db
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType, OwnershipType
from app.utils.audit_decorators import audit_model_change, audit_operation
from sqlalchemy.exc import IntegrityError

class VehicleService:
    """Service for vehicle operations"""

    @staticmethod
    def get_all_vehicles(organization_unit_id: Optional[int] = None) -> List[Vehicle]:
        """Get all vehicles, optionally filtered by organization unit"""
        query = Vehicle.query.filter_by(is_active=True)
        if organization_unit_id:
            query = query.filter_by(organization_unit_id=organization_unit_id)
        return query.order_by(Vehicle.license_plate).all()

    @staticmethod
    def get_vehicle_by_id(vehicle_id: int) -> Optional[Vehicle]:
        """Get vehicle by ID"""
        return Vehicle.query.filter_by(id=vehicle_id, is_active=True).first()

    @staticmethod
    def get_vehicle_by_license_plate(license_plate: str) -> Optional[Vehicle]:
        """Get vehicle by license plate"""
        return Vehicle.query.filter_by(license_plate=license_plate, is_active=True).first()

    @staticmethod
    @audit_model_change('Vehicle', 'CREATE')
    def create_vehicle(license_plate: str, make: str, model: str, year: int,
                      vehicle_type: VehicleType, ownership_type: OwnershipType,
                      organization_unit_id: Optional[int] = None,
                      color: Optional[str] = None, vin: Optional[str] = None,
                      fuel_type: Optional[str] = None, fuel_capacity: Optional[int] = None,
                      notes: Optional[str] = None) -> Vehicle:
        """Create a new vehicle"""
        # Normalize VIN: convert empty strings to None so UNIQUE(NULL) behavior applies
        normalized_vin = None
        if vin is not None:
            try:
                normalized_vin = vin.strip()
            except Exception:
                normalized_vin = vin
            if normalized_vin == "":
                normalized_vin = None

        vehicle = Vehicle(
            license_plate=license_plate,
            make=make,
            model=model,
            year=year,
            vehicle_type=vehicle_type,
            ownership_type=ownership_type,
            organization_unit_id=organization_unit_id,
            color=color,
            vin=normalized_vin,
            fuel_type=fuel_type,
            fuel_capacity=fuel_capacity,
            notes=notes
        )

        db.session.add(vehicle)
        try:
            db.session.commit()
        except IntegrityError as e:
            # Roll back session to allow future transactions
            db.session.rollback()
            # Provide a friendlier error for duplicate VIN
            if 'vin' in str(e).lower() or 'unique constraint' in str(e).lower():
                raise ValueError('VIN already exists or invalid') from e
            raise

        db.session.refresh(vehicle)
        return vehicle

    @staticmethod
    @audit_model_change('Vehicle', 'UPDATE')
    def update_vehicle(vehicle_id: int, **kwargs) -> Optional[Vehicle]:
        """Update vehicle information"""
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return None

        # Apply updates
        for key, value in kwargs.items():
            if hasattr(vehicle, key) and value is not None:
                setattr(vehicle, key, value)

        db.session.commit()
        db.session.refresh(vehicle)

        return vehicle

    @staticmethod
    @audit_model_change('Vehicle', 'DELETE')
    def delete_vehicle(vehicle_id: int) -> bool:
        """Soft delete a vehicle"""
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False

        vehicle.is_active = False
        db.session.commit()

        return True
    
    @staticmethod
    def update_vehicle_status(vehicle_id: int, status: VehicleStatus) -> Optional[Vehicle]:
        """Update vehicle status"""
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return None
        
        vehicle.status = status
        db.session.commit()
        db.session.refresh(vehicle)
        
        return vehicle
    
    @staticmethod
    def search_vehicles(search_term: str) -> List[Vehicle]:
        """Search vehicles by license plate, make, or model"""
        search_pattern = f"%{search_term}%"
        return Vehicle.query.filter(
            Vehicle.is_active == True,
            or_(
                Vehicle.license_plate.ilike(search_pattern),
                Vehicle.make.ilike(search_pattern),
                Vehicle.model.ilike(search_pattern)
            )
        ).all()
    
    @staticmethod
    def get_available_vehicles() -> List[Vehicle]:
        """Get all available vehicles"""
        return Vehicle.query.filter_by(
            is_active=True,
            status=VehicleStatus.AVAILABLE
        ).all()
