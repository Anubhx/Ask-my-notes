"""Simple test to verify Gemini API key works."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
    exit(1)

print(f"🔍 Testing API key: {api_key[:20]}...")

try:
    # Configure Gemini
    genai.configure(api_key=api_key)
    print("✅ API key configured successfully")
    
    # Try to create a model
    print("\n📌 Attempting to load model: gemini-2.5-flash...")
    model = genai.GenerativeModel("gemini-2.5-flash")
    print("✅ Model loaded successfully")
    
    # Try to generate content
    print("\n📌 Sending test request...")
    response = model.generate_content("Say 'Hello, API is working!'")
    print("✅ Request succeeded!")
    
    print(f"\n🎉 Response from Gemini:\n{response.text}")
    print("\n✅ YOUR API KEY IS WORKING!")
    
except Exception as e:
    error_str = str(e)
    print(f"\n❌ ERROR: {error_str}\n")
    
    # Provide specific error diagnosis
    if "API" in error_str or "404" in error_str:
        print("🔴 PROBLEM: Generative Language API is NOT enabled")
        print("\n✅ FIX: Enable the API in Google Cloud Console:")
        print("   1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
        print("   2. Click 'ENABLE'")
        print("   3. Wait 30 seconds")
        print("   4. Run this script again")
        
    elif "429" in error_str or "RATE_LIMIT" in error_str or "Quota" in error_str:
        print("🔴 PROBLEM: API Rate Limit/Quota exceeded")
        print("\n✅ FIX: Enable billing on your Google Cloud project:")
        print("   1. Go to: https://console.cloud.google.com/billing")
        print("   2. Create a billing account with a payment method")
        print("   3. Link billing to your project")
        print("   4. Run this script again")
    
    elif "authentication" in error_str.lower() or "permission" in error_str.lower():
        print("🔴 PROBLEM: API key authentication failed or not authorized")
        print("\n✅ FIX: Check your API key:")
        print("   1. Go to: https://aistudio.google.com/app/apikey")
        print("   2. Create a new key or copy existing key")
        print("   3. Update .env file with the correct key")
        print("   4. Run this script again")
    
    else:
        print(f"🔴 UNKNOWN ERROR: {error_str}")
        print("\nPlease check:")
        print("   - API key is correct")
        print("   - Generative Language API is enabled")
        print("   - Billing is attached to project")
