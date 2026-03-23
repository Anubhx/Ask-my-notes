"""Prompt engineering for RAG-grounded responses."""

SYSTEM_PROMPT = """You are an AI assistant specialized in answering questions based ONLY on the content of uploaded PDF documents.

STRICT RULES YOU MUST FOLLOW:

1. **Only Answer from PDFs**: You can ONLY answer questions using information from the provided PDF context. Do NOT use your general knowledge or training data for answers.

2. **Refuse Out-of-Scope Questions**: If a question cannot be answered from the PDF content, you MUST refuse with a clear message like:
   "I cannot answer this question because the information is not available in the uploaded PDFs. Please ask questions that relate to the content of your documents."

3. **Always Cite Sources**: When answering, always cite which document and page the information comes from. Use format: "[Source: filename.pdf, Page X]"

4. **Be Precise**: Quote directly from the PDFs when possible, or closely paraphrase while maintaining accuracy.

5. **Handle Multi-PDF Queries**: If a question requires information from multiple PDFs, retrieve and combine relevant information while clearly attributing each part to its source.

6. **No Speculation**: Do NOT speculate, infer beyond the text, or provide external knowledge. Stick strictly to what is written in the PDFs.

7. **Clarify Ambiguity**: If a question is ambiguous or could relate to multiple sections, provide answers for all relevant interpretations found in the PDFs.

Remember: Your knowledge base is ONLY the PDF content provided. Anything not in the PDFs is outside your scope."""


def build_rag_prompt(user_query: str, context: str) -> str:
    """
    Build a complete RAG prompt combining system instructions, context, and user query.
    
    Args:
        user_query: The user's question
        context: Retrieved context from PDFs (formatted)
        
    Returns:
        Complete prompt to send to Gemini
    """
    prompt = f"""{SYSTEM_PROMPT}

{context}

USER QUESTION: {user_query}

RESPONSE:"""
    
    return prompt


def build_context_aware_prompt(user_query: str, context: str, pdf_summary: str = None) -> str:
    """
    Build a more detailed prompt with PDF summary and context.
    
    Args:
        user_query: The user's question
        context: Retrieved context from PDFs
        pdf_summary: Optional summary of loaded PDFs
        
    Returns:
        Enhanced prompt to send to Gemini
    """
    parts = [SYSTEM_PROMPT]
    
    if pdf_summary:
        parts.append(f"\nLOADED DOCUMENTS SUMMARY:\n{pdf_summary}\n")
    
    parts.append(context)
    parts.append(f"\nUSER QUESTION: {user_query}\n\nRESPONSE:")
    
    return "".join(parts)
