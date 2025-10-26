"""Provider service"""
from typing import List, Optional
from app.extensions import db
from app.models.provider import Provider, ProviderType

class ProviderService:
    """Service for provider operations"""

    @staticmethod
    def get_all_providers() -> List[Provider]:
        """Get all active providers"""
        return Provider.query.filter_by(is_active=True).order_by(Provider.name).all()

    @staticmethod
    def get_providers_by_type(provider_type: ProviderType) -> List[Provider]:
        """Get providers by type"""
        return Provider.query.filter_by(provider_type=provider_type, is_active=True).order_by(Provider.name).all()

    @staticmethod
    def get_provider_by_id(provider_id: int) -> Optional[Provider]:
        """Get provider by ID"""
        return Provider.query.filter_by(id=provider_id, is_active=True).first()

    @staticmethod
    def create_provider(name: str, provider_type: ProviderType,
                       contact_person: Optional[str] = None, phone: Optional[str] = None,
                       email: Optional[str] = None, address: Optional[str] = None,
                       website: Optional[str] = None, notes: Optional[str] = None) -> Provider:
        """Create a new provider"""
        # Validate required fields
        if not name or not name.strip():
            raise ValueError('El nombre es obligatorio')

        provider = Provider(
            name=name.strip(),
            provider_type=provider_type,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address,
            website=website,
            notes=notes
        )

        db.session.add(provider)
        db.session.commit()
        db.session.refresh(provider)

        return provider

    @staticmethod
    def update_provider(provider_id: int, **kwargs) -> Optional[Provider]:
        """Update provider information"""
        provider = ProviderService.get_provider_by_id(provider_id)
        if not provider:
            return None

        # Validate name if provided
        if 'name' in kwargs and kwargs['name']:
            name = kwargs['name'].strip()
            if not name:
                raise ValueError('El nombre es obligatorio')
            kwargs['name'] = name

        for key, value in kwargs.items():
            if hasattr(provider, key) and value is not None:
                setattr(provider, key, value)

        db.session.commit()
        db.session.refresh(provider)

        return provider

    @staticmethod
    def delete_provider(provider_id: int) -> bool:
        """Soft delete a provider"""
        provider = ProviderService.get_provider_by_id(provider_id)
        if not provider:
            return False

        provider.is_active = False
        db.session.commit()

        return True
