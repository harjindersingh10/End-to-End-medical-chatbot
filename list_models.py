import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv('GEMINI_API').strip('"')
print(f"Gemini API Key: {GEMINI_API_KEY[:10]}...")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

print("\n[INFO] Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
        
# Test the first available model
try:
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if models:
        model_name = models[0].name
        print(f"\n[TEST] Testing first available model: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("What is paracetamol?")
        print(f"[SUCCESS] Model works!")
        print(f"Response: {response.text[:200]}...")
        
except Exception as e:
    print(f"[ERROR] Test failed: {e}")