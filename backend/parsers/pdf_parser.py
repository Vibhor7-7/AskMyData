"""
PDF Parser Module for AskMyData

This module provides comprehensive PDF parsing functionality with multiple approaches:

MAIN FUNCTIONS:
1. parse_pdf_file(file_path) - Extract text, tables, and metadata from PDF
2. parse_pdf_to_df(file_path) - Get unified DataFrame output (tables or text)
3. parse_pdf_adaptive(file_path) - Automatically choose best parsing strategy

SPECIALIZED FUNCTIONS:
- parse_text(file_path) - Extract raw text with page markers
- parse_text_structured(file_path) - Extract text as paragraph-level DataFrame
- parse_tabular(file_path) - Extract tables as list of DataFrames
- parse_tabular_with_context(file_path) - Extract tables with page context
- get_metadata(file_path) - Get PDF metadata (pages, file info, etc.)
- analyze_pdf_type(file_path) - Determine if PDF is text/table/mixed

HELPER FUNCTIONS:
- split_into_paragraphs(text) - Split text into paragraph chunks

Usage:
    from pdf_parser import parse_pdf_file, parse_pdf_to_df
    
    # Basic usage - get all content
    result = parse_pdf_file('document.pdf')
    
    # Get as DataFrame (recommended for consistency)
    df = parse_pdf_to_df('document.pdf')
"""

import pdfplumber  # Best all-around library
import pandas as pd
import os 
import re 


def parse_pdf_file(file_path): 
    
    #Break down the pdf into three main components (text, tables, metadata)
    # Main function returns a dictionary with 'text, 'tables', and 'metadata' 
    try:
        results = {
            'text': '',
            'tables':[],
            'metadata': {}
        }
        results['text'] = parse_text(file_path)
        results['tables'] = parse_tabular(file_path)
        results['metadata'] = get_metadata(file_path)

        return results
    except Exception as e:
        print(f"Error parsing PDF file: {e}")
        return {
            'text': '',
            'tables':[],
            'metadata': {'error': str(e)}
        }

def parse_text(file_path):
    " Extract text from PDF using pdfplumber"
    # Open pdf using pdfplumber:
    # Loop through each page 
    # Extract text from each page 
    # combine all the text with page seperators 

    full_text = []

    with pdfplumber.open(file_path) as pdf: 
        for page_num, page in enumerate(pdf.pages, start = 1):
            text = page.extract_text()
            if text: 
                full_text.append(f"--- Page {page_num} ---\n{text}\n")

    return "\n".join(full_text)


def parse_tabular(file_path):
    " Extract tables from PDF using pdfplumber"
    # Open pdf using pdfplumber:
    # Check each page for tables 
    # Convert each table to pandas DataFrame
    # Store DataFrames in a list and return

    all_tables = []

    with pdfplumber.open(file_path) as pdf: 
        for page_num, page in enumerate(pdf.pages, start = 1):
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables):
                    if table: #convert the table to a DataFrame if it exists
                        df = pd.DataFrame(table[1:], columns=table[0])

                        #Add metadata about page and table number
                        df.attrs['page'] = page_num
                        df.attrs['table_num'] = table_num + 1

                        all_tables.append(df)
    return all_tables


def parse_tabular_with_context(file_path):
    """Extract tables with surrounding context"""
    all_tables = []
    
    with pdfplumber.open(file_path) as pdf: 
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables):
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    
                    # Enhanced metadata
                    df.attrs['page'] = page_num
                    df.attrs['table_num'] = table_num + 1
                    df.attrs['page_text'] = page_text[:500]  # First 500 chars of page
                    df.attrs['row_count'] = len(df)
                    df.attrs['col_count'] = len(df.columns)
                    
                    all_tables.append(df)
    
    return all_tables


def get_metadata(file_path):
    " Extract metadata from PDF using pdfplumber"
    # Open pdf using pdfplumber:
    # Count pages 
    # Check if tables exist
    # Get file info 

    with pdfplumber.open(file_path) as pdf:
        num_pages = len(pdf.pages)

        has_tables = False 
        for page in pdf.pages:
            if page.extract_tables():
                has_tables = True
                break
        
    return {
        'num_pages': num_pages,
        'has_tables': has_tables,
        'file_size_bytes': os.path.getsize(file_path),
        'file_name': os.path.basename(file_path)
    }   

def split_into_paragraphs(text):
    """Split text into paragraphs"""
    # Split on double newlines or large gaps
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]

def parse_text_structured(file_path):
    """Extract text with paragraph-level granularity"""
    all_chunks = []
    
    with pdfplumber.open(file_path) as pdf: 
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                paragraphs = split_into_paragraphs(text)
                
                for para_num, paragraph in enumerate(paragraphs, start=1):
                    all_chunks.append({
                        'page': page_num,
                        'paragraph': para_num,
                        'content': paragraph,
                        'length': len(paragraph)
                    })
    
    return pd.DataFrame(all_chunks)  # Already a DataFrame!



