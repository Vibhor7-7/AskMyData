# AskMyData

**A Full-Stack RAG-Powered Data Analysis Platform**

AskMyData is an intelligent web application that allows users to upload their own structured data files (CSV, JSON, PDF, iCal) and ask natural language questions about them. The system uses Retrieval-Augmented Generation (RAG) with ChromaDB for vector search and Ollama for local LLM inference to provide accurate, context-aware answers grounded in your uploaded data.

---

## Project Overview

### The Problem
Traditional data analysis requires knowledge of SQL, Python, or spreadsheet formulas. Non-technical users struggle to extract insights from their data, and even technical users face friction when exploring unfamiliar datasets.

### The Solution
AskMyData bridges this gap by enabling natural language interaction with your data. Upload a file, ask questions in plain English, and get intelligent answers grounded in uploaded context. 

**Example Interactions:**
- Upload a sales CSV → "What was our revenue in Q3?"
- Upload a resume PDF → "What programming languages does this candidate know?"
- Upload a calendar file → "How many meetings do I have next week?"

### Why It's Useful
- **Accessible:** Anyone can analyze data without technical skills
- **Private:** Runs locally with Ollama—your data never leaves your machine
- **Flexible:** Works with CSV, JSON, PDF, and iCal files
- **Intelligent:** Uses RAG to provide accurate, source-grounded answers

---
## High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  Next.js + TypeScript + Radix UI + Tailwind CSS                 │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/REST API (Port 3000)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI REST API (Port 5001)               │
│  • Authentication   • File Upload    • Query Processing         │
│  • CORS Handler     • Session Mgmt   • Error Handling           │
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
        │  1. Chunking Module                      │
        │     └─> Convert data to text chunks      │
        │                                          │
        │  2. Embeddings (Ollama)                  │
        │     └─> nomic-embed-text (768-dim)       │
        │                                          │
        │  3. Vector Store (ChromaDB)              │
        │     └─> Persistent similarity search     │
        │                                          │
        │  4. Query Processor                      │
        │     └─> Embed query → Retrieve context   │
        │                                          │
        │  5. LLM Generation (Ollama)              │
        │     └─> llama3.2 generates answer        │
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
- Configurable top-k (revised to 10-15 for better performance) 

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


## Getting Started

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

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ by Vibhor Sharma**
