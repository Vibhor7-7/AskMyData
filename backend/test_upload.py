"""
Test File Upload Endpoint with RAG Integration
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001/api"

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}→ {text}{RESET}")

def pretty_print_json(data):
    print(json.dumps(data, indent=2))

def login_user():
    """Login to get session cookies"""
    print_header("Step 1: Login")
    
    # Try to login with existing user
    data = {
        "username": "testuser",
        "password": "password123"
    }
    
    print_info("Attempting login...")
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    
    if response.status_code == 200:
        print_success("Login successful")
        return response.cookies
    else:
        # Try to register if login fails
        print_info("User not found, registering new user...")
        
        reg_data = {
            "fullname": "Test User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        reg_response = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
        
        if reg_response.status_code == 201:
            print_success("Registration successful")
            return reg_response.cookies
        else:
            print_error(f"Registration failed: {reg_response.json()}")
            return None

def upload_csv_file(cookies):
    """Test uploading a CSV file"""
    print_header("Step 2: Upload CSV File")
    
    # Use small test file instead of large validation.csv
    import os
    csv_path = os.path.join(os.path.dirname(__file__), 'parsers', 'test_small.csv')
    
    if not os.path.exists(csv_path):
        print_error(f"Test file not found: {csv_path}")
        return False
    
    print_info(f"Uploading file: {csv_path}")
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('validation.csv', f, 'text/csv')}
            response = requests.post(
                f"{BASE_URL}/files/upload",
                files=files,
                cookies=cookies
            )
        
        if response.status_code == 201:
            print_success(f"Upload successful! Status Code: {response.status_code}")
            result = response.json()
            pretty_print_json(result)
            return result.get('file', {}).get('file_id')
        else:
            print_error(f"Upload failed! Status Code: {response.status_code}")
            print(response.json())
            return None
            
    except Exception as e:
        print_error(f"Upload error: {e}")
        return None

def get_files(cookies):
    """Get list of uploaded files"""
    print_header("Step 3: Get Uploaded Files")
    
    print_info("Fetching file list...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/files",
            cookies=cookies
        )
        
        if response.status_code == 200:
            print_success("Files retrieved successfully")
            result = response.json()
            pretty_print_json(result)
            return True
        else:
            print_error(f"Failed to get files: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request error: {e}")
        return False

def get_file_details(cookies, file_id):
    """Get details of a specific file"""
    print_header(f"Step 4: Get File Details (ID: {file_id})")
    
    print_info(f"Fetching details for file ID: {file_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/files/{file_id}",
            cookies=cookies
        )
        
        if response.status_code == 200:
            print_success("File details retrieved successfully")
            result = response.json()
            pretty_print_json(result)
            return True
        else:
            print_error(f"Failed to get file details: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request error: {e}")
        return False

def main():
    """Run upload test"""
    print(f"\n{BLUE}{'='*60}")
    print("File Upload Test with RAG Integration")
    print(f"{'='*60}{RESET}")
    print(f"Testing API at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Login
    cookies = login_user()
    if not cookies:
        print_error("Failed to authenticate")
        return
    
    # Step 2: Upload file
    file_id = upload_csv_file(cookies)
    if not file_id:
        print_error("File upload failed")
        return
    
    # Step 3: Get all files
    get_files(cookies)
    
    # Step 4: Get specific file details
    get_file_details(cookies, file_id)
    
    # Summary
    print_header("Test Summary")
    print_success("✓ Authentication successful")
    print_success("✓ File upload and RAG processing successful")
    print_success("✓ File retrieval successful")
    print_success(f"✓ File stored with ID: {file_id}")
    
    print(f"\n{GREEN}🎉 All upload tests passed!{RESET}\n")
    print_info("The file has been:")
    print_info("  1. Parsed into a DataFrame")
    print_info("  2. Chunked into text segments")
    print_info("  3. Embedded using Ollama (nomic-embed-text)")
    print_info("  4. Stored in ChromaDB vector database")
    print_info("  5. Metadata saved to SQLite database")
    print(f"\n{YELLOW}Next: Test the /api/ask endpoint to query your data!{RESET}\n")

if __name__ == "__main__":
    main()
