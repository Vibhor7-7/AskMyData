"""
AskMyData REST API
RESTful backend for data analysis with RAG pipeline
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'AskMyData'  # Change this in production!

# Configure CORS
CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:3000", "http://localhost:5173"])  # Allow frontend

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_db():
    """Initialize database tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        fullname TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Files table
    c.execute('''CREATE TABLE IF NOT EXISTS files (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_path TEXT NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        num_rows INTEGER,
        num_columns INTEGER,
        collection_name TEXT,
        FOREIGN KEY (username) REFERENCES users(username)
    )''')
    
    # Chat history table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        file_id INTEGER,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES users(username),
        FOREIGN KEY (file_id) REFERENCES files(file_id)
    )''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

# Initialize on startup
init_db()

# ============================================
# AUTHENTICATION DECORATOR
# ============================================

def login_required(f):
    """
    Decorator to protect routes that require authentication
    
    Usage:
    @app.route('/api/protected')
    @login_required
    def protected_route():
        username = session['username']
        return jsonify({"message": f"Hello {username}"})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({
                "error": "Authentication required",
                "authenticated": False
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Response: 200 OK
    {
        "status": "ok",
        "message": "API is running",
        "timestamp": "2025-12-22T10:30:00"
    }
    """
    return jsonify({
        "status": "ok",
        "message": "AskMyData API is running",
        "timestamp": datetime.now().isoformat()
    })

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register new user
    
    Request Body:
    {
        "fullname": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "password": "password123"
    }
    
    Response: 201 Created
    {
        "success": true,
        "message": "User registered successfully",
        "user": {
            "username": "johndoe",
            "fullname": "John Doe",
            "email": "john@example.com"
        }
    }
    """
    # Get JSON data from request body
    data = request.get_json()
    
    # Validation
    required_fields = ['fullname', 'username', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400
    
    fullname = data['fullname']
    username = data['username']
    email = data['email']
    password = data['password']
    
    # Hash password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Insert into database
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)",
            (fullname, username, email, hashed_password)
        )
        conn.commit()
        conn.close()
        
        # Set session
        session['username'] = username
        
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user": {
                "username": username,
                "fullname": fullname,
                "email": email
            }
        }), 201
        
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Username already exists"
        }), 409

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login user
    
    Request Body:
    {
        "username": "johndoe",
        "password": "password123"
    }
    
    Response: 200 OK
    {
        "success": true,
        "message": "Logged in successfully",
        "user": {
            "username": "johndoe",
            "fullname": "John Doe",
            "email": "john@example.com"
        }
    }
    """
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            "error": "Username and password required"
        }), 400
    
    # Query database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT password, fullname, email FROM users WHERE username = ?",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    
    # Check credentials
    if row is None or not check_password_hash(row[0], password):
        return jsonify({
            "error": "Invalid username or password"
        }), 401
    
    # Set session
    session['username'] = username
    
    return jsonify({
        "success": True,
        "message": "Logged in successfully",
        "user": {
            "username": username,
            "fullname": row[1],
            "email": row[2]
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """
    Logout current user
    
    Response: 200 OK
    {
        "success": true,
        "message": "Logged out successfully"
    }
    """
    session.pop('username', None)
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })

@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get current logged-in user
    
    Response: 200 OK
    {
        "authenticated": true,
        "user": {
            "username": "johndoe",
            "fullname": "John Doe",
            "email": "john@example.com"
        }
    }
    """
    username = session['username']
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT fullname, email FROM users WHERE username = ?",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            "authenticated": True,
            "user": {
                "username": username,
                "fullname": row[0],
                "email": row[1]
            }
        })
    
    return jsonify({"authenticated": False}), 401

# ============================================
# FILE ENDPOINTS (TODO: Will implement next)
# ============================================

@app.route('/api/files/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload and process file"""
    return jsonify({"message": "Coming soon - will integrate RAG pipeline"}), 501

@app.route('/api/files', methods=['GET'])
@login_required
def get_files():
    """Get all files for current user"""
    username = session['username']
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT file_id, filename, original_filename, file_type, 
                  upload_date, num_rows, num_columns 
           FROM files WHERE username = ? 
           ORDER BY upload_date DESC""",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    
    files = []
    for row in rows:
        files.append({
            "file_id": row[0],
            "filename": row[1],
            "original_filename": row[2],
            "file_type": row[3],
            "upload_date": row[4],
            "num_rows": row[5],
            "num_columns": row[6]
        })
    
    return jsonify({
        "success": True,
        "files": files,
        "count": len(files)
    })

@app.route('/api/files/<int:file_id>', methods=['GET'])
@login_required
def get_file(file_id):
    """Get specific file details"""
    username = session['username']
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT file_id, filename, original_filename, file_type, 
                  upload_date, num_rows, num_columns, file_path 
           FROM files WHERE file_id = ? AND username = ?""",
        (file_id, username)
    )
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "File not found"}), 404
    
    return jsonify({
        "success": True,
        "file": {
            "file_id": row[0],
            "filename": row[1],
            "original_filename": row[2],
            "file_type": row[3],
            "upload_date": row[4],
            "num_rows": row[5],
            "num_columns": row[6],
            "file_path": row[7]
        }
    })

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """Delete a file"""
    username = session['username']
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get file path
    c.execute(
        "SELECT file_path FROM files WHERE file_id = ? AND username = ?",
        (file_id, username)
    )
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "File not found"}), 404
    
    file_path = row[0]
    
    # Delete from database
    c.execute("DELETE FROM files WHERE file_id = ?", (file_id,))
    c.execute("DELETE FROM chat_history WHERE file_id = ?", (file_id,))
    conn.commit()
    conn.close()
    
    # Delete physical file
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return jsonify({
        "success": True,
        "message": "File deleted successfully"
    })

# ============================================
# QUERY ENDPOINT (TODO: Will implement next)
# ============================================

@app.route('/api/ask', methods=['POST'])
@login_required
def ask_question():
    """Ask question about data"""
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({"error": "Question required"}), 400
    
    # TODO: Implement QueryProcessor integration
    return jsonify({
        "success": True,
        "question": question,
        "answer": "This will be replaced with RAG pipeline output",
        "context_used": [],
        "message": "RAG pipeline integration coming soon"
    })

@app.route('/api/ask/history', methods=['GET'])
@login_required
def get_chat_history():
    """Get chat history for current user"""
    username = session['username']
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT id, question, answer, timestamp, file_id 
           FROM chat_history WHERE username = ? 
           ORDER BY timestamp DESC 
           LIMIT 50""",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "timestamp": row[3],
            "file_id": row[4]
        })
    
    return jsonify({
        "success": True,
        "history": history,
        "count": len(history)
    })

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "status": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "status": 500
    }), 500

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("AskMyData REST API")
    print("=" * 60)
    print("Server running on: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("=" * 60)
    app.run(debug=True, port=5000)
