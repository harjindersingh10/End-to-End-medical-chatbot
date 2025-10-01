from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='frontend/public', static_url_path='')
CORS(app)

print("Starting MediBot Application...")

# Try to import AI components
try:
    import google.generativeai as genai
    
    # Configure Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API', '').strip('"')
    
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try different models
        model_names = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
        gemini_model = None
        
        for model_name in model_names:
            try:
                gemini_model = genai.GenerativeModel(model_name)
                print(f"Successfully loaded: {model_name}")
                break
            except Exception as e:
                print(f"Failed {model_name}: {str(e)[:50]}...")
                continue
    else:
        gemini_model = None
        print("No Gemini API key found")

except ImportError:
    print("Gemini library not available")
    gemini_model = None

# Try to import Pinecone
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_pinecone import PineconeVectorStore
    
    PINECONE_API_KEY = os.getenv('PINECONE_API', '').strip('"')
    
    if PINECONE_API_KEY:
        os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        docsearch = PineconeVectorStore.from_existing_index(
            index_name="medical-chatbot",
            embedding=embeddings
        )
        retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        print("Pinecone connected successfully!")
    else:
        retriever = None
        print("No Pinecone API key found")

except Exception as e:
    print(f"Pinecone setup failed: {e}")
    retriever = None

def get_ai_response(question):
    """Get AI response with fallback mechanisms"""
    
    # Try with knowledge base first
    if retriever and gemini_model:
        try:
            retrieved_docs = retriever.invoke(question)
            context = "\n".join([doc.page_content for doc in retrieved_docs])
            
            prompt = f"""You are MediBot, a medical AI assistant. Based on the medical information below, provide a helpful answer:

Medical Context:
{context}

Question: {question}

Provide a clear, helpful medical response. Always remind users to consult healthcare professionals for serious concerns.

Response:"""
            
            response = gemini_model.generate_content(prompt)
            return response.text, len(retrieved_docs)
            
        except Exception as e:
            print(f"Knowledge base error: {e}")
    
    # Fallback to direct AI
    if gemini_model:
        try:
            prompt = f"""You are MediBot, a medical AI assistant. Answer this medical question: {question}

Always remind users to consult healthcare professionals for medical advice.

Response:"""
            
            response = gemini_model.generate_content(prompt)
            return response.text + "\n\nNote: Limited knowledge base access. Please consult healthcare professionals.", 0
            
        except Exception as e:
            if "quota" in str(e).lower():
                return "I'm experiencing high demand right now. Please try again later or consult a healthcare professional.", 0
            else:
                return "I encountered an error. Please consult a healthcare professional for medical advice.", 0
    
    # Final fallback
    return f"Thank you for asking about '{question}'. I'm MediBot, but I'm currently experiencing technical difficulties. Please consult a healthcare professional for medical advice.", 0

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
        
        # Get AI response
        response, sources = get_ai_response(question)
        
        return jsonify({
            'response': response,
            'sources': sources,
            'model': 'medibot'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("CLINIXAI MEDICAL CHATBOT")
    print("=" * 50)
    print("URL: http://localhost:5000")
    print("Your futuristic UI is ready!")
    print("=" * 50)
    
    app.run(debug=True, port=5000, host='127.0.0.1')