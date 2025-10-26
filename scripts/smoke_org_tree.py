import sys, os
repo = r'C:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, repo)
from app.main import create_app
app = create_app()
app.testing = True
c = app.test_client()
with app.app_context():
    # Ensure an admin user exists and login
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    if not User.query.filter_by(username='admin').first():
        u = User(username='admin', email='admin@example.com', hashed_password=get_password_hash('admin123'), role=UserRole.ADMIN, is_active=True, is_superuser=True)
        from app.extensions import db
        db.session.add(u)
        db.session.commit()

    # Get login page and extract csrf
    resp = c.get('/auth/login')
    import re
    html = resp.data.decode('utf-8')
    m = re.search(r"name=['\"]csrf_token['\"]\s+value=['\"]([^'\"]+)['\"]", html)
    token = m.group(1) if m else None
    post = c.post('/auth/login', data={'username':'admin','password':'admin123','csrf_token': token}, follow_redirects=True)
    print('login status', post.status_code)

    r = c.get('/organizations/')
    print('status', r.status_code)
    print('len', len(r.data))
    text = r.data.decode('utf-8')
    # try to extract the JS treeData assignment
    import re
    # print the JS enhancement block if present
    mjs = re.search(r"<script>.*?</script>", text, re.S)
    if mjs:
        print('\nFound <script> block (first 800 chars):\n')
        print(mjs.group(0)[:800])
    else:
        print('\nNo inline <script> block found')
    # optionally show a small snippet around the tree div
    idx = text.find('id="org-tree"')
    if idx != -1:
        print('\nSnippet around org-tree:')
        print(text[idx-200:idx+400])

    # Fetch the JSON endpoint and print a brief summary
    rjson = c.get('/organizations/tree.json')
    print('\n/tree.json status', rjson.status_code)
    if rjson.status_code == 200:
        try:
            data = rjson.get_json()
            print('tree.json length:', len(data))
            if len(data):
                print('first node keys:', list(data[0].keys()))
        except Exception as e:
            print('Error parsing JSON:', e)
