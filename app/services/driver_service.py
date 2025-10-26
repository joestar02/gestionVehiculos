"""Driver service"""
from typing import List, Optional
from sqlalchemy import or_
from app.extensions import db
from app.models.driver import Driver, DriverType, DriverStatus

class DriverService:
    """Service for driver operations"""
    
    @staticmethod
    def get_all_drivers(organization_unit_id: Optional[int] = None) -> List[Driver]:
        """Get all drivers, optionally filtered by organization unit"""
        query = Driver.query.filter_by(is_active=True)
        if organization_unit_id:
            query = query.filter_by(organization_unit_id=organization_unit_id)
        return query.order_by(Driver.last_name, Driver.first_name).all()
    
    @staticmethod
    def get_driver_by_id(driver_id: int) -> Optional[Driver]:
        """Get driver by ID"""
        return Driver.query.filter_by(id=driver_id, is_active=True).first()
    
    @staticmethod
    def get_driver_by_document(document_number: str) -> Optional[Driver]:
        """Get driver by document number"""
        return Driver.query.filter_by(document_number=document_number, is_active=True).first()
    
    @staticmethod
    def create_driver(first_name: str, last_name: str, document_type: str,
                     document_number: str, driver_license_number: str,
                     driver_license_expiry, driver_type: DriverType,
                     organization_unit_id: Optional[int] = None,
                     email: Optional[str] = None, phone: Optional[str] = None,
                     address: Optional[str] = None, notes: Optional[str] = None) -> Driver:
        """Create a new driver"""
        # Validate required fields
        if not email or email.strip() == '':
            raise ValueError('El email es obligatorio')

        if not first_name or not last_name:
            raise ValueError('Nombre y apellido son obligatorios')

        # Check if email already exists
        existing_driver = Driver.query.filter_by(email=email.strip(), is_active=True).first()
        if existing_driver:
            raise ValueError(f'Ya existe un conductor con el email {email}')

        # Check if document number already exists
        existing_driver = Driver.query.filter_by(document_number=document_number, is_active=True).first()
        if existing_driver:
            raise ValueError(f'Ya existe un conductor con el número de documento {document_number}')

        # Check if license number already exists
        existing_driver = Driver.query.filter_by(driver_license_number=driver_license_number, is_active=True).first()
        if existing_driver:
            raise ValueError(f'Ya existe un conductor con el número de licencia {driver_license_number}')

        driver = Driver(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            document_type=document_type,
            document_number=document_number,
            driver_license_number=driver_license_number,
            driver_license_expiry=driver_license_expiry,
            driver_type=driver_type,
            organization_unit_id=organization_unit_id,
            email=email.strip().lower() if email else None,
            phone=phone,
            address=address,
            notes=notes,
            status=DriverStatus.ACTIVE
        )

        try:
            db.session.add(driver)
            db.session.commit()
            db.session.refresh(driver)
            return driver
        except Exception as e:
            db.session.rollback()
            # log with id for correlation
            from app.utils.error_helpers import log_exception
            log_exception(e, __name__)
            raise
    
    @staticmethod
    def update_driver(driver_id: int, **kwargs) -> Optional[Driver]:
        """Update driver information"""
        driver = DriverService.get_driver_by_id(driver_id)
        if not driver:
            return None

        # Validate email if provided
        if 'email' in kwargs and kwargs['email']:
            email = kwargs['email'].strip().lower()
            if not email:
                raise ValueError('El email es obligatorio')

            # Check if email already exists for another driver
            existing_driver = Driver.query.filter(
                Driver.email == email,
                Driver.id != driver_id,
                Driver.is_active == True
            ).first()
            if existing_driver:
                raise ValueError(f'Ya existe otro conductor con el email {email}')
            kwargs['email'] = email

        # Validate other required fields if provided
        if 'first_name' in kwargs and not kwargs['first_name'].strip():
            raise ValueError('El nombre es obligatorio')

        if 'last_name' in kwargs and not kwargs['last_name'].strip():
            raise ValueError('El apellido es obligatorio')

        for key, value in kwargs.items():
            if hasattr(driver, key) and value is not None:
                setattr(driver, key, value.strip() if isinstance(value, str) else value)

        try:
            db.session.commit()
            db.session.refresh(driver)
            return driver
        except Exception as e:
            db.session.rollback()
            from app.utils.error_helpers import log_exception
            log_exception(e, __name__)
            raise
    
    @staticmethod
    def delete_driver(driver_id: int) -> bool:
        """Soft delete a driver"""
        driver = DriverService.get_driver_by_id(driver_id)
        if not driver:
            return False
        
        driver.is_active = False
        db.session.commit()
        
        return True
    
    @staticmethod
    def update_driver_status(driver_id: int, status: DriverStatus) -> Optional[Driver]:
        """Update driver status"""
        driver = DriverService.get_driver_by_id(driver_id)
        if not driver:
            return None
        
        driver.status = status
        db.session.commit()
        db.session.refresh(driver)
        
        return driver
    
    @staticmethod
    def search_drivers(search_term: str) -> List[Driver]:
        """Search drivers by name or document"""
        search_pattern = f"%{search_term}%"
        return Driver.query.filter(
            Driver.is_active == True,
            or_(
                Driver.first_name.ilike(search_pattern),
                Driver.last_name.ilike(search_pattern),
                Driver.document_number.ilike(search_pattern),
                Driver.driver_license_number.ilike(search_pattern)
            )
        ).all()
    
    @staticmethod
    def get_active_drivers() -> List[Driver]:
        """Get all active drivers"""
        return Driver.query.filter_by(
            is_active=True,
            status=DriverStatus.ACTIVE
        ).all()
