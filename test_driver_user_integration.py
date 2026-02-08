#!/usr/bin/env python
"""Test script to validate driver/user integration"""

import os
import sys
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.driver import Driver, DriverType, DriverStatus
from app.services.auth_service import AuthService
from app.services.driver_service import DriverService

def test_driver_user_integration():
    """Test creating a driver with an associated user account"""
    
    # Create test app with testing config
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        # Create all tables first
        db.create_all()
        
        # Clean up any existing test data
        test_user = User.query.filter_by(username='test_driver').first()
        if test_user:
            Driver.query.filter_by(user_id=test_user.id).delete()
            User.query.filter_by(username='test_driver').delete()
            db.session.commit()
        
        print("=" * 60)
        print("Testing Driver/User Integration")
        print("=" * 60)
        
        # Test 1: Create a user first
        print("\n1. Creating user account...")
        try:
            # Call the static method directly
            user = AuthService.create_user(
                username='test_driver',
                email='test_driver@example.com',
                password='password123',
                first_name='Juan',
                last_name='Garcia',
                role=UserRole.DRIVER
            )
            print(f"   [PASS] User created: {user.username} (ID: {user.id})")
            print(f"   [PASS] User role: {user.role}")
            assert user.role == UserRole.DRIVER, "User role should be DRIVER"
            assert user.username == 'test_driver', "Username mismatch"
        except Exception as e:
            print(f"   [FAIL] Error creating user: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 2: Create a driver linked to the user
        print("\n2. Creating driver linked to user...")
        try:
            license_expiry = datetime.now() + timedelta(days=365)
            driver = DriverService.create_driver(
                first_name='Juan',
                last_name='Garcia',
                document_type='DNI',
                document_number='12345678A',
                driver_license_number='DL123456',
                driver_license_expiry=license_expiry,
                driver_type=DriverType.OFFICIAL,
                email='test_driver@example.com',
                phone='555-1234',
                address='123 Test St',
                notes='Test driver',
                user_id=user.id  # Link to the user
            )
            print(f"   [PASS] Driver created: {driver.full_name} (ID: {driver.id})")
            print(f"   [PASS] Driver user_id: {driver.user_id}")
            assert driver.user_id == user.id, "Driver user_id should match created user"
        except Exception as e:
            print(f"   [FAIL] Error creating driver: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 3: Verify relationship works
        print("\n3. Verifying relationships...")
        try:
            # Check driver -> user relationship
            driver_from_db = Driver.query.get(driver.id)
            assert driver_from_db.user is not None, "Driver should have associated user"
            assert driver_from_db.user.id == user.id, "Driver user relationship incorrect"
            print(f"   [PASS] Driver.user relationship works: {driver_from_db.user.username}")
            
            # Check user -> driver relationship
            user_from_db = User.query.get(user.id)
            assert user_from_db.driver is not None, "User should have associated driver"
            assert user_from_db.driver.id == driver.id, "User driver relationship incorrect"
            print(f"   [PASS] User.driver relationship works: {user_from_db.driver.full_name}")
        except Exception as e:
            print(f"   [FAIL] Error verifying relationships: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 4: Verify driver appears in list filtered by user role
        print("\n4. Verifying driver appears in DRIVER role list...")
        try:
            driver_users = User.query.filter_by(role=UserRole.DRIVER, is_active=True).all()
            driver_ids = [d.id for d in driver_users]
            assert user.id in driver_ids, "User not found in DRIVER role list"
            
            driver_list = [u.driver for u in driver_users if u.driver and u.driver.is_active]
            found = False
            for d in driver_list:
                if d.id == driver.id:
                    found = True
                    print(f"   [PASS] Driver found in filtered list: {d.full_name}")
                    break
            
            assert found, "Driver not found in filtered list"
        except Exception as e:
            print(f"   [FAIL] Error verifying filtered list: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 5: Verify email sync
        print("\n5. Verifying email consistency...")
        try:
            driver_check = Driver.query.get(driver.id)
            user_check = User.query.get(user.id)
            assert driver_check.email == user_check.email, "Email mismatch between driver and user"
            print(f"   [PASS] Email consistent: {driver_check.email} == {user_check.email}")
        except Exception as e:
            print(f"   [FAIL] Error verifying email: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Clean up
        print("\n6. Cleaning up test data...")
        try:
            Driver.query.filter_by(id=driver.id).delete()
            User.query.filter_by(id=user.id).delete()
            db.session.commit()
            print("   [PASS] Test data cleaned up")
        except Exception as e:
            print(f"   [FAIL] Error cleaning up: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = test_driver_user_integration()
    sys.exit(0 if success else 1)
