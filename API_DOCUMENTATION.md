# AskMyData API Documentation 📚

Welcome! This guide explains how to use the AskMyData REST API. 

---

## 🌐 What is an API?

An API (Application Programming Interface) is like a waiter at a restaurant:
- You (frontend) make a **request** (order food)
- The API delivers it to the kitchen (backend)
- The kitchen processes it (database, AI)
- The API brings back a **response** (your food)

---

## 🔗 Base URL

All API requests start with:
```
http://localhost:5001/api
```

**Example:** To login, you'd call: `http://localhost:5001/api/auth/login`

---

## 📖 Table of Contents

1. [Authentication](#authentication)
2. [File Management](#file-management)
3. [Asking Questions](#asking-questions)
4. [Error Handling](#error-handling)

---

## 🔐 Authentication

Before you can upload files or ask questions, users need to register and login.

### 1. Register a New User

**What it does:** Creates a new user account

**Endpoint:** `POST /api/auth/register`

**What to send:**
```json
{
  "fullname": "John Doe",
  "username": "john123",
  "email": "john@example.com",
  "password": "mySecurePassword"
}
```

**What you get back (Success):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "username": "john123",
    "fullname": "John Doe",
    "email": "john@example.com"
  }
}
```

**Status Code:** `201 Created`

**What can go wrong:**
- Username already exists → `409 Conflict`
- Missing required fields → `400 Bad Request`

**Frontend Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:5001/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Important! Saves session cookie
  body: JSON.stringify({
    fullname: "John Doe",
    username: "john123",
    email: "john@example.com",
    password: "mySecurePassword"
  })
});

const data = await response.json();
console.log(data); // { success: true, user: {...} }
```

---

### 2. Login

**What it does:** Logs in an existing user and creates a session

**Endpoint:** `POST /api/auth/login`

**What to send:**
```json
{
  "username": "john123",
  "password": "mySecurePassword"
}
```

**What you get back (Success):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "username": "john123",
    "fullname": "John Doe",
    "email": "john@example.com"
  }
}
```

**Status Code:** `200 OK`

**Important:** The server sends back a **session cookie** that keeps you logged in. Make sure to include `credentials: 'include'` in your fetch requests!

**What can go wrong:**
- Wrong username/password → `401 Unauthorized`
- Missing fields → `400 Bad Request`

---

### 3. Get Current User

**What it does:** Check who is currently logged in

**Endpoint:** `GET /api/auth/me`

**What to send:** Nothing! Just make the request.

**What you get back (Success):**
```json
{
  "authenticated": true,
  "user": {
    "username": "john123",
    "fullname": "John Doe",
    "email": "john@example.com"
  }
}
```

**Status Code:** `200 OK`

**What can go wrong:**
- Not logged in → `401 Unauthorized`

**Use Case:** Check if user is still logged in when page loads

---

### 4. Logout

**What it does:** Logs out the current user

**Endpoint:** `POST /api/auth/logout`

**What to send:** Nothing!

**What you get back (Success):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Status Code:** `200 OK`

---

## 📁 File Management

Once logged in, users can upload and manage their data files.

### 5. Upload a File

**What it does:** Uploads a file, parses it, generates embeddings, and stores it in the vector database

**Endpoint:** `POST /api/files/upload`

**What to send:** A file using `multipart/form-data`

**Supported File Types:**
- CSV (`.csv`)
- JSON (`.json`)
- PDF (`.pdf`)
- iCal/Calendar (`.ics`)

**What you get back (Success):**
```json
{
  "success": true,
  "message": "File uploaded and processed successfully",
  "file": {
    "file_id": 1,
    "filename": "data_20251222_123456.csv",
    "original_filename": "data.csv",
    "file_type": "csv",
    "num_rows": 100,
    "num_columns": 5,
    "num_chunks": 25,
    "upload_date": "2025-12-22 12:34:56"
  }
}
```

**Status Code:** `201 Created`

**Frontend Example (JavaScript):**
```javascript
const fileInput = document.querySelector('input[type="file"]');
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:5001/api/files/upload', {
  method: 'POST',
  credentials: 'include',
  body: formData // Don't set Content-Type header - browser does it automatically
});

