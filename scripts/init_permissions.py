#!/usr/bin/env python3
"""
Initialize permissions and role permissions in the database.
Run this after creating the permission tables.
"""
import os
import sys

# Set up environment
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_SQLITE'] = 'True'

# Add the project directory to the path
project_dir = r'c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, project_dir)

def init_permissions():
    from app.main import create_app
    app = create_app()
    with app.app_context():
        # Import after app context
        from app.extensions import db
        from app.models.permission import Permission, RolePermission
        from app.models.user import UserRole
        from app.core.permission_config import PERMISSIONS, ROLE_PERMISSIONS

        # Create permissions
        for perm_name, description in PERMISSIONS.items():
            if not Permission.query.filter_by(name=perm_name).first():
                perm = Permission(name=perm_name, description=description)
                db.session.add(perm)

        db.session.commit()

        # Create role permissions
        for role, perms in ROLE_PERMISSIONS.items():
            for perm_name in perms:
                perm = Permission.query.filter_by(name=perm_name).first()
                if perm and not RolePermission.query.filter_by(role=role.value, permission_id=perm.id).first():
                    rp = RolePermission(role=role.value, permission_id=perm.id)
                    db.session.add(rp)

        db.session.commit()
        print("Permissions initialized successfully!")

if __name__ == "__main__":
    init_permissions()