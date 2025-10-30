#!/usr/bin/env python3
"""Test script to verify application can start without errors"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing application imports...")
    from app.main import create_app
    print("✓ Successfully imported create_app")

    print("Creating Flask application...")
    app = create_app()
    print("✓ Successfully created Flask application")

    print("Testing blueprint registration...")
    with app.app_context():
        from app.controllers.organization_controller import organization_bp
        print("✓ Successfully imported organization controller")

    print("✓ All tests passed! Application should start correctly.")
    print("You can now run: python run.py")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
