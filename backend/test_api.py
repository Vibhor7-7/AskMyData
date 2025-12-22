"""
REST API Test Script for AskMyData
Tests all authentication endpoints

Run this script while the Flask server is running:
python app.py (in another terminal)
python test_api.py
"""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:5001/api"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{YELLOW}→ {text}{RESET}")

def pretty_print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def test_health():
    """Test health check endpoint"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        print_info("Make sure Flask server is running: python app.py")
        return False

def test_register():
    """Test user registration"""
    print_header("TEST 2: User Registration")
    
    # Use timestamp to make username unique
    timestamp = datetime.now().strftime("%H%M%S")
    
    data = {
        "fullname": "Test User",
        "username": f"testuser{timestamp}",
        "email": f"test{timestamp}@example.com",
        "password": "password123"
    }
    
    print_info(f"Registering user: {data['username']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=data
        )
        
        if response.status_code == 201:
            print_success(f"Status Code: {response.status_code}")
            result = response.json()
            pretty_print_json(result)
            return response.cookies, result['user']['username']
        else:
            print_error(f"Status Code: {response.status_code}")
            print(response.json())
            return None, None
    except Exception as e:
        print_error(f"Request failed: {e}")
        return None, None

def test_register_duplicate(username):
    """Test registering with existing username"""
    print_header("TEST 3: Register Duplicate (Should Fail)")
    
    data = {
        "fullname": "Duplicate User",
        "username": username,
        "email": "duplicate@example.com",
        "password": "password123"
    }
    
    print_info(f"Attempting to register duplicate username: {username}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=data
        )
        
        if response.status_code == 409:
            print_success(f"Correctly rejected with Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return True
        else:
            print_error(f"Unexpected Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_login(username):
    """Test user login"""
    print_header("TEST 4: User Login")
    
    data = {
        "username": username,
        "password": "password123"
    }
    
    print_info(f"Logging in as: {username}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=data
        )
        
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return response.cookies
        else:
            print_error(f"Status Code: {response.status_code}")
            print(response.json())
            return None
    except Exception as e:
        print_error(f"Request failed: {e}")
        return None

def test_login_invalid():
    """Test login with invalid credentials"""
    print_header("TEST 5: Invalid Login (Should Fail)")
    
    data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    print_info("Attempting login with invalid credentials")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=data
        )
        
        if response.status_code == 401:
            print_success(f"Correctly rejected with Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return True
        else:
            print_error(f"Unexpected Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_get_current_user(cookies):
    """Test getting current user info"""
    print_header("TEST 6: Get Current User")
    
    print_info("Fetching current user info")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            cookies=cookies
        )
        
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_get_user_without_auth():
    """Test accessing protected route without authentication"""
    print_header("TEST 7: Access Protected Route Without Auth (Should Fail)")
    
    print_info("Attempting to access /auth/me without session cookie")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        
        if response.status_code == 401:
            print_success(f"Correctly rejected with Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return True
        else:
            print_error(f"Unexpected Status Code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_logout(cookies):
    """Test user logout"""
    print_header("TEST 8: User Logout")
    
    print_info("Logging out")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            cookies=cookies
        )
        
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_get_files(cookies):
    """Test getting user's files"""
    print_header("TEST 9: Get User Files")
    
    print_info("Fetching user's files")
    
    try:
        response = requests.get(
            f"{BASE_URL}/files",
            cookies=cookies
        )
        
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def test_ask_question(cookies):
    """Test asking a question"""
    print_header("TEST 10: Ask Question (Mock Response)")
    
    data = {
        "question": "What is the average age?"
    }
    
    print_info(f"Asking: {data['question']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json=data,
            cookies=cookies
        )
        
        if response.status_code == 200:
            print_success(f"Status Code: {response.status_code}")
            pretty_print_json(response.json())
            return True
        else:
            print_error(f"Status Code: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print("AskMyData REST API Test Suite")
    print(f"{'='*60}{RESET}")
    print(f"Testing API at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print_error("\n⚠️  Server is not running. Please start it with: python app.py")
        return
    
    # Test 2-3: Registration
    cookies, username = test_register()
    if cookies and username:
        results.append(("Register", True))
        results.append(("Duplicate Register", test_register_duplicate(username)))
    else:
        results.append(("Register", False))
        return
    
    # Test 4-5: Login
    results.append(("Login", bool(test_login(username))))
    results.append(("Invalid Login", test_login_invalid()))
    
    # Test 6-7: Authentication
    results.append(("Get Current User", test_get_current_user(cookies)))
    results.append(("Unauthorized Access", test_get_user_without_auth()))
    
    # Test 8: Logout
    results.append(("Logout", test_logout(cookies)))
    
    # Test 9-10: Files and Questions (with new login)
    new_cookies = test_login(username)
    if new_cookies:
        results.append(("Get Files", test_get_files(new_cookies)))
        results.append(("Ask Question", test_ask_question(new_cookies)))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{BLUE}{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}{RESET}\n")
    
    if passed == total:
        print_success("🎉 All tests passed!")
    else:
        print_error(f"⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    run_all_tests()
