# 🧠 AskMyData

**A Full-Stack RAG-Powered Data Analysis Platform**

AskMyData is an intelligent web application that allows users to upload their own structured data files (CSV, JSON, PDF, iCal) and ask natural language questions about them. The system uses Retrieval-Augmented Generation (RAG) with ChromaDB for vector search and Ollama for local LLM inference to provide accurate, context-aware answers grounded in your uploaded data.

---

## 📖 Project Overview

### The Problem
Traditional data analysis requires knowledge of SQL, Python, or spreadsheet formulas. Non-technical users struggle to extract insights from their data, and even technical users face friction when exploring unfamiliar datasets.

### The Solution
AskMyData bridges this gap by enabling natural language interaction with your data. Upload a file, ask questions in plain English, and get intelligent answers powered by AI—no coding required.

**Example Interactions:**
- Upload a sales CSV → "What was our revenue in Q3?"
- Upload a resume PDF → "What programming languages does this candidate know?"
- Upload a calendar file → "How many meetings do I have next week?"

### Why It's Useful
- **Accessible:** Anyone can analyze data without technical skills
- **Fast:** Get insights in seconds, not hours
- **Private:** Runs locally with Ollama—your data never leaves your machine
- **Flexible:** Works with CSV, JSON, PDF, and iCal files
- **Intelligent:** Uses RAG to provide accurate, source-grounded answers

---

## ✨ Key Features

### 🗂️ Multi-Format File Support
- **CSV:** Tabular data with automatic type detection
- **JSON:** Nested data structures flattened intelligently
- **PDF:** Text extraction with table detection (powered by pdfplumber)
- **iCal:** Calendar events parsed into queryable format

### 🤖 RAG-Based Question Answering
- **Semantic Search:** Finds relevant data chunks using vector embeddings
- **Context-Aware Responses:** LLM generates answers using retrieved context
- **Source Attribution:** Shows which data chunks were used for each answer
- **Multi-File Support:** Query specific files or search across all uploads

### 🔍 Vector Embeddings & Search
- **ChromaDB Integration:** Persistent vector database for fast similarity search
- **Nomic Embeddings:** 768-dimensional embeddings via Ollama
- **Metadata Filtering:** Queries isolated to specific files
- **Efficient Chunking:** Row-based chunking for structured data, semantic chunking for documents

### 🚀 Local LLM Inference
- **Ollama Integration:** Run models completely offline
- **llama3.2 Model:** Fast, capable 3B parameter model
- **Custom Prompts:** Tailored prompts for data analysis vs document Q&A
- **Streaming Support:** Real-time response generation (future enhancement)

### 📊 User Management & Persistence
- **Authentication:** Secure session-based login with password hashing
- **Multi-User Support:** Each user's files and chats are isolated
- **Chat History:** Persistent conversation logs
- **Dashboard Analytics:** File counts, query stats, recent activity

### 🎨 Modern UI/UX
- **Next.js Frontend:** Fast, responsive React application
- **Dark/Light Mode:** Theme toggle with system preference detection
- **Real-Time Updates:** Instant feedback on uploads and queries
- **Drag-and-Drop Upload:** Intuitive file management

---

## 🏗️ High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  Next.js + TypeScript + Radix UI + Tailwind CSS                │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/REST API (Port 3000)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK REST API (Port 5001)                 │
│  • Authentication   • File Upload    • Query Processing         │
│  • CORS Handler     • Session Mgmt   • Error Handling          │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌──────────────┐
   │ SQLite  │  │ File    │  │ RAG Pipeline │
   │ Database│  │ Parsers │  │              │
   └─────────┘  └─────────┘  └──────────────┘
   • Users          • CSV          │
   • Files          • JSON         │
   • Chat History   • PDF          │
                    • iCal         │
                                   ▼
        ┌──────────────────────────────────────────┐
        │         RAG PIPELINE FLOW                │
        │                                          │
        │  1. Chunking Module                     │
        │     └─> Convert data to text chunks     │
        │                                          │
        │  2. Embeddings (Ollama)                 │
        │     └─> nomic-embed-text (768-dim)      │
        │                                          │
        │  3. Vector Store (ChromaDB)             │
        │     └─> Persistent similarity search    │
        │                                          │
        │  4. Query Processor                     │
        │     └─> Embed query → Retrieve context  │
        │                                          │
        │  5. LLM Generation (Ollama)             │
        │     └─> llama3.2 generates answer       │
        └──────────────────────────────────────────┘
