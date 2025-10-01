// Medical Chatbot JavaScript with Backend Integration
let isLoading = false;

// Initialize chat
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    
    // Enter key to send message
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Check backend health on load
    checkBackendHealth();
});

// Check if backend is running
async function checkBackendHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateAssistantSpeech("I'm online and ready to help with your medical questions!");
            updateStatusIndicator(true);
        }
    } catch (error) {
        console.error('Backend not available:', error);
        updateAssistantSpeech("I'm having trouble connecting. Please make sure the backend is running.");
        updateStatusIndicator(false);
    }
}

// Update status indicator
function updateStatusIndicator(isOnline) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-indicator span');
    
    if (isOnline) {
        statusDot.style.background = '#00ff7f';
        statusText.textContent = 'Online';
    } else {
        statusDot.style.background = '#ff4444';
        statusText.textContent = 'Offline';
    }
}

// Send message function
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message || isLoading) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    messageInput.value = '';
    
    // Show loading
    showLoading();
    
    try {
        // Send to backend API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Hide loading
        hideLoading();
        
        if (response.ok) {
            // Add bot response
            addMessage(data.response, 'bot', data.sources);
            if (data.sources > 0) {
                updateAssistantSpeech(`I found information from ${data.sources} medical sources to help answer your question!`);
            } else {
                updateAssistantSpeech("I've used my medical knowledge to help answer your question!");
            }
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            updateAssistantSpeech("I'm having some technical difficulties.");
        }
    } catch (error) {
        hideLoading();
        console.error('Error:', error);
        addMessage('Sorry, I cannot connect to the medical database right now. Please try again later.', 'bot');
        updateAssistantSpeech("I'm having trouble connecting to my medical database.");
    }
}

// Send quick message
function sendQuickMessage(message) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = message;
    sendMessage();
}

// Add message to chat
function addMessage(text, sender, sources = null) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    let sourcesText = '';
    if (sources && sources > 0) {
        sourcesText = `<div style="font-size: 0.8rem; opacity: 0.8; margin-top: 5px; color: #ffffff;">📚 Based on ${sources} medical sources</div>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${sender === 'user' ? '👤' : '🤖'}</div>
        <div class="message-content" style="color: #ffffff;">
            <p style="color: #ffffff; margin: 0;">${text}</p>
            ${sourcesText}
        </div>
        <div class="message-time">${currentTime}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show loading indicator
function showLoading() {
    isLoading = true;
    const chatMessages = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message';
    loadingDiv.id = 'loading-message';
    
    loadingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content loading-message" style="color: #ffffff;">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <span style="color: #ffffff;">Searching medical database...</span>
        </div>
    `;
    
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Disable send button
    const sendBtn = document.querySelector('.send-btn');
    sendBtn.disabled = true;
    
    // Update assistant speech
    updateAssistantSpeech("Let me search my medical knowledge base for you...");
}

// Hide loading indicator
function hideLoading() {
    isLoading = false;
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
    
    // Enable send button
    const sendBtn = document.querySelector('.send-btn');
    sendBtn.disabled = false;
}

// Update assistant speech bubble
function updateAssistantSpeech(text) {
    const speechBubble = document.querySelector('.assistant-speech-bubble p');
    speechBubble.textContent = text;
    
    // Add a subtle animation
    speechBubble.style.opacity = '0';
    setTimeout(() => {
        speechBubble.style.opacity = '1';
    }, 100);
}