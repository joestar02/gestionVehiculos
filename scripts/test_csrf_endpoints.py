import re
from app.main import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.core.security import get_password_hash


def extract_csrf(html):
    m = re.search(r"name=[\"']csrf_token[\"']\s+value=[\"']([^\"']+)[\"']", html)
    if m:
        return m.group(1)
    # fallback: search for bare token rendered somewhere
    m2 = re.search(r"csrf-token\" content=\"([^\"]+)\"", html)
    if m2:
        return m2.group(1)
    return None


def test_endpoint(client, get_path, post_path, post_data=None):
    print(f"\nTesting GET {get_path} -> POST {post_path}")
    r = client.get(get_path)
    if r.status_code != 200:
        print(f"  GET returned status {r.status_code}; content-length={len(r.data)}")
    html = r.data.decode('utf-8')
    token = extract_csrf(html)
    if not token:
        print("  Could not extract CSRF token from GET response")
        return False
    data = post_data.copy() if post_data else {}
    data['csrf_token'] = token
    pr = client.post(post_path, data=data)
    txt = pr.data.decode('utf-8')
    if 'The CSRF token is missing' in txt or 'The CSRF token is invalid' in txt:
        print("  CSRF check FAILED: server reported missing/invalid token")
        return False
    # if server returns 400 with csrf failure, it's also failure
    if pr.status_code == 400:
        print(f"  POST returned 400; checking body for CSRF issue... len={len(txt)}")
        if 'CSRF' in txt or 'csrf' in txt:
            print("  CSRF check FAILED (400 + CSRF message)")
            return False
    print(f"  POST status {pr.status_code} -> CSRF appears OK (server did not reject token)")
    return True


def main():
    app = create_app()
    app.testing = True
    client = app.test_client()

    # Ensure admin user exists
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print('Creating admin user for tests...')
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
            print('Admin user created: admin/admin123')

    # Login via auth form (needs CSRF)
    login_get = client.get('/auth/login')
    login_html = login_get.data.decode('utf-8')
    login_token = extract_csrf(login_html)
    if not login_token:
        print('Could not extract CSRF token from login page; aborting tests')
        return

    resp = client.post('/auth/login', data={'username': 'admin', 'password': 'admin123', 'csrf_token': login_token}, follow_redirects=True)
    if resp.status_code != 200 or b'Dashboard' not in resp.data and b'Dashboard' not in resp.data:
        print('Login may have failed; status:', resp.status_code)
    else:
        print('Logged in as admin for tests')

    endpoints = [
        ('/compliance/authorizations/new', '/compliance/authorizations/new'),
        ('/compliance/itv/new', '/compliance/itv/new'),
        ('/compliance/taxes/new', '/compliance/taxes/new'),
        ('/compliance/fines/new', '/compliance/fines/new'),
        ('/compliance/insurances/new', '/compliance/insurances/new'),
    ]

    results = {}
    for get_path, post_path in endpoints:
        try:
            ok = test_endpoint(client, get_path, post_path, post_data={})
            results[get_path] = ok
        except Exception as e:
            import traceback
            print(f"  Exception testing {get_path}: {e}")
            traceback.print_exc()
            results[get_path] = False

    print('\nSummary:')
    for k, v in results.items():
        print(f" - {k}: {'OK' if v else 'FAILED'}")


if __name__ == '__main__':
    main()