```

### Frontend Architecture
**Technology:** Next.js 16 (App Router), TypeScript, React

**Key Components:**
- **Pages:** `/login`, `/register`, `/dashboard`, `/upload`, `/chat`, `/files`
- **API Client:** Type-safe API wrapper with error handling
- **State Management:** React hooks (useState, useEffect, useCallback)
- **Styling:** Tailwind CSS with Radix UI primitives
- **Animations:** Framer Motion for smooth transitions

**Key Features:**
- Client-side routing with URL parameters for file context
- Real-time form validation
- Toast notifications for user feedback
- Responsive design (mobile-friendly)

### Backend Architecture
**Technology:** Flask 3.x, Python 3.10+

**REST API Endpoints:**
```
Authentication:
  POST   /api/auth/register
  POST   /api/auth/login
  POST   /api/auth/logout
  GET    /api/auth/me

File Management:
  POST   /api/files/upload
  GET    /api/files
  GET    /api/files/<id>
  DELETE /api/files/<id>

Query & Chat:
  POST   /api/ask
  GET    /api/ask/history

Health Check:
  GET    /api/health
```

**Data Flow:**
1. File upload → Parse → Chunk → Embed → Store in ChromaDB + SQLite
2. Question → Embed → Search ChromaDB → Retrieve top-k → LLM → Answer

### RAG Pipeline Deep Dive

**1. Data Ingestion & Chunking**
```python
File → Parser → Standardized DataFrame → Row-to-Text Chunks
```
- **CSV/JSON:** Each row becomes a text chunk with column labels
- **PDF:** Paragraphs or table rows extracted as chunks
- **iCal:** Events converted to structured text

**2. Embedding Generation**
```python
Text Chunks → Ollama (nomic-embed-text) → 768-dim Vectors
```
- Batch processing for efficiency
- Metadata attached (filename, chunk_id, source)

**3. Vector Storage**
```python
Embeddings + Metadata → ChromaDB Collection
```
- User-specific collections: `user_{username}_files`
- Persistent storage with automatic indexing

**4. Query Processing**
```python
Question → Embed → Similarity Search → Top-K Chunks → Context
```
- Metadata filtering for file-specific queries
- Configurable top-k (default: 5-10 chunks)

**5. Answer Generation**
```python
Context + Question → Prompt Template → Ollama (llama3.2) → Answer
```
- Custom prompts for structured data vs documents
- Temperature control for consistency
- Context-grounded responses (reduces hallucinations)

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Next.js 16.0.10** | React framework with App Router |
| **TypeScript** | Type-safe development |
| **Radix UI** | Accessible component primitives |
| **Tailwind CSS** | Utility-first styling |
| **Framer Motion** | Animation library |
| **Lucide Icons** | Icon set |

### Backend
| Technology | Purpose |
|-----------|---------|
| **Flask 3.x** | Python web framework |
| **SQLite** | Relational database |
| **Pandas** | Data manipulation |
| **NumPy** | Numerical operations |
| **Werkzeug** | Password hashing |

### File Parsing
| Technology | Purpose |
|-----------|---------|
| **pdfplumber** | PDF text & table extraction |
| **icalendar** | iCal/ICS parsing |
| **pandas** | CSV/JSON parsing |

### RAG & AI
| Technology | Purpose |
|-----------|---------|
| **Ollama** | Local LLM inference |
| **ChromaDB** | Vector database |
| **nomic-embed-text** | Embedding model (768-dim) |
| **llama3.2** | Language model (3B params) |
| **tiktoken** | Token counting |

### Development Tools
| Technology | Purpose |
|-----------|---------|
| **npm** | Frontend package manager |
| **pip** | Python package manager |
| **Git** | Version control |

---

## 📚 What I Learned

### RAG & Vector Databases
- **Chunking Strategy Matters:** Row-based chunking works well for tabular data, but documents need semantic chunking (paragraphs, not pages)
- **Metadata is Powerful:** Filtering by filename/source in ChromaDB enables multi-file collections without cross-contamination
- **Embedding Quality:** Nomic-embed-text provides excellent semantic search despite being lightweight (768-dim vs 1536-dim for OpenAI)
- **Top-K Tuning:** More context (k=10) improves answer quality but increases latency and LLM token usage

### Prompt Engineering & Grounding
- **Explicit Instructions:** LLMs need clear, structured prompts ("Answer based ONLY on the data provided")
- **Context Window Management:** Too much context confuses small models; too little loses important details
- **Grounding Prevents Hallucinations:** By providing retrieved chunks as context, the model stays factual
- **Template Adaptation:** Different data types (CSV vs resume PDF) benefit from specialized prompt templates

### Full-Stack Integration
- **Type Safety End-to-End:** TypeScript on frontend + clear API contracts reduced bugs significantly
- **Session Management:** Flask sessions work well for authentication without JWT complexity
- **CORS Configuration:** Proper CORS setup is critical for local development (localhost:3000 ↔ localhost:5001)
- **Error Handling:** Consistent error responses (ApiError class) improve debugging and UX
- **State Management:** React hooks are sufficient for medium-complexity apps; no need for Redux

### Performance & Optimization
- **Lazy Loading:** Initializing Ollama connections only when needed reduces startup time
- **Batch Embeddings:** Processing 50+ chunks at once is 10x faster than sequential
- **Collection Pooling:** Reusing ChromaDB collections across files saves space and improves search speed
- **Frontend Caching:** useEffect dependencies prevent unnecessary re-fetches

### Challenges Overcome
1. **ChromaDB Collection Conflicts:** Initially created one collection per file; switched to per-user collections with metadata filtering
2. **PDF Parsing Quality:** pdfplumber struggles with multi-column layouts; added custom chunking logic
3. **Model Size vs Quality:** llama3.2 (3B) is fast but limited; balancing speed vs accuracy is key
4. **File Context Switching:** Needed URL parameters + API changes to query specific files instead of always using the latest

---

## 🚀 Getting Started

### Prerequisites
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull nomic-embed-text
ollama pull llama3.2

# Python 3.10+ and Node.js 18+
python3 --version
node --version
```

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/AskMyData-1.git
cd AskMyData-1
```

**2. Backend Setup**
```bash
cd backend

