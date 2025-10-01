from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

print("🚀 Starting MediBot backend...")

# Try to import and configure AI components
try:
    import google.generativeai as genai
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_pinecone import PineconeVectorStore
    
    # Configure APIs
    PINECONE_API_KEY = os.getenv('PINECONE_API', '').strip('"')
    GEMINI_API_KEY = os.getenv('GEMINI_API', '').strip('"')
    
    print(f"📋 API Keys loaded - Pinecone: {PINECONE_API_KEY[:10] if PINECONE_API_KEY else 'Missing'}...")
    print(f"📋 API Keys loaded - Gemini: {GEMINI_API_KEY[:10] if GEMINI_API_KEY else 'Missing'}...")
    
    # Configure Gemini
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Try different models
        model_names = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
        gemini_model = None
        
        for model_name in model_names:
            try:
                gemini_model = genai.GenerativeModel(model_name)
                print(f"✅ Successfully initialized model: {model_name}")
                break
            except Exception as e:
                print(f"❌ Failed to initialize {model_name}: {str(e)[:100]}")
                continue
    else:
        gemini_model = None
        print("⚠️ No Gemini API key found")
    
    # Initialize embeddings and vector store
    if PINECONE_API_KEY:
        try:
            os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            docsearch = PineconeVectorStore.from_existing_index(
                index_name="medical-chatbot",
                embedding=embeddings
            )
            retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
            print("✅ Successfully connected to Pinecone!")
        except Exception as e:
            print(f"❌ Failed to connect to Pinecone: {str(e)[:100]}")
            retriever = None
    else:
        retriever = None
        print("⚠️ No Pinecone API key found")

except ImportError as e:
    print(f"⚠️ Some AI libraries not available: {e}")
    gemini_model = None
    retriever = None

class GeminiLLM:
    def __init__(self, model):
        self.model = model

    def __call__(self, prompt_text):
        if not self.model:
            return "AI model is not available. Please check your API configuration."
        
        try:
            response = self.model.generate_content(prompt_text)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                return "I'm currently experiencing high demand. Please try again later."
            else:
                return f"I encountered an error: {error_msg[:100]}..."

# Initialize LLM
llm = GeminiLLM(gemini_model) if gemini_model else None

@app.route('/api/health', methods=['GET'])
def health():
    status = {
        'status': 'healthy',
        'gemini_available': gemini_model is not None,
        'pinecone_available': retriever is not None,
        'message': 'MediBot backend is running!'
    }
    return jsonify(status)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('message', '')
        
        print(f"📝 Received question: {question}")
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        # If we have both AI components, use them
        if llm and retriever:
            try:
                # Retrieve relevant documents
                retrieved_docs = retriever.invoke(question)
                context = "\n".join([doc.page_content for doc in retrieved_docs])
                
                # Create prompt
                prompt = f"""You are MediBot, a medical AI assistant. Based on the following medical information, provide a helpful answer:

Medical Context:
{context}

Question: {question}

Provide a clear, helpful medical response. Always remind users to consult healthcare professionals for serious concerns.

Response:"""
                
                response = llm(prompt)
                
                return jsonify({
                    'response': response,
                    'sources': len(retrieved_docs),
                    'model': 'gemini-with-knowledge-base'
                })
                
            except Exception as e:
                print(f"❌ Error with full AI pipeline: {e}")
                # Fallback to simple AI
                pass
        
        # Fallback: Simple AI response
        if llm:
            simple_prompt = f"You are MediBot, a medical assistant. Answer this question: {question}\n\nAlways remind users to consult healthcare professionals."
            response = llm(simple_prompt)
            
            return jsonify({
                'response': response + "\n\n⚠️ Note: Limited knowledge base access. Please consult healthcare professionals.",
                'sources': 0,
                'model': 'gemini-simple'
            })
        
        # Final fallback: Static response
        response = f"Thank you for asking about '{question}'. I'm MediBot, but I'm currently experiencing technical difficulties with my AI components. Please consult a healthcare professional for medical advice."
        
        return jsonify({
            'response': response,
            'sources': 0,
            'model': 'fallback'
        })
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'MediBot API is working!',
        'endpoints': ['/api/health', '/api/chat', '/api/test']
    })

if __name__ == '__main__':
    print("🌟 MediBot backend ready!")
    print("🔗 Backend URL: http://localhost:5000")
    print("🔗 Health check: http://localhost:5000/api/health")
    print("=" * 50)
    app.run(debug=True, port=5000, host='0.0.0.0')