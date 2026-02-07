#!/usr/bin/env python3
"""
Script to start API and run demo
"""
import subprocess
import time
import sys
import requests
import signal
import os

def wait_for_api(max_retries=30, delay=1):
    """Wait for API to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:8000/health', timeout=2)
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if i < max_retries - 1:
            print(f"⏳ Waiting for API... ({i+1}/{max_retries})")
            time.sleep(delay)
    
    print("❌ API did not start in time")
    return False

def main():
    """Start API and run demo"""
    print("🚀 Starting API server...")
    
    # Start API process
    api_process = subprocess.Popen(
        [sys.executable, 'api_simple.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    try:
        # Wait for API to be ready
        if not wait_for_api():
            api_process.terminate()
            sys.exit(1)
        
        print("\n🎯 Running API Demo...")
        time.sleep(1)  # Give it a moment more
        
        # Run demo
        demo_process = subprocess.run(
            [sys.executable, 'demo_api.py'],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        sys.exit(demo_process.returncode)
        
    finally:
        # Cleanup
        print("\n🛑 Stopping API server...")
        api_process.terminate()
        try:
            api_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
            api_process.wait()
        print("✅ API server stopped")

if __name__ == '__main__':
    main()
