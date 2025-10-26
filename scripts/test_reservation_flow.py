from app.main import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import re


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
            print('Created admin admin/admin123')

    # login
    r = client.get('/auth/login')
    token = extract_csrf(r.data.decode('utf-8'))
    resp = client.post('/auth/login', data={'username': 'admin', 'password': 'admin123', 'csrf_token': token}, follow_redirects=True)
    if resp.status_code == 200:
        print('Logged in as admin')
    else:
        print('Login failed', resp.status_code)
        return

    # Prepare data: pick first vehicle and first driver
    # GET reservations form to find available vehicles/drivers and CSRF
    r = client.get('/reservations/new')
    html = r.data.decode('utf-8')
    token = extract_csrf(html)
    # crude extraction of first vehicle and driver ids
    veh_match = re.search(r"<option value=\"(\d+)\">[\s\S]*?<?\w*?>?(.*?)</option>", html)
    vehicle_id = None
    if veh_match:
        vehicle_id = veh_match.group(1)
    driver_match = re.search(r"<option value=\"(\d+)\">[\s\S]*?<?\w*?>?(.*?)</option>", html)
    driver_id = vehicle_id  # fallback

    # create a reservation
    from datetime import datetime, timedelta
    start = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
    end = (datetime.utcnow() + timedelta(days=1, hours=2)).strftime('%Y-%m-%dT%H:%M')

    data = {
        'csrf_token': token,
        'vehicle_id': vehicle_id or 1,
        'driver_id': driver_id or 1,
        'start_date': start,
        'end_date': end,
        'purpose': 'Prueba automatizada',
        'destination': 'Oficina',
        'notes': 'Creada por script de pruebas',
        'organization_unit_id': 1
    }

    pr = client.post('/reservations/new', data=data, follow_redirects=True)
    if pr.status_code == 200 and b'Reserva creada exitosamente' in pr.data:
        print('Create reservation: OK')
    else:
        print('Create reservation may have failed; status', pr.status_code)
        print(pr.data.decode('utf-8')[:1000])
        return

    # get reservation id from redirect page
    m = re.search(r"/reservations/(\d+)", pr.request.path)
    # fallback: scan page for "Reserva #ID"
    if m:
        res_id = int(m.group(1))
    else:
        mm = re.search(r"Reserva #([0-9]+)", pr.data.decode('utf-8'))
        res_id = int(mm.group(1)) if mm else None

    print('Created reservation id:', res_id)

    # edit reservation: load edit form (not implemented explicitly - reuse new form route if edit exists)
    edit_url = f'/reservations/{res_id}/edit'
    r = client.get(edit_url)
    if r.status_code == 200:
        token = extract_csrf(r.data.decode('utf-8'))
        data['csrf_token'] = token
        data['purpose'] = 'Prueba automatizada - editada'
        pr = client.post(edit_url, data=data, follow_redirects=True)
        if pr.status_code == 200:
            print('Edit reservation: OK')
        else:
            print('Edit reservation failed', pr.status_code)
    else:
        print('Edit form not found; skipping edit')

    # confirm
    r = client.post(f'/reservations/{res_id}/confirm', data={'csrf_token': token}, follow_redirects=True)
    if r.status_code == 200:
        print('Confirm reservation: OK')
    else:
        print('Confirm failed', r.status_code)

    # start reservation (simulate starting)
    r = client.post(f'/reservations/{res_id}/start', data={'csrf_token': token, 'actual_start_mileage': '100'}, follow_redirects=True)
    if r.status_code == 200:
        print('Start reservation: OK')
    else:
        print('Start failed', r.status_code)

    # complete reservation
    r = client.post(f'/reservations/{res_id}/complete', data={'csrf_token': token, 'actual_end_mileage': '120', 'completion_notes': 'Todo OK'}, follow_redirects=True)
    if r.status_code == 200:
        print('Complete reservation: OK')
    else:
        print('Complete failed', r.status_code)

    # cancel reservation (should be possible only if pending/confirmed; may not apply now)
    r = client.post(f'/reservations/{res_id}/cancel', data={'csrf_token': token, 'cancellation_reason': 'Prueba cancel'}, follow_redirects=True)
    if r.status_code == 200:
        print('Cancel reservation request: OK')
    else:
        print('Cancel failed', r.status_code)


if __name__ == '__main__':
    main()
