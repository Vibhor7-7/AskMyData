"""
AskMyData REST API
RESTful backend for data analysis with RAG pipeline
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import sqlite3
import os
from datetime import datetime
import traceback

# Import RAG pipeline components
from parsers.file_parser import parse_file
from rag.chunking_module import dataframe_to_chunks
from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStore
from rag.query_processor import QueryProcessor

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'AskMyData'  # Change this in production!

# Configure CORS - Allow all origins for development
CORS(app, 
     supports_credentials=True,
     origins="*",
     allow_headers="*",
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), 'rag', 'chroma_db')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'json', 'pdf', 'ics'}

# RAG components - initialized lazily
embedding_generator = None
vector_store = None

def get_embedding_generator():
    """Lazy initialization of embedding generator"""
    global embedding_generator
    if embedding_generator is None:
        print("Initializing embedding generator...")
        embedding_generator = EmbeddingGenerator()
    return embedding_generator

def get_vector_store():
    """Lazy initialization of vector store"""
    global vector_store
    if vector_store is None:
        print("Initializing vector store...")
        vector_store = VectorStore(persist_directory=CHROMA_DB_PATH)
    return vector_store

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
# ROOT & HEALTH CHECK
# ============================================

@app.route('/', methods=['GET'])
def home():
    """Root endpoint"""
    return jsonify({
        "service": "AskMyData REST API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "auth": {
                "register": "/api/auth/register (POST)",
                "login": "/api/auth/login (POST)",
                "logout": "/api/auth/logout (POST)",
                "me": "/api/auth/me (GET)"
            },
            "files": {
                "upload": "/api/files/upload (POST)",
                "list": "/api/files (GET)",
                "details": "/api/files/<id> (GET)",
                "delete": "/api/files/<id> (DELETE)"
            },
            "query": {
                "ask": "/api/ask (POST)"
            }
        }
    })

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



@app.route('/api/files/upload', methods=['POST'])
@login_required
def upload_file():
    """
    Upload and process file with RAG pipeline
    
    Request: multipart/form-data
    - file: The file to upload
    
    Response: 201 Created
    {
        "success": true,
        "message": "File uploaded and processed successfully",
        "file": {
            "file_id": 1,
            "filename": "data_123456.csv",
            "original_filename": "data.csv",
            "file_type": "csv",
            "num_rows": 100,
            "num_columns": 5,
            "num_chunks": 10,
            "upload_date": "2025-12-22 10:30:00"
        }
    }
    """
    username = session['username']
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({
            "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400
    
    try:
        # Secure the filename and add timestamp
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_parts = original_filename.rsplit('.', 1)
        filename = f"{filename_parts[0]}_{timestamp}.{filename_parts[1]}"
        
        # Save file to uploads folder
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Determine file type
        file_type = filename_parts[1].lower()
        
        # Step 1: Parse the file
        print(f"Parsing file: {filename}")
        df = parse_file(file_path)
        
        if df is None or df.empty:
            os.remove(file_path)  # Clean up
            return jsonify({"error": "Failed to parse file or file is empty"}), 400
        
        num_rows = len(df)
        num_columns = len(df.columns)
        
        print(f"Parsed {num_rows} rows and {num_columns} columns")
        
        # Step 2: Chunk the data
        print("Chunking data...")
        chunks = dataframe_to_chunks(
            df,
            chunk_strategy="row",
            max_tokens=500
        )
        
        if not chunks:
            os.remove(file_path)  # Clean up
            return jsonify({"error": "Failed to create chunks from file"}), 400
        
        print(f"Created {len(chunks)} chunks")
        
        # Step 3: Generate embeddings (adds 'embedding' to each chunk)
        print("Generating embeddings...")
        emb_gen = get_embedding_generator()
        chunks_with_embeddings = emb_gen.embed_chunks(chunks)
        
        if not chunks_with_embeddings:
            os.remove(file_path)  # Clean up
            return jsonify({"error": "Failed to generate embeddings"}), 500
        
        print(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
        
        # Step 4: Store in vector database
        # Create user-specific collection name
        collection_name = f"user_{username}_files"
        
        print(f"Storing in vector database (collection: {collection_name})...")
        
        # Create or get collection
        vs = get_vector_store()
        vs.create_collection(collection_name)
        
        # Add filename metadata to chunks
        for chunk in chunks_with_embeddings:
            if 'metadata' not in chunk:
                chunk['metadata'] = {}
            chunk['metadata']['filename'] = original_filename
            chunk['metadata']['file_id'] = filename
        
        # add_chunks expects chunks with 'text', 'embedding', and 'metadata' fields
        vs.add_chunks(chunks_with_embeddings)
        
        print("Successfully stored in vector database")
        
        # Step 5: Save file metadata to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute(
            """INSERT INTO files 
               (username, filename, original_filename, file_type, file_path, 
                upload_date, num_rows, num_columns, collection_name) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (username, filename, original_filename, file_type, file_path,
             upload_date, num_rows, num_columns, collection_name)
        )
        
        file_id = c.lastrowid
        conn.commit()
        conn.close()
        
        print(f"File metadata saved to database (ID: {file_id})")
        
        # Return success response
        return jsonify({
            "success": True,
            "message": "File uploaded and processed successfully",
            "file": {
                "file_id": file_id,
                "filename": filename,
                "original_filename": original_filename,
                "file_type": file_type,
                "num_rows": num_rows,
                "num_columns": num_columns,
                "num_chunks": len(chunks),
                "upload_date": upload_date
            }
        }), 201
        
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        print(traceback.format_exc())
        
        # Clean up file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            "error": "Failed to process file",
            "details": str(e)
        }), 500

