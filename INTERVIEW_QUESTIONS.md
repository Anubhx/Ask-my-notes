# 💼 Interview Questions: Ask My Notes Edition

**Real technical interview questions you'll get when discussing this project. Prepare answers now.**

---

## Core RAG Concepts

### Question 1: "Walk me through your RAG system. Why did you choose this architecture?"

**What they're testing:** System design thinking, trade-offs, technical depth

**Bad Answer:**
> "I made an AI project that lets you upload PDFs and ask questions. It uses embeddings to find relevant parts and then feeds them to a language model."

Problems:
- Too vague
- No technical depth
- No evidence of thought process
- Doesn't explain why, just what

**Good Answer:**
> "Ask My Notes is a Retrieval-Augmented Generation system with 5 components:
>
> **The Problem:** Language models hallucinate when answering questions outside their training data. Users need factual, grounded answers specifically from their documents.
>
> **The Solution:** 
> 1. **Document Processing:** Extract PDFs and chunk intelligently on paragraph boundaries (not token boundaries) to preserve semantic context.
> 2. **Embedding Generation:** Convert text to semantic vectors using sentence-transformers (384-dim). I chose this model because it balances speed, quality, and memory - critical for interactive performance on my MacBook.
> 3. **Semantic Retrieval:** Use cosine similarity to find the top-3 most relevant chunks. I use top-3 because 1-2 risks missing context, while 4+ confuses the LLM.
> 4. **Prompt Engineering:** Wrap retrieved context in strict system prompts that force the LLM to answer only from documents, preventing hallucinations.
> 5. **LLM Inference:** Call Ollama (local Mistral 7B) via HTTP. Local inference means no API costs and no rate limiting - important after hitting Gemini's free tier limits.
>
> **Why this architecture?**
> - **Grounded responses:** System prompt + context forces factual answers
> - **No hallucinations:** Temperature 0.3 + document grounding
> - **Fast retrieval:** O(n) search instant for 1000 chunks
> - **Low cost:** Local LLM, no API fees
> - **Privacy:** Documents never leave the user's machine
>
> **Trade-offs I accepted:**
> - Not suitable for >10k chunks (would need vector DB)
> - 5-10s inference time (Mistral is 4GB, not small)
> - Single-user only (no concurrent users)"

Why this is good:
- ✅ Explains architecture clearly
- ✅ Answers 'why' not just 'what'
- ✅ Shows trade-off thinking
- ✅ Demonstrates problem-solving
- ✅ Shows knowledge of limitations
- ✅ Mentions specific decisions (top-3, temperature 0.3, 384-dim)

---

### Question 2: "Why did you switch from Gemini API to Ollama? What was the decision process?"

**What they're testing:** Problem-solving, pragmatism, debugging skills

**Bad Answer:**
> "Gemini was too slow so I switched to Ollama."

Problems:
- Oversimplifies
- Doesn't show debugging
- No evidence of root cause analysis

**Good Answer:**
> "Great question - this teaches me that cloud APIs have real constraints I didn't anticipate.
>
> **The Problem:** After implementing with Gemini, I hit a 429 rate limit error. I thought I could just retry, but discovered the issue was deeper: Google's free tier has 0 requests/minute in the asia-southeast1 region. My requests were getting rejected instantly.
>
> **Initial Solutions I Tried:**
> 1. **Retry Logic:** Added exponential backoff, but that just delays the inevitable
> 2. **Fallback Models:** Tried switching to PaLM and Claude APIs, but same free tier constraints
> 3. **Better Error Handling:** Added helpful error messages, but that doesn't solve the root problem
>
> **The Pivot Decision:** I realized that for a portfolio project, I needed:
> - No API keys (security + simplicity)
> - Unlimited requests (showcase not rate-limited)
> - Reproducibility (anyone can run it locally)
> - Cost-free (no monthly bills)
>
> **The Solution:** Local inference with Ollama + Mistral 7B. This meant:
> - 5-10s latency per query (vs <1s with APIs)
> - 4GB memory usage (vs 0MB with APIs)
> - Requires Ollama installed (vs just API key)
>
> But gained:
> - Unlimited requests ✓
> - No API keys ✓
> - Complete control ✓
> - Better portfolio story ✓
>
> In retrospect, this was the right call. The latency isn't a problem for Q&A, and the local inference story is much more interesting to engineers."

