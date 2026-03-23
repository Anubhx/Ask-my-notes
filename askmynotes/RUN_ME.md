# ⚡ Quick Command Reference

## 🚀 Run the App (Pick One)

### Option 1: Simple Terminal Command (Recommended)
```bash
cd /Users/anubhav/agentic-ai/askmynotes
source .venv/bin/activate
streamlit run app.py
```

**What happens:**
- Terminal shows: `Local URL: http://localhost:8501`
- Browser opens automatically to the app
- First run: Shows "Loading embedding model..." (takes 30-60s)
- Subsequent interactions: Instant (model cached)

### Option 2: Using Launcher Script
```bash
bash /Users/anubhav/agentic-ai/askmynotes/run.sh
```

---

## ✅ What You Should See

**First Run (loading screen):**
```
🚀 Starting Ask My Notes...
📚 Streamlit app will open at: http://localhost:8501

Loading embedding model...  [████████████████████░░░░░░░░░░░░░░░░░░]  50%
```

**Once Loaded:**
```
📚 Ask My Notes
Smart Q&A from your PDFs using Gemini & RAG

[📄 PDF Upload sidebar on LEFT with file uploader]
[❓ Ask Your Questions input on RIGHT side]
```

---

## 🎯 Usage Flow

1. **Upload PDFs**
   - Click "Choose PDF files" in sidebar
   - Select 1+ PDF files
   - Click "Process PDFs" button

2. **Ask Questions**
   - Type question in main area
   - Model retrieves relevant PDF chunks
   - Answers with citations

3. **View Results**
   - Answer displayed
   - Click "Retrieved Context" to see source chunks
   - Source attribution (PDF name + page #)

---

## ❌ If It Breaks

### Error: "GOOGLE_API_KEY not found"
```bash
# Add your API key to .env:
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Error: "No module named streamlit"
```bash
# You're not in the virtual environment, try:
source .venv/bin/activate
streamlit run app.py
```

### Error: "Address already in use"
Port 8501 is already running. Stop it:
```bash
# Kill the process:
lsof -ti:8501 | xargs kill -9

# Or use a different port:
streamlit run app.py --server.port 8502
```

### Model Loading Hangs
- First run downloads ~100MB (this is normal)
- Wait 30-60 seconds, do NOT close the terminal
- See spinner "Loading embedding model..."

### BrokenPipeError (Should be fixed now)
- This was the original error
- Now fixed with `@st.cache_resource` caching
- If you still see it, try clearing cache:
  ```bash
  rm -rf ~/.cache/streamlit ~/.cache/huggingface
  streamlit run app.py
  ```

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit app ← RUN THIS |
| `run.sh` | Convenience launcher script |
| `embeddings.py` | Embedding caching (FIXED) |
| `.env` | API key configuration |
| `FIX_REPORT.md` | Detailed fix documentation |
| `README.md` | Full project documentation |

---

## 🎓 Architecture

```
Your Browser (http://localhost:8501)
        ↓
    Streamlit UI
        ↓
PDF Handler → Embeddings (CACHED) → Retriever → Gemini API
        ↓
   Grounded Answer
```

---

## 💡 Tips

- **First instance takes time**: Model downloads ~100MB on first run (cached after)
- **No internet needed**: PDF processing is local only
- **Privacy safe**: Only PDF chunks sent to Gemini (not full PDFs)
- **Session isolated**: Each browser session has its own cached model

---

## ✨ Performance

| Action | Time |
|--------|------|
| First app start | 30-60s (model download) |
| PDF upload | <1s (instant) |
| Query + Gemini response | 2-5s |
| Subsequent interactions | Instant (cached) |

---

## 🔗 Links

- **App**: http://localhost:8501 (opens automatically)
- **Docs**: See README.md for full documentation
- **Fix Details**: See FIX_REPORT.md for technical details

---

**Ready?** Run: `streamlit run app.py` 🚀
