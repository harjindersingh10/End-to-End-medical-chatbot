import os
import sys
import subprocess
import time
import threading
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='frontend/public', static_url_path='')
CORS(app)

print("Starting Complete MediBot Application...")

# Try to import AI components
try:
    import google.generativeai as genai
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_pinecone import PineconeVectorStore
    
    # Configure APIs
    PINECONE_API_KEY = os.getenv('PINECONE_API', '').strip('"')
    GEMINI_API_KEY = os.getenv('GEMINI_API', '').strip('"')
    
    print(f"Gemini API: {'Found' if GEMINI_API_KEY else 'Missing'}")
    print(f"Pinecone API: {'Found' if PINECONE_API_KEY else 'Missing'}")
    
    # Configure Gemini
    gemini_model = None
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model_names = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
            
            for model_name in model_names:
                try:
                    gemini_model = genai.GenerativeModel(model_name)
                    test_response = gemini_model.generate_content("Hello")
                    print(f"Gemini model working: {model_name}")
                    break
                except Exception as e:
                    if "quota" in str(e).lower():
                        print(f"{model_name} quota exceeded")
                    continue
        except Exception as e:
            print(f"Gemini setup failed: {e}")
    
    # Configure Pinecone
    retriever = None
    if PINECONE_API_KEY:
        try:
            os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            docsearch = PineconeVectorStore.from_existing_index(
                index_name="medical-chatbot",
                embedding=embeddings
            )
            retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
            print("Pinecone connected successfully!")
        except Exception as e:
            print(f"Pinecone setup failed: {e}")

except ImportError as e:
    print(f"AI libraries not available: {e}")
    gemini_model = None
    retriever = None

class MediBotAI:
    def __init__(self, model):
        self.model = model

    def get_response(self, question, context=None):
        if not self.model:
            return "I'm currently experiencing technical difficulties. Please consult a healthcare professional for medical advice."
        
        try:
            if context:
                prompt = f"""You are MediBot, a medical AI assistant. Based on the medical information below, provide a helpful answer:

Medical Context:
{context}

Question: {question}

Provide a clear, helpful medical response. Always remind users to consult healthcare professionals for serious concerns.

Response:"""
            else:
                prompt = f"""You are MediBot, a medical AI assistant. Answer this medical question: {question}

Always remind users to consult healthcare professionals for medical advice.

Response:"""
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "quota" in str(e).lower():
                return "I'm experiencing high demand right now. Please try again later or consult a healthcare professional."
            return f"I encountered an error. Please consult a healthcare professional for medical advice."

# Initialize AI
medibot = MediBotAI(gemini_model)

# Serve the main HTML file
@app.route('/')
def index():
    return send_from_directory('frontend/public', 'index.html')

# Serve static files
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('frontend/public', filename)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'gemini_available': gemini_model is not None,
        'pinecone_available': retriever is not None,
        'message': 'MediBot is running!'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"Question: {question}")
        
        # Try with knowledge base first
        if retriever:
            try:
                retrieved_docs = retriever.invoke(question)
                context = "\n".join([doc.page_content for doc in retrieved_docs])
                response = medibot.get_response(question, context)
                
                return jsonify({
                    'response': response,
                    'sources': len(retrieved_docs),
                    'model': 'medibot-with-knowledge'
                })
            except Exception as e:
                print(f"Knowledge base error: {e}")
        
        # Fallback to direct AI
        response = medibot.get_response(question)
        
        return jsonify({
            'response': response + "\n\nNote: Limited knowledge base access. Please consult healthcare professionals.",
            'sources': 0,
            'model': 'medibot-direct'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def open_browser():
    time.sleep(2)
    try:
        import webbrowser
        webbrowser.open('http://localhost:5000')
        print("Opening browser...")
    except:
        print("Please open your browser and go to: http://localhost:5000")

if __name__ == '__main__':
    print("=" * 60)
    print("CLINIXAI MEDICAL CHATBOT")
    print("=" * 60)
    print("URL: http://localhost:5000")
    print("UI: Your custom futuristic design")
    print("AI: Gemini + Pinecone knowledge base")
    print("=" * 60)
    
    # Start browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Flask app
    app.run(debug=False, port=5000, host='0.0.0.0')