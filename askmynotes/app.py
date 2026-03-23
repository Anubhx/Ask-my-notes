"""Ask My Notes - RAG-based Q&A app using Ollama and PDF documents."""

import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
from pdf_handler import process_pdfs
from embeddings import EmbeddingManager
from retriever import Retriever
from prompts import build_rag_prompt

# Load environment variables
load_dotenv()

# Ollama configuration
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral"

# Page configuration
st.set_page_config(
    page_title="Ask My Notes",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Ask My Notes")
st.markdown("""
**Smart Q&A from your PDFs using Local AI (Ollama) & RAG**

Upload PDF documents and ask questions that will be answered *only* from their content.
Works completely offline with no API keys needed!
""")

# Initialize session state with cached embedding manager
@st.cache_resource(show_spinner="Loading embedding model...")
def init_embedding_manager():
    """Initialize embedding manager once and cache it."""
    return EmbeddingManager()


def check_ollama_running() -> bool:
    """
    Check if Ollama server is running on localhost:11434
    
    Returns:
        True if Ollama is running, False otherwise
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False


def call_ollama_api(prompt: str) -> str:
    """
    Call Ollama API for local LLM inference.
    
    Args:
        prompt: The prompt to send to Ollama
    
    Returns:
        The response text from Ollama
    """
    if not check_ollama_running():
        raise Exception(
            f"❌ Ollama is not running!\n\n"
            f"Please start Ollama with: ollama serve\n\n"
            f"Then pull the model: ollama pull {OLLAMA_MODEL}\n\n"
            f"Keep the Ollama server running while using this app."
        )
    
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,  # Low temperature for factual responses
            },
            timeout=120  # 2 minute timeout for inference
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response from model")
    except requests.Timeout:
        raise Exception(
            f"⏱️ Ollama inference timed out (>120s).\n\n"
            f"This usually means the model is still loading or your hardware is slow.\n"
            f"Try a smaller model: ollama pull mistral"
        )
    except requests.ConnectionError:
        raise Exception(
            f"❌ Cannot connect to Ollama at {OLLAMA_API_URL}\n\n"
            f"Make sure Ollama server is running: ollama serve"
        )
    except Exception as e:
        raise Exception(f"Ollama API error: {str(e)}")

if "embedding_manager" not in st.session_state:
    st.session_state.embedding_manager = init_embedding_manager()
    st.session_state.retriever = None
    st.session_state.uploaded_pdfs = []
    st.session_state.pdf_chunks = []

# Sidebar for PDF upload
with st.sidebar:
    st.header("📄 PDF Upload")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        key="pdf_uploader"
    )
    
    if uploaded_files:
        if st.button("Process PDFs", use_container_width=True):
            with st.spinner("Processing PDFs..."):
                try:
                    # Clear previous data
                    st.session_state.embedding_manager.clear()
                    st.session_state.uploaded_pdfs = []
                    st.session_state.pdf_chunks = []
                    
                    # Process PDFs
                    chunks = process_pdfs(uploaded_files)
                    
                    if chunks:
                        # Add chunks to embedding manager
                        st.session_state.embedding_manager.add_chunks(chunks)
                        st.session_state.pdf_chunks = chunks
                        st.session_state.retriever = Retriever(st.session_state.embedding_manager)
                        st.session_state.uploaded_pdfs = [f.name for f in uploaded_files]
                        
                        st.success(f"✅ Processed {len(uploaded_files)} PDF(s) into {len(chunks)} chunks!")
                    else:
                        st.error("❌ No text could be extracted from the PDFs")
                
                except Exception as e:
                    st.error(f"Error processing PDFs: {str(e)}")
    
    # Display loaded PDFs
    if st.session_state.uploaded_pdfs:
        st.divider()
        st.subheader("Loaded PDFs")
        for pdf_name in st.session_state.uploaded_pdfs:
            st.write(f"✓ {pdf_name}")
        
        st.metric("Total Chunks", st.session_state.embedding_manager.get_chunks_count())
        
        if st.button("Clear PDFs", type="secondary", use_container_width=True):
            st.session_state.embedding_manager.clear()
            st.session_state.uploaded_pdfs = []
            st.session_state.pdf_chunks = []
            st.session_state.retriever = None
            st.rerun()

# Main query interface
if not st.session_state.uploaded_pdfs:
    st.info("👈 Please upload and process PDF files from the sidebar to get started.")
else:
    # Query section
    st.header("❓ Ask Your Questions")
    
    query = st.text_input(
        "What would you like to know about your documents?",
        placeholder="Type your question here...",
        label_visibility="collapsed"
    )
    
    if query:
        with st.spinner("Searching documents and generating response..."):
            try:
                # Retrieve relevant chunks
                retrieved_chunks = st.session_state.retriever.retrieve(query, top_k=3)
                
                if not retrieved_chunks:
                    st.warning("⚠️ No relevant information found in your PDFs for this query.")
                else:
                    # Format context
                    context = st.session_state.retriever.format_context(retrieved_chunks)
                    
                    # Build prompt
                    full_prompt = build_rag_prompt(query, context)
                    
                    # Call Ollama API
                    try:
                        response_text = call_ollama_api(full_prompt)
                        
                        # Display retrieval context (expandable)
                        with st.expander("📖 Retrieved Context (click to expand)"):
                            for i, chunk in enumerate(retrieved_chunks, 1):
                                st.markdown(f"**[{i}] {chunk['source']} • Page {chunk['page']} (Match: {chunk['similarity_score']:.0%})**")
                                st.text(chunk['text'])
                                st.divider()
                        
                        # Display answer
                        st.subheader("Answer")
                        st.markdown(response_text)
                        
                    except Exception as e:
                        st.error(str(e))
            
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")

# Footer
st.divider()
st.caption("📝 **Ask My Notes** — Grounded Q&A from your PDF documents using RAG and local Ollama AI")
 

