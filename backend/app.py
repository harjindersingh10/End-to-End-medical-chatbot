from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure APIs
PINECONE_API_KEY = os.getenv('PINECONE_API').strip('"')
GEMINI_API_KEY = os.getenv('GEMINI_API').strip('"')

print(f"Loaded API keys - Pinecone: {PINECONE_API_KEY[:10]}..., Gemini: {GEMINI_API_KEY[:10]}...")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
# Try different models in order of preference
model_names = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
gemini_model = None

for model_name in model_names:
    try:
        gemini_model = genai.GenerativeModel(model_name)
        # Test the model
        test_response = gemini_model.generate_content("Hello")
        print(f"Successfully initialized model: {model_name}")
        break
    except Exception as e:
        print(f"Failed to initialize {model_name}: {e}")
        continue

if gemini_model is None:
    print("ERROR: No working Gemini model found!")
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")  # Fallback

# Initialize embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
index_name = "medical-chatbot"

# Set Pinecone API key
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# Load existing vector store
print("Connecting to Pinecone vector store...")
try:
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings
    )
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    print("Successfully connected to Pinecone!")
except Exception as e:
    print(f"Error connecting to Pinecone: {e}")
    retriever = None

class GeminiLLM:
    def __init__(self, model):
        self.model = model

    def __call__(self, prompt_text):
        try:
            response = self.model.generate_content(prompt_text)
            return response.text
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini API Error: {error_msg}")
            
            if "quota" in error_msg.lower() or "429" in error_msg:
                return "I'm currently experiencing high demand. The Gemini API quota has been exceeded. Please try again later or contact support to increase your quota limits."
            elif "404" in error_msg:
                return "The AI model is currently unavailable. Please try again later."
            else:
                return f"I encountered an error while processing your request: {error_msg[:100]}... Please try again."

llm = GeminiLLM(gemini_model)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('message', '')
        
        print(f"Received question: {question}")
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
            
        if retriever is None:
            # Fallback to direct Gemini response without knowledge base
            print("Vector store not available, using direct Gemini response")
            simple_prompt = f"""You are MediBot, a medical AI assistant. Provide a helpful medical response to this question: {question}
            
Note: Always remind users to consult healthcare professionals for medical advice.
            
Response:"""
            response = llm(simple_prompt)
            return jsonify({
                'response': response + "\n\n⚠️ Note: Knowledge base unavailable. Please consult healthcare professionals for medical advice.",
                'sources': 0,
                'timestamp': datetime.now().isoformat(),
                'model': 'gemini-direct-fallback'
            })
        
        # Retrieve relevant documents
        retrieved_docs = retriever.invoke(question)
        
        # Create context from retrieved documents
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        
        # Create prompt for medical chatbot (matching your trials.ipynb approach)
        prompt = f"""You are MediBot, a knowledgeable medical AI assistant. Based on the following medical information from reliable medical sources, provide a clear, accurate, and helpful answer to the user's question.

Medical Knowledge Base Context:
{context}

User Question: {question}

Instructions:
- Provide accurate medical information based on the context
- Be clear and easy to understand
- If the context doesn't contain relevant information, acknowledge this and provide general guidance
- Always remind users to consult healthcare professionals for serious concerns
- Keep responses concise but informative

MediBot Response:"""
        
        # Get response from Gemini
        print(f"Sending prompt to Gemini: {prompt[:200]}...")
        response = llm(prompt)
        print(f"Gemini response: {response}")
        
        return jsonify({
            'response': response,
            'sources': len(retrieved_docs),
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini-2.5-flash',
            'knowledge_base': 'medical_knowledge_base.pdf'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    try:
        data = request.get_json()
        question = data.get('message', 'What is paracetamol?')
        
        # Test Gemini directly without vector search (fallback mode)
        simple_prompt = f"""You are MediBot, a medical AI assistant. Provide a helpful medical response to this question: {question}
        
Note: Always remind users to consult healthcare professionals for medical advice.
        
Response:"""
        response = llm(simple_prompt)
        
        return jsonify({
            'response': response + "\n\n⚠️ Note: This is a direct AI response without knowledge base context. Please consult healthcare professionals for medical advice.",
            'test': True,
            'timestamp': datetime.now().isoformat(),
            'model': 'gemini-2.5-flash-direct'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)