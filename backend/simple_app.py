from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

print("Starting MediBot backend...")

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'MediBot backend is running!'})

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        # Simple response for now
        response = f"Thank you for asking: '{question}'. I'm MediBot and I'm working! However, the AI model is currently being set up. Please try again in a moment."
        
        return jsonify({
            'response': response,
            'sources': 0,
            'model': 'simple-response'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("MediBot backend starting on http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')