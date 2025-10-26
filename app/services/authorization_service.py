"""Authorization service"""
from typing import List, Optional
from datetime import datetime, timedelta
from app.extensions import db
from app.models.authorization import UrbanAccessAuthorization

class AuthorizationService:
    @staticmethod
    def get_all_authorizations() -> List[UrbanAccessAuthorization]:
        """Get all authorizations"""
        return UrbanAccessAuthorization.query.order_by(UrbanAccessAuthorization.end_date.desc()).all()
    
    @staticmethod
    def get_authorization_by_id(auth_id: int) -> Optional[UrbanAccessAuthorization]:
        """Get authorization by ID"""
        return UrbanAccessAuthorization.query.get(auth_id)
    
    @staticmethod
    def get_authorizations_by_vehicle(vehicle_id: int) -> List[UrbanAccessAuthorization]:
        """Get all authorizations for a vehicle"""
        return UrbanAccessAuthorization.query.filter_by(vehicle_id=vehicle_id).order_by(UrbanAccessAuthorization.end_date.desc()).all()
    
    @staticmethod
    def get_active_authorizations() -> List[UrbanAccessAuthorization]:
        """Get all active authorizations"""
        return UrbanAccessAuthorization.query.filter(
            UrbanAccessAuthorization.is_active == True,
            UrbanAccessAuthorization.end_date >= datetime.now()
        ).all()
    
    @staticmethod
    def get_expiring_soon(days: int = 30) -> List[UrbanAccessAuthorization]:
        """Get authorizations expiring soon"""
        expiry_threshold = datetime.now() + timedelta(days=days)
        return UrbanAccessAuthorization.query.filter(
            UrbanAccessAuthorization.is_active == True,
            UrbanAccessAuthorization.end_date <= expiry_threshold,
            UrbanAccessAuthorization.end_date >= datetime.now()
        ).all()
    
    @staticmethod
    def create_authorization(
        vehicle_id: int,
        authorization_type: str,
        issuing_authority: str,
        authorization_number: str,
        start_date: datetime,
        end_date: datetime,
        **kwargs
    ) -> UrbanAccessAuthorization:
        """Create new authorization"""
        auth = UrbanAccessAuthorization(
            vehicle_id=vehicle_id,
            authorization_type=authorization_type,
            issuing_authority=issuing_authority,
            authorization_number=authorization_number,
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )
        db.session.add(auth)
        db.session.commit()
        return auth
    
    @staticmethod
    def deactivate_authorization(auth_id: int) -> Optional[UrbanAccessAuthorization]:
        """Deactivate an authorization"""
        auth = UrbanAccessAuthorization.query.get(auth_id)
        if auth:
            auth.is_active = False
            db.session.commit()
        return auth
    
    @staticmethod
    def update_authorization(auth_id: int, **kwargs) -> Optional[UrbanAccessAuthorization]:
        """Update authorization"""
        auth = UrbanAccessAuthorization.query.get(auth_id)
        if auth:
            for key, value in kwargs.items():
                if hasattr(auth, key):
                    setattr(auth, key, value)
            db.session.commit()
        return auth
    
    @staticmethod
    def delete_authorization(auth_id: int) -> bool:
        """Delete authorization"""
        auth = UrbanAccessAuthorization.query.get(auth_id)
        if auth:
            db.session.delete(auth)
            db.session.commit()
            return True
        return False
