import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv('GEMINI_API').strip('"')
print(f"Gemini API Key: {GEMINI_API_KEY[:10]}...")

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("[OK] Gemini API configured successfully")
    
    # Test with different model names
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    for model_name in models:
        try:
            print(f"\n[TEST] Testing model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            # Simple test
            response = model.generate_content("What is paracetamol used for?")
            print(f"[SUCCESS] {model_name} works!")
            print(f"Response: {response.text[:100]}...")
            print(f"\n[RECOMMENDED] Use model: {model_name}")
            break
            
        except Exception as e:
            print(f"[ERROR] {model_name} failed: {e}")
            continue
    
except Exception as e:
    print(f"[ERROR] Failed to configure Gemini API: {e}")