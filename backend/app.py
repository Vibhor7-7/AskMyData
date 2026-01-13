"""
AskMyData REST API - FastAPI Upgrade 
Backend for the RAG Pipeline 
"""

from fastapi import FastAPI,  HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from typing import Optional, Dict, List, Annotated
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

# Password hashing - Passlib is FastAPI's standard
from passlib.context import CryptContext

# JWT authentication
from jose import JWTError, jwt
from fastapi import Cookie
from dotenv import load_dotenv 

# File and system utilities
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime, timedelta
import traceback
from contextlib import asynccontextmanager


# RAG Pipeline imports 
from parsers.file_parser import parse_file
from rag.chunking_module import dataframe_to_chunks
from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStore
from rag.query_processor import QueryProcessor

# ============================================
# LIFESPAN EVENTS
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager - handles startup and shutdown events
    """
    # Startup
    init_db()
    print("=" * 60)
    print("AskMyData REST API - FastAPI")
    print("=" * 60)
    print("Swagger UI: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("=" * 60)
    yield
    # Shutdown (cleanup if needed)
    print("Shutting down...")

# ============================================
# APP INITIALIZATION
# ============================================

app = FastAPI(
    title = 'AskMyData REST API', 
    description = "Data analysis with RAG", 
    version = '1.5.0',
    docs_url = '/docs', 
    redoc_url= '/redoc',
    lifespan=lifespan
)

#JWT Configuration (Flask has secert key and sessions)
SECRET_KEY = "Vibhors_Secret_key_until_prod"   
ALGORITHM =  "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24 # user has to revalidate after 24 hours 

# pasword hashing 
pwd_context = CryptContext(schemes=['argon2'], deprecated = "auto")


# CORS Configuration 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # Backend itself
    ],
    allow_credentials=True,    # Allow cookies
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)

# Database and file paths
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), 'rag', 'chroma_db')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# Allowed file extensions 
ALLOWED_EXTENSIONS = {'csv', 'json', 'pdf', 'ics'}

# RAG components - initialized 
embedding_generator = None
vector_store = None

class UserRegister(BaseModel):
    """User registration request"""
    fullname: str
    username: str 
    email: EmailStr # Automatically validates email format 
    password: str 

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password length"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        if len(v) > 128:
            raise ValueError('Password is too long (max 128 characters)')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fullname": "John Doe",
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepass123"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for login request"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Schema for user data response"""
    username: str
    fullname: str
    email: str

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str

class QuestionRequest(BaseModel):
    """Schema for asking questions"""
    question: str
    file_id: Optional[int] = None  # Optional field with default None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "What is the average value?",
                "file_id": 1
            }
        }
    )

class FileResponse(BaseModel):
    """Schema for file information"""
    file_id: int
    filename: str
    original_filename: str
    file_type: str
    num_rows: int
    num_columns: int
    num_chunks: int
    upload_date: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash
    Replaces: check_password_hash(hashed, plain)
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        # Hash format not recognized (likely old hash from previous version)
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password using argon2
    Replaces: generate_password_hash(password)
    """
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """
    Create a JWT access token
    
    This replaces Flask's session management:
    - Flask: session['username'] = 'john'
    - FastAPI: Create JWT token with username inside
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    Verify JWT token and extract username
    
    Returns username if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # 'sub' is standard JWT claim for subject
        return username
    except JWTError:
        return None

