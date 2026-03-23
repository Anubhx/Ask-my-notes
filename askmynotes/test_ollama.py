#!/usr/bin/env python3
"""Test script to verify Ollama setup is working."""

import requests
import sys

OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "dolphin-mixtral"


def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False


def list_models():
    """List available Ollama models."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])
        return [m["name"] for m in models]
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []


def test_model(model_name):
    """Test if a specific model can generate a response."""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": "What is 2+2? Respond in one word.",
                "stream": False,
                "temperature": 0.1,
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"


def main():
    print("🔍 Testing Ollama Setup...\n")
    
    # Check if Ollama is running
    print("1️⃣  Checking if Ollama server is running...")
    if not check_ollama_running():
        print("   ❌ FAILED: Ollama is not running!")
        print("   👉 Please start it with: ollama serve")
        print("   📌 Keep that terminal open while using the app!")
        return False
    print("   ✅ PASSED: Ollama server is running!\n")
    
    # List available models
    print("2️⃣  Checking available models...")
    models = list_models()
    if not models:
        print("   ❌ FAILED: No models found!")
        print("   👉 Pull a model first: ollama pull dolphin-mixtral")
        return False
    
    print(f"   ✅ PASSED: Found {len(models)} model(s):")
    for model in models:
        print(f"      • {model}")
    
    # Check if dolphin-mixtral is available
    if OLLAMA_MODEL not in models:
        print(f"\n   ⚠️  WARNING: {OLLAMA_MODEL} not found!")
        print(f"      Pull it with: ollama pull {OLLAMA_MODEL}")
        if models:
            print(f"\n   💡 Using available model '{models[0]}' instead for test...")
            test_model_name = models[0]
        else:
            return False
    else:
        test_model_name = OLLAMA_MODEL
    
    print()
    
    # Test inference
    print(f"3️⃣  Testing model inference ({test_model_name})...")
    response = test_model(test_model_name)
    
    if response.startswith("ERROR"):
        print(f"   ❌ FAILED: {response}")
        return False
    
    print(f"   ✅ PASSED: Model responded!")
    print(f"   📝 Response: {response}\n")
    
    # Final summary
    print("=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("=" * 50)
    print("\nYou're ready to run:\n")
    print("  cd /Users/anubhav/agentic-ai/askmynotes")
    print("  source .venv/bin/activate")
    print("  streamlit run app.py")
    print("\n✅ Keep 'ollama serve' running in another terminal!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
