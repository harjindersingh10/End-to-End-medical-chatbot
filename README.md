# Medical Chatbot - End-to-End Application

A complete medical chatbot application with React frontend and Flask backend, powered by Gemini AI and Pinecone vector database.

## Features

- 🏥 Medical knowledge base with 39,919+ text chunks
- 🤖 AI-powered responses using Google Gemini 2.5 Flash
- 🔍 Semantic search with Pinecone vector database
- ⚛️ Modern React frontend with real-time chat
- 🔒 Secure API key management
- 📱 Responsive design for all devices

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Double-click start_app.bat or run:
start_app.bat
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## Environment Variables

Create a `.env` file in the root directory:
```
PINECONE_API="your_pinecone_api_key"
GEMINI_API="your_gemini_api_key"
```

## API Endpoints

- `POST /api/chat` - Send message to chatbot
- `GET /api/health` - Health check

## Technology Stack

- **Frontend**: React, Axios, CSS3
- **Backend**: Flask, Python
- **AI**: Google Gemini 2.5 Flash
- **Vector DB**: Pinecone
- **Embeddings**: HuggingFace Sentence Transformers
- **Document Processing**: LangChain

## Usage

1. Start the application using `start_app.bat`
2. Open http://localhost:3000 in your browser
3. Ask medical questions like:
   - "What is the use of paracetamol?"
   - "What are the symptoms of diabetes?"
   - "How to treat a headache?"

## Project Structure

```
medical_chatbot/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Styling
│   │   └── index.js       # React entry point
│   ├── public/
│   │   └── index.html     # HTML template
│   └── package.json       # Node dependencies
├── research/
│   └── trials.ipynb       # Model development notebook
├── Data/
│   └── medical_knowledge_base.pdf
├── .env                    # Environment variables
├── .env.example           # Environment template
├── start_app.bat          # Quick start script
└── README.md              # This file
```

## Security

- API keys are stored in `.env` file (excluded from Git)
- CORS enabled for frontend-backend communication
- Input validation and error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.