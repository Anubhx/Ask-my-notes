# 🚀 Quick Start - Copy & Paste Commands

## Step 1: Install Ollama (5 minutes)

### Option A: Homebrew (Easiest)
```bash
brew install ollama
```

### Option B: Direct Download
1. Go to https://ollama.ai/download
2. Download macOS version
3. Drag to Applications

## Step 2: Download Model (15-20 minutes)

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

Wait for: `Listening on [::1]:11434`

**Terminal 2 - Download Model:**
```bash
ollama pull dolphin-mixtral
```

Wait for: `✓ Processed 1 image in XXXs`

## Step 3: Verify Everything Works (1 minute)

**Still in Terminal 2:**
```bash
cd /Users/anubhav/agentic-ai/askmynotes
python test_ollama.py
```

Should see: `✅ ALL TESTS PASSED!`

## Step 4: Run the App (2 minutes)

**Terminal 2:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Browser opens automatically to: `http://localhost:8501`

---

## 📌 Important: Keep Terminal 1 Open!

Your Ollama server must keep running:
```
Terminal 1: ollama serve
Terminal 2: streamlit run app.py
```

If you close Terminal 1, the app won't work!

---

## 🎯 Using the App

1. **Sidebar**: Click "Choose PDF files" → Select PDFs → Click "Process PDFs"
2. **Main Area**: Type your question in "Ask Your Questions"
3. **Results**: 
   - Answer appears
   - Click "Retrieved Context" to see source PDFs
   - All grounded in your documents!

---

## ✅ Installation Checklist

```
☐ Ollama installed (ollama --version works)
☐ 'ollama serve' running in Terminal 1
☐ Dolphin Mixtral model downloaded (ollama list shows it)
☐ test_ollama.py passes (✅ ALL TESTS PASSED!)
☐ Streamlit app running (http://localhost:8501 opens)
☐ Can upload PDFs
☐ Can ask questions and get answers
```

---

## 🆘 Troubleshooting

### "Ollama: command not found"
```bash
brew install ollama
# OR download from https://ollama.ai/download
```

### "Error: model not found"
```bash
ollama pull dolphin-mixtral
# Wait 15-20 minutes for 26GB download
```

### "Connection refused"
- Check Terminal 1 still says: `Listening on [::1]:11434`
- If not, restart: `ollama serve`

### "Port already in use"
```bash
lsof -i :11434  # Find what's using port
kill -9 <PID>   # Kill it
```

### "Model is slow"
Use smaller model:
```bash
ollama pull mistral  # 4GB, faster
# Then edit app.py: OLLAMA_MODEL = "mistral"
```

---

## 🎉 You're Done!

Your portfolio AI project is ready!

**Next: Check out `PORTFOLIO_GUIDE.md` for LinkedIn/sales tips**


### Embedding Model Taking Too Long?
The first run downloads a ~100MB model (happens once). Subsequent runs use cached model.

### "API Key Error"?
```bash
cat .env
# Should show: GEMINI_API_KEY=AIzaSy...
# If empty, add your key from https://ai.google.dev
```

### Streamlit not starting?
```bash
# Try with verbose output:
streamlit run app.py --verbose
```

## 📚 File Structure
```
askmynotes/
├── app.py                 # 👈 Main app (run this)
├── pdf_handler.py         # PDF extraction 
├── embeddings.py          # Free embeddings (sentence-transformers)
├── retriever.py           # Semantic search
├── prompts.py             # System prompt preventing hallucinations
├── requirements.txt       # Dependencies (already installed)
├── .env                   # API key (already configured)
└── README.md              # Full documentation
```

## 🎮 How to Use
1. Upload PDF → Process → Ask Question → Get Answer (from PDF only!) → Expand to see sources

## ⚡ Key Features
- ✅ Multiple PDFs supported
- ✅ No external knowledge leaking (forced grounding in PDFs)
- ✅ Shows which PDF and page the answer came from
- ✅ Free models only (no $$ subscriptions needed)
- ✅ All data processed locally (privacy-safe)

## 💡 Tips
- Rephrase questions if you get no results
- Shorter, specific questions work better than long ones  
- PDFs with selectable text work best (not scanned images)
- First embedding generation takes ~30s (model download)

---

**That's it!** 🎉 Your RAG-powered Q&A app is ready.
