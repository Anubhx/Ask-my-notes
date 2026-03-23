# 🏗️ Ask My Notes: Technical Architecture Deep Dive

**Complete technical guide for understanding, extending, and deploying the system.**

---

## System Overview

```
┌────────────────────────────────────────────────────────────────┐
│                    ASK MY NOTES ARCHITECTURE                   │
└────────────────────────────────────────────────────────────────┘

LAYER 1: DATA INPUT
│
├─ PDF Upload (Streamlit file uploader)
└─ Document Processing (PyPDF2 extraction + intelligent chunking)

LAYER 2: SEMANTIC REPRESENTATION
│
├─ Text → Embeddings (sentence-transformers, 384-dim vectors)
├─ Embedding Storage (in-memory session state)
└─ Vector Index (no external DB yet, just numpy arrays)

LAYER 3: RETRIEVAL
│
├─ Query → Embedding (same model as documents)
├─ Similarity Search (cosine similarity via scikit-learn)
└─ Top-K Selection (retrieve most relevant chunks)

LAYER 4: REASONING & GENERATION
│
├─ Context Formatting (combine retrieved chunks)
├─ Prompt Building (add system prompt + user context)
├─ LLM Inference (HTTP call to Ollama)
└─ Response Streaming (return to Streamlit UI)

LAYER 5: DISPLAY
│
├─ Answer Rendering (markdown formatting)
├─ Context Visualization (expandable retrieved chunks)
├─ Source Attribution (PDF name, page number)
└─ User Feedback (implicit: did they ask follow-up?)
```

---

## Component Deep Dives

### 1. PDF Handler (`pdf_handler.py`)

**Purpose:** Extract and intelligently chunk PDFs

**Flow:**
```
PDF File
   ↓
[PyPDF2 text extraction]
   ↓
[Page + Text + Metadata]
   ↓
[Intelligent chunking algorithm]
   ↓
[Chunks with context overlap]
```

**Key Function: `chunk_text()`**
```python
def chunk_text(text, source, page, chunk_size=400, overlap=100):
    """
    Split text into semantic chunks with overlap.
    
    Why not naive token splitting?
    - Problem: Loses context at split boundaries
    - Solution: Split on paragraph boundaries (double newlines)
    - Benefit: Preserves meaning, not just tokens
    """
```

**Chunking Strategy:**
```
Input: "Paragraph A. Paragraph B. Paragraph C."

Naive approach:
- Chunk 1: "Paragraph A. Par"
- Chunk 2: "aragraph B. Para"
- Chunk 3: "agraph C."
Problem: Boundaries cut through thoughts!

Our approach:
- Split on: "\n\n" (paragraph breaks = natural semantic boundaries)
- Add overlap: 100 tokens between chunks
- Result:
  - Chunk 1: [A] + [overlap into B]
  - Chunk 2: [B] + [overlap into C]
  - Chunk 3: [C]
Benefit: Maintains semantic coherence!
```

**Performance:**
- Extraction: ~100 pages/second
- Chunking: ~10,000 tokens/second
- Memory: O(document size)

---

### 2. Embeddings (`embeddings.py`)

**Purpose:** Convert text to semantic vectors

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
```
Input text → [384-dimensional vector]
       ↓
    Captures semantic meaning
       ↓
    Enables similarity search
```

**Why this model?**
```
Dimension    Speed     Quality   Memory
1536-dim     Slow      Great     High (OpenAI)
768-dim      Medium    Good      Medium
384-dim      Fast      Good      Low        ← Our choice
256-dim      Very fast OK        Very low
```

**Trade-off:** We chose 384-dim because:
- ✅ Fast generation (important for interactive app)
- ✅ Good quality (still captures meaning well)
- ✅ Memory efficient (fits in RAM easily)
- ✅ Free (no API costs)

**Caching Strategy:**
```python
@st.cache_resource(show_spinner="Loading embedding model...")
def load_embedding_model(model_name):
    return SentenceTransformer(model_name)
```

Why cache?
- Problem: Model loading = 5+ seconds, 400MB download
- Solution: Load once, reuse forever
- Result: First run takes 5s, subsequent runs instant

**Embedding Generation:**
```python
# Batch process for efficiency
embeddings = model.encode(texts, batch_size=32)
# Result: [len(texts), 384] ndarray
```

**Memory Usage:**
- Model: ~100MB (cached)
- 1000 chunks: ~1.5MB (1000 × 384 × 4 bytes)
- Total: ~100-200MB for typical use

---

### 3. Retriever (`retriever.py`)

**Purpose:** Find relevant chunks using semantic similarity

