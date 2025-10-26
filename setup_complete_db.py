#!/usr/bin/env python3
"""
Complete database setup script with sample data
"""
import os
import sys

# Set up environment
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_SQLITE'] = 'True'

# Add the project directory to the path
project_dir = r'c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, project_dir)

def create_complete_database():
    """Create complete database with all tables and sample data"""
    try:
        print("Starting complete database setup...")

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

            print("Creating users...")
            from app.models.user import User, UserRole
            from app.models.driver import Driver, DriverType, DriverStatus
            from app.models.organization import OrganizationUnit
            from app.core.security import get_password_hash

            # Create organization units
            org1 = OrganizationUnit(
                name="Direccion General",
                code="DG",
                description="Direccion General",
                manager_name="Juan Perez",
                contact_email="juan.perez@empresa.com",
                contact_phone="+34 600 000 001"
            )
            db.session.add(org1)

            org2 = OrganizationUnit(
                name="Departamento de Ventas",
                code="DV",
                description="Departamento de Ventas",
                manager_name="Maria Garcia",
                contact_email="maria.garcia@empresa.com",
                contact_phone="+34 600 000 002",
                parent_id=1  # Child of Direccion General
            )
            db.session.add(org2)
            db.session.commit()

            # Create admin user
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

            # Create manager user
            manager_user = User(
                username='manager',
                email='manager@empresa.com',
                hashed_password=get_password_hash('manager123'),
                first_name='Gerente',
                last_name='Flota',
                role=UserRole.FLEET_MANAGER,
                is_active=True,
                is_superuser=False
            )
            db.session.add(manager_user)

            # Create driver user
            driver_user = User(
                username='conductor1',
                email='conductor1@empresa.com',
                hashed_password=get_password_hash('driver123'),
                first_name='Carlos',
                last_name='Rodriguez',
                role=UserRole.DRIVER,
                is_active=True,
                is_superuser=False
            )
            db.session.add(driver_user)
            db.session.commit()

            print("Creating vehicles...")
            from app.models.vehicle import Vehicle, VehicleType, OwnershipType, VehicleStatus

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
                fuel_capacity=50,
                notes="Vehiculo de empresa para uso general"
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
                fuel_capacity=80,
                notes="Furgoneta para transporte de mercancias"
            )
            db.session.add(vehicle2)
            db.session.commit()

            print("Creating drivers...")
            driver1 = Driver(
                first_name="Carlos",
                last_name="Rodriguez",
                document_type="DNI",
                document_number="12345678A",
                driver_license_number="B123456789",
                driver_license_expiry=datetime(2025, 12, 31),
                driver_type=DriverType.OFFICIAL,
                organization_unit_id=2,  # Departamento de Ventas
                email="carlos.rodriguez@empresa.com",
                phone="+34 600 000 003",
                address="Calle Mayor 123, Madrid",
                notes="Conductor oficial del departamento de ventas",
                user_id=3  # Associated with driver_user
            )
            db.session.add(driver1)

            driver2 = Driver(
                first_name="Ana",
                last_name="Martinez",
                document_type="DNI",
                document_number="87654321B",
                driver_license_number="B987654321",
                driver_license_expiry=datetime(2024, 6, 30),
                driver_type=DriverType.OFFICIAL,
                organization_unit_id=1,  # Direccion General
                email="ana.martinez@empresa.com",
                phone="+34 600 000 004",
                address="Avenida Diagonal 456, Barcelona",
                notes="Conductor oficial de direccion general"
            )
            db.session.add(driver2)
            db.session.commit()

            print("Creating providers...")
            from app.models.provider import Provider, ProviderType

            provider1 = Provider(
                name="Talleres Hermanos Lopez",
                provider_type=ProviderType.WORKSHOP,
                contact_person="Miguel Lopez",
                phone="+34 91 123 45 67",
                email="info@tallereslopez.com",
                address="Calle Mecanicos 789, Madrid",
                website="https://tallereslopez.com",
                notes="Taller especializado en mantenimiento de vehiculos Toyota"
            )
            db.session.add(provider1)

            provider2 = Provider(
                name="Lavadero Express",
                provider_type=ProviderType.CAR_WASH,
                contact_person="Carmen Ruiz",
                phone="+34 91 987 65 43",
                email="info@lavaderoexpress.com",
                address="Avenida Limpieza 321, Madrid",
                notes="Servicio de lavado y limpieza de vehiculos"
            )
            db.session.add(provider2)
            db.session.commit()

            print("Creating sample maintenance record...")
            from app.models.maintenance import MaintenanceRecord, MaintenanceType, MaintenanceStatus

            maintenance1 = MaintenanceRecord(
                vehicle_id=1,
                maintenance_type=MaintenanceType.PREVENTIVE,
                scheduled_date=datetime.now(),
                description="Mantenimiento preventivo 10.000 km",
                estimated_cost=150.0,
                provider_id=1,
                notes="Revision general segun programa de mantenimiento"
            )
            db.session.add(maintenance1)
            db.session.commit()

            print("Creating sample reservation...")
            from app.models.reservation import Reservation, ReservationStatus
            from datetime import timedelta

            tomorrow = datetime.now() + timedelta(days=1)
            day_after = tomorrow + timedelta(hours=4)

            reservation1 = Reservation(
                vehicle_id=1,
                driver_id=1,
                start_date=tomorrow,
                end_date=day_after,
                purpose="Visita a cliente importante",
                destination="Oficina central cliente, Barcelona",
                status=ReservationStatus.PENDING,
                user_id=1,  # Created by admin
                organization_unit_id=2
            )
            db.session.add(reservation1)
            db.session.commit()

            print("Database setup completed successfully!")

            # Verify all tables exist
            print("Verifying all tables...")
            from sqlalchemy import text

            tables_to_check = [
                'providers', 'drivers', 'vehicles', 'users', 'organization_units',
                'maintenance_records', 'reservations', 'vehicle_driver_associations'
            ]

            for table in tables_to_check:
                try:
                    result = db.session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                    if result.fetchone():
                        print(f"Table {table} exists")
                    else:
                        print(f"Table {table} missing")
                except Exception as e:
                    print(f"Error checking {table}: {e}")

            return True

    except Exception as e:
        print(f"Error during database setup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_complete_database()
    if success:
        print("\nComplete database setup successful!")
        print("\nAvailable test accounts:")
        print("  Admin: admin / admin123")
        print("  Manager: manager / manager123")
        print("  Driver: conductor1 / driver123")
        print("\nYou can now run: python run.py")
    else:
        print("\nDatabase setup failed!")
    sys.exit(0 if success else 1)
