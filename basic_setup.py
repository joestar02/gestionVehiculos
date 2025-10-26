#!/usr/bin/env python3
"""
Simplified database setup script with sample data
"""
import os
import sys

# Set up environment
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_SQLITE'] = 'True'

# Add the project directory to the path
project_dir = r'c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, project_dir)

def create_basic_database():
    """Create basic database with essential data"""
    try:
        print("Starting basic database setup...")

        # Import Flask app
        from app.main import create_app
        print("Flask app imported")

        app = create_app()

        with app.app_context():
            print("Application context established")

            # Import database
            from app.extensions import db

            print("Importing all models...")
            # Import all models to register them with SQLAlchemy
            from app.models import (
                provider, driver, vehicle, user, organization,
                maintenance, reservation, fine, insurance,
                itv, tax, accident, authorization,
                renting_contract, vehicle_driver_association,
                vehicle_pickup
            )

            print("Creating all database tables...")
            db.create_all()

            print("Creating basic users...")
            from app.models.user import User, UserRole
            from app.core.security import get_password_hash

            # Create admin user (only required fields)
            admin_user = User(
                username='admin',
                email='admin@empresa.com',
                hashed_password=get_password_hash('admin123'),
                first_name='Administrador',
                last_name='Sistema',
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True
            )
            db.session.add(admin_user)
            db.session.commit()

            print("Creating basic organization unit...")
            from app.models.organization import OrganizationUnit

            org1 = OrganizationUnit(
                name="Direccion General",
                code="DG",
                description="Direccion General",
                manager_name="Juan Perez",
                contact_email="juan.perez@empresa.com",
                contact_phone="+34 600 000 001"
            )
            db.session.add(org1)
            db.session.commit()

            print("Creating basic vehicles...")
            from app.models.vehicle import Vehicle, VehicleType, OwnershipType

            vehicle1 = Vehicle(
                license_plate="1234ABC",
                make="Toyota",
                model="Corolla",
                year=2020,
                vehicle_type=VehicleType.SEDAN,
                ownership_type=OwnershipType.COMPANY,
                color="Blanco",
                vin="1HGCM82633A123456",
                fuel_type="Gasolina",
                fuel_capacity=50
            )
            db.session.add(vehicle1)

            vehicle2 = Vehicle(
                license_plate="5678DEF",
                make="Ford",
                model="Transit",
                year=2019,
                vehicle_type=VehicleType.VAN,
                ownership_type=OwnershipType.COMPANY,
                color="Azul",
                vin="2HGCM82633A123456",
                fuel_type="Diesel",
                fuel_capacity=80
            )
            db.session.add(vehicle2)
            db.session.commit()

            print("Creating basic providers...")
            from app.models.provider import Provider, ProviderType

            provider1 = Provider(
                name="Talleres Hermanos Lopez",
                provider_type=ProviderType.WORKSHOP,
                contact_person="Miguel Lopez",
                phone="+34 91 123 45 67",
                email="info@tallereslopez.com",
                address="Calle Mecanicos 789, Madrid"
            )
            db.session.add(provider1)
            db.session.commit()

            print("Database setup completed successfully!")

            # Verify providers table exists
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='providers'"))
            if result.fetchone():
                print("Providers table exists and is ready!")
            else:
                print("Providers table not found!")

            return True

    except Exception as e:
        print(f"Error during database setup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_basic_database()
    if success:
        print("\nBasic database setup successful!")
        print("\nTest account:")
        print("  Admin: admin / admin123")
        print("\nYou can now:")
        print("1. Run: python run.py")
        print("2. Login at: http://127.0.0.1:5000/auth/login")
        print("3. Access: /reservations/new (should work with CSRF)")
    else:
        print("\nDatabase setup failed!")
    sys.exit(0 if success else 1)
