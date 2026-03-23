"""Generate and manage embeddings for RAG retrieval using sentence-transformers."""

from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import streamlit as st


@st.cache_resource(show_spinner=True)
def load_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    """Cache the embedding model to avoid reloading on every Streamlit rerun."""
    return SentenceTransformer(model_name, trust_remote_code=True)


class EmbeddingManager:
    """Manage embeddings for PDF chunks using free sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding manager.
        
        Args:
            model_name: Name of the sentence-transformers model to use
                       (all-MiniLM-L6-v2 is lightweight and free)
        """
        self.model = load_embedding_model(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.chunks = []
        self.embeddings = np.array([])
    
    def add_chunks(self, chunks: List[Dict]) -> None:
        """
        Add text chunks and generate their embeddings.
        
        Args:
            chunks: List of dicts with 'text', 'source', 'page' keys
        """
        if not chunks:
            return
        
        self.chunks.extend(chunks)
        
        # Extract text and generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        new_embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        # Append to existing embeddings
        if len(self.embeddings) == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
    
    def clear(self) -> None:
        """Clear all stored chunks and embeddings."""
        self.chunks = []
        self.embeddings = np.array([])
    
    def get_chunks_count(self) -> int:
        """Get total number of chunks stored."""
        return len(self.chunks)
    
    def get_chunk(self, idx: int) -> Dict:
        """Get a chunk by index."""
        if 0 <= idx < len(self.chunks):
            return self.chunks[idx]
        return None
    
    def get_embeddings_matrix(self) -> np.ndarray:
        """Get the embeddings matrix."""
        return self.embeddings
