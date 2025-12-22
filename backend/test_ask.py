"""
Test the /api/ask endpoint with RAG integration
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
    
    data = {
        "username": "testuser",
        "password": "password123"
    }
    
    print_info("Logging in...")
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    
    if response.status_code == 200:
        print_success("Login successful")
        return response.cookies
    else:
        print_error(f"Login failed: {response.json()}")
        return None

def ask_questions(cookies):
    """Test asking questions"""
    print_header("Step 2: Ask Questions About Data")
    
    questions = [
        "What columns are in the dataset?",
        "How many rows are there?",
        "What is the first entry?",
        "Summarize the data"
    ]
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n{YELLOW}Question {i}/{len(questions)}:{RESET}")
        print(f"  {question}")
        
        data = {"question": question}
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                json=data,
                cookies=cookies
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Answer received (Status: {response.status_code})")
                print(f"\n{GREEN}Answer:{RESET}")
                print(f"  {result.get('answer', 'No answer')}")
                print(f"\n{BLUE}Metadata:{RESET}")
                print(f"  Chunks used: {result.get('num_chunks_used', 0)}")
                print(f"  Sources: {', '.join(result.get('sources', []))}")
                results.append(True)
            else:
                print_error(f"Failed (Status: {response.status_code})")
                print(response.json())
                results.append(False)
                
        except Exception as e:
            print_error(f"Request error: {e}")
            results.append(False)
    
    return results

def get_chat_history(cookies):
    """Get chat history"""
    print_header("Step 3: Get Chat History")
    
    print_info("Fetching chat history...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/ask/history",
            cookies=cookies
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Retrieved {result.get('count', 0)} chat messages")
            
            if result.get('history'):
                print("\n" + BLUE + "Recent Questions:" + RESET)
                for chat in result['history'][:5]:  # Show last 5
                    print(f"\n  Q: {chat['question']}")
                    print(f"  A: {chat['answer'][:100]}...")
                    print(f"  Time: {chat['timestamp']}")
            
            return True
        else:
            print_error(f"Failed to get history: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request error: {e}")
        return False

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print("AskMyData /api/ask Endpoint Test")
    print(f"{'='*60}{RESET}")
    print(f"Testing API at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Login
    cookies = login_user()
    if not cookies:
        print_error("\n⚠️  Authentication failed")
        return
    
    # Step 2: Ask questions
    results = ask_questions(cookies)
    
    # Step 3: Get chat history
    history_ok = get_chat_history(cookies)
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(results) + (1 if history_ok else 0)
    total = len(results) + 1
    
    print(f"Questions answered: {sum(results)}/{len(results)}")
    if history_ok:
        print_success("Chat history: PASSED")
    else:
        print_error("Chat history: FAILED")
    
    print(f"\n{BLUE}{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}{RESET}\n")
    
    if passed == total:
        print_success("🎉 All tests passed!")
        print(f"\n{GREEN}Your RAG pipeline is working end-to-end!{RESET}")
        print_info("You can now:")
        print_info("  1. Upload files via /api/files/upload")
        print_info("  2. Ask questions via /api/ask")
        print_info("  3. View history via /api/ask/history")
    else:
        print_error(f"⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    main()
