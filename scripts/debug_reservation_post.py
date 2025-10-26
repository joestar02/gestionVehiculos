import re
import sys
import os
# Ensure repo root is on sys.path so 'app' package can be imported when running script directly
repo_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, repo_root)
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

app = create_app()
app.testing = True
client = app.test_client()
ensure_admin(app)

r = client.get('/auth/login')
html = r.data.decode('utf-8')
print('Login page fetched, len=', len(html))
token = extract_csrf(html)
print('csrf token:', token)
resp = client.post('/auth/login', data={'username':'admin','password':'admin123','csrf_token': token}, follow_redirects=True)
print('login status', resp.status_code)

r = client.get('/reservations/new')
html = r.data.decode('utf-8')
print('GET /reservations/new len=', len(html))
ctoken = extract_csrf(html)
print('form csrf', ctoken)
start = (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
end = (datetime.utcnow() + timedelta(days=2, hours=3)).strftime('%Y-%m-%dT%H:%M')
data = {'csrf_token': ctoken,'vehicle_id':1,'driver_id':1,'start_date':start,'end_date':end,'purpose':'Debug','destination':'X','notes':''}
pr = client.post('/reservations/new', data=data, follow_redirects=True)
print('POST status', pr.status_code)
print(pr.data.decode('utf-8'))
