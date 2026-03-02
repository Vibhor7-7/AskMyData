# AskMyData — Product Requirements Document

> **Status:** Current Implementation Reference
> **Last Updated:** March 2026
> **Branch:** main

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Architecture Overview](#2-architecture-overview)
3. [Backend — FastAPI Application](#3-backend--fastapi-application)
4. [RAG Pipeline](#4-rag-pipeline)
5. [File Parsing System](#5-file-parsing-system)
6. [Frontend — Next.js Application](#6-frontend--nextjs-application)
7. [Authentication & Security](#7-authentication--security)
8. [Database Schema](#8-database-schema)
9. [External Dependencies](#9-external-dependencies)
10. [Data Flow](#10-data-flow)
11. [Key Design Decisions](#11-key-design-decisions)
12. [Areas for Improvement](#12-areas-for-improvement)
13. [Development Setup](#13-development-setup)

---

## 1. Product Overview

**AskMyData** is a privacy-first, local RAG (Retrieval-Augmented Generation) platform that lets users upload structured data files and query them in natural language. It runs entirely on the user's machine — no cloud API calls, no data leaving the device.

### Core Value Proposition

- Ask natural language questions about CSV, JSON, PDF, and iCal files
- All inference runs locally via Ollama (no external LLM API keys required)
- Multi-user support with isolated data and chat history per user
- Simple upload-and-chat workflow accessible to non-technical users

### Supported File Formats

| Format | Parser | Use Case |
|--------|--------|----------|
| CSV | pandas | Tabular data, spreadsheets |
| JSON | pandas + json.load | API responses, structured records |
| PDF | pdfplumber | Reports, documents, scanned tables |
| iCal (.ics) | icalendar | Calendar exports, event data |

---

## 2. Architecture Overview

```
┌────────────────────────────────────────────────────┐
│              Browser (Next.js 16, React 19)         │
│     Landing / Login / Register / Dashboard / Chat  │
└───────────────────────┬────────────────────────────┘
                        │  HTTP REST  (port 3000 → 8000)
                        │  Cookie-based JWT auth
┌───────────────────────▼────────────────────────────┐
│              FastAPI Backend  (port 8000)           │
│  /api/auth   /api/files   /api/ask   /api/health   │
└──────┬──────────────┬────────────────┬─────────────┘
       │              │                │
  SQLite DB     File Parsers       RAG Pipeline
  users.db    CSV/JSON/PDF/iCal   (embed → store → retrieve → generate)
                                       │
                          ┌────────────┼────────────┐
                     ChromaDB       nomic-      llama3.2
                   (vector store)  embed-text  (via Ollama)
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript 5, Tailwind CSS v4 |
| Backend | FastAPI, Python 3.10+, Uvicorn |
| Auth | JWT (python-jose), argon2 password hashing (passlib) |
| Database | SQLite (`users.db`) |
| Vector Store | ChromaDB (persistent) |
| Embeddings | nomic-embed-text via Ollama (768-dim) |
| LLM | llama3.2 3B via Ollama |
| Parsing | pdfplumber, pandas, icalendar, tiktoken |
| UI Primitives | Radix UI, Lucide Icons, Framer Motion, Sonner |

---

## 3. Backend — FastAPI Application

**Entry Point:** `backend/app.py`
**Port:** 8000
**Docs:** `http://localhost:8000/docs` (Swagger), `/redoc`

### 3.1 API Endpoints

#### Authentication (`/api/auth`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login, receive JWT cookie | No |
| POST | `/api/auth/logout` | Clear session cookie | No |
| GET | `/api/auth/me` | Get current user info | Yes |

**Registration payload:**
```json
{ "fullname": "Alice", "username": "alice", "email": "alice@example.com", "password": "secret" }
```

**Login payload:**
```json
{ "username": "alice", "password": "secret" }
```

#### File Management (`/api/files`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/api/files/upload` | Upload and process file | Yes |
| GET | `/api/files` | List all user files | Yes |
| GET | `/api/files/{id}` | Get specific file details | Yes |
| DELETE | `/api/files/{id}` | Delete file and its data | Yes |

**Upload response:**
```json
{
  "file_id": 1,
  "original_filename": "sales.csv",
  "file_type": "csv",
  "num_rows": 500,
  "num_columns": 8,
  "num_chunks": 500
}
```

#### Query (`/api/ask`)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | `/api/ask` | Ask a question about uploaded data | Yes |
| GET | `/api/ask/history` | Get chat history (last 50) | Yes |

**Ask payload:**
```json
{ "question": "What is the average revenue?", "file_id": 1 }
```

**Ask response:**
```json
{
  "question": "What is the average revenue?",
  "answer": "The average revenue is $42,350 based on 500 records.",
  "success": true,
  "num_chunks_used": 5
}
```

#### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service health check |

### 3.2 Authentication Flow

```
Registration:
  1. Receive UserRegister model (fullname, username, email, password)
  2. Validate: password 6–128 chars
  3. Hash password with argon2
  4. INSERT into users table
  5. Create JWT (sub=username, exp=+24h, alg=HS256)
  6. Set httponly cookie → redirect to dashboard

Login:
  1. Receive UserLogin (username, password)
  2. Fetch user from DB
  3. argon2.verify(password, hash)
  4. Create JWT → set httponly cookie
```

**Dependency injection:** All protected routes use `get_current_user()` which extracts and validates the JWT from the cookie.

### 3.3 File Upload Pipeline

```
POST /api/files/upload
  ↓
1. Validate MIME / extension (csv, json, pdf, ics)
2. Save to disk: backend/uploads/{name}_{timestamp}.{ext}
3. Route to correct parser → standardized DataFrame
4. dataframe_to_chunks() → list of text chunks + metadata
5. EmbeddingGenerator.embed_chunks() → attach 768-dim vectors
6. VectorStore.add_chunks() → persist to ChromaDB
7. INSERT file metadata into files table
8. Return file stats (rows, columns, chunks)
```

---

## 4. RAG Pipeline

All RAG code lives in `backend/rag/`.

### 4.1 Chunking (`chunking_module.py`, `improved_chunking.py`)

**Default strategy:** Row-based — each DataFrame row becomes one text chunk.

**Row format:**
```
name: Alice, age: 25, city: New York, role: Engineer
```

**Token budgeting:** tiktoken counts tokens per chunk; chunks exceeding `max_tokens=512` are flagged.

**Metadata per chunk:**
```python
{
  "source_file": "sales.csv",
  "content_type": "csv",
  "row_index": 0,
  "chunk_id": "sales.csv_0",
  "token_count": 14
}
```

**Alternative formats** (in `improved_chunking.py`, not used by default):

| Format | Example | Best For |
|--------|---------|----------|
| Natural Language | "Alice is 25 and lives in NYC." | Semantic queries |
| Structured Text | "• Name: Alice\n• Age: 25" | Readability |
| Q&A | "Q: What is the name? A: Alice" | Factual lookup |
| Summary (recommended) | "This is a record about Alice. Key Details: ..." | Overall accuracy |

### 4.2 Embeddings (`embeddings.py`)

**Class:** `EmbeddingGenerator`
**Model:** `nomic-embed-text` (768-dimensional vectors)
**Backend:** Ollama local API

```python
# Core call
response = ollama.embeddings(model="nomic-embed-text", prompt=text)
embedding = response["embedding"]  # list of 768 floats
```

On error, returns a zero vector (silent degradation).

Helper: `cosine_similarity(vec1, vec2)` for manual similarity checks.

### 4.3 Vector Store (`vector_store.py`)

**Class:** `VectorStore`
**Database:** ChromaDB (persistent at `backend/rag/chroma_db/`)

**Collection naming:** `user_{username}_files` — one collection per user, all files in same collection.

**Key operations:**

```python
create_collection(name, reset=False)   # idempotent
add_chunks(chunks)                      # batch upsert
search(query_embedding, top_k=5,        # ANN search
       where_filter={"filename": "x"})
get_collection_stats()                  # count, metadata
```

**Search output:**
```python
{
  "documents": ["chunk text..."],
  "metadatas": [{"filename": "sales.csv", ...}],
  "distances": [0.15, 0.23, ...]   # lower = more similar
}
```

### 4.4 Query Processor (`query_processor.py`)

**Class:** `QueryProcessor` — orchestrates the full RAG loop.

```
process_query(question, top_k=5, filename_filter=None)

[1/4] Embed question   → 768-dim vector via nomic-embed-text
[2/4] Search ChromaDB  → top_k most similar chunks
[3/4] Build prompt     → inject context chunks into system prompt
[4/4] Call llama3.2    → return natural language answer
```

**Response:**
```python
{
  "question": "...",
  "answer": "...",
  "success": True,
  "num_chunks_used": 5,
  "metadata": { "context_chunks": [...], "similarity_scores": [...] }
}
```

### 4.5 LLM Wrapper (`ollama_control.py`)

**Class:** `OllamaLLM`
**Model:** `llama3.2` (3B parameters)

**Generation settings:**
- Temperature: `0.3` (low for deterministic, accurate answers)
- Max tokens: `100` (brief, focused responses)
- Streaming: disabled by default

**System prompt template:**
```
You are a helpful data analyst assistant. Your job is to answer questions
based ONLY on the provided data context.

DATA CONTEXT:
{context_chunks}

INSTRUCTIONS:
1. Answer using ONLY the information in the DATA CONTEXT above
2. If the answer cannot be determined, say "I cannot answer this based on the provided data"
3. Be specific and cite relevant data points
4. Perform calculations accurately if needed

QUESTION: {question}

ANSWER (be accurate and provide relevant answer while still being brief):
```

---

## 5. File Parsing System

All parsers in `backend/parsers/`. Entry point: `parse_file(file_path)` auto-routes by extension.

### Standardization Contract

Every parser returns a DataFrame with these standard columns prepended:

| Column | Description |
|--------|-------------|
| `source_file` | Original filename |
| `content_type` | `csv`, `json`, `pdf`, or `ics` |
| `row_index` | Integer row position |
| `...data columns` | File-specific content |

### 5.1 CSV Parser (`csv_parser.py`)

```python
pd.read_csv(file_path)  # → DataFrame
# Adds metadata columns, returns
```

### 5.2 JSON Parser (`json_parser.py`)

```python
# Attempt 1: pd.read_json()
# Attempt 2 (fallback): json.load() → pd.json_normalize()
# Handles both list[dict] and nested dict structures
```

### 5.3 PDF Parser (`pdf_parser.py`)

**Library:** pdfplumber

**Strategy:**
```
Contains tables?
  Yes → Extract tables → combine into DataFrame
  No  → Extract text → split into paragraphs → DataFrame
```

**Key functions:**

| Function | Returns |
|----------|---------|
| `parse_pdf_to_df(path)` | Unified DataFrame (recommended) |
| `parse_pdf_file(path)` | Raw text + tables + metadata dict |
| `parse_text_structured(path)` | Paragraph-level DataFrame |
| `analyze_pdf_type(path)` | `"text"`, `"table"`, or `"mixed"` |

Page markers (`--- Page N ---`) are preserved in extracted text.

### 5.4 iCal Parser (`ical_parser.py`)

Extracts per-event fields: `summary`, `start`, `end`, `duration_hours`, `location`, `description`.
Each calendar event becomes one DataFrame row.

### 5.5 Utilities (`parser_utils.py`)

```python
standardize_dataframe(df, source_file, content_type)
validate_dataframe(df)
merge_dataframes(dfs)
detect_content_type(file_path)
```

---

## 6. Frontend — Next.js Application

**Directory:** `frontend/`
**Port:** 3000
**Router:** App Router (Next.js 16)

### 6.1 Route Structure

| Route | Auth | Description |
|-------|------|-------------|
| `/` | Public | Landing page with features + CTA |
| `/login` | Public | Login form |
| `/register` | Public | Registration form |
| `/dashboard` | Protected | Welcome + stats + quick actions |
| `/upload` | Protected | File upload interface |
| `/chat` | Protected | Chat interface with file context |
| `/files` | Protected | File management (list, delete) |

### 6.2 API Client (`lib/api.ts`)

All API communication is centralized here. Uses `fetch` with `credentials: 'include'` so the JWT cookie is automatically sent.

```typescript
authApi.register(data)          // POST /api/auth/register
authApi.login(credentials)      // POST /api/auth/login
authApi.logout()                // POST /api/auth/logout
authApi.getCurrentUser()        // GET  /api/auth/me

filesApi.upload(file)           // POST /api/files/upload
filesApi.list()                 // GET  /api/files
filesApi.get(id)                // GET  /api/files/{id}
filesApi.delete(id)             // DELETE /api/files/{id}

askApi.ask(question, fileId?)   // POST /api/ask
askApi.getHistory()             // GET  /api/ask/history

healthApi.check()               // GET  /api/health
```

Custom `ApiError` class wraps HTTP errors with status code + message.

### 6.3 Key Components

#### Authentication

**`LoginForm.tsx`**
- Username + password with visibility toggle
- Loading state during submit
- Toast on error, redirect to `/dashboard` on success

**`RegisterForm.tsx`**
- Full name, username, email, password, confirm password
- Live password strength display (8 chars, uppercase, number)
- Duplicate username error handling

#### File Upload

**`FileDropzone.tsx`**
- Drag-and-drop + click-to-select
- File type icons for supported formats
- Upload progress bar
- Post-upload stats (rows, columns, chunks)
- Recent uploads list below dropzone
- "Start Asking Questions" → `/chat?file_id=N`

#### Chat Interface

**`ChatInterface.tsx`** — Root container; loads history on mount, orchestrates Q&A loop
**`ChatMessages.tsx`** — Scrollable message list; user + assistant bubbles with timestamps
**`ChatInput.tsx`** — Text input + send button; disabled while awaiting response
**`FileContextPanel.tsx`** — Sidebar listing available files; click to filter query context

#### Dashboard & Files

**`DashboardPage`** — Stats cards, quick actions (upload, chat), recent activity

**`FilesPage`** — Cards per file with:
- Icon, name, type, upload date (relative)
- Row / column / chunk counts
- Chat button → `/chat?file_id=N`
- Delete button with confirmation dialog

### 6.4 State Management

No global state library. Uses React hooks throughout:
- `useState` / `useEffect` for local component state
- `useCallback` for stable references
- `useRouter` (Next.js) for navigation
- `useToast` (Sonner) for notifications
- React Hook Form + Zod for form validation

### 6.5 Styling

- **Tailwind CSS v4** utility-first
- **Dark theme** with emerald-to-blue gradient accents
- `glass` class for glassmorphism cards
- Fully responsive grid layouts

---

## 7. Authentication & Security

### JWT Configuration

| Setting | Value |
|---------|-------|
| Algorithm | HS256 |
| Expiry | 24 hours (1440 minutes) |
| Storage | HTTP-only cookie (backend sets) |
| Payload | `{ "sub": "username", "exp": timestamp }` |

### Password Policy

- Hashing: argon2 (via passlib)
- Min length: 6 characters
- Max length: 128 characters

### CORS

Allowed origins: `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:8000`
Credentials: enabled
Methods & Headers: all

### User Isolation

Each user has their own ChromaDB collection: `user_{username}_files`. All DB queries are scoped by `username` extracted from the validated JWT.

---

## 8. Database Schema

**Type:** SQLite
**File:** `backend/users.db`

```sql
CREATE TABLE users (
    username    TEXT PRIMARY KEY,
    fullname    TEXT NOT NULL,
    email       TEXT NOT NULL,
    password    TEXT NOT NULL,       -- argon2 hash
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
    file_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    username          TEXT NOT NULL REFERENCES users(username),
    filename          TEXT NOT NULL,  -- disk name with timestamp suffix
    original_filename TEXT NOT NULL,  -- user-visible name
    file_type         TEXT NOT NULL,  -- csv | json | pdf | ics
    file_path         TEXT NOT NULL,  -- absolute path on disk
    upload_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num_rows          INTEGER,
    num_columns       INTEGER,
    collection_name   TEXT            -- ChromaDB collection
);

CREATE TABLE chat_history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT NOT NULL REFERENCES users(username),
    file_id   INTEGER REFERENCES files(file_id),
    question  TEXT NOT NULL,
    answer    TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**File storage:** `backend/uploads/`
**Vector storage:** `backend/rag/chroma_db/`

---

## 9. External Dependencies

### Ollama (Required — local)

| Model | Role | Dimensions |
|-------|------|-----------|
| `nomic-embed-text` | Embedding generation | 768-dim vectors |
| `llama3.2` | Answer generation | 3B parameters |

```bash
ollama pull nomic-embed-text
ollama pull llama3.2
ollama serve   # must be running on localhost:11434
```

### Backend Python Packages (key)

```
fastapi, uvicorn[standard]
python-multipart          # file uploads
python-jose[cryptography] # JWT
passlib[argon2]           # password hashing
pandas, numpy             # data processing
pdfplumber                # PDF parsing
icalendar                 # iCal parsing
tiktoken                  # token counting
chromadb                  # vector store
ollama                    # Ollama Python client
```

### Frontend npm Packages (key)

```
next@16           react@19          typescript@5
tailwindcss@4     @radix-ui/*        lucide-react
framer-motion     sonner            react-hook-form
zod               class-variance-authority
```

---

## 10. Data Flow

### File Upload → Query (End-to-End)

```
[Browser] FileDropzone
    │  POST /api/files/upload  (multipart, cookie)
    ▼
[FastAPI] /api/files/upload
    │  Save file to backend/uploads/
    │  parse_file() → DataFrame
    │  dataframe_to_chunks() → [{text, metadata}]
    │  EmbeddingGenerator.embed_chunks() → [{...embedding[]}]
    │  VectorStore.add_chunks() → ChromaDB persisted
    │  INSERT INTO files (metadata)
    │  → { file_id, num_rows, num_cols, num_chunks }
    ▼
[Browser] ChatInterface (with file_id from URL)
    │  POST /api/ask  { question, file_id }
    ▼
[FastAPI] /api/ask
    │  QueryProcessor.process_query(question, file_id)
    │    → embed question (nomic-embed-text)
    │    → VectorStore.search(query_embedding, top_k=5)
    │    → OllamaLLM.answer_question(question, chunks)
    │    → { answer, num_chunks_used, ... }
    │  INSERT INTO chat_history
    │  → { question, answer, success }
    ▼
[Browser] Display assistant message
```

---

## 11. Key Design Decisions

### 1. Local-First Architecture
**Decision:** Use Ollama for both embeddings and LLM inference instead of OpenAI/Anthropic APIs.
**Rationale:** Privacy-preserving; no API costs; no data sent to third parties. Suited for sensitive datasets (finance, HR, health).
**Trade-off:** Requires Ollama installed locally; inference slower than hosted APIs; model quality lower than frontier models.

### 2. Single ChromaDB Collection per User
**Decision:** All files for a user share one ChromaDB collection (`user_{username}_files`), distinguished by filename metadata.
**Rationale:** Simplifies collection lifecycle; allows cross-file queries.
**Trade-off:** Cannot delete a single file's vectors without rebuilding the collection. Metadata filtering adds overhead at search time.

### 3. Row-Based Chunking as Default
**Decision:** Each DataFrame row becomes one chunk (not sliding window or semantic chunking).
**Rationale:** Preserves row-level atomicity; avoids splitting related fields; predictable for tabular data.
**Trade-off:** Poor for text-heavy PDFs; very long rows may exceed token limits; no cross-row context captured.

### 4. SQLite for Relational Data
**Decision:** SQLite for users, files, and chat history instead of PostgreSQL.
**Rationale:** Zero-setup, file-based, sufficient for single-machine local deployment.
**Trade-off:** Not suitable for multi-process or multi-machine deployments; no connection pooling.

### 5. JWT in HTTP-Only Cookies
**Decision:** Store JWT in httponly cookie rather than localStorage.
**Rationale:** Protects against XSS; cookie sent automatically by browser.
**Trade-off:** Requires CORS `credentials: include`; CSRF risk (mitigated by SameSite policy).

### 6. Max 100 LLM Output Tokens
**Decision:** Cap LLM response at 100 tokens.
**Rationale:** Fast responses; forces brevity; reduces hallucination surface.
**Trade-off:** Complex multi-part answers get truncated; no room for explanations or calculations shown step-by-step.

### 7. No Streaming
**Decision:** Return complete LLM responses in one HTTP response rather than streaming.
**Rationale:** Simpler implementation; no SSE/WebSocket setup needed.
**Trade-off:** Users wait with no feedback until full response arrives; poor UX for longer answers.

### 8. `improved_chunking.py` Not Wired Up
**Decision:** Alternative chunking formats (natural language, Q&A, summary) exist but are not used in the upload pipeline.
**Rationale:** Likely exploratory/experimental code.
**Trade-off:** Better RAG accuracy is available but not leveraged.

---

## 12. Areas for Improvement

### High Priority

#### 1. Streaming LLM Responses
The biggest UX gap. Users see a blank chat while waiting for Ollama.
**Fix:** Use `ollama.generate(..., stream=True)` on the backend, return via FastAPI `StreamingResponse`, and consume with `ReadableStream` on the frontend.

#### 2. File Deletion Does Not Clean Up ChromaDB
Deleting a file removes it from SQLite and disk but **not** from ChromaDB. Old embeddings persist and can pollute future queries.
**Fix:** On `DELETE /api/files/{id}`, call `VectorStore.delete_by_filter({"file_id": id})` or rebuild the collection without those chunks.

#### 3. Switch to Summary Chunking for PDFs
`improved_chunking.py` has a summary format that significantly improves RAG accuracy, but the upload pipeline uses raw row-based chunking even for PDFs.
**Fix:** Route PDF uploads through summary-style chunking; use row chunking only for CSV/JSON.

#### 4. Token Cap Too Low
100 max tokens frequently truncates answers.
**Fix:** Raise to 300–500 tokens. For data analysis questions, allow structured multi-line responses.

### Medium Priority

#### 5. No Input Validation on Questions
The `/api/ask` endpoint accepts arbitrary question strings with no length limit or sanitization.
**Fix:** Add Pydantic field constraints (`max_length=500`); reject empty questions early.

#### 6. Chat History Not Linked to File Context
`chat_history.file_id` can be NULL; the UI loads all history regardless of which file is active.
**Fix:** Always associate questions with a file_id; filter history display by current file context.

#### 7. No Progress Feedback During Upload
Large files (multi-MB PDFs) take time to embed. The frontend shows a simple progress bar based on upload bytes, not actual processing progress.
**Fix:** Return a job ID on upload; poll a `/api/files/{id}/status` endpoint that reflects embedding progress.

#### 8. EmbeddingGenerator Zero-Vector Fallback
On embedding failure, a zero vector is silently returned. Zero vectors will match everything poorly and corrupt search results.
**Fix:** Raise an exception on embedding failure; surface error to user rather than silently inserting bad data.

#### 9. Environment Variables Partially Hardcoded
Some values (like CORS origins, Ollama model names) are hardcoded in `app.py` rather than read from `.env`.
**Fix:** Move all configuration to `.env` with `pydantic-settings` for type-safe config loading.

#### 10. No Email Uniqueness Check on Registration
The `email` column in `users` has no UNIQUE constraint. Two users can register with the same email.
**Fix:** Add `UNIQUE` constraint to `users.email`; validate uniqueness before insert.

### Lower Priority

#### 11. Single Collection Per User Complicates Deletion
See design decision #2. The current architecture makes it expensive to remove one file's embeddings.
**Fix (long-term):** Give each file its own ChromaDB collection (`user_{username}_file_{file_id}`). Deletion is then a `client.delete_collection()` call.

#### 12. No Rate Limiting
The API has no rate limiting. A single user could flood the Ollama server with concurrent requests.
**Fix:** Add `slowapi` or middleware-level rate limiting per user.

#### 13. No Multi-File Query Support
Users can filter to one file but cannot ask questions that span multiple files simultaneously.
**Fix:** Allow the `/api/ask` endpoint to accept a list of `file_ids`; aggregate retrieved chunks from all specified files before prompting the LLM.

#### 14. No Caching of Common Questions
The same question asked twice hits Ollama twice.
**Fix:** Cache `(question_hash, collection_name)` → answer in a simple in-memory LRU or Redis store.

#### 15. Frontend Has No Loading Skeleton
Data fetches (file list, chat history) show no loading state — the list just appears.
**Fix:** Add skeleton loaders for all async-loaded lists.

---

## 13. Development Setup

```bash
# 1. Install and start Ollama
brew install ollama          # macOS
ollama pull nomic-embed-text
ollama pull llama3.2
ollama serve                 # stays running on :11434

# 2. Backend
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env         # set SECRET_KEY
python3 app.py               # → http://localhost:8000

# 3. Frontend
cd frontend
npm install
npm run dev                  # → http://localhost:3000
```

### Environment Variables (`backend/.env`)

```
SECRET_KEY=<random 64-char string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_PATH=users.db
CHROMA_DB_PATH=rag/chroma_db
```

### Frontend Environment (`frontend/.env.local`)

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | `http://localhost:3000` |
| Backend API | `http://localhost:8000` |
| Swagger Docs | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| Ollama | `http://localhost:11434` |