**Algorithm:**
```python
# 1. Encode query to same space as documents
query_embedding = model.encode(query)  # [384,]

# 2. Compute cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
similarities = cosine_similarity(
    query_embedding.reshape(1, -1),
    doc_embeddings
)  # [1, n_documents]

# 3. Find top-k
top_indices = np.argsort(similarities[0])[-k:][::-1]

# 4. Return chunks with similarity scores
return chunks[top_indices]
```

**Why Cosine Similarity?**

```
Image different vectors:

Query: [0.1, 0.9, 0.2]  (thinking about "learning")
Doc1:  [0.1, 0.85, 0.3] (talks about education)  → High similarity
Doc2:  [0.8, 0.1, 0.8]  (talks about physics)     → Low similarity

Cosine similarity: Measures angle between vectors
- Same direction = high similarity (~1.0)
- Perpendicular = low similarity (~0.5)
- Opposite = very low similarity (~-1.0)

Why not euclidean distance?
- Magnitude matters less than direction
- A long vector pointing same way should be similar
- Cosine focuses purely on direction (semantic meaning)
```

**Performance:**
- Retrieval: O(n_chunks) linear search
- Speed: Instant (<100ms) for 1000 chunks
- Scalability: Bottleneck at ~100k chunks (need vector DB)

**Top-k Selection:**
```python
# Always retrieve top-3 chunks for context
top_k = 3  # Why 3?
# - Not too few (might miss context)
# - Not too many (confuses LLM with info)
# - Sweet spot for M4 MacBook memory
```

---

### 4. Prompts (`prompts.py`)

**Purpose:** Engineer prompts to constrain LLM behavior

**System Prompt:**
```python
SYSTEM_PROMPT = """
You are an AI assistant that answers questions ONLY based on 
the provided documents. Follow these rules:

1. Only answer from the documents provided
2. If the answer isn't in documents, say "Not in documents"
3. Always cite sources (which document, which page)
4. Don't make up information or use external knowledge
5. Be concise and factual
6. If unsure, ask for clarification

Your goal: Provide accurate, grounded answers that users can trust.
"""
```

**Why strict prompts?**
```
Without prompt:
User: "What's the capital of France?"
PDF: About AI companies in Paris
LLM: "Paris is the capital of France" ✅ Correct but from training data
     (Hallucination!)

With strict prompt:
User: "What's the capital of France?"
PDF: About AI companies in Paris
LLM: "Not mentioned in the documents" ✅ Prevents hallucination
```

**Prompt Building:**
```python
def build_rag_prompt(user_query, context):
    """
    Build final prompt for LLM.
    
    Structure:
    1. System Prompt (instructions)
    2. Context (retrieved chunks)
    3. User Query
    4. Response Format
    """
    return f"""
{SYSTEM_PROMPT}

DOCUMENTS:
{context}

QUESTION: {user_query}

ANSWER:
"""
```

---

### 5. Application (`app.py`)

**Purpose:** Streamlit UI + orchestration

**Architecture:**

```python
@st.cache_resource
def init_embedding_manager():
    """Initialize once, reuse forever"""
    return EmbeddingManager()

# Session State Management
if "embedding_manager" not in st.session_state:
    st.session_state.embedding_manager = init_embedding_manager()
    st.session_state.retriever = None
    st.session_state.uploaded_pdfs = []

# Sidebar: PDF Upload
with st.sidebar:
    uploaded_files = st.file_uploader(...)
    if st.button("Process PDFs"):
        chunks = process_pdfs(uploaded_files)
        st.session_state.embedding_manager.add_chunks(chunks)
        st.session_state.retriever = Retriever(...)

# Main: Query Interface
if st.session_state.uploaded_pdfs:
    query = st.text_input("Ask Your Questions")
    if query:
        retrieved_chunks = st.session_state.retriever.retrieve(query, top_k=3)
        context = format_context(retrieved_chunks)
        prompt = build_rag_prompt(query, context)
        answer = call_ollama_api(prompt)
        st.write(answer)
        st.expander("Retrieved Context").write(retrieved_chunks)
```

**State Management:**
```
Why st.session_state?

Problem: Streamlit re-executes page on every interaction
Solution: Use session_state to persist across reruns

Session state lifecycle:
1. User uploads PDF
2. Page reruns, but session_state.pdf_chunks persists
3. User asks question
4. Page reruns, but session_state.retriever persists
5. ...no reprocessing, instant response
```

---

### 6. LLM Integration (Ollama API)

**Connection:**

```python
def call_ollama_api(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,  # Low = factual
            "top_p": 0.9,
            "timeout": 120,
        }
    )
    return response.json()["response"]
```

