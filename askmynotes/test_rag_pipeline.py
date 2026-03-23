"""Test script to validate RAG pipeline setup."""

import sys
from pdf_handler import process_pdfs, chunk_text
from embeddings import EmbeddingManager
from retriever import Retriever
from prompts import build_rag_prompt, SYSTEM_PROMPT

print("=" * 60)
print("🧪 ASK MY NOTES - RAG PIPELINE TEST")
print("=" * 60)

# Test 1: Embedding Manager
print("\n[Test 1] Initializing Embedding Manager...")
try:
    em = EmbeddingManager()
    print(f"✅ EmbeddingManager initialized")
    print(f"   - Model: all-MiniLM-L6-v2")
    print(f"   - Embedding dimension: {em.embedding_dim}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 2: Text chunking
print("\n[Test 2] Testing text chunking...")
try:
    sample_text = """
    This is a test document.
    It contains multiple paragraphs to test the chunking logic.
    
    Here's another paragraph with some content.
    The chunking should preserve paragraph boundaries.
    """
    chunks = chunk_text(sample_text, "test.pdf", page=1, chunk_size=100)
    print(f"✅ Text chunked successfully")
    print(f"   - Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"   - Chunk {i+1}: {len(chunk['text'])} chars")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 3: Adding chunks to embedding manager
print("\n[Test 3] Adding chunks to Embedding Manager...")
try:
    em.add_chunks(chunks)
    print(f"✅ Chunks added successfully")
    print(f"   - Total chunks stored: {em.get_chunks_count()}")
    print(f"   - Embeddings matrix shape: {em.get_embeddings_matrix().shape}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 4: Retriever initialization and search
print("\n[Test 4] Testing semantic search retriever...")
try:
    retriever = Retriever(em)
    query = "test document content"
    results = retriever.retrieve(query, top_k=2)
    print(f"✅ Retriever initialized and search works")
    print(f"   - Query: '{query}'")
    print(f"   - Results found: {len(results)}")
    for i, result in enumerate(results):
        print(f"   - Result {i+1}: Match {result['similarity_score']:.0%}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

# Test 5: RAG prompt generation
print("\n[Test 5] Testing RAG prompt generation...")
try:
    context = retriever.format_context(results)
    prompt = build_rag_prompt("What is in this document?", context)
    print(f"✅ RAG prompt generated successfully")
    print(f"   - Prompt length: {len(prompt)} characters")
    print(f"   - System prompt enforces PDF-only responses: {('only answer from' in SYSTEM_PROMPT.lower())}")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n📝 RAG Pipeline is ready to use:")
print("   1. Upload PDFs in the Streamlit sidebar")
print("   2. PDFs are extracted and chunked")
print("   3. Chunks are converted to embeddings")
print("   4. User queries are matched to relevant chunks")
print("   5. Gemini generates responses grounded in PDF content")
print("\n🚀 To start the app, run:")
print("   streamlit run app.py")
print("\n" + "=" * 60)
