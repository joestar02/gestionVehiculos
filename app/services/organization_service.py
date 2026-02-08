"""Organization service"""
from typing import List, Optional
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.organization import OrganizationUnit

class OrganizationService:
    """Service for organization operations"""
    
    @staticmethod
    def get_all_organizations() -> List[OrganizationUnit]:
        """Get all organization units"""
        return OrganizationUnit.query.filter_by(is_active=True).order_by(
            OrganizationUnit.name
        ).all()
    
    @staticmethod
    def get_all_organization_units() -> List[OrganizationUnit]:
        """Get all organization units (alias for get_all_organizations)"""
        return OrganizationService.get_all_organizations()
    
    @staticmethod
    def get_organization_by_id(org_id: int) -> Optional[OrganizationUnit]:
        """Get organization unit by ID"""
        return OrganizationUnit.query.filter_by(id=org_id, is_active=True).first()
    
    @staticmethod
    def get_organization_by_code(code: str) -> Optional[OrganizationUnit]:
        """Get organization unit by code"""
        return OrganizationUnit.query.filter_by(code=code, is_active=True).first()
    
    @staticmethod
    def get_root_organizations() -> List[OrganizationUnit]:
        """Get root level organizations (no parent)"""
        return OrganizationUnit.query.filter_by(parent_id=None, is_active=True).order_by(
            OrganizationUnit.name
        ).all()
    
    @staticmethod
    def get_child_organizations(parent_id: int) -> List[OrganizationUnit]:
        """Get child organizations of a specific parent"""
        return OrganizationUnit.query.filter_by(parent_id=parent_id, is_active=True).order_by(
            OrganizationUnit.name
        ).all()

    @staticmethod
    def get_organizations_with_levels() -> List[OrganizationUnit]:
        """Return all active organizations annotated with a `level` attribute
        representing depth in the tree (0 = root). This is useful for
        rendering select dropdowns ordered by hierarchy.
        """
        all_orgs = OrganizationService.get_all_organizations()

        def build(level_list, parent_id=None, level=0):
            for org in [o for o in level_list if o.parent_id == parent_id]:
                org.level = level
                yield org
                yield from build(level_list, parent_id=org.id, level=level+1)

        return list(build(all_orgs, parent_id=None, level=0))
    
    @staticmethod
    def create_organization(name: str, code: str, description: Optional[str] = None,
                          manager_name: Optional[str] = None,
                          contact_email: Optional[str] = None,
                          contact_phone: Optional[str] = None,
                          parent_id: Optional[int] = None) -> OrganizationUnit:
        """Create a new organization unit"""
        org = OrganizationUnit(
            name=name,
            code=code,
            description=description,
            manager_name=manager_name,
            contact_email=contact_email,
            contact_phone=contact_phone,
            parent_id=parent_id
        )
        
        db.session.add(org)
        db.session.commit()
        db.session.refresh(org)
        
        return org
    
    @staticmethod
    def update_organization(org_id: int, **kwargs) -> Optional[OrganizationUnit]:
        """Update organization unit"""
        org = OrganizationService.get_organization_by_id(org_id)
        if not org:
            return None
        
        for key, value in kwargs.items():
            if hasattr(org, key) and value is not None:
                setattr(org, key, value)
        
        db.session.commit()
        db.session.refresh(org)
        
        return org
    
    @staticmethod
    def delete_organization(org_id: int) -> bool:
        """Soft delete an organization unit"""
        org = OrganizationService.get_organization_by_id(org_id)
        if not org:
            return False
        
        org.is_active = False
        db.session.commit()
        
        return True
