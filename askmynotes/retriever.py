"""Semantic search and retrieval for RAG pipeline."""

from typing import List, Dict, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class Retriever:
    """Retrieve relevant chunks from PDF documents using semantic similarity."""
    
    def __init__(self, embedding_manager):
        """
        Initialize the retriever.
        
        Args:
            embedding_manager: EmbeddingManager instance with encoded chunks
        """
        self.embedding_manager = embedding_manager
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks for a query.
        
        Args:
            query: User query string
            top_k: Number of top results to return (default: 3)
            
        Returns:
            List of relevant chunks with similarity scores, sorted by relevance
        """
        if self.embedding_manager.get_chunks_count() == 0:
            return []
        
        # Encode the query
        query_embedding = self.embedding_manager.model.encode([query], convert_to_numpy=True)
        
        # Calculate cosine similarity between query and all chunks
        embeddings_matrix = self.embedding_manager.get_embeddings_matrix()
        similarities = cosine_similarity(query_embedding, embeddings_matrix)[0]
        
        # Get top-k indices
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build result list
        results = []
        for idx in top_k_indices:
            if similarities[idx] > 0.0:  # Only include if there's some similarity
                chunk = self.embedding_manager.get_chunk(int(idx))
                if chunk:
                    results.append({
                        **chunk,
                        "similarity_score": float(similarities[idx])
                    })
        
        return results
    
    def format_context(self, retrieved_chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into a context string for the LLM.
        
        Args:
            retrieved_chunks: List of retrieved chunk dicts
            
        Returns:
            Formatted context string with source attribution
        """
        if not retrieved_chunks:
            return "No relevant context found in the uploaded PDFs."
        
        context_parts = []
        context_parts.append("=== CONTEXT FROM UPLOADED PDFs ===\n")
        
        for i, chunk in enumerate(retrieved_chunks, 1):
            source = chunk.get("source", "Unknown")
            page = chunk.get("page", "?")
            text = chunk.get("text", "")
            score = chunk.get("similarity_score", 0)
            
            context_parts.append(f"[Source {i}]: {source}, Page {page} (Relevance: {score:.2%})")
            context_parts.append(f"{text}\n")
            context_parts.append("-" * 50 + "\n")
        
        context_parts.append("=== END CONTEXT ===\n")
        return "".join(context_parts)
