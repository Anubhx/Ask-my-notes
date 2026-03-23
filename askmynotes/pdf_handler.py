"""Handle PDF upload and text extraction for RAG pipeline."""

import io
from typing import List, Dict, Tuple
import PyPDF2


def extract_text_from_pdf(pdf_bytes: bytes, filename: str) -> Tuple[str, List[Dict]]:
    """
    Extract text and metadata from a PDF file.
    
    Args:
        pdf_bytes: PDF file content as bytes
        filename: Name of the PDF file
        
    Returns:
        Tuple of (full_text, chunks_with_metadata)
        where chunks_with_metadata contains dicts with 'text', 'page', 'source'
    """
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        full_text = ""
        chunks_with_metadata = []
        
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            page_text = page.extract_text()
            full_text += page_text + "\n"
            
            # Store page-level metadata
            if page_text.strip():
                chunks_with_metadata.append({
                    "text": page_text,
                    "page": page_num,
                    "source": filename
                })
        
        if not full_text.strip():
            return "", []
            
        return full_text, chunks_with_metadata
    
    except Exception as e:
        raise ValueError(f"Error extracting text from {filename}: {str(e)}")


def chunk_text(text: str, source: str, page: int = None, chunk_size: int = 400, overlap: int = 100) -> List[Dict]:
    """
    Split text into overlapping chunks, preserving paragraph structure.
    
    Args:
        text: Text to chunk
        source: Source filename
        page: Page number (optional)
        chunk_size: Size of each chunk (characters)
        overlap: Overlap between chunks (characters)
        
    Returns:
        List of dicts with 'text', 'source', 'page'
    """
    # Split by paragraphs first (double newline)
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If adding this paragraph would exceed chunk_size, save current chunk and start new one
        if len(current_chunk) + len(para) + 2 > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "source": source,
                "page": page
            })
            # Create overlap by keeping last part of previous chunk
            current_chunk = current_chunk[-overlap:] + "\n\n" + para
        else:
            current_chunk += "\n\n" + para if current_chunk else para
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "source": source,
            "page": page
        })
    
    return chunks


def process_pdfs(uploaded_files: List) -> List[Dict]:
    """
    Process multiple uploaded PDF files and return chunks with metadata.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects
        
    Returns:
        List of chunk dicts with 'text', 'page', 'source' keys
    """
    all_chunks = []
    
    for uploaded_file in uploaded_files:
        try:
            pdf_bytes = uploaded_file.read()
            filename = uploaded_file.name
            
            # Extract text from PDF
            full_text, page_chunks = extract_text_from_pdf(pdf_bytes, filename)
            
            if not full_text.strip():
                continue
            
            # Further chunk the text for better retrieval
            for page_chunk in page_chunks:
                fine_chunks = chunk_text(
                    page_chunk["text"],
                    source=filename,
                    page=page_chunk["page"]
                )
                all_chunks.extend(fine_chunks)
        
        except Exception as e:
            print(f"Error processing {uploaded_file.name}: {str(e)}")
            continue
    
    return all_chunks
