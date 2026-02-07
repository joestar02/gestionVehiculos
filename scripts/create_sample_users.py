#!/usr/bin/env python3
"""
Create sample users with different roles for testing the permission system.
Run this after initializing permissions.
"""
import os
import sys

# Set up environment
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_SQLITE'] = 'True'

# Add the project directory to the path
project_dir = r'c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, project_dir)

from app.main import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.models.organization import OrganizationUnit
from app.models.driver import Driver

def create_sample_users():
    app = create_app()
    with app.app_context():
        print("Creating sample users with different roles...")

        # Get or create organization unit
        try:
            org_unit = OrganizationUnit.query.filter_by(name="Dirección General").first()
            if not org_unit:
                org_unit = OrganizationUnit(
                    name="Dirección General",
                    code="DG",
                    description="Unidad organizativa principal"
                )
                db.session.add(org_unit)
                db.session.commit()
                print("Created organization unit: Dirección General")
        except Exception as e:
            print(f"Warning: Could not create organization unit: {e}")
            # Try to get existing one or use None
            org_unit = OrganizationUnit.query.first()
            if not org_unit:
                print("No organization units found, skipping driver creation")
                org_unit = None

        # Sample users data
        users_data = [
            {
                "email": "admin@juntadeandalucia.es",
                "username": "admin",
                "password": "admin123",
                "first_name": "Administrador",
                "last_name": "Sistema",
                "role": UserRole.ADMIN,
                "is_superuser": True
            },
            {
                "email": "fleet.manager@juntadeandalucia.es",
                "username": "fleet_manager",
                "password": "fleet123",
                "first_name": "María",
                "last_name": "García",
                "role": UserRole.FLEET_MANAGER,
                "is_superuser": False
            },
            {
                "email": "operations.manager@juntadeandalucia.es",
                "username": "ops_manager",
                "password": "ops123",
                "first_name": "Carlos",
                "last_name": "Rodríguez",
                "role": UserRole.OPERATIONS_MANAGER,
                "is_superuser": False
            },
            {
                "email": "conductor1@juntadeandalucia.es",
                "username": "conductor1",
                "password": "driver123",
                "first_name": "Juan",
                "last_name": "Pérez",
                "role": UserRole.DRIVER,
                "is_superuser": False
            },
            {
                "email": "visor@juntadeandalucia.es",
                "username": "visor",
                "password": "view123",
                "first_name": "Ana",
                "last_name": "López",
                "role": UserRole.VIEWER,
                "is_superuser": False
            }
        ]

        created_users = []
        for user_data in users_data:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data["username"]).first()
            if existing_user:
                print(f"User {user_data['username']} already exists, skipping...")
                continue

            # Create user
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                is_superuser=user_data["is_superuser"]
            )

            # Hash password
            user.hashed_password = AuthService.get_password_hash(user_data["password"])

            db.session.add(user)
            db.session.commit()

            # If it's a driver, create driver profile
            if user_data["role"] == UserRole.DRIVER and org_unit:
                try:
                    driver = Driver(
                        user=user,  # Use relationship instead of user_id
                        license_number=f"DRV{user.id:03d}",
                        license_type="B",
                        organization_unit=org_unit
                    )
                    db.session.add(driver)
                    db.session.commit()
                    print(f"Created driver profile for {user.username}")
                except Exception as e:
                    print(f"Warning: Could not create driver profile for {user.username}: {e}")

            created_users.append(user)
            print(f"Created user: {user.username} ({user.role.value}) - Password: {user_data['password']}")

        print(f"\n✅ Created {len(created_users)} sample users successfully!")
        print("\n📋 User Credentials:")
        for user_data in users_data:
            print(f"  {user_data['username']}: {user_data['password']} ({user_data['role'].value})")

        print("\n🔐 Access Levels:")
        print("  ADMIN: Full access to all features")
        print("  FLEET_MANAGER: Fleet management, reservations, assignments")
        print("  OPERATIONS_MANAGER: Provider management, maintenance operations")
        print("  DRIVER: Limited access to own reservations and assignments")
        print("  VIEWER: Read-only access to general information")

if __name__ == "__main__":
    create_sample_users()