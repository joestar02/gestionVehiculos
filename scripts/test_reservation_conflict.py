from app.main import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import re
from datetime import datetime, timedelta


def extract_csrf(html):
    m = re.search(r"name=[\"']csrf_token[\"']\s+value=[\"']([^\"']+)[\"']", html)
    if m:
        return m.group(1)
    m2 = re.search(r"csrf-token\" content=\"([^\"]+)\"", html)
    if m2:
        return m2.group(1)
    return None


def main():
    app = create_app()
    app.testing = True
    client = app.test_client()

    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                hashed_password=get_password_hash('admin123'),
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True
            )
            db.session.add(admin)
            db.session.commit()

    # login
    r = client.get('/auth/login')
    token = extract_csrf(r.data.decode('utf-8'))
    client.post('/auth/login', data={'username': 'admin', 'password': 'admin123', 'csrf_token': token}, follow_redirects=True)

    # create first reservation
    r = client.get('/reservations/new')
    token = extract_csrf(r.data.decode('utf-8'))
    start = (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
    end = (datetime.utcnow() + timedelta(days=2, hours=2)).strftime('%Y-%m-%dT%H:%M')
    data = {
        'csrf_token': token,
        'vehicle_id': 1,
        'driver_id': 1,
        'start_date': start,
        'end_date': end,
        'purpose': 'Reserva A',
        'destination': 'Test',
        'notes': ''
    }
    pr = client.post('/reservations/new', data=data, follow_redirects=True)
    print('Create A status', pr.status_code)

    # attempt overlapping reservation B
    r = client.get('/reservations/new')
    token = extract_csrf(r.data.decode('utf-8'))
    # B overlaps (start inside A)
    bstart = (datetime.utcnow() + timedelta(days=2, hours=1)).strftime('%Y-%m-%dT%H:%M')
    bend = (datetime.utcnow() + timedelta(days=2, hours=3)).strftime('%Y-%m-%dT%H:%M')
    data = {
        'csrf_token': token,
        'vehicle_id': 1,
        'driver_id': 1,
        'start_date': bstart,
        'end_date': bend,
        'purpose': 'Reserva B (overlap)',
        'destination': 'Test',
        'notes': ''
    }
    pr = client.post('/reservations/new', data=data, follow_redirects=True)
    content = pr.data.decode('utf-8')
    print('Create B status', pr.status_code)
    # Check if conflict template content present
    if 'Conflicto de Reserva' in content:
        print('Conflict page rendered')
    else:
        print('Conflict page NOT rendered - output snippet:')
        print(content[:1000])

if __name__ == '__main__':
    main()
