"""Vehicle service"""
from typing import List, Optional
from sqlalchemy import or_
from app.extensions import db
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType, OwnershipType
from app.services.security_audit_service import SecurityAudit

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
    def create_vehicle(license_plate: str, make: str, model: str, year: int,
                      vehicle_type: VehicleType, ownership_type: OwnershipType,
                      organization_unit_id: Optional[int] = None,
                      color: Optional[str] = None, vin: Optional[str] = None,
                      fuel_type: Optional[str] = None, fuel_capacity: Optional[int] = None,
                      notes: Optional[str] = None) -> Vehicle:
        """Create a new vehicle"""
        vehicle = Vehicle(
            license_plate=license_plate,
            make=make,
            model=model,
            year=year,
            vehicle_type=vehicle_type,
            ownership_type=ownership_type,
            organization_unit_id=organization_unit_id,
            color=color,
            vin=vin,
            fuel_type=fuel_type,
            fuel_capacity=fuel_capacity,
            notes=notes
        )

        db.session.add(vehicle)
        db.session.commit()
        db.session.refresh(vehicle)

        # Log vehicle creation
        SecurityAudit.log_model_change(
            model_class='Vehicle',
            operation='CREATE',
            instance_id=str(vehicle.id),
            new_data={
                'license_plate': vehicle.license_plate,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'vehicle_type': vehicle.vehicle_type.value,
                'ownership_type': vehicle.ownership_type.value,
                'organization_unit_id': vehicle.organization_unit_id,
                'color': vehicle.color,
                'vin': vehicle.vin,
                'fuel_type': vehicle.fuel_type,
                'fuel_capacity': vehicle.fuel_capacity,
                'status': vehicle.status.value
            },
            details={
                'action': 'vehicle_created',
                'created_by_service': 'VehicleService.create_vehicle'
            }
        )

        return vehicle

    @staticmethod
    def update_vehicle(vehicle_id: int, **kwargs) -> Optional[Vehicle]:
        """Update vehicle information"""
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return None

        # Capture old values for logging
        old_data = {
            'license_plate': vehicle.license_plate,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'vehicle_type': vehicle.vehicle_type.value if vehicle.vehicle_type else None,
            'ownership_type': vehicle.ownership_type.value if vehicle.ownership_type else None,
            'organization_unit_id': vehicle.organization_unit_id,
            'color': vehicle.color,
            'vin': vehicle.vin,
            'fuel_type': vehicle.fuel_type,
            'fuel_capacity': vehicle.fuel_capacity,
            'status': vehicle.status.value if vehicle.status else None,
            'notes': vehicle.notes
        }

        # Apply updates
        updated_fields = []
        for key, value in kwargs.items():
            if hasattr(vehicle, key) and value is not None:
                current_value = getattr(vehicle, key)
                if current_value != value:
                    setattr(vehicle, key, value)
                    updated_fields.append(key)

        if updated_fields:  # Only commit and log if something actually changed
            db.session.commit()
            db.session.refresh(vehicle)

            # Capture new values
            new_data = {
                'license_plate': vehicle.license_plate,
                'make': vehicle.make,
                'model': vehicle.model,
                'year': vehicle.year,
                'vehicle_type': vehicle.vehicle_type.value if vehicle.vehicle_type else None,
                'ownership_type': vehicle.ownership_type.value if vehicle.ownership_type else None,
                'organization_unit_id': vehicle.organization_unit_id,
                'color': vehicle.color,
                'vin': vehicle.vin,
                'fuel_type': vehicle.fuel_type,
                'fuel_capacity': vehicle.fuel_capacity,
                'status': vehicle.status.value if vehicle.status else None,
                'notes': vehicle.notes
            }

            # Log vehicle update
            SecurityAudit.log_model_change(
                model_class='Vehicle',
                operation='UPDATE',
                instance_id=str(vehicle.id),
                old_data=old_data,
                new_data=new_data,
                details={
                    'action': 'vehicle_updated',
                    'updated_fields': updated_fields,
                    'updated_by_service': 'VehicleService.update_vehicle'
                }
            )
        else:
            db.session.rollback()  # No changes made

        return vehicle

    @staticmethod
    def delete_vehicle(vehicle_id: int) -> bool:
        """Soft delete a vehicle"""
        vehicle = VehicleService.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False

        # Capture vehicle data before deletion
        vehicle_data = {
            'id': vehicle.id,
            'license_plate': vehicle.license_plate,
            'make': vehicle.make,
            'model': vehicle.model,
            'year': vehicle.year,
            'vehicle_type': vehicle.vehicle_type.value if vehicle.vehicle_type else None,
            'ownership_type': vehicle.ownership_type.value if vehicle.ownership_type else None,
            'status': vehicle.status.value if vehicle.status else None,
            'is_active': vehicle.is_active
        }

        vehicle.is_active = False
        db.session.commit()

        # Log vehicle deletion
        SecurityAudit.log_model_change(
            model_class='Vehicle',
            operation='DELETE',
            instance_id=str(vehicle_id),
            old_data=vehicle_data,
            details={
                'action': 'vehicle_soft_deleted',
                'deletion_type': 'soft_delete',
                'deleted_by_service': 'VehicleService.delete_vehicle'
            }
        )

        return True
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
