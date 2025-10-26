"""
Script para inicializar la base de datos Flask con datos de prueba
"""
from datetime import datetime, timedelta, time
from app.main import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.organization import OrganizationUnit
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus, OwnershipType
from app.models.driver import Driver
from app.models.insurance import VehicleInsurance
from app.models.vehicle_assignment import VehicleAssignment
from app.services.auth_service import AuthService

def init_db():
    """Crear todas las tablas y datos iniciales"""
    app = create_app()
    
    with app.app_context():
        print("🗄️  Creando tablas...")
        db.create_all()
        print("✅ Tablas creadas")
        
        # Verificar si ya existe el usuario admin
        existing_user = User.query.filter_by(username="admin").first()
        if existing_user:
            print("⚠️  El usuario admin ya existe")
            return
        
        print("👤 Creando usuario administrador...")
        admin_user = AuthService.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            first_name="Administrador",
            last_name="Sistema",
            role=UserRole.ADMIN
        )
        admin_user.is_superuser = True
        db.session.commit()
        
        print("🏢 Creando unidades organizativas...")
        org_units = [
            OrganizationUnit(
                name="Dirección General",
                code="DG",
                description="Dirección General de la organización",
                manager_name="Juan Pérez",
                contact_email="juan.perez@example.com",
                contact_phone="+34 600 000 001"
            ),
            OrganizationUnit(
                name="Departamento de Operaciones",
                code="OPS",
                description="Gestión de operaciones diarias",
                manager_name="María García",
                contact_email="maria.garcia@example.com",
                contact_phone="+34 600 000 002"
            ),
            OrganizationUnit(
                name="Departamento Comercial",
                code="COM",
                description="Área comercial y ventas",
                manager_name="Carlos López",
                contact_email="carlos.lopez@example.com",
                contact_phone="+34 600 000 003"
            )
        ]
        
        for org_unit in org_units:
            db.session.add(org_unit)
        db.session.commit()
        
        print("🚗 Creando vehículos de ejemplo...")
        vehicles = [
            Vehicle(
                license_plate="1234ABC",
                make="Toyota",
                model="Corolla",
                year=2022,
                color="Blanco",
                vin="JT2BF18K0X0123456",
                vehicle_type=VehicleType.CAR,
                status=VehicleStatus.AVAILABLE,
                ownership_type=OwnershipType.OWNED,
                organization_unit_id=org_units[0].id,
                current_mileage=15000,
                fuel_type="gasoline",
                fuel_capacity=50,
                notes="Vehículo en excelente estado"
            ),
            Vehicle(
                license_plate="5678DEF",
                make="Ford",
                model="Transit",
                year=2021,
                color="Azul",
                vin="WF0XXXGCDXKW12345",
                vehicle_type=VehicleType.VAN,
                status=VehicleStatus.AVAILABLE,
                ownership_type=OwnershipType.OWNED,
                organization_unit_id=org_units[1].id,
                current_mileage=45000,
                fuel_type="diesel",
                fuel_capacity=80,
                notes="Furgoneta para transporte de mercancías"
            ),
            Vehicle(
                license_plate="9012GHI",
                make="Mercedes-Benz",
                model="Sprinter",
                year=2023,
                color="Blanco",
                vin="WDB9066331N123456",
                vehicle_type=VehicleType.VAN,
                status=VehicleStatus.IN_USE,
                ownership_type=OwnershipType.RENTING,
                organization_unit_id=org_units[1].id,
                current_mileage=8000,
                fuel_type="diesel",
                fuel_capacity=75,
                notes="Vehículo en renting a 36 meses"
            ),
            Vehicle(
                license_plate="3456JKL",
                make="Volkswagen",
                model="Golf",
                year=2020,
                color="Gris",
                vin="WVWZZZ1KZLW123456",
                vehicle_type=VehicleType.CAR,
                status=VehicleStatus.MAINTENANCE,
                ownership_type=OwnershipType.OWNED,
                organization_unit_id=org_units[2].id,
                current_mileage=65000,
                fuel_type="diesel",
                fuel_capacity=50,
                notes="En mantenimiento preventivo"
            ),
            Vehicle(
                license_plate="7890MNO",
                make="Tesla",
                model="Model 3",
                year=2023,
                color="Negro",
                vin="5YJ3E1EA1KF123456",
                vehicle_type=VehicleType.CAR,
                status=VehicleStatus.AVAILABLE,
                ownership_type=OwnershipType.LEASING,
                organization_unit_id=org_units[0].id,
                current_mileage=5000,
                fuel_type="electric",
                fuel_capacity=75,
                notes="Vehículo eléctrico en leasing"
            )
        ]
        
        for vehicle in vehicles:
            db.session.add(vehicle)
        db.session.commit()
        
        print("👨‍💼 Creando conductores de ejemplo...")
        from app.models.driver import DriverType, DriverStatus
        drivers = [
            Driver(
                first_name="Pedro",
                last_name="Martínez",
                document_type="DNI",
                document_number="12345678A",
                driver_license_number="B-12345678",
                driver_license_expiry=datetime.now() + timedelta(days=730),
                driver_type=DriverType.OFFICIAL,
                status=DriverStatus.ACTIVE,
                email="pedro.martinez@example.com",
                phone="+34 600 100 001",
                organization_unit_id=org_units[0].id
            ),
            Driver(
                first_name="Ana",
                last_name="Rodríguez",
                document_type="DNI",
                document_number="87654321B",
                driver_license_number="B-87654321",
                driver_license_expiry=datetime.now() + timedelta(days=1095),
                driver_type=DriverType.OFFICIAL,
                status=DriverStatus.ACTIVE,
                email="ana.rodriguez@example.com",
                phone="+34 600 100 002",
                organization_unit_id=org_units[1].id
            ),
            Driver(
                first_name="Luis",
                last_name="Fernández",
                document_type="DNI",
                document_number="11223344C",
                driver_license_number="C-11223344",
                driver_license_expiry=datetime.now() + timedelta(days=365),
                driver_type=DriverType.OFFICIAL,
                status=DriverStatus.ACTIVE,
                email="luis.fernandez@example.com",
                phone="+34 600 100 003",
                organization_unit_id=org_units[1].id
            )
        ]
        
        for driver in drivers:
            db.session.add(driver)
        db.session.commit()
        
        print("✅ Base de datos inicializada correctamente")
        print("\n📋 Credenciales de acceso:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("\n🚀 Puedes iniciar la aplicación con: python run.py")

if __name__ == "__main__":
    init_db()
