import os, sys
project_dir = r'c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app.main import create_app
from app.extensions import db
from app.services.vehicle_service import VehicleService
from app.models.vehicle import VehicleType, OwnershipType

app = create_app()
with app.app_context():
    try:
        v = VehicleService.create_vehicle(
            license_plate='TEST123',
            make='Ford',
            model='Transit',
            year=2000,
            vehicle_type=VehicleType.VAN,
            ownership_type=OwnershipType.RENTING,
            organization_unit_id=1,
            color='az',
            vin='',
            fuel_type='diesel',
            fuel_capacity=34,
            notes=''
        )
        print('Created vehicle:', v.id, v.license_plate, v.vin)
    except Exception as e:
        print('Error creating vehicle:', type(e).__name__, str(e))
