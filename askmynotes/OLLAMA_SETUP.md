# 🚀 Ollama Setup Guide for M4 MacBook

## Step 1: Install Ollama

### Option A: Using Homebrew (Easiest)
```bash
brew install ollama
```

### Option B: Direct Download
1. Go to: https://ollama.ai/download
2. Click "macOS" 
3. Download and install the app
4. Move to Applications folder

---

## Step 2: Start Ollama Server

After installation, start the Ollama service:

```bash
# If installed via Homebrew:
ollama serve

# If installed as app, it runs automatically in background
# To verify it's running, open terminal and run:
curl http://localhost:11434/api/tags
```

You should see: `{"models":[]}`

**Keep this terminal window open** while using the app!

---

## Step 3: Pull the Dolphin Mixtral Model

In a **NEW terminal window** (keep the Ollama server running in the first one):

```bash
ollama pull dolphin-mixtral
```

⏳ **This will take 10-20 minutes** (26GB download)

You'll see progress like:
```
pulling e60b6c3e1853...
pulling 5d39b16cd61c...
pulling 4c1db93f8c0f...  90% ▓▓▓▓▓▓▓▓▓░
```

When done, you'll see:
```
✓ Processed 1 image in 4.23s
```

---

## Step 4: Verify Model is Ready

```bash
ollama list
```

Should show:
```
NAME              ID              SIZE    MODIFIED
dolphin-mixtral   8e2ec7e4cfe7    26 GB   2 minutes ago
```

---

## ✅ You're Ready!

Now you have:
- ✅ Ollama running locally on `localhost:11434`
- ✅ Dolphin Mixtral model loaded (26GB)
- ✅ No API limits, no costs, no internet needed
- ✅ Can run completely offline

**Next step**: Update the Ask My Notes app to use Ollama instead of Gemini.

---

## 📊 Space Check

```
Your situation:
- Total SSD: 256GB
- Free space: 50GB
- Model size: 26GB
- After download: ~24GB free (plenty for the app!)
```

✅ You're good!

---

## 🛑 Troubleshooting

### "ollama: command not found"
```bash
# If Homebrew install didn't work, try:
/usr/local/bin/ollama --help

# Or reinstall:
brew uninstall ollama
brew install ollama
```

### "Failed to download model"
- Check internet connection
- Try again (resumable)
- Or use smaller model: `ollama pull mistral` (4GB)

### "Ollama won't start"
- Make sure it's in Applications folder
- Or restart your Mac

### "Port 11434 already in use"
```bash
# See what's using it:
lsof -i :11434

# Kill the process (first number in output):
kill -9 <PID>
```

---

## 📝 Keep This Running

**IMPORTANT**: Keep the Ollama server running in a terminal while using the Ask My Notes app.

The command is:
```bash
ollama serve
```

This starts the API server on `http://localhost:11434`

**Don't close this window** while using the Streamlit app!

---

Once Ollama and the model are ready, I'll update the Ask My Notes app to use it! 🚀
