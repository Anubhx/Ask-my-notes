# 🚀 Getting Started with Ask My Notes

A complete step-by-step guide to set up and run the RAG system.

---

## ⚡ 5-Minute Quick Start

### 1. Install Ollama
```bash
brew install ollama
# OR download from https://ollama.ai/download
```

### 2. Start Ollama (Terminal 1)
```bash
ollama serve
# Wait for: "Listening on [::1]:11434"
```

### 3. Pull Model (Terminal 2)
```bash
ollama pull mistral
# Downloads 4GB model (~2 minutes)
```

### 4. Setup & Run App (Terminal 2)
```bash
cd /Users/anubhav/agentic-ai/askmynotes
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### 5. Use It!
1. Browser opens to `http://localhost:8501`
2. Upload PDF (left sidebar)
3. Click "Process PDFs"
4. Ask a question
5. Get grounded answer from your documents

---

## 📋 Detailed Setup (Step-by-Step)

### Prerequisites
- macOS with 10GB free space
- Python 3.8+
- Ollama installed

### Step 1: Navigate to Project

```bash
cd /Users/anubhav/agentic-ai/askmynotes
```

### Step 2: Create Virtual Environment

```bash
# Create isolated Python environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
# You should see (.venv) at terminal start
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What's installing:**
- `streamlit` - Web UI framework
- `requests` - HTTP client for Ollama API
- `python-dotenv` - Environment variable management
- `PyPDF2>=3.0.0` - PDF text extraction
- `sentence-transformers` - Embedding generation
- `numpy` - Vector operations
- `scikit-learn` - Similarity calculations

### Step 4: Ensure Ollama is Running

**Terminal 1:**
```bash
ollama serve
```

**Expected output:**
```
time=2024-03-24T19:47:43.123Z level=INFO msg="Starting Ollama server..."
time=2024-03-24T19:47:43.456Z level=INFO msg="Listening on [::1]:11434"
```

**Keep this terminal open!** The Ollama server must stay running.

### Step 5: Download Model

**Terminal 2:** (while Ollama serves)
```bash
ollama pull mistral
```

**Progress indicator:**
```
pulling manifest
pulling 8daa9ba and 9 more layers... 100%
pulling 8b299f6 and 9 more layers... 100%
verifying sha256 digest
writing manifest
success
```

**Check it's installed:**
```bash
ollama list
```

Should show:
```
NAME            ID          SIZE    MODIFIED
mistral:latest  2dfbe34...  4.1GB   just now
```

### Step 6: Run the Application

**Terminal 2:**
```bash
# Must have activated venv first
source .venv/bin/activate

# Run Streamlit
streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

Browser should open automatically. If not, go to: `http://localhost:8501`

---

## 🎯 First Test

### Upload a PDF

1. **Sidebar:** "Choose PDF files"
2. **Select** any PDF from your computer
3. **Click:** "Process PDFs"
4. **Wait** for: "✅ Processed X PDF(s) into Y chunks"

### Ask a Question

1. **Main area:** "Ask Your Questions" field
2. **Type:** Simple question about the PDF content
   - Example: "What is this document about?"
   - Example: "What are the key points?"

3. **Press:** Enter or wait for response
4. **See:**
   - Answer from Ollama
   - Retrieved chunks (click to expand)
   - Source attribution

### Success!

You should see:
- ✅ An answer grounded in your PDF
- ✅ Retrieved chunks showing relevance
- ✅ Source file and page numbers
- ✅ No API calls made (all local!)

---

## 🔧 Troubleshooting

### "Ollama: command not found"

**Solution:**
```bash
# Install Ollama
brew install ollama

# OR download from https://ollama.ai/download
# Then restart terminal
```

### "Connection refused to localhost:11434"

**Solution:**
- Ensure `ollama serve` is running in Terminal 1
- Check it's still showing "Listening on [::1]:11434"
- Try: `curl http://localhost:11434/api/tags`

### "Model not found: mistral"

**Solution:**
```bash
ollama pull mistral
# Wait for 2-minute download
```

### "Ollama inference timed out"

