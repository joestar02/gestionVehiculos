#!/usr/bin/env python3
"""Simple script to create database tables"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import Flask app factory
    from app.main import create_app

    print("Creating Flask app...")
    app = create_app()

    print("Setting up app context...")
    with app.app_context():
        # Import database extension
        from app.extensions import db

        print("Importing all models to ensure they are registered...")
        # Import all models to make sure they are registered with SQLAlchemy
        from app.models import (
            provider, driver, vehicle, user, organization,
            maintenance, reservation, fine, insurance,
            itv, tax, accident, authorization,
            renting_contract, vehicle_driver_association,
            vehicle_pickup
        )

        print("Creating all database tables...")
        db.create_all()

        print("✅ Database tables created successfully!")

        # Verify the providers table exists
        try:
            from sqlalchemy import text
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='providers'"))
            if result.fetchone():
                print("✅ Providers table exists and is ready!")
            else:
                print("❌ Providers table not found!")
        except Exception as e:
            print(f"Error checking providers table: {e}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("🎉 Database setup complete!")
