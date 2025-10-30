"""
Script para probar las rutas de cumplimiento
"""
from app.main import create_app

def test_compliance_routes():
    """Test compliance routes"""
    app = create_app()

    with app.app_context():
        with app.test_client() as client:
            # Test login first
            login_response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=True)

            if login_response.status_code == 200:
                print("✅ Login successful")

                # Test compliance routes
                routes_to_test = [
                    '/compliance/itv',
                    '/compliance/taxes',
                    '/compliance/fines',
                    '/compliance/authorizations'
                ]

                for route in routes_to_test:
                    response = client.get(route)
                    print(f"Route {route}: {response.status_code}")
                    if response.status_code == 200:
                        print(f"  ✅ {route} accessible")
                    else:
                        print(f"  ❌ {route} error: {response.status_code}")
            else:
                print("❌ Login failed")

if __name__ == "__main__":
    print("Testing compliance routes...")
    test_compliance_routes()