**Solutions:**
```bash
# Option 1: Use smaller model
ollama pull neural-chat  # 4GB, faster

# Option 2: Increase timeout in app.py
# Change: timeout=120 to timeout=300

# Option 3: Warm up model first
curl http://localhost:11434/api/generate \
  -d '{"model":"mistral","prompt":"hi","stream":false}'
# Wait 30+ seconds, then try again
```

### "PDF upload fails"

**Solutions:**
- Maximum file size: 200MB per file
- Supported format: PDF only
- Try: Smaller, simpler PDFs first
- Check: PDF isn't image-based/scanned

### "Python version error"

**Solution:**
```bash
# Check Python version
python --version
# Need: 3.8+

# Update if needed
brew install python@3.11
```

---

## 📊 What's Happening Under the Hood?

### 1. PDF Upload & Processing
```
Your PDF
  ↓
PyPDF2 extracts text
  ↓
Split into chunks (400 tokens, 100-token overlap)
  ↓
Store chunks in memory
```

### 2. Query Processing
```
Your question
  ↓
Convert to vector (sentence-transformers)
  ↓
Find similar chunks (cosine similarity)
  ↓
Build prompt with top-3 chunks
```

### 3. LLM Inference
```
Complete prompt
  ↓
Send to Ollama (localhost:11434)
  ↓
Mistral 7B generates response
  ↓
Send back to Streamlit UI
```

### 4. Display
```
Answer
  ↓
Show retrieved chunks (expandable)
  ↓
Show source attribution
```

**All 100% local. No external APIs.**

---

## 🚀 Next Steps

### Learn More:
- Read: `askmynotes/README.md` (architecture details)
- See: `askmynotes/QUICKSTART.md` (copy-paste commands)
- Study: Code in `askmynotes/` folder

### Customize:
- Change embedding model: Edit `embeddings.py`
- Switch LLM: Change `OLLAMA_MODEL` in `app.py`
- Adjust chunk size: Edit `pdf_handler.py`
- Try different prompts: Edit `prompts.py`

### Extend:
- Add chat memory
- Support more document types
- Integrate with databases
- Deploy to cloud
- Add authentication

### Career:
- Read: `../CAREER_PATH.md`
- Post on LinkedIn
- Interview preparation
- Build portfolio

---

## 💡 Pro Tips

### Faster Inference
```bash
# Use smaller model
ollama pull neural-chat  # 4GB instead of 4GB
# Edit app.py: OLLAMA_MODEL = "neural-chat"
```

### Better Quality Answers
```bash
# Use larger model (if you have space)
ollama pull mistral:text  # Same 4GB, optimized
# Or dolphin-mixtral (26GB, very capable)
```

### Batch Multiple PDFs
1. Upload multiple files at once
2. Click "Process PDFs" (processes all)
3. Queries search across all documents
4. Great for knowledge base

### Save Answers
1. Run query
2. Copy text from answer
3. Paste into file
4. Build knowledge base as you go

---

## 📞 Getting Help

### Check These First:
1. `askmynotes/TROUBLESHOOTING.md` - Common issues
2. `askmynotes/README.md` - Architecture explanation
3. Terminal output - Often shows error details

### Useful Commands:
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check Python environment
python --version
pip list

# Check disk space
df -h

# Kill Ollama if stuck
pkill ollama
# Then: ollama serve again
```

---

## ✅ Verification Checklist

```
Pre-Launch:
☐ Ollama installed (ollama --version works)
☐ Ollama serving (Terminal 1 shows "Listening...")
☐ Mistral pulled (ollama list shows it)
☐ .venv activated (Terminal 2 shows (.venv))
☐ Dependencies installed (pip list shows all)

At Launch:
☐ Streamlit runs without error
☐ Browser opens to localhost:8501
☐ UI loads correctly
☐ PDF upload works

First Query:
☐ PDF processes successfully
☐ Query responds with answer
☐ Retrieved chunks shown
☐ Source attribution appears
```

---

## 🎉 You're Ready!

Your local RAG system is running. Now:

1. **Upload some PDFs** about topics you care about
2. **Ask interesting questions**
3. **See how RAG works** in practice
4. **Read the code** to understand it
5. **Modify and experiment**

Welcome to Agentic AI! 🚀

---

**Questions? Check askmynotes/README.md or QUICKSTART.md**
