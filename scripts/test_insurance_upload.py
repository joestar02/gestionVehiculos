from app.main import create_app
from io import BytesIO
import os

app = create_app()
app.testing = True
client = app.test_client()

# Ensure admin exists and login
with app.app_context():
    from app.models.user import User, UserRole
    from app.extensions import db
    from app.core.security import get_password_hash
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com', hashed_password=get_password_hash('admin123'), first_name='Admin', last_name='User', role=UserRole.ADMIN, is_active=True, is_superuser=True)
        db.session.add(admin)
        db.session.commit()

# login
r = client.get('/auth/login')
html = r.data.decode('utf-8')
import re
m = re.search(r"name=['\"]csrf_token['\"]\s+value=['\"]([^'\"]+)['\"]", html)
if not m:
    print('Could not find csrf token on login page')
    raise SystemExit(1)
token = m.group(1)
resp = client.post('/auth/login', data={'username':'admin','password':'admin123','csrf_token':token}, follow_redirects=True)
print('Login status', resp.status_code)

# GET insurance new page to get csrf and form
r2 = client.get('/compliance/insurances/new')
html2 = r2.data.decode('utf-8')
m2 = re.search(r"name=['\"]csrf_token['\"]\s+value=['\"]([^'\"]+)['\"]", html2)
if not m2:
    print('No csrf on insurance form')
    raise SystemExit(1)
form_token = m2.group(1)

# prepare file
fake_pdf = BytesIO(b"%PDF-1.4\n%FakePDF\n")
fake_pdf.name = 'policy.pdf'
fake_pdf.seek(0)

# get a vehicle id from DB
with app.app_context():
    from app.models.vehicle import Vehicle
    v = Vehicle.query.first()
    if not v:
        print('No vehicle in DB to attach insurance to; aborting test')
        raise SystemExit(1)
    vid = v.id

post = {
    'vehicle_id': str(vid),
    'insurance_type': 'responsabilidad_civil',
    'insurance_company': 'ACME Seguros',
    'policy_number': 'TEST-POL-12345',
    'premium_amount': '123.45',
    'start_date': '2025-10-01',
    'end_date': '2026-10-01',
    'coverage_details': 'Cobertura completa',
    'notes': 'Prueba'
}

data = {**post, 'csrf_token': form_token, 'document': (fake_pdf, fake_pdf.name)}
resp2 = client.post('/compliance/insurances/new', data=data, content_type='multipart/form-data', follow_redirects=True)
print('POST status', resp2.status_code)
print('Response length', len(resp2.data))

# Check that the insurance record exists
with app.app_context():
    from app.models.insurance import VehicleInsurance
    ins = VehicleInsurance.query.filter_by(policy_number='TEST-POL-12345').first()
    if ins:
        print('Insurance created, id=', ins.id, 'document_path=', ins.document_path)
    else:
        print('Insurance not found after POST')
