import sys, os, json
repo = r'C:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, repo)
from app.main import create_app
app = create_app()
app.testing = True
c = app.test_client()
with app.app_context():
    # ensure admin
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    from app.extensions import db
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin', email='admin@example.com', hashed_password=get_password_hash('admin123'), role=UserRole.ADMIN, is_active=True, is_superuser=True)
        db.session.add(u); db.session.commit()
    # login
    r = c.get('/auth/login')
    import re
    m = re.search(r"name=['\"]csrf_token['\"]\s+value=['\"]([^'\"]+)['\"]", r.data.decode('utf-8'))
    token = m.group(1) if m else None
    c.post('/auth/login', data={'username':'admin','password':'admin123','csrf_token': token}, follow_redirects=True)
    # call json endpoint
    r = c.get('/organizations/tree.json')
    print('status', r.status_code)
    data = r.get_json()
    print('json len', len(json.dumps(data)))
    print(data)