const data = await response.json();
console.log(`Uploaded! File ID: ${data.file.file_id}`);
```

**What happens behind the scenes:**
1. File is saved to server
2. File is parsed into structured data
3. Data is broken into chunks
4. Each chunk is converted to an embedding (vector)
5. Embeddings are stored in ChromaDB
6. File metadata is saved to database

**What can go wrong:**
- File type not allowed → `400 Bad Request`
- File is empty → `400 Bad Request`
- Processing error → `500 Internal Server Error`

---

### 6. List All Files

**What it does:** Gets a list of all files uploaded by the current user

**Endpoint:** `GET /api/files`

**What to send:** Nothing!

**What you get back (Success):**
```json
{
  "success": true,
  "files": [
    {
      "file_id": 1,
      "filename": "data_20251222_123456.csv",
      "original_filename": "data.csv",
      "file_type": "csv",
      "upload_date": "2025-12-22 12:34:56",
      "num_rows": 100,
      "num_columns": 5
    },
    {
      "file_id": 2,
      "filename": "report_20251222_130000.pdf",
      "original_filename": "report.pdf",
      "file_type": "pdf",
      "upload_date": "2025-12-22 13:00:00",
      "num_rows": 50,
      "num_columns": 3
    }
  ],
  "count": 2
}
```

**Status Code:** `200 OK`

**Use Case:** Show a list of uploaded files in the UI

---

### 7. Get File Details

**What it does:** Gets detailed information about a specific file

**Endpoint:** `GET /api/files/:id`

**Example:** `GET /api/files/1`

**What to send:** Nothing! Just the file ID in the URL.

**What you get back (Success):**
```json
{
  "success": true,
  "file": {
    "file_id": 1,
    "filename": "data_20251222_123456.csv",
    "original_filename": "data.csv",
    "file_type": "csv",
    "upload_date": "2025-12-22 12:34:56",
    "num_rows": 100,
    "num_columns": 5,
    "file_path": "/uploads/data_20251222_123456.csv"
  }
}
```

**Status Code:** `200 OK`

**What can go wrong:**
- File doesn't exist or doesn't belong to user → `404 Not Found`

---

### 8. Delete a File

**What it does:** Deletes a file and all its associated data

**Endpoint:** `DELETE /api/files/:id`

**Example:** `DELETE /api/files/1`

**What to send:** Nothing! Just the file ID in the URL.

**What you get back (Success):**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

**Status Code:** `200 OK`

**What gets deleted:**
- File from disk
- File metadata from database
- Chat history related to this file
- (Note: Embeddings in ChromaDB are shared across all user files)

**What can go wrong:**
- File doesn't exist → `404 Not Found`

---

## 💬 Asking Questions

The main feature! Ask natural language questions about your uploaded data.

### 9. Ask a Question

**What it does:** Uses AI (RAG pipeline) to answer questions about your uploaded data

**Endpoint:** `POST /api/ask`

**What to send:**
```json
{
  "question": "What is the average age in the dataset?",
  "file_id": 1  // OPTIONAL - if not provided, searches all your files
}
```

**What you get back (Success):**
```json
{
  "success": true,
  "chat_id": 42,
  "question": "What is the average age in the dataset?",
  "answer": "Based on the data, the average age is 32.5 years. This was calculated from 100 entries in the dataset.",
  "num_chunks_used": 5,
  "sources": ["data.csv"],
  "timestamp": "2025-12-22 14:30:00"
}
```

**Status Code:** `200 OK`

**What happens behind the scenes:**
1. Your question is converted to an embedding (vector)
2. Similar chunks are found in the vector database
3. Top 5 most relevant chunks are retrieved
4. Chunks are sent to the LLM (llama3.2) as context
5. LLM generates a natural language answer
6. Answer is saved to chat history

**Example Questions:**
- "What is the average age?"
- "How many rows are in the dataset?"
- "Show me entries from New York"
- "What columns are available?"
- "Summarize the data"

**What can go wrong:**
- No files uploaded → `400 Bad Request`
- Question is empty → `400 Bad Request`
- Processing error → `500 Internal Server Error`

**Frontend Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:5001/api/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    question: "What is the average age?"
  })
});

const data = await response.json();
console.log(`Q: ${data.question}`);
console.log(`A: ${data.answer}`);
console.log(`Used ${data.num_chunks_used} chunks from: ${data.sources.join(', ')}`);
```

---

### 10. Get Chat History

**What it does:** Retrieves previous questions and answers

**Endpoint:** `GET /api/ask/history`

**What to send:** Nothing!

