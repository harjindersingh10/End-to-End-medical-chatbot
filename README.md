# ClinixAI - Medical Chatbot

A complete medical chatbot with user authentication, AI responses, and SQLite database.

## Features

- 🔐 User Authentication (Email/Password + Google OAuth)
- 🤖 AI-powered medical responses (Gemini AI)
- 🗄️ SQLite database for user data and chat history
- 🔍 Pinecone vector database for medical knowledge
- 📱 Responsive futuristic UI

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create `.env.local` file:
   ```
   PINECONE_API="your_pinecone_api_key"
   GEMINI_API="your_gemini_api_key"
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the app:**
   - Main app: http://localhost:2800
   - Login page: http://localhost:2800/login

## Project Structure

```
medical_chatbot/
├── app.py              # Main Flask application
├── auth.py             # Authentication manager
├── database.py         # SQLite database handler
├── index.html          # Main chatbot interface
├── login.html          # Login/Register page
├── styles.css          # UI styling
├── script.js           # Main chatbot JavaScript
├── auth.js             # Authentication JavaScript
├── requirements.txt    # Python dependencies
├── .env               # Environment template
├── .env.local         # Your actual API keys (not in git)
└── README.md          # This file
```

## API Endpoints

- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/verify` - Verify authentication
- `POST /api/chat` - Send message to chatbot (requires auth)
- `GET /api/history` - Get chat history (requires auth)
- `POST /api/feedback` - Save user feedback

## Database Tables

- `users` - User accounts
- `chat_history` - Chat conversations
- `medical_kb` - Medical knowledge base
- `feedback` - User ratings and feedback

## Security

- JWT token authentication
- Password hashing
- API key protection
- User-specific data isolation

## License

MIT License