#!/usr/bin/env python3
"""Test script to verify application can start without CSRF errors"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all controller imports work correctly"""
    try:
        print("Testing imports...")

        # Test main app creation
        from app.main import create_app
        print("✓ Successfully imported create_app")

        # Test individual controllers that had csrf_exempt issues
        from app.controllers.provider_controller import provider_bp
        print("✓ Successfully imported provider controller")

        from app.controllers.organization_controller import organization_bp
        print("✓ Successfully imported organization controller")

        from app.controllers.maintenance_controller import maintenance_bp
        print("✓ Successfully imported maintenance controller")

        from app.controllers.driver_controller import driver_bp
        print("✓ Successfully imported driver controller")

        # Test app creation
        print("Creating Flask application...")
        app = create_app()
        print("✓ Successfully created Flask application")

        print("✓ All tests passed! CSRF exempt errors should be resolved.")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