def parse_pdf_to_df(file_path):
    """
    Unified DataFrame output for any PDF content
    Returns a single DataFrame regardless of content type
    """
    result = parse_pdf_file(file_path)
    
    # Priority 1: If tables exist, combine all tables
    if result['tables']:
        # Option A: Return all tables concatenated
        combined_df = pd.concat(result['tables'], ignore_index=True)
        combined_df.attrs['source'] = 'tables'
        return combined_df
        
        # Option B: Return just first table (current approach)
        # return result['tables'][0]
    
    # Priority 2: If only text, create structured DataFrame
    else:
        # Convert text to page-level DataFrame
        pages_data = []
        text_by_page = result['text'].split('--- Page')
        
        for page_section in text_by_page[1:]:  # Skip first empty split
            parts = page_section.split('---\n', 1)
            if len(parts) == 2:
                page_num = parts[0].strip()
                content = parts[1].strip()
                pages_data.append({
                    'page': page_num,
                    'content': content
                })
        
        df = pd.DataFrame(pages_data)
        df.attrs['source'] = 'text'
        return df

def analyze_pdf_type(file_path):
    """
    Determine if PDF is primarily text, tables, or mixed
    """
    metadata = get_metadata(file_path)
    result = parse_pdf_file(file_path)
    
    text_length = len(result['text'])
    table_count = len(result['tables'])
    
    if table_count == 0:
        return 'text_only'
    elif text_length < 500 and table_count > 0:
        return 'table_heavy'
    else:
        return 'mixed'

def parse_pdf_adaptive(file_path):
    """
    Parse PDF differently based on content type
    """
    pdf_type = analyze_pdf_type(file_path)
    
    if pdf_type == 'text_only':
        return parse_text_structured(file_path)  # Paragraph-level DF
    elif pdf_type == 'table_heavy':
        return parse_pdf_to_df(file_path)  # Combined tables
    else:
        # For mixed content, return both
        return {
            'text_df': parse_text_structured(file_path),
            'tables': parse_tabular_with_context(file_path)
        }

def main():
    """
    Comprehensive test of all PDF parser functions
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '_Vibhor_Sharma_.pdf')
    
    if not os.path.exists(file_path):
        print(f"Error: Test file not found at {file_path}")
        print("Please add a 'sample.pdf' file to the parsers directory for testing.")
        return
    
    print("="*60)
    print("PDF PARSER - COMPREHENSIVE TEST")
    print("="*60)
    
    # Test 1: Basic parsing with parse_pdf_file()
    print("\n1. Testing parse_pdf_file() - Full extraction:")
    print("-" * 60)
    try:
        results = parse_pdf_file(file_path)
        
        print(f"✓ Text extracted: {len(results['text'])} characters")
        print(f"✓ Tables found: {len(results['tables'])}")
        print(f"✓ Metadata: {results['metadata']}")
        
        if results['text']:
            print(f"\nFirst 300 chars of text:\n{results['text'][:300]}...")
        
        if results['tables']:
            print(f"\nFirst table preview:")
            print(results['tables'][0].head())
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Structured text parsing
    print("\n\n2. Testing parse_text_structured() - Paragraph-level:")
    print("-" * 60)
    try:
        text_df = parse_text_structured(file_path)
        print(f"✓ Extracted {len(text_df)} paragraphs")
        print(f"✓ DataFrame shape: {text_df.shape}")
        print(f"\nFirst few paragraphs:")
        print(text_df.head())
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Tables with context
    print("\n\n3. Testing parse_tabular_with_context():")
    print("-" * 60)
    try:
        tables_with_context = parse_tabular_with_context(file_path)
        print(f"✓ Extracted {len(tables_with_context)} tables with context")
        
        for i, table in enumerate(tables_with_context):
            print(f"\nTable {i+1}:")
            print(f"  - Page: {table.attrs.get('page', 'N/A')}")
            print(f"  - Dimensions: {table.attrs.get('row_count', 0)} rows × {table.attrs.get('col_count', 0)} cols")
            print(f"  - Context preview: {table.attrs.get('page_text', '')[:100]}...")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: PDF type analysis
    print("\n\n4. Testing analyze_pdf_type():")
    print("-" * 60)
    try:
        pdf_type = analyze_pdf_type(file_path)
        print(f"✓ PDF Type: {pdf_type}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Adaptive parsing
    print("\n\n5. Testing parse_pdf_adaptive():")
    print("-" * 60)
    try:
        adaptive_result = parse_pdf_adaptive(file_path)
        
        if isinstance(adaptive_result, dict):
            print(f"✓ Mixed content detected")
            print(f"  - Text DataFrame: {adaptive_result['text_df'].shape}")
            print(f"  - Tables: {len(adaptive_result['tables'])}")
        elif isinstance(adaptive_result, pd.DataFrame):
            print(f"✓ Single DataFrame returned: {adaptive_result.shape}")
            print(f"  - Source: {adaptive_result.attrs.get('source', 'unknown')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: Unified DataFrame output
    print("\n\n6. Testing parse_pdf_to_df():")
    print("-" * 60)
    try:
        unified_df = parse_pdf_to_df(file_path)
        print(f"✓ Unified DataFrame created: {unified_df.shape}")
        print(f"✓ Source: {unified_df.attrs.get('source', 'unknown')}")
        print(f"\nDataFrame preview:")
        print(unified_df.head())
        print(f"\nColumns: {list(unified_df.columns)}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()