**What you get back (Success):**
```json
{
  "success": true,
  "history": [
    {
      "id": 42,
      "question": "What is the average age?",
      "answer": "The average age is 32.5 years.",
      "timestamp": "2025-12-22 14:30:00",
      "file_id": 1
    },
    {
      "id": 41,
      "question": "How many rows?",
      "answer": "There are 100 rows in the dataset.",
      "timestamp": "2025-12-22 14:25:00",
      "file_id": 1
    }
  ],
  "count": 2
}
```

**Status Code:** `200 OK`

**Note:** Returns last 50 messages, most recent first

**Use Case:** Show conversation history in the UI

---

## 🏥 Health Check

### 11. Health Check

**What it does:** Checks if the server is running

**Endpoint:** `GET /api/health`

**What to send:** Nothing!

**What you get back (Success):**
```json
{
  "status": "healthy",
  "message": "AskMyData API is running",
  "timestamp": "2025-12-22 15:00:00"
}
```

**Status Code:** `200 OK`

**Use Case:** Frontend can ping this to check if backend is alive

---

## ❌ Error Handling

All errors follow this format:

```json
{
  "error": "Brief error message",
  "details": "Detailed explanation (optional)"
}
```

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| `200` | OK | Request succeeded |
| `201` | Created | File uploaded, user registered |
| `400` | Bad Request | Missing required fields |
| `401` | Unauthorized | Not logged in |
| `404` | Not Found | File doesn't exist |
| `409` | Conflict | Username already taken |
| `500` | Server Error | Something went wrong on the server |

### Example Error Response

```json
{
  "error": "Authentication required",
  "authenticated": false
}
```

---

## 🔒 Important Notes

### 1. **Authentication Required**

Most endpoints require you to be logged in. Always include `credentials: 'include'` in your fetch requests to send the session cookie:

```javascript
fetch(url, {
  credentials: 'include' // This sends cookies!
})
```

### 2. **CORS (Cross-Origin Requests)**

The backend allows requests from:
- `http://localhost:3000` (Next.js dev server)
- `http://localhost:5173` (Vite dev server)

If your frontend runs on a different port, you'll need to update the CORS settings in `app.py`.

### 3. **File Size Limit**

Maximum file size: **16MB**

### 4. **Rate Limiting**

To prevent abuse, you might want to add rate limiting in production (not implemented yet).

---

## 🧪 Testing the API

### Using cURL (Command Line)

**Register a user:**
```bash
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"fullname":"Test User","username":"test","email":"test@example.com","password":"test123"}'
```

**Login:**
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"test","password":"test123"}'
```

**Upload a file:**
```bash
curl -X POST http://localhost:5001/api/files/upload \
  -b cookies.txt \
  -F "file=@/path/to/your/file.csv"
```

**Ask a question:**
```bash
curl -X POST http://localhost:5001/api/ask \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"question":"What is the average age?"}'
```

### Using Python Test Scripts

We've created test scripts for you:

```bash
# Test authentication
python3 test_api.py

# Test file upload
python3 test_upload.py

# Test asking questions
python3 test_ask.py
```

---

## 🚀 Quick Start Guide

**1. Start the server:**
```bash
cd backend
python3 app.py
```

**2. Register a user:**
```javascript
await fetch('http://localhost:5001/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    fullname: "Your Name",
    username: "youruser",
    email: "you@example.com",
    password: "yourpassword"
  })
});
```

**3. Upload a file:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

await fetch('http://localhost:5001/api/files/upload', {
  method: 'POST',
  credentials: 'include',
  body: formData
});
```

**4. Ask a question:**
```javascript
const response = await fetch('http://localhost:5001/api/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    question: "What is the average age?"
  })
});

const data = await response.json();
console.log(data.answer);
```

---

If something isn't working:

1. **Check if the server is running:**
   - Visit `http://localhost:5001/api/health`
   - Should return `{"status": "healthy"}`

2. **Check if you're logged in:**
   - Visit `http://localhost:5001/api/auth/me`
   - Should return your user info, not a 401 error

3. **Check browser console** for error messages

4. **Check server logs** in the terminal where `python3 app.py` is running

---



**Remember:**
- Always include `credentials: 'include'` for authenticated requests
- Handle errors gracefully (check response.ok before processing)
- Show loading states while waiting for RAG pipeline responses
- The `/api/ask` endpoint can take 5-30 seconds depending on data size

---

**Last Updated:** December 22, 2025
**API Version:** 1.0
**Server:** Flask 3.x
**Port:** 5001