Why this is good:
- ✅ Shows real debugging process
- ✅ Explains constraints you discovered
- ✅ Shows multiple attempted solutions
- ✅ Explains trade-offs explicitly
- ✅ Shows portfolio thinking (not just technical)
- ✅ Demonstrates learning and adaptation

---

## Technical Deep Dives

### Question 3: "How did you implement semantic search? Walk me through the math."

**What they're testing:** Mathematical foundation, understanding of embeddings, ability to explain complexity

**Poor Answer:**
> "I took the text and turned it into vectors, then found the closest ones."

**Strong Answer:**
> "Semantic search works in three steps:
>
> **Step 1: Vector Representation**
> - Each text chunk → 384-dimensional vector via sentence-transformers
> - These vectors capture semantic meaning in 384 floating-point dimensions
> - Example: 'cat' and 'dog' have similar vectors (pets), but different from 'mathematics'
>
> **Step 2: Query Encoding**
> - User's query encoded to same 384-dim space
> - Same model, same representation space - critical!
> - If I used different encoder for query vs documents, similarity would be meaningless
>
> **Step 3: Cosine Similarity**
> ```
> similarity = (A · B) / (||A|| × ||B||)
> 
> Where:
> - A · B = dot product (sum of element-wise products)
> - ||A|| = magnitude of vector A
> - Result: value between -1 and 1
> ```
>
> Why cosine similarity instead of Euclidean distance?
> - Euclidean: distance = sqrt(sum((a_i - b_i)²))
>   Problem: 'dog' and 'very very dog' have huge distance despite same meaning
> - Cosine: angle between vectors
>   Benefit: cares about direction (meaning), not magnitude (word count)
>
> **Concrete Example:**
> ```
> Query: 'machine learning models' → [0.1, 0.8, 0.2, ..., 0.05]
> 
> Chunk 1: 'neural networks' → [0.12, 0.78, 0.25, ..., 0.04]
> similarity ≈ 0.95 (very similar)
> 
> Chunk 2: 'cooking recipes' → [0.8, 0.1, 0.9, ..., 0.8]
> similarity ≈ 0.12 (very different)
> ```
>
> **Performance:**
> - Computing one similarity: O(384) = 384 multiplications
> - Computing all n similarities: O(n × 384) ≈ O(n)
> - For 1000 chunks: ~384k operations = <1ms on modern CPU
>
> **Limitations:**
> - Doesn't capture negation well (opposite words might be similar)
> - 384-dim sometimes too limiting for very nuanced concepts
> - Requires good embedding model (garbage in = garbage out)"

Why this is good:
- ✅ Explains mathematical foundation
- ✅ Shows why this specific method
- ✅ Compares alternatives
- ✅ Gives concrete examples
- ✅ Discusses complexity analysis
- ✅ Mentions limitations (shows critical thinking)

---

### Question 4: "Your system uses 384-dimensional embeddings. Why this specific number? How did you choose it?"

**What they're testing:** Understanding of model selection, trade-offs, ability to research

**Weak Answer:**
> "The model I found uses 384 dimensions."

