"""Test script to check the organizations tree endpoint"""
import requests

# Update the base URL if your application is running on a different address
BASE_URL = 'http://localhost:5000'

def test_tree_endpoint():
    """Test the organizations tree endpoint"""
    url = f"{BASE_URL}/organizations/tree.json"
    print(f"Testing URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print("Response Headers:", response.headers)
        
        try:
            data = response.json()
            print("Response JSON:", data)
            return True
        except ValueError:
            print("Response is not valid JSON")
            print("Response Text:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return False

if __name__ == "__main__":
    test_tree_endpoint()
