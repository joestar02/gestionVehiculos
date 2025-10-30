import sys
import types
from types import SimpleNamespace
from datetime import datetime, timedelta
import importlib


def make_query_stub(items):
    class Q:
        def filter_by(self, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return items

    return Q()


def setup_fake_models():
    # Create simple mock records with the attributes the service expects
    now = datetime.utcnow()

    assignment = SimpleNamespace(
        start_date=now - timedelta(days=30),
        end_date=now - timedelta(days=10),
        driver=SimpleNamespace(full_name='Juan Perez'),
        created_at=now - timedelta(days=31)
    )

    maintenance = SimpleNamespace(
        scheduled_date=now - timedelta(days=20),
        maintenance_type='Cambio de aceite',
        description='Cambio completo',
        cost=120.5,
        created_at=now - timedelta(days=21)
    )

    insurance = SimpleNamespace(
        start_date=now - timedelta(days=200),
        end_date=now + timedelta(days=165),
        insurance_company='Seguros S.A.',
        created_at=now - timedelta(days=200)
    )

    inspection = SimpleNamespace(
        inspection_date=now - timedelta(days=400),
        result='Apto',
        next_inspection_date=now + timedelta(days=360),
        created_at=now - timedelta(days=401)
    )

    tax = SimpleNamespace(
        due_date=now - timedelta(days=60),
        amount=200.0,
        payment_status=SimpleNamespace(value='pagado'),
        created_at=now - timedelta(days=61)
    )

    fine = SimpleNamespace(
        fine_date=now - timedelta(days=15),
        amount=75.0,
        status=SimpleNamespace(value='pendiente'),
        created_at=now - timedelta(days=16)
    )

    auth = SimpleNamespace(
        start_date=now - timedelta(days=100),
        authorization_type='ZBE',
        authorization_number='AUTH-123',
        issuing_authority='Ayuntamiento',
        zone_description='Centro',
        end_date=now + timedelta(days=200),
        created_at=now - timedelta(days=101)
    )

    # Prepare fake modules
    mods = {}
    mods['app.extensions'] = types.ModuleType('app.extensions')
    # minimal db placeholder: provide a Model base so model class definitions don't fail
    mods['app.extensions'].db = SimpleNamespace(Model=type('ModelBase', (), {}))

    mods['app.models.vehicle_assignment'] = types.ModuleType('app.models.vehicle_assignment')
    mods['app.models.vehicle_assignment'].VehicleAssignment = SimpleNamespace(query=make_query_stub([assignment]))

    mods['app.models.maintenance'] = types.ModuleType('app.models.maintenance')
    mods['app.models.maintenance'].MaintenanceRecord = SimpleNamespace(query=make_query_stub([maintenance]))

    mods['app.models.insurance'] = types.ModuleType('app.models.insurance')
    mods['app.models.insurance'].VehicleInsurance = SimpleNamespace(query=make_query_stub([insurance]))

    mods['app.models.itv'] = types.ModuleType('app.models.itv')
    mods['app.models.itv'].ITVRecord = SimpleNamespace(query=make_query_stub([inspection]))

    mods['app.models.tax'] = types.ModuleType('app.models.tax')
    mods['app.models.tax'].VehicleTax = SimpleNamespace(query=make_query_stub([tax]))

    mods['app.models.fine'] = types.ModuleType('app.models.fine')
    mods['app.models.fine'].Fine = SimpleNamespace(query=make_query_stub([fine]))

    mods['app.models.authorization'] = types.ModuleType('app.models.authorization')
    mods['app.models.authorization'].UrbanAccessAuthorization = SimpleNamespace(query=make_query_stub([auth]))

    # Insert fake modules into sys.modules
    for name, module in mods.items():
        sys.modules[name] = module


def test_get_vehicle_history_no_crash():
    """Ensure VehicleHistoryService.get_vehicle_history runs without raising and returns items."""
    setup_fake_models()

    # Import the service after faking modules
    vh = importlib.import_module('app.services.vehicle_history_service')

    history = vh.VehicleHistoryService.get_vehicle_history(1)

    assert isinstance(history, list)
    # Should contain at least one of each type we mocked
    types_present = {item['type'] for item in history}
    assert 'assignment' in types_present
    assert 'maintenance' in types_present
    assert 'insurance' in types_present
    assert 'inspection' in types_present
    assert 'tax' in types_present
    assert 'fine' in types_present
    assert 'authorization' in types_present