**Why these parameters?**
```
Parameter    Value   Why?
────────────────────────────────────────
model        mistral Fast (4GB), capable enough
stream       False   Simpler for Streamlit
temperature  0.3     Low = deterministic, factual (prevent hallucination)
top_p        0.9     High = diverse but not random
timeout      120s    Inference can be slow on CPU
```

**Inference Flow:**
```
Prompt (500 tokens) → Ollama Server → Mistral Model
   ↓
[Token generation happens ~100ms/token on M4]
   ↓
~5-10 second response time
   ↓
Return to Streamlit → Display to user
```

---

## Data Flow Diagram

```
 ┌─────────────┐
 │  PDF Upload │
 └──────┬──────┘
        │
        ├─ Extract text (PyPDF2)
        │  Extract metadata (page #, filename)
        │
        ├─ Chunk text (paragraph boundaries)
        │  Size: ~400 tokens
        │  Overlap: 100 tokens
        │
        └─ Store in SessionState
           chunks = [
               {text: "...", source: "file.pdf", page: 1},
               {text: "...", source: "file.pdf", page: 1},
               ...
           ]

 ┌──────────────────────┐
 │ Embedding Generation │
 └──────────┬───────────┘
            │
            ├─ Load model (sentence-transformers)
            │  Cached: no reload on each interaction
            │
            ├─ Encode all chunks
            │  Input:  [n_chunks, variable_length]
            │  Output: [n_chunks, 384]
            │  (384-dim vectors)
            │
            └─ Store embeddings in SessionState
               embeddings = np.array([
                   [0.1, 0.2, ..., 0.05],  # chunk 1
                   [0.3, 0.1, ..., 0.12],  # chunk 2
                   ...
               ])

 ┌──────────────────┐
 │ User Asks Query  │
 └──────────┬───────┘
            │
            ├─ Encode query
            │  Input:  query_string
            │  Output: [384] vector
            │
            ├─ Compute similarity (cosine)
            │  sim = cosine_similarity(query_vec, all_chunk_vecs)
            │  Result: similarity score for each chunk
            │
            ├─ Select top-3 chunks
            │  chunks_to_use = chunks.iloc[top_3_indices]
            │
            └─ Format context
               context_text = "CHUNK 1:\n..." + \
                              "CHUNK 2:\n..." + \
                              "CHUNK 3:\n..."

 ┌──────────────────────┐
 │ Prompt Engineering   │
 └──────────┬───────────┘
            │
            ├─ Combine:
            │  1. System prompt (instructions)
            │  2. Retrieved context (facts)
            │  3. User question
            │
            └─ Final prompt:
               "You are an AI that..."
               "QUESTION: [system prompt]"
               "DOCUMENTS:\n[context]"
               "QUESTION: [user_query]"
               "ANSWER:"

 ┌──────────────────────┐
 │ LLM Inference        │
 └──────────┬───────────┘
            │
            ├─ POST to http://localhost:11434/api/generate
            │  Body: {model, prompt, temperature, etc.}
            │
            ├─ Mistral 7B generates response
            │  Token by token (~5-10 seconds)
            │
            └─ Return answer text

 ┌──────────────────────┐
 │ Display Results      │
 └──────────┬───────────┘
            │
            ├─ Show answer (markdown)
            │
            ├─ Allow expand "Retrieved Context"
            │  Show which chunks were used
            │  Show similarity scores
            │  Show source PDFs
            │
            └─ User reads and learns
```

---

## Performance Analysis

### Latency Breakdown (M4 MacBook)

```
Task                      Time      Notes
─────────────────────────────────────────────
PDF upload                0.5s      Network dependent
Text extraction (10p)     0.2s      PyPDF2
Chunking (1000 tokens)    0.1s      Text splitting
Embedding generation      2-3s      First run loads model
                          <0.1s     Subsequent (cached)
─────────────────────────────────────────────
Query submitted           <0.1s     
Query encoding            0.1s      
Similarity search         <0.1s     Cosine distance
─────────────────────────────────────────────
Ollama inference          5-10s     Most time spent here
─────────────────────────────────────────────
TOTAL (first PDF)         ~8-13s    
TOTAL (cached)            ~6-11s    After first PDF

Most queries: 6-11 seconds (mostly LLM generation)
```

### Memory Usage

```
Component              Typical Size
────────────────────────────────
Embedding model (cached)   100-200MB
Query embeddings          ~1.5MB per 1000 chunks
Original PDFs             Variable (upload limited 200MB)
Mistral 7B model (Ollama)  4GB (separate process)
─────────────────────────
Total app memory           ~150-300MB (excluding Ollama)
Total system             ~4.3-4.5GB when running
```

### Scalability Bottlenecks

