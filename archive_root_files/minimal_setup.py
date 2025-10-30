#!/usr/bin/env python3
"""
Minimal database setup script
"""
import os
import sys

# Set up environment
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_SQLITE'] = 'True'

# Add the project directory to the path
project_dir = r'c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, project_dir)

def create_minimal_database():
    """Create minimal database with just tables"""
    try:
        print("Creating Flask application...")
        from app.main import create_app
        app = create_app()

        with app.app_context():
            print("Application context established")

            from app.extensions import db

            print("Creating all database tables...")
            db.create_all()

            print("SUCCESS: All database tables created!")

            # Check if providers table exists
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='providers'"))
            if result.fetchone():
                print("SUCCESS: Providers table exists!")
            else:
                print("ERROR: Providers table not found!")

            return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_minimal_database()
    if success:
        print("\nMinimal database setup successful!")
        print("You can now run: python run.py")
    else:
        print("\nDatabase setup failed!")
    sys.exit(0 if success else 1)