# Create virtual environment
python3 -m venv ../.venv
source ../.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Flask server (port 5001)
python3 app.py
```

**3. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js dev server (port 3000)
npm run dev
```

**4. Start Ollama**
```bash
ollama serve
```

**5. Open Application**
Navigate to `http://localhost:3000`

---

## 📖 Usage Guide

1. **Register/Login:** Create an account or log in
2. **Upload Files:** Drag and drop CSV, JSON, PDF, or iCal files
3. **Wait for Processing:** Files are parsed, chunked, embedded, and stored
4. **Ask Questions:** Type natural language questions about your data
5. **View Context:** See which data chunks were used for each answer
6. **Manage Files:** View all uploads, delete files, or switch between files in chat

---

## 🔮 Future Enhancements

- [ ] Streaming responses for real-time answer generation
- [ ] CSV preview with data profiling (nulls, types, distributions)
- [ ] Chart generation from natural language ("show me a bar chart of revenue by region")
- [ ] Multi-file queries ("compare sales.csv with last_year.csv")
- [ ] Export chat history as PDF/Markdown
- [ ] Docker containerization for one-click deployment
- [ ] Support for Excel (.xlsx) and Parquet files
- [ ] Fine-tuned prompt templates per file type
- [ ] Upgrade to larger models (llama3.1:8b, mistral)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **Ollama** for making local LLMs accessible
- **ChromaDB** for a simple yet powerful vector database
- **Next.js** and **Flask** for excellent developer experience
- **Radix UI** for accessible component primitives

---

**Built with ❤️ by Vibhor Sharma**