@app.route('/api/files', methods=['GET'])
@login_required
def get_files():
    """Get all files for current user"""
    username = session['username']
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT file_id, filename, original_filename, file_type, 
                  upload_date, num_rows, num_columns, file_path, collection_name 
           FROM files WHERE username = ? 
           ORDER BY upload_date DESC""",
        (username,)
    )
    rows = c.fetchall()
    conn.close()
    
    files = []
    for row in rows:
        # Get file size from file_path
        file_size = 0
        try:
            if row[7] and os.path.exists(row[7]):
                file_size = os.path.getsize(row[7])
        except:
            pass
        
        # Estimate num_chunks (if collection exists, try to get count)
        num_chunks = 0
        try:
            vector_store = get_vector_store()
            collection = vector_store.client.get_collection(row[8])  # collection_name
            num_chunks = collection.count()
        except:
            # If can't get from ChromaDB, estimate from rows
            num_chunks = row[5]  # Approximate: one chunk per row
        
        files.append({
            "file_id": row[0],
            "filename": row[1],
            "original_filename": row[2],
            "file_type": row[3],
            "upload_date": row[4],
            "num_rows": row[5],
            "num_columns": row[6],
            "file_size": file_size,
            "collection_name": row[8],
            "num_chunks": num_chunks
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

# QUERY ENDPOINT


@app.route('/api/ask', methods=['POST'])
@login_required
def ask_question():
    """
    Ask a question about uploaded data using RAG pipeline
    
    Request Body:
    {
        "question": "What is the average age?",
        "file_id": 1  // optional - if not provided, searches all user's files
    }
    
    Response: 200 OK
    {
        "success": true,
        "question": "What is the average age?",
        "answer": "The average age is 28.5 years based on the data.",
        "num_chunks_used": 5,
        "sources": ["data.csv"]
    }
    """
    username = session['username']
    data = request.get_json()
    
    question = data.get('question')
    file_id = data.get('file_id')  # Optional - specific file
    
    if not question:
        return jsonify({"error": "Question required"}), 400
    
    try:
        # Determine collection name (user-specific)
        collection_name = f"user_{username}_files"
        
        # Check if user has any files uploaded
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM files WHERE username = ?",
            (username,)
        )
        file_count = c.fetchone()[0]
        
        if file_count == 0:
            conn.close()
            return jsonify({
                "error": "No files uploaded. Please upload a file first.",
                "suggestion": "Use POST /api/files/upload to upload data files"
            }), 400
        
        # Get file info for filtering and response
        filename_filter = None
        if file_id:
            c.execute(
                "SELECT original_filename FROM files WHERE file_id = ? AND username = ?",
                (file_id, username)
            )
            file_row = c.fetchone()
            if not file_row:
                conn.close()
                return jsonify({"error": "File not found"}), 404
            filename_filter = file_row[0]
            sources = [file_row[0]]
        else:
            # No file_id specified - use most recent file
            c.execute(
                "SELECT original_filename FROM files WHERE username = ? ORDER BY upload_date DESC LIMIT 1",
                (username,)
            )
            file_row = c.fetchone()
            if file_row:
                filename_filter = file_row[0]
                sources = [file_row[0]]
            else:
                # Fallback: get all files
                c.execute(
                    "SELECT DISTINCT original_filename FROM files WHERE username = ?",
                    (username,)
                )
                sources = [row[0] for row in c.fetchall()]
        
        conn.close()
        
        print(f"Processing question: {question}")
        print(f"Collection: {collection_name}")
        if filename_filter:
            print(f"Filtering by file: {filename_filter}")
        
        # Initialize QueryProcessor with collection name and persist directory
        query_processor = QueryProcessor(
            collection_name=collection_name,
            embedding_model='nomic-embed-text',
            llm_model='llama3.2',
            chroma_persist_dir=CHROMA_DB_PATH
        )
        
        # Process the query with filename filter
        print("Running RAG pipeline...")
        result = query_processor.process_query(question, filename_filter=filename_filter)
        
        if not result or 'answer' not in result:
            return jsonify({
                "error": "Failed to generate answer",
                "details": "Query processor returned empty result"
            }), 500
        
        answer = result['answer']
        context_used = result.get('context', [])
        
        print(f"Answer generated: {answer[:100]}...")
        print(f"Used {len(context_used)} context chunks")
        
        # Save to chat history
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute(
            """INSERT INTO chat_history (username, file_id, question, answer, timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (username, file_id, question, answer, timestamp)
        )
        
        chat_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "chat_id": chat_id,
            "question": question,
            "answer": answer,
            "num_chunks_used": len(context_used),
            "sources": sources,
            "timestamp": timestamp
        })
        
    except Exception as e:
        print(f"Error processing question: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            "error": "Failed to process question",
            "details": str(e)
        }), 500

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

# ERROR HANDLERS


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


# RUN SERVER


if __name__ == '__main__':
    PORT = 5001  # Changed from 5000 due to macOS AirPlay using port 5000
    print("=" * 60)
    print("AskMyData REST API")
    print("=" * 60)
    print(f"Server running on: http://localhost:{PORT}")
    print(f"Health check: http://localhost:{PORT}/api/health")
    print("=" * 60)
    app.run(debug=True, port=PORT, host='127.0.0.1')