# Authentication dependency 
async def get_current_user(
    access_token: Annotated[Optional[str], Cookie()] = None
) -> str:
    """
    Dependency function that extracts and validates the user from JWT cookie
    
    REPLACES Flask's @login_required decorator
    
    Flask way:
        @app.route('/protected')
        @login_required
        def protected():
            username = session['username']
    
    FastAPI way:
        @app.get('/protected')
        async def protected(username: str = Depends(get_current_user)):
            # username is automatically extracted
    """
    # Check if token exists
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    # Verify token and get username
    username = verify_token(access_token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    return username

# RAG helper functions 

def get_embedding_generator():
    """Lazy initialization of embedding generator"""
    global embedding_generator
    if embedding_generator is None:
        print("Initializing embedding generator...")
        embedding_generator = EmbeddingGenerator()
    return embedding_generator

def get_vector_store():
    """Lazy initialization of vector store """
    global vector_store
    if vector_store is None:
        print("Initializing vector store...")
        vector_store = VectorStore(persist_directory=CHROMA_DB_PATH)
    return vector_store

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database setup 

def init_db():
    """ Initialize SQLite db tables"""
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

# ============================================
# ROOT & HEALTH CHECK ENDPOINTS
# ============================================

@app.get("/", tags=["root"])
async def home():
    """Root endpoint - API documentation"""
    return {
        "service": "AskMyData REST API",
        "version": "1.5.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
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
                "details": "/api/files/{id} (GET)",
                "delete": "/api/files/{id} (DELETE)"
            },
            "query": {
                "ask": "/api/ask (POST)",
                "history": "/api/ask/history (GET)"
            }
        }
    }

@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "AskMyData API is running",
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/api/auth/register", response_model=Dict, status_code=status.HTTP_201_CREATED, tags=["auth"])
async def register(user: UserRegister):
    """Register new user"""
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Insert into database
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)",
            (user.fullname, user.username, user.email, hashed_password)
        )
        conn.commit()
        conn.close()
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.username})
        
        # Create response with token as cookie
        response = JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "message": "User registered successfully",
                "user": {
                    "username": user.username,
                    "fullname": user.fullname,
                    "email": user.email
                }
            }
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        
        return response
        
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

