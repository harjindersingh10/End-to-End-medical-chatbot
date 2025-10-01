from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='frontend/public', static_url_path='')
CORS(app)

print("Starting MediBot...")

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
        'message': 'MediBot is running!'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        question = data.get('message', '')
        
        if not question:
            return jsonify({'error': 'No message provided'}), 400
        
        # Simple response for now
        response = f"Hello! You asked: '{question}'. I'm MediBot and I'm working! The AI components are being loaded. For now, please consult healthcare professionals for medical advice."
        
        return jsonify({
            'response': response,
            'sources': 0,
            'model': 'simple-test'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("MediBot starting on http://localhost:5000")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, port=5000, host='127.0.0.1')