"""
Script para inicializar la base de datos con datos de prueba
"""
from datetime import datetime, timedelta, time
from app.db.session import engine
from app.db.base import Base
from app.models import *
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

def init_db():
    """Crear todas las tablas y datos iniciales"""
    print("🗄️  Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas")
    
    db = Session(bind=engine)
    
    try:
        # Verificar si ya existe el usuario admin
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("⚠️  El usuario admin ya existe")
            return
        
        print("👤 Creando usuario administrador...")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            first_name="Administrador",
            last_name="Sistema",
            role=UserRole.ADMIN,
            is_superuser=True,
            is_active=True
        )
        db.add(admin_user)
        db.flush()
        
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
                description="Departamento de Operaciones",
                manager_name="María García",
                contact_email="maria.garcia@example.com",
                contact_phone="+34 600 000 002",
                parent_id=org_units[0].id if 'org_units' in locals() else None  # This will be set after creation
            ),
            OrganizationUnit(
                name="Departamento de Logística",
                code="LOG",
                description="Departamento de Logística",
                manager_name="Carlos Ruiz",
                contact_email="carlos.ruiz@example.com",
                contact_phone="+34 600 000 003",
                parent_id=org_units[0].id if 'org_units' in locals() else None  # This will be set after creation
            ),
            OrganizationUnit(
                name="Sección de Transportes",
                code="TRANS",
                description="Sección especializada en transporte",
                manager_name="Ana López",
                contact_email="ana.lopez@example.com",
                contact_phone="+34 600 000 004",
                parent_id=org_units[1].id if 'org_units' in locals() else None  # This will be set after creation
            ),
            OrganizationUnit(
                name="Sección de Mantenimiento",
                code="MANT",
                description="Sección de mantenimiento de vehículos",
                manager_name="Luis Fernández",
                contact_email="luis.fernandez@example.com",
                contact_phone="+34 600 000 005",
                parent_id=org_units[2].id if 'org_units' in locals() else None  # This will be set after creation
            )
        ]
        
        # Create organizations in order and set parent relationships properly
        for i, org in enumerate(org_units):
            if org.parent_id is None:
                db.add(org)
                db.flush()
            else:
                # Find parent by code and set parent_id
                parent_code = ["DG", "OPS", "DG", "OPS", "LOG"][i]
                parent = db.query(OrganizationUnit).filter_by(code=parent_code).first()
                if parent:
                    org.parent_id = parent.id
                db.add(org)
                db.flush()
        
        print("🏪 Creando proveedores de prueba...")
        providers = [
            Provider(
                name="Taller Mecánico Central",
                provider_type=ProviderType.WORKSHOP,
                contact_person="Antonio Ruiz",
                phone="+34 91 555 0001",
                email="info@tallermecanico.com",
                address="Calle Mayor 15, Madrid",
                website="https://tallermecanico.com",
                notes="Taller especializado en vehículos oficiales"
            ),
            Provider(
                name="Lavadero Express",
                provider_type=ProviderType.CAR_WASH,
                contact_person="María Santos",
                phone="+34 91 555 0002",
                email="contacto@lavaderoexpress.com",
                address="Avenida de la Paz 25, Madrid",
                notes="Servicio de limpieza especializado para flota oficial"
            ),
            Provider(
                name="Recambios Andalucía S.L.",
                provider_type=ProviderType.PARTS_STORE,
                contact_person="Francisco López",
                phone="+34 91 555 0003",
                email="ventas@recambiosandalucia.com",
                address="Polígono Industrial, Nave 12, Madrid",
                website="https://recambiosandalucia.com",
                notes="Proveedor oficial de piezas de repuesto"
            ),
            Provider(
                name="Asistencia 24h",
                provider_type=ProviderType.OTHER,
                contact_person="Carmen García",
                phone="+34 91 555 0004",
                email="info@asistencia24h.com",
                address="Calle de las Urgencias 1, Madrid",
                website="https://asistencia24h.com",
                notes="Servicio de asistencia en carretera 24/7"
            )
        ]
        for provider in providers:
            db.add(provider)
        db.flush()
        
        print("🚗 Creando vehículos de prueba...")
        vehicles = [
            Vehicle(
                license_plate="1234ABC",
                make="Toyota",
                model="Corolla",
                year=2022,
                color="Blanco",
                vin="JT2BF18K5X0123456",
                vehicle_type=VehicleType.CAR,
                status=VehicleStatus.AVAILABLE,
                ownership_type=OwnershipType.OWNED,
                organization_unit_id=org_units[0].id,
                current_mileage=15000,
                fuel_type="Gasolina",
                fuel_capacity=50
            ),
            Vehicle(
                license_plate="5678DEF",
                make="Ford",
                model="Transit",
                year=2021,
                color="Azul",
                vin="WF0RXXGBFRW123456",
                vehicle_type=VehicleType.VAN,
                status=VehicleStatus.AVAILABLE,
                ownership_type=OwnershipType.RENTING,
                organization_unit_id=org_units[1].id,
                current_mileage=45000,
                fuel_type="Diesel",
                fuel_capacity=80
            ),
            Vehicle(
                license_plate="9012GHI",
                make="Renault",
                model="Clio",
                year=2023,
                color="Rojo",
                vin="VF1RJA00123456789",
                vehicle_type=VehicleType.CAR,
                status=VehicleStatus.IN_USE,
                ownership_type=OwnershipType.OWNED,
                organization_unit_id=org_units[2].id,
                current_mileage=5000,
                fuel_type="Gasolina",
                fuel_capacity=45
            ),
            Vehicle(
                license_plate="3456JKL",
                make="Mercedes",
                model="Sprinter",
                year=2020,
                color="Blanco",
                vin="WDB9066331N123456",
                vehicle_type=VehicleType.VAN,
                status=VehicleStatus.MAINTENANCE,
                ownership_type=OwnershipType.RENTING,
                organization_unit_id=org_units[1].id,
                current_mileage=78000,
                fuel_type="Diesel",
                fuel_capacity=100
            )
        ]
        for vehicle in vehicles:
            db.add(vehicle)
        db.flush()
        
        print("👨‍✈️ Creando conductores de prueba...")
        drivers = [
            Driver(
                first_name="Pedro",
                last_name="Martínez",
                document_type="DNI",
                document_number="12345678A",
                driver_license_number="DL001234",
                driver_license_expiry=datetime.now() + timedelta(days=365*2),
                driver_type=DriverType.OFFICIAL,
                status=DriverStatus.ACTIVE,
                email="pedro.martinez@example.com",
                phone="+34 600 111 111",
                organization_unit_id=org_units[0].id,
                created_by=admin_user.id
            ),
            Driver(
                first_name="Ana",
                last_name="López",
                document_type="DNI",
                document_number="87654321B",
                driver_license_number="DL005678",
                driver_license_expiry=datetime.now() + timedelta(days=365*3),
                driver_type=DriverType.OFFICIAL,
                status=DriverStatus.ACTIVE,
                email="ana.lopez@example.com",
                phone="+34 600 222 222",
                organization_unit_id=org_units[1].id,
                created_by=admin_user.id
            ),
            Driver(
                first_name="Luis",
                last_name="Fernández",
                document_type="DNI",
                document_number="11223344C",
                driver_license_number="DL009012",
                driver_license_expiry=datetime.now() + timedelta(days=365),
                driver_type=DriverType.AUTHORIZED,
                status=DriverStatus.ACTIVE,
                email="luis.fernandez@example.com",
                phone="+34 600 333 333",
                organization_unit_id=org_units[2].id,
                created_by=admin_user.id
            )
        ]
        for driver in drivers:
            db.add(driver)
        db.flush()
        
        print("📅 Creando reservas de prueba...")
        today = datetime.now().date()
        reservations = [
            Reservation(
                vehicle_id=vehicles[0].id,
                driver_id=drivers[0].id,
                organization_unit_id=org_units[0].id,
                reservation_date=datetime.combine(today + timedelta(days=1), datetime.min.time()),
                start_time=time(9, 0),
                end_time=time(17, 0),
                status=ReservationStatus.CONFIRMED,
                purpose="Reunión con cliente",
                destination="Madrid Centro",
                estimated_km=50,
                created_by=admin_user.id
            ),
            Reservation(
                vehicle_id=vehicles[1].id,
                driver_id=drivers[1].id,
                organization_unit_id=org_units[1].id,
                reservation_date=datetime.combine(today + timedelta(days=2), datetime.min.time()),
                start_time=time(8, 0),
                end_time=time(14, 0),
                status=ReservationStatus.CONFIRMED,
                purpose="Entrega de material",
                destination="Zona Industrial",
                estimated_km=120,
                created_by=admin_user.id
            )
        ]
        for reservation in reservations:
            db.add(reservation)
        db.flush()
        
        print("🔧 Creando registros de mantenimiento...")
        maintenance_records = [
            MaintenanceRecord(
                vehicle_id=vehicles[3].id,
                maintenance_type=MaintenanceType.GENERAL_INSPECTION,
                status=MaintenanceStatus.IN_PROGRESS,
                scheduled_date=datetime.now(),
                mileage_at_service=78000,
                provider_id=providers[0].id,
                provider_name=providers[0].name,
                provider_contact=providers[0].contact_person,
                description="Revisión general programada",
                created_by=admin_user.id
            )
        ]
        for record in maintenance_records:
            db.add(record)
        db.flush()
        
        print("🚦 Creando registros de ITV...")
        itv_records = [
            ITVRecord(
                vehicle_id=vehicles[0].id,
                inspection_date=datetime.now() - timedelta(days=180),
                next_inspection_date=datetime.now() + timedelta(days=185),
                result="Favorable",
                station_name="ITV Madrid Norte",
                station_code="ITV001",
                certificate_number="CERT2024001"
            )
        ]
        for record in itv_records:
            db.add(record)
        
        db.commit()
        print("✅ Base de datos inicializada correctamente!")
        print("\n" + "="*50)
        print("📋 CREDENCIALES DE ACCESO:")
        print("="*50)
        print("Usuario: admin")
        print("Contraseña: admin123")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
