from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

application = Flask(__name__)
CORS(application)

print("Starting ClinixAI Medical Chatbot on AWS...")

# Try to load AI components
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv('GEMINI_API', '').strip('"')
    
    if GEMINI_API_KEY and GEMINI_API_KEY != 'your_gemini_api_key_here':
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        print("Gemini AI loaded successfully!")
    else:
        gemini_model = None
        print("No valid Gemini API key found")
except Exception as e:
    gemini_model = None
    print(f"Gemini not available: {e}")

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
    if not gemini_model:
        return "I'm currently experiencing technical difficulties. Please consult a healthcare professional for medical advice.", 0
    
    try:
        context = ""
        sources = 0
        
        if retriever:
            try:
                retrieved_docs = retriever.invoke(question)
                if retrieved_docs:
                    context = "\n".join([doc.page_content for doc in retrieved_docs])
                    sources = len(retrieved_docs)
            except Exception as e:
                print(f"Knowledge base search failed: {e}")
        
        if context:
            prompt = f"""You are MediBot, a medical AI assistant. Based on this medical context: {context}

Question: {question}

Provide a helpful medical response. Always remind users to consult healthcare professionals."""
        else:
            prompt = f"""You are MediBot, a medical AI assistant. Answer: {question}

Always remind users to consult healthcare professionals for medical advice."""
        
        response = gemini_model.generate_content(prompt)
        return response.text, sources
        
    except Exception as e:
        return "I encountered an error. Please consult a healthcare professional for medical advice.", 0

@application.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@application.route('/styles.css')
def css():
    with open('styles.css', 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

@application.route('/script.js')
def js():
    with open('script.js', 'r', encoding='utf-8') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

@application.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'gemini_available': gemini_model is not None,
        'pinecone_available': retriever is not None,
        'message': 'ClinixAI MediBot is running on AWS!'
    })

@application.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        response, sources = get_ai_response(question)
        
        return jsonify({
            'response': response,
            'sources': sources,
            'model': 'clinixai-aws'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=8000)