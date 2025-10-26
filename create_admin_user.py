#!/usr/bin/env python3
"""
Script to create initial admin user for testing
"""
import os
import sys

# Set up environment
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_SQLITE'] = 'True'

# Add the project directory to the path
project_dir = r'c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, project_dir)

def create_admin_user():
    """Create initial admin user"""
    try:
        print("Creating Flask application...")
        from app.main import create_app
        app = create_app()

        with app.app_context():
            print("Application context established")

            from app.extensions import db
            from app.models.user import User, UserRole
            from app.core.security import get_password_hash

            # Check if admin user already exists
            existing_admin = User.query.filter_by(username='admin').first()
            if existing_admin:
                print("Admin user already exists!")
                return True

            print("Creating admin user...")
            admin_user = User(
                username='admin',
                email='admin@example.com',
                hashed_password=get_password_hash('admin123'),
                first_name='Administrador',
                last_name='Sistema',
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True
            )

            db.session.add(admin_user)
            db.session.commit()

            print("Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("You can now log in and access the application!")

            return True

    except Exception as e:
        print(f"Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_admin_user()
    if success:
        print("\nSetup completed! You can now:")
        print("1. Run: python run.py")
        print("2. Go to: http://127.0.0.1:5000/auth/login")
        print("3. Login with admin/admin123")
    else:
        print("\nFailed to create admin user!")
    sys.exit(0 if success else 1)