@app.post("/api/auth/login", response_model=Dict, tags=["auth"])
async def login(user: UserLogin):
    """Login user"""
    # Query database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT password, fullname, email FROM users WHERE username = ?",
        (user.username,)
    )
    row = c.fetchone()
    conn.close()
    
    # Check credentials
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not verify_password(user.password, row[0]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password. If you registered before the migration, please register again."
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.username})
    
    # Create response with token as cookie
    response = JSONResponse(
        content={
            "success": True,
            "message": "Logged in successfully",
            "user": {
                "username": user.username,
                "fullname": row[1],
                "email": row[2]
            }
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return response

@app.post("/api/auth/logout", tags=["auth"])
async def logout(username: str = Depends(get_current_user)):
    """Logout current user"""
    response = JSONResponse(
        content={
            "success": True,
            "message": "Logged out successfully"
        }
    )
    response.delete_cookie(key="access_token")
    return response

@app.get("/api/auth/me", tags=["auth"])
async def get_current_user_info(username: str = Depends(get_current_user)):
    """Get current logged-in user information"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT fullname, email FROM users WHERE username = ?",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "authenticated": True,
            "user": {
                "username": username,
                "fullname": row[0],
                "email": row[1]
            }
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )

# ============================================
# FILE MANAGEMENT ENDPOINTS
# ============================================

@app.post("/api/files/upload", status_code=status.HTTP_201_CREATED, tags=["files"])
async def upload_file(
    file: UploadFile = File(...),
    username: str = Depends(get_current_user)
):
    """Upload and process file with RAG pipeline"""
    # Check if file is selected
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file selected"
        )
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # Secure the filename and add timestamp
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_parts = original_filename.rsplit('.', 1)
        filename = f"{filename_parts[0]}_{timestamp}.{filename_parts[1]}"
        
        # Save file to uploads folder
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # FastAPI's UploadFile.file is async, read content
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Determine file type
        file_type = filename_parts[1].lower()
        
        # Step 1: Parse the file
        print(f"Parsing file: {filename}")
        df = parse_file(file_path)
        
        if df is None or df.empty:
            os.remove(file_path)  # Clean up
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse file or file is empty"
            )
        
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
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create chunks from file"
            )
        
        print(f"Created {len(chunks)} chunks")
        
        # Step 3: Generate embeddings
        print("Generating embeddings...")
        emb_gen = get_embedding_generator()
        chunks_with_embeddings = emb_gen.embed_chunks(chunks)
        
        if not chunks_with_embeddings:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate embeddings"
            )
        
        print(f"Generated embeddings for {len(chunks_with_embeddings)} chunks")
        
        # Step 4: Store in vector database
        collection_name = f"user_{username}_files"
        
        print(f"Storing in vector database (collection: {collection_name})...")
        
        vs = get_vector_store()
        vs.create_collection(collection_name)
        
        # Add filename metadata to chunks
        for chunk in chunks_with_embeddings:
            if 'metadata' not in chunk:
                chunk['metadata'] = {}
            chunk['metadata']['filename'] = original_filename
            chunk['metadata']['file_id'] = filename
        
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
        
        return {
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
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        print(traceback.format_exc())
        
        # Clean up file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )

@app.get("/api/files", tags=["files"])
async def get_files(username: str = Depends(get_current_user)):
    """Get all files for current user"""
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
        # Get file size
        file_size = 0
        try:
            if row[7] and os.path.exists(row[7]):
                file_size = os.path.getsize(row[7])
        except:
            pass
        
        # Estimate num_chunks
        num_chunks = 0
        try:
            vector_store = get_vector_store()
            collection = vector_store.client.get_collection(row[8])
            num_chunks = collection.count()
        except:
            num_chunks = row[5]
        
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
    
    return {
        "success": True,
        "files": files,
        "count": len(files)
    }

@app.get("/api/files/{file_id}", tags=["files"])
async def get_file(file_id: int, username: str = Depends(get_current_user)):
    """Get specific file details"""
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {
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
    }

@app.delete("/api/files/{file_id}", tags=["files"])
async def delete_file(file_id: int, username: str = Depends(get_current_user)):
    """Delete a file"""
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file_path = row[0]
    
    # Delete from database
    c.execute("DELETE FROM files WHERE file_id = ?", (file_id,))
    c.execute("DELETE FROM chat_history WHERE file_id = ?", (file_id,))
    conn.commit()
    conn.close()
    
    # Delete physical file
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return {
        "success": True,
        "message": "File deleted successfully"
    }

# ============================================
# QUERY ENDPOINTS
# ============================================

@app.post("/api/ask", tags=["query"])
async def ask_question(
    question_data: QuestionRequest,
    username: str = Depends(get_current_user)
):
    """Ask a question about uploaded data using RAG pipeline"""
    question = question_data.question
    file_id = question_data.file_id
    
    try:
        # Determine collection name
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files uploaded. Please upload a file first."
            )
        
        # Get file info for filtering
        filename_filter = None
        if file_id:
            c.execute(
                "SELECT original_filename FROM files WHERE file_id = ? AND username = ?",
                (file_id, username)
            )
            file_row = c.fetchone()
            if not file_row:
                conn.close()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            filename_filter = file_row[0]
            sources = [file_row[0]]
        else:
            # Use most recent file
            c.execute(
                "SELECT original_filename FROM files WHERE username = ? ORDER BY upload_date DESC LIMIT 1",
                (username,)
            )
            file_row = c.fetchone()
            if file_row:
                filename_filter = file_row[0]
                sources = [file_row[0]]
            else:
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
        
        # Initialize QueryProcessor
        query_processor = QueryProcessor(
            collection_name=collection_name,
            embedding_model='nomic-embed-text',
            llm_model='llama3.2',
            chroma_persist_dir=CHROMA_DB_PATH
        )
        
        # Process the query
        print("Running RAG pipeline...")
        result = query_processor.process_query(question, filename_filter=filename_filter)
        
        if not result or 'answer' not in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate answer"
            )
        
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
        
        return {
            "success": True,
            "chat_id": chat_id,
            "question": question,
            "answer": answer,
            "num_chunks_used": len(context_used),
            "sources": sources,
            "timestamp": timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing question: {str(e)}")
        print(traceback.format_exc())
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process question: {str(e)}"
        )

@app.get("/api/ask/history", tags=["query"])
async def get_chat_history(username: str = Depends(get_current_user)):
    """Get chat history for current user"""
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
    
    return {
        "success": True,
        "history": history,
        "count": len(history)
    }

# ============================================
# RUN SERVER (for development)
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

