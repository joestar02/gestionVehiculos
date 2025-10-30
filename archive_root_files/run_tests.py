#!/usr/bin/env python3
"""
Test runner script for the vehicle management system
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests"""
    print("🚀 Running Vehicle Management System Tests")
    print("=" * 50)

    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'

    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/',
            '-v',
            '--tb=short',
            '--color=yes'
        ], capture_output=False, text=True)

        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")

        return result.returncode

    except FileNotFoundError:
        print("❌ pytest not found. Please install testing dependencies:")
        print("   pip install -r requirements-dev.txt")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

def run_security_tests():
    """Run only security tests"""
    print("🔒 Running Security Tests")
    print("=" * 30)

    os.environ['FLASK_ENV'] = 'testing'

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/test_security.py',
            '-v',
            '--tb=short',
            '--color=yes'
        ], capture_output=False, text=True)

        return result.returncode

    except Exception as e:
        print(f"❌ Error running security tests: {e}")
        return 1

def run_coverage():
    """Run tests with coverage report"""
    print("📊 Running Tests with Coverage")
    print("=" * 35)

    os.environ['FLASK_ENV'] = 'testing'

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/',
            '--cov=app',
            '--cov-report=html',
            '--cov-report=term-missing',
            '-v'
        ], capture_output=False, text=True)

        print("\n📄 Coverage report generated in htmlcov/index.html")
        return result.returncode

    except Exception as e:
        print(f"❌ Error running coverage: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "security":
            exit_code = run_security_tests()
        elif command == "coverage":
            exit_code = run_coverage()
        else:
            print("❌ Unknown command. Use: security, coverage, or run without arguments")
            exit_code = 1
    else:
        exit_code = run_tests()

    sys.exit(exit_code)