```
Chunks      Linear Search   Recommended Solution
──────────────────────────────────────────────
100        Instant (<10ms)   Current (numpy)
1,000      Instant (<50ms)   Current (numpy)
10,000     Slow (500ms+)     Switch to vector DB
100,000    Very slow (5s+)   Vector DB mandatory
1,000,000  Unusable          Distributed databases

When to switch from numpy to vector DB:
- If you have >10k chunks
- If response time becomes >1s
- If you want to filter by metadata
- If you need multi-user support

Vector DB options:
- Pinecone (cloud, easiest)
- Weaviate (self-hosted)
- Milvus (open source)
- Qdrant (fast, simple)
```

---

## Extension Ideas

### 1. Chat Memory
**Complexity:** Medium

```python
# Store conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# On each query:
st.session_state.conversation.append({
    "role": "user",
    "content": query
})
st.session_state.conversation.append({
    "role": "assistant", 
    "content": answer
})

# Use for context-aware responses
# Include last 5 exchanges in prompt for continuity
```

### 2. Multiple Embedding Models
**Complexity:** Easy

```python
embedding_model = st.selectbox(
    "Choose embedding model",
    ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "bge-base-en-v1.5"]
)

# Switch between models based on:
# - Quality vs Speed trade-off
# - Domain-specific models (medical, legal, etc.)
```

### 3. Vector Database Integration
**Complexity:** Hard

```python
from pinecone import Pinecone

# Instead of numpy array:
pc = Pinecone(api_key="...")
index = pc.Index("ask-my-notes")

# Add embeddings with metadata
index.upsert(vectors=[{
    "id": chunk_id,
    "values": embedding,
    "metadata": {
        "source": "file.pdf",
        "page": 1,
        "text": chunk_text
    }
}])

# Retrieve with filter
results = index.query(query_vector, filter=...)
```

### 4. Streaming Responses
**Complexity:** Medium

```python
# For long-running inference, stream tokens as they arrive
# Ollama supports streaming natively

response = requests.post(
    "http://localhost:11434/api/generate",
    json={...},
    stream=True  # ← Enable streaming
)

st.write_stream(response.iter_lines())  # Stream to UI
```

### 5. Multi-LLM Support
**Complexity:** Easy

```python
selected_model = st.selectbox(
    "Choose model",
    ["mistral", "neural-chat", "llama2"]
)

# Change behavior based on model
if selected_model == "neural-chat":
    temperature = 0.7  # Chat optimized
else:
    temperature = 0.3  # Factual optimized

response = call_ollama_api(prompt, model=selected_model)
```

---

## Deployment Options

### Option 1: Local (Current)
- Run on your MacBook
- Ollama + Streamlit
- Perfect for demos, learning

### Option 2: Docker (Recommended)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

```bash
docker build -t askmynotes .
docker run -p 8501:8501 askmynotes
```

### Option 3: Cloud with Local Ollama
- Run Streamlit on cloud (AWS, GCP, Heroku)
- Keep Ollama local (or use managed service)
- Users connect to cloud UI, local inference handles generation

### Option 4: Fully Cloud
- Deploy Ollama on cloud GPU (expensive)
- Streamlit on cloud
- Full cloud solution (easier but pricier)

---

## Testing Strategy

### Unit Tests
```python
def test_embedding_generation():
    model = load_embedding_model()
    embeddings = model.encode(["test document"])
    assert embeddings.shape == (1, 384)
    assert -1 <= embeddings[0][0] <= 1  # Normalized

def test_chunking():
    text = "Para A.\n\nPara B.\n\nPara C."
    chunks = chunk_text(text)
    assert len(chunks) == 3
    assert chunks[0]["text"] contains "Para A"
```

### Integration Tests
```python
def test_rag_pipeline():
    # Upload PDF
    # Extract chunks
    # Generate embeddings
    # Retrieve chunks
    # Generate answer
    # Check answer is grounded in document
```

### Manual Testing
```
✓ Upload PDF
✓ Process PDFs
✓ Ask simple question (in document)
✓ Ask complex question (needs reasoning)
✓ Ask out-of-scope question (should refuse)
✓ Multiple PDFs (should search all)
✓ Large PDF (performance check)
```

---

## Conclusion

**Ask My Notes demonstrates:**
- ✅ End-to-end RAG system
- ✅ Production-quality code
- ✅ Thoughtful design decisions
- ✅ Scalability considerations
- ✅ Clear technical thinking

**This architecture is foundation for:**
- Multi-agent systems
- Knowledge graph integration
- Agentic reasoning loops
- Enterprise AI applications

---

**Now you understand the full system. Ready to extend it? 🚀**
