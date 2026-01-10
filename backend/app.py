"""
AskMyData REST API - FastAPI Upgrade 
Backend for the RAG Pipeline 
"""

from fastapi import FastAPI,  HTTPException, Depends, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from typing import Optional, Dict, List, Annotated
from pydantic import BaseModel, EmailStr

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


# RAG Pipeline imports 
from parsers.file_parser import parse_file
from rag.chunking_module import dataframe_to_chunks
from rag.embeddings import EmbeddingGenerator
from rag.vector_store import VectorStore
from rag.query_processor import QueryProcessor


# App initialization and configs 

app = FastAPI(
    title = 'AskMyData REST API', 
    description = "Data analysis with RAG", 
    version = '1.5.0',
    docs_url = '/docs', 
    redoc_url= '/re_doc' 
)

#JWT Configuration (Flask has secert key and sessions)
SECRET_KEY = "Vibhors_Secret_key_until_prod"   
ALGORITHM =  "  HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24 # user has to revalidate after 24 hours 

# pasword hashing 
pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")


# CORS Configuration 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # In production, specify exact origins
    allow_credentials=True,    # Allow cookies
    allow_methods=["*"],       # Allow all HTTP methods
    allow_headers=["*"],       # Allow all headers
)
