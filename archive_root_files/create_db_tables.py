import os
import sys

# Set up environment
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_SQLITE'] = 'True'

# Add the project directory to the path
project_dir = r'c:\Users\ramon\OneDrive\Documentos\windsurf\gestionVehiculos'
sys.path.insert(0, project_dir)

def create_tables():
    try:
        print("Creating Flask application...")
        from app.main import create_app
        app = create_app()

        with app.app_context():
            print("Application context established")

            # Import database
            from app.extensions import db

            print("Importing all models...")
            # Import models to register them with SQLAlchemy
            from app.models import provider, driver, vehicle, user, organization
            from app.models import maintenance, reservation, fine, insurance
            from app.models import itv, tax, accident, authorization
            from app.models import renting_contract, vehicle_driver_association, vehicle_pickup
            from app.models import permission

            print("Creating database tables...")
            db.create_all()

            print("Verifying providers table...")
            # Check if providers table exists
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='providers'"))
            if result.fetchone():
                print("SUCCESS: Providers table created!")
                return True
            else:
                print("ERROR: Providers table not found!")
                return False

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\nDatabase tables created successfully!")
        print("You can now run: python run.py")
    else:
        print("\nFailed to create database tables!")
    sys.exit(0 if success else 1)