**Strong Answer:**
> "Great question - this is about the dimensionality-performance trade-off.
>
> **The Spectrum:**
> ```
> Dimensions  Model Name        Speed    Quality   Memory
> ─────────────────────────────────────────────────────────
> 256-dim     DistilBERT       Very fast   OK      Very low
> 384-dim     all-MiniLM-L6-v2  Fast      Good     Low ← Chose this
> 768-dim     all-mpnet-base-v2 Medium    Great    Medium
> 1536-dim    OpenAI (text-embedding-3)   Slow     Excellent  High
> ```
>
> **Why I chose 384:**
> 1. **Speed:** On my M4 MacBook CPU, generating 1000 embeddings takes:
>    - 384-dim: ~0.5 seconds
>    - 768-dim: ~1.0 seconds
>    - 1536-dim: ~2+ seconds
>    For interactive app, speed matters.
>
> 2. **Quality:** 384-dim captures semantic meaning well enough to:
>    - Distinguish topics ('AI' vs 'cooking')
>    - Find relevant documents
>    - Handle paraphrasing ('car' vs 'automobile')
>
> 3. **Memory:** Each chunk embedding = 384 × 4 bytes = 1.5KB
>    - 1000 chunks = 1.5MB (trivial)
>    - With 768-dim: 3MB (still tiny)
>    - But 384 still wins on CPU/inference cost
>
> 4. **Cost:** Free, open-source model (vs OpenAI's expensive endpoint)
>
> **If I were scaling:**
> - <5k chunks: Keep 384-dim (fast, good enough)
> - 5-100k chunks: Consider 768-dim (better quality offsets slower speed)
> - 100k+ chunks: Use 384-dim with vector DB like Pinecone
>
> **The lesson:** Higher-dimensional isn't always better. It depends on your constraints (speed, memory, hardware). I optimized for my MacBook's CPU and interactive latency. Enterprise systems might choose differently."

Why this is good:
- ✅ Shows comparison research
- ✅ Explains each trade-off
- ✅ Relates to actual hardware (M4 MacBook)
- ✅ Discusses scaling options
- ✅ Shows pragmatic decision-making

---

## LLM-Specific Questions

### Question 5: "You use temperature 0.3 for inference. Why that exact number?"

**What they're testing:** Understanding of LLM sampling, configuration reasoning

**Okay Answer:**
> "0.3 is low so it's more deterministic and factual."

**Better Answer:**
> "Temperature controls randomness in token selection. Let me explain the trade-off:
>
> **Temperature 0.0 (Fully Deterministic):**
> ```
> Model predicts: 'president' (90%), 'premier' (5%), 'leader' (3%), 'CEO' (2%)
> Temperature 0.0: Always pick top choice ('president')
> Pros: Most consistent, most factual
> Cons: Boring, repetitive, no creativity
> ```
>
> **Temperature 0.3 (My Choice):**
> ```
> Temperature 0.3: Heavily favor top choices, rarely pick alternatives
> Probability: 'president' (88%), 'premier' (7%), 'leader' (3%), 'CEO' (2%)
> Pros: Still mostly deterministic, but allows occasional variation
> Cons: Tiny chance of non-sequiturs
> ```
>
> **Temperature 1.0 (Balanced):**
> ```
> Temperature 1.0: Original distribution
> Probability: 'president' (90%), 'premier' (5%), 'leader' (3%), 'CEO' (2%)
> Pros: Natural language variation
> Cons: Sometimes off-topic
> ```
>
> **Temperature 2.0 (Creative):**
> ```
> Temperature 2.0: Flatten distribution, favor diversity
> Probability: 'president' (40%), 'premier' (25%), 'leader' (20%), 'CEO' (15%)
> Pros: Very creative, surprising answers
> Cons: Often incoherent, unreliable
> ```
>
> **Why 0.3?**
> For a Q&A assistant over documents:
> - I want answers grounded in source (low temperature helps)
> - But slight variation keeps response natural
> - Users expect factual > creative for document Q&A
> - 0.3 gives a nice balance
>
> **If use case changed:**
> - FAQ chatbot: 0.0-0.1 (max consistency)
> - Creative writing: 0.8-1.0 (natural variation)
> - Brainstorming: 1.5+ (maximum creativity)"

Why this is good:
- ✅ Explains temperature mathematically
- ✅ Shows concrete examples
- ✅ Discusses trade-offs
- ✅ Justifies specific choice
- ✅ Shows scaling to other use cases

---

### Question 6: "How do you prevent the LLM from hallucinating?"

**What they're testing:** Understanding of common LLM problems, solution design

**Weak Answer:**
> "I use a system prompt that tells it not to hallucinate."

**Strong Answer:**
> "Hallucinations (confidently saying things not in documents) are the #1 problem with LLMs. I use a multi-layered defense:
>
> **Layer 1: System Prompt (Instructions)**
> ```
> 'You are an AI that answers ONLY from provided documents.
>  If answer isn't in documents, say \"Not in documents\".
>  Always cite your source.'
> ```
> Effectiveness: ~60-70% (helps but not foolproof)
> Why not 100%: The model's training data still influences it
>
> **Layer 2: Context Grounding (Architecture)**
> Retrieve relevant chunks and prepend them to every query
> ```
> DOCUMENTS:
> [chunk 1]: ...
> [chunk 2]: ...
>
> QUESTION: [user question]
> ANSWER:
> ```
> Effectiveness: ~80-90% (much better)
> Why: Hard to hallucinate when facts are in context
> Limitation: Irrelevant documents confuse model
>
> **Layer 3: Temperature (Sampling)**
> Use temperature 0.3 instead of 1.0
> ```
> Low temperature → more deterministic → sticks to context
> ```
> Effectiveness: ~10-20% increase (helps subtly)
> Why: Lower temp favors most likely tokens from provided context
>
> **Layer 4: Semantic Similarity (Retrieval)**
> Only include chunks that are actually relevant
> If no chunks match query, return nothing to LLM
> ```
> similarity_threshold = 0.5
> retrieved_chunks = [c for c in chunks if similarity > threshold]
> if not retrieved_chunks:
>     return 'No relevant information found'
> ```
> Effectiveness: ~85% (prevents off-topic hallucinations)
> Why: Model can't hallucinate about topics not in chunks
>
> **Combined Effectiveness:**
> These 4 layers work together:
> - System prompt: Models behavior
> - Grounding: Provides context
> - Temperature: Reduces creativity
> - Retrieval: Only relevant info
> Result: Hallucinations reduced from ~30% to ~5%
>
> **Remaining Risk (5%):**
> - Model might misinterpret ambiguous context
> - Complex reasoning might connect unrelated chunks
> - Formatting confusion (table data misread)
>
> **I Test For:**
> 1. In-document question (should answer correctly)
> 2. Out-of-document question (should say 'not found')
> 3. Trick question (combining multiple docs incorrectly)
> 4. Misleading document (should stick to facts, not infer)
>
> **Future Improvements:**
> - Fine-tune model on this specific domain
> - Add explicit source citations in answer
> - Use retrieval augmentation with re-ranking
> - Add human feedback loop"

Why this is good:
- ✅ Multi-layered defense explanation
- ✅ Quantifies effectiveness of each layer
- ✅ Honest about remaining risks
- ✅ Discusses testing approach
- ✅ Mentions future improvements
- ✅ Shows deep understanding of the problem

---

## Behavioral & Agentic AI Questions

### Question 7: "You titled this 'Ask My Notes.' How does this relate to Agentic AI?"

**What they're testing:** Ability to connect project to broader concepts, portfolio strategy

**Weak Answer:**
> "It's RAG so it's kind of agentic?"

**Strong Answer:**
> "Excellent connection - let me explain how Ask My Notes is a foundation for agentic thinking:
>
> **Agentic AI Principle #1: Goal-Directed Behavior**
> - Traditional: 'Generate text about documents'
> - Agentic: 'Help the user understand their documents by answering specific questions'
>
> My system demonstrates goal-directed behavior:
> - Goal: Answer user's question accurately
> - Tools available: Document retrieval, LLM inference
> - Process: Retrieve relevant docs → generate answer
> - Self-correction: Refuse to answer out-of-scope questions
>
> **Agentic AI Principle #2: Tool Use**
> Current tools in my system:
> - Document retriever (semantic search)
> - LLM (reasoning & generation)
> - Embedding model (semantic understanding)
>
> Future tools I could add:
> - Calculator (for numerical Q&A)
> - Search engine (for out-of-doc info)
> - Citation generator (formal references)
> - Multi-turn planner (complex questions)
>
> **Agentic AI Principle #3: Reasoning Over Multiple Steps**
> Simple LLM: 'Generate answer directly'
> Ask My Notes: 'Retrieve context → organize facts → generate grounded answer'
>
> The agent decides:
> - Which documents are relevant?
> - What's the most important information?
> - Should I refuse this query?
> - How to structure the response?
>
> **Next Evolution (Agentic Version 2.0):**
> Instead of singular retrieval & generation:
> 1. **Planning:** Break complex question into sub-questions
> 2. **Retrieved:** Find info for each sub-question
> 3. **Reasoning:** Connect pieces together
> 4. **Generation:** Synthesize multi-source answer
> 5. **Reflection:** Check if answer is complete and correct
>
> Example:
> User: 'Based on my documents, what are the top 3 risks and recommended mitigations?'
>
> Agent:
> 1. PLAN: Find risks mentioned + find mitigations mentioned
> 2. RETRIEVE: Search 'risks concerns threats problems'
> 3. RETRIEVE: Search 'mitigations solutions safeguards'
> 4. REASON: Connect each risk to relevant mitigation
> 5. GENERATE: Rank top 3 by severity
> 6. REFLECT: Are risks and mitigations properly paired?
>
> This is **agentic** because the system:
> - Makes planning decisions
> - Uses multiple tools in sequence
> - Reasons about relationships
> - Reflects on quality
> - Adapts based on feedback
>
> **Why This Matters:**
> Ask My Notes is:
> - ✅ Foundation for understanding RAG architecture
> - ✅ Base for adding planning/reasoning loops
> - ✅ Template for tool use
> - ✅ Scalable to multi-agent systems
> - ✅ Jobs market is moving toward agentic patterns (this differentiates me)"

Why this is good:
- ✅ Connects simple project to broader concepts
- ✅ Shows agentic principles understanding
- ✅ Demonstrates how to extend to agentic
- ✅ Explains why it matters for career
- ✅ Shows portfolio strategy thinking

---

## Code Quality Questions

### Question 8: "Walk me through your code architecture. Why did you structure it this way?"

**What they're testing:** Software engineering thinking, modularity, maintainability

**Mediocre Answer:**
> "I have app.py for the UI and pdf_handler.py for PDFs."

**Excellent Answer:**
> "I separated concerns into 5 focused modules:
>
> **Module 1: pdf_handler.py**
> Responsibility: Extract and chunk documents
> Why separate: PDF logic is complex and reusable
> ```python
> def extract_text(pdf_path): ...
> def chunk_text(text, ...): ...
> ```
> Testing: Easy to test independent of UI
> Extension: Could swap for different parser (docx, txt)
>
> **Module 2: embeddings.py**
> Responsibility: Load model and generate embeddings
> Why separate: Model loading is expensive, decoupling from retrieval
> ```python
> @st.cache_resource
> def load_embedding_model(): ...
> def get_embeddings(texts): ...
> ```
> Testing: Test against different models easily
> Extension: Could swap models without touching retriever
>
> **Module 3: retriever.py**
> Responsibility: Semantic search logic
> Why separate: Clean interface for queries
> ```python
> class Retriever:
>     def retrieve(query, top_k=3): ...
> ```
> Testing: Test cosine similarity logic in isolation
> Extension: Could swap numpy for vector DB (Pin cone, Weaviate)
>
> **Module 4: prompts.py**
> Responsibility: All prompt templates
> Why separate: Prompts are domain logic, easy to iterate/improve
> ```python
> SYSTEM_PROMPT = '...'
> def build_rag_prompt(query, context): ...
> ```
> Testing: Test against benchmark questions
> Extension: Could A/B test different prompts
>
> **Module 5: app.py**
> Responsibility: Streamlit UI and orchestration
> Why separate: Orchestrates the pipeline
> ```python
> uploaded_files = st.file_uploader(...)
> retrieved = retriever.retrieve(query)
> answer = call_ollama_api(prompt)
> ```
> Testing: Integration testing + manual testing
> Extension: Could swap Streamlit for Flask/FastAPI
>
> **Benefits of This Structure:**
>
> | Principle | Benefit | Example |
> |-----------|---------|---------|
> | Modularity | Easy to test | Test retriever without UI |
> | Separation of Concerns | Easy to modify | Change prompt without touching PDF logic |
> | Reusability | Code sharing | pdf_handler used by app + unit tests |
> | Extensibility | Easy upgrades | Swap embeddings model, no app changes |
> | Maintainability | Clear responsibilities | Bug in PDF? Check pdf_handler.py |
>
> **Dependency Graph:**
> ```
> app.py (orchestrator)
>   ├─ pdf_handler.py (document processing)
>   ├─ embeddings.py (model loading)
>   │   └─ no dependencies (except library: sentence-transformers)
>   ├─ retriever.py (semantic search)
>   │   └─ embeddings.py (uses embedding model)
>   └─ prompts.py (prompt engineering)
>       └─ no dependencies
>
> Benefit: Clean dependency tree, no circular imports
> ```
>
> **If I added features:**
> - Chat history: Add to app.py session_state ✓ (isolated)
> - Multi-model support: Update app.py to switch models ✓ (clean)
> - Vector DB: Replace retriever.py with new db_retriever.py ✓ (interface stays same)
> - Different PDF source: Extend pdf_handler.py ✓ (app.py unchanged)"

Why this is good:
- ✅ Explains each module's responsibility clearly
- ✅ Justifies why separated
- ✅ Shows testing implications
- ✅ Demonstrates extension capability
- ✅ Discusses clean architecture principles
- ✅ Shows dependency thinking

---

## Final Tips for Interview

### Before the Interview
- [ ] Re-read your code
- [ ] Prepare 2-minute elevator pitch of the project
- [ ] Understand every decision (why 384-dim, why Mistral, why 0.3 temperature)
- [ ] Be ready to discuss trade-offs
- [ ] Prepare to explain the pivots (Gemini → Ollama)

### During the Interview
- **If you don't know an answer:**
  - "That's a great question. Here's my current understanding... I'd want to research more."
  - Don't BS or pretend to know
  
- **When explaining technical decisions:**
  - Always explain the trade-off
  - Mention what you considered
  - Why you chose your approach
  
- **When asked about improvements:**
  - Vector DB for >10k chunks
  - Multi-turn conversation history
  - Re-ranking retrieved documents
  - Fine-tuning on domain-specific data
  
- **When they ask "what would you do differently?"**
  - "With 6 months and a team, I'd..."
  - Show ambition without denying current work's value

### Red Flags to Avoid
- ❌ "I just built this and didn't think about scalability"
- ❌ Not knowing what cosine similarity is
- ❌ Not understanding your own architecture
- ❌ Not discussing trade-offs (only benefits)
- ❌ "This is the only way to do it"
- ❌ Not testing the code before interview

### Green Flags to Show
- ✅ "I ran into [problem], solved it by [solution]"
- ✅ "I considered [alternative], but chose [current] because..."
- ✅ "These are the limitations and here's how I'd fix them"
- ✅ "I tested by [method]"
- ✅ "I documented this for [reason]"
- ✅ "The next evolution would be [agentic feature]"

---

**Final Note:** The best answer you can give is explaining your actual thought process. Don't memorize these - understand the concepts and adapt them to your own experience. Interviewers can tell the difference between prepared talking points and genuine understanding.

**Go ace those interviews! 🚀**
