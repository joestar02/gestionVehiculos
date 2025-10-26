import re
from app.main import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from datetime import datetime, timedelta


def extract_csrf(html):
    m = re.search(r"name=[\"']csrf_token[\"']\s+value=[\"']([^\"']+)[\"']", html)
    if m:
        return m.group(1)
    m2 = re.search(r"csrf-token\" content=\"([^\"]+)\"", html)
    if m2:
        return m2.group(1)
    return None


def ensure_admin(app):
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


def test_reservation_flow():
    app = create_app()
    app.testing = True
    client = app.test_client()

    ensure_admin(app)

    # login
    r = client.get('/auth/login')
    token = extract_csrf(r.data.decode('utf-8'))
    resp = client.post('/auth/login', data={'username': 'admin', 'password': 'admin123', 'csrf_token': token}, follow_redirects=True)
    assert resp.status_code == 200

    # create reservation
    r = client.get('/reservations/new')
    token = extract_csrf(r.data.decode('utf-8'))
    start = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
    end = (datetime.utcnow() + timedelta(days=1, hours=2)).strftime('%Y-%m-%dT%H:%M')
    data = {
        'csrf_token': token,
        'vehicle_id': 1,
        'driver_id': 1,
        'start_date': start,
        'end_date': end,
        'purpose': 'PyTest: crear reserva',
        'destination': 'Test',
        'notes': ''
    }
    pr = client.post('/reservations/new', data=data, follow_redirects=True)
    assert pr.status_code == 200
    # Accept success or conflict (test DB may already contain reservations)
    ok = (b'Reserva creada exitosamente' in pr.data or b'Reserva creada' in pr.data)
    conflict = b'Conflicto de Reserva' in pr.data or b'Reserva conflictiva' in pr.data
    assert ok or conflict

    # extract id
    mm = re.search(r"Reserva #([0-9]+)", pr.data.decode('utf-8'))
    res_id = int(mm.group(1)) if mm else None
    assert res_id is not None

    # edit
    edit_url = f'/reservations/{res_id}/edit'
    r = client.get(edit_url)
    if r.status_code == 200:
        token = extract_csrf(r.data.decode('utf-8'))
        data['csrf_token'] = token
        data['purpose'] = 'PyTest: editado'
        pr = client.post(edit_url, data=data, follow_redirects=True)
        assert pr.status_code == 200

    # confirm
    r = client.post(f'/reservations/{res_id}/confirm', data={'csrf_token': token}, follow_redirects=True)
    assert r.status_code == 200

    # start
    r = client.post(f'/reservations/{res_id}/start', data={'csrf_token': token, 'actual_start_mileage': '100'}, follow_redirects=True)
    assert r.status_code == 200

    # complete
    r = client.post(f'/reservations/{res_id}/complete', data={'csrf_token': token, 'actual_end_mileage': '120', 'completion_notes': 'OK'}, follow_redirects=True)
    assert r.status_code == 200

    # cancel (may be allowed even if completed; check response)
    r = client.post(f'/reservations/{res_id}/cancel', data={'csrf_token': token, 'cancellation_reason': 'Test cancel'}, follow_redirects=True)
    assert r.status_code == 200
