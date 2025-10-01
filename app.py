from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env.local first, then .env
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv()

app = Flask(__name__)
CORS(app)

print("Starting ClinixAI Medical Chatbot...")

# Try to load AI components
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv('GEMINI_API', '').strip('"')
    
    if GEMINI_API_KEY and GEMINI_API_KEY != 'your_gemini_api_key_here':
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
        print("No valid Gemini API key found")
except:
    gemini_model = None
    print("Gemini not available")

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_pinecone import PineconeVectorStore
    
    PINECONE_API_KEY = os.getenv('PINECONE_API', '').strip('"')
    
    if PINECONE_API_KEY and PINECONE_API_KEY != 'your_pinecone_api_key_here':
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
        print("No valid Pinecone API key found")
except Exception as e:
    retriever = None
    print(f"Pinecone setup failed: {e}")

def get_ai_response(question):
    """Enhanced AI response with both knowledge base and general medical knowledge"""
    
    if not gemini_model:
        return "I'm currently experiencing technical difficulties. Please consult a healthcare professional for medical advice.", 0
    
    try:
        # First, try to get relevant context from knowledge base
        context = ""
        sources = 0
        
        if retriever:
            try:
                retrieved_docs = retriever.invoke(question)
                if retrieved_docs:
                    context = "\n".join([doc.page_content for doc in retrieved_docs])
                    sources = len(retrieved_docs)
                    print(f"Found {sources} relevant documents")
            except Exception as e:
                print(f"Knowledge base search failed: {e}")
        
        # Create comprehensive prompt that uses both knowledge base and AI's medical knowledge
        if context:
            prompt = f"""You are MediBot, a knowledgeable medical AI assistant. You have access to a comprehensive medical knowledge base and your own medical training.

Medical Knowledge Base Context:
{context}

User Question: {question}

Instructions:
- First, use the provided medical context if it's relevant to answer the question
- If the context doesn't fully answer the question, supplement with your general medical knowledge
- Provide accurate, clear, and helpful medical information
- Always remind users to consult healthcare professionals for serious concerns
- Be conversational and empathetic
- Keep responses informative but concise

MediBot Response:"""
        else:
            # No relevant context found, use AI's general medical knowledge
            prompt = f"""You are MediBot, a knowledgeable medical AI assistant. Answer the following medical question using your medical knowledge and training.

User Question: {question}

Instructions:
- Provide accurate medical information based on your knowledge
- Be clear, helpful, and easy to understand
- Always remind users to consult healthcare professionals for diagnosis and treatment
- Be conversational and empathetic
- If you're unsure about something, acknowledge it and recommend professional consultation

MediBot Response:"""
        
        response = gemini_model.generate_content(prompt)
        return response.text, sources
        
    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            return "I'm experiencing high demand right now. Please try again later or consult a healthcare professional.", 0
        else:
            return "I encountered an error while processing your request. Please consult a healthcare professional for medical advice.", 0

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/styles.css')
def css():
    with open('styles.css', 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

@app.route('/script.js')
def js():
    with open('script.js', 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

@app.route('/logo.png')
def logo():
    try:
        # Try SVG logo first
        with open('logo.svg', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'image/svg+xml'}
    except:
        try:
            # Try PNG logo
            with open('logo.png', 'rb') as f:
                return f.read(), 200, {'Content-Type': 'image/png'}
        except:
            # Create a simple medical cross as fallback
            svg_logo = '''<svg width="50" height="50" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg">
<circle cx="25" cy="25" r="25" fill="#00D4FF"/>
<path d="M25 10V40M10 25H40" stroke="white" stroke-width="4" stroke-linecap="round"/>
</svg>'''
            return svg_logo, 200, {'Content-Type': 'image/svg+xml'}

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'gemini_available': gemini_model is not None,
        'pinecone_available': retriever is not None,
        'message': 'ClinixAI MediBot is running!'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"Question: {question}")
        
        # Get enhanced AI response
        response, sources = get_ai_response(question)
        
        return jsonify({
            'response': response,
            'sources': sources,
            'model': 'clinixai-enhanced'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)