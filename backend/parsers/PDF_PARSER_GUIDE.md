# PDF Parser Usage Guide

## Overview
The PDF parser provides multiple ways to extract and normalize content from PDF files.

## Installation
Make sure `pdfplumber` is installed:
```bash
pip install pdfplumber
```

## Quick Start

### 1. Basic Usage - Get All Content
```python
from pdf_parser import parse_pdf_file

result = parse_pdf_file('document.pdf')

# Access components
print(result['text'])           # All text
print(result['tables'])         # List of DataFrames
print(result['metadata'])       # PDF info
```

### 2. Recommended - Get Unified DataFrame
```python
from pdf_parser import parse_pdf_to_df

df = parse_pdf_to_df('document.pdf')
# Returns a single DataFrame regardless of content type
```

### 3. Smart Parsing - Auto-detect Content Type
```python
from pdf_parser import parse_pdf_adaptive

result = parse_pdf_adaptive('document.pdf')
# Returns appropriate format based on content
```

## Function Reference

### Main Functions

#### `parse_pdf_file(file_path)`
**Returns:** Dictionary with `text`, `tables`, `metadata`
**Use when:** You need access to all components separately

#### `parse_pdf_to_df(file_path)`
**Returns:** Single pandas DataFrame
**Use when:** You want consistent output format (recommended)

#### `parse_pdf_adaptive(file_path)`
**Returns:** DataFrame or dict (depending on content type)
**Use when:** You want the parser to automatically choose the best strategy

### Specialized Functions

#### `parse_text(file_path)`
**Returns:** String with page markers
**Use when:** You need raw text extraction

#### `parse_text_structured(file_path)`
**Returns:** DataFrame with columns: page, paragraph, content, length
**Use when:** You need paragraph-level analysis

#### `parse_tabular(file_path)`
**Returns:** List of DataFrames (basic metadata)
**Use when:** You only need tables

#### `parse_tabular_with_context(file_path)`
**Returns:** List of DataFrames (enhanced metadata with page context)
**Use when:** You need tables with surrounding text

#### `analyze_pdf_type(file_path)`
**Returns:** String: 'text_only', 'table_heavy', or 'mixed'
**Use when:** You want to know content type before parsing

## Testing

Run the comprehensive test:
```bash
cd backend/parsers
python pdf_parser.py
```

Place a `sample.pdf` in the parsers directory to test all functions.

## Integration Example

```python
from pdf_parser import parse_pdf_to_df
import os

def handle_uploaded_pdf(file_path, username):
    """Process uploaded PDF and store in database"""
    try:
        # Parse PDF to DataFrame
        df = parse_pdf_to_df(file_path)
        
        # Check source type
        source = df.attrs.get('source', 'unknown')
        
        if source == 'tables':
            print(f"Extracted {len(df)} rows from tables")
        else:
            print(f"Extracted {len(df)} pages/paragraphs of text")
        
        # Save to database or process further
        # ... your logic here ...
        
        return df
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None
```

## Notes

- All table extraction includes metadata: `df.attrs['page']`, `df.attrs['table_num']`
- Text extraction preserves page boundaries
- For large PDFs, consider processing page-by-page
- Empty PDFs return empty DataFrames (not errors)
