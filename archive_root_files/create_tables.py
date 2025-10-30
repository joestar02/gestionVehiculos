#!/usr/bin/env python3
"""
Script to create database tables using Flask-SQLAlchemy
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_tables():
    """Create all database tables"""
    try:
        from app.main import create_app
        print("Creating Flask application...")
        app = create_app()

        with app.app_context():
            from sqlalchemy import text
            from app.extensions import db
            from app.models.provider import Provider
            from app.models.driver import Driver
            from app.models.vehicle import Vehicle
            from app.models.user import User
            from app.models.organization import OrganizationUnit
            from app.models.maintenance import MaintenanceRecord
            from app.models.reservation import Reservation
            from app.models.fine import Fine
            # insurance.py defines VehicleInsurance (table: vehicle_insurances)
            # import the actual class so SQLAlchemy registers the model
            from app.models.insurance import VehicleInsurance
            from app.models.itv import ITVRecord
            from app.models.tax import VehicleTax
            from app.models.accident import Accident
            from app.models.authorization import UrbanAccessAuthorization
            from app.models.renting_contract import RentingContract
            from app.models.vehicle_driver_association import VehicleDriverAssociation
            from app.models.vehicle_pickup import VehiclePickup

            print("Creating all database tables...")
            db.create_all()
            print("✅ All tables created successfully!")

            # Verify providers table exists (use text() for raw SQL)
            try:
                result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='providers'"))
                if result.fetchone():
                    print("✅ Providers table exists!")
                else:
                    print("❌ Providers table not found!")
            except Exception as e:
                print(f"❌ Error checking providers table: {e}")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)
