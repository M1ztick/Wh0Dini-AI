// Wh0Dini-AI Web UI JavaScript
class Wh0DiniChat {
    constructor() {
        this.apiBase = '';
        this.isStreaming = true;
        this.conversationHistory = [];
        this.isTyping = false;
        
        this.initializeElements();
        this.bindEvents();
        this.checkApiStatus();
        this.setWelcomeTime();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.streamToggle = document.getElementById('streamToggle');
        this.statusDot = document.getElementById('status-dot');
        this.statusText = document.getElementById('status-text');
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }

    bindEvents() {
        // Send message events
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Input events
        this.messageInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
            this.updateSendButton();
        });

        // Control events
        this.clearButton.addEventListener('click', () => this.clearChat());
        this.streamToggle.addEventListener('click', () => this.toggleStreaming());

        // Auto-resize textarea
        this.adjustTextareaHeight();
    }

    setWelcomeTime() {
        const welcomeTime = document.getElementById('welcomeTime');
        if (welcomeTime) {
            welcomeTime.textContent = this.formatTime(new Date());
        }
    }

    adjustTextareaHeight() {
        const textarea = this.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isTyping;
    }

    async checkApiStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.setStatus('connected', 'Connected');
            } else if (data.status === 'degraded') {
                this.setStatus('warning', 'Degraded');
            } else {
                this.setStatus('error', 'Error');
            }
        } catch (error) {
            this.setStatus('error', 'Offline');
            console.error('Health check failed:', error);
        }
    }

    setStatus(type, text) {
        this.statusDot.className = `status-dot ${type}`;
        this.statusText.textContent = text;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // Add user message to UI
        this.addMessage('user', message);
        this.conversationHistory.push({ role: 'user', content: message });

        // Clear input
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        this.updateSendButton();

        // Set typing state
        this.setTyping(true);

        try {
            if (this.isStreaming) {
                await this.sendStreamingMessage();
            } else {
                await this.sendRegularMessage();
            }
        } catch (error) {
            this.addMessage('bot', '❌ Sorry, I encountered an error. Please try again.');
            console.error('Send message error:', error);
        } finally {
            this.setTyping(false);
        }
    }

    async sendRegularMessage() {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: this.conversationHistory,
                stream: false
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        this.addMessage('bot', data.response);
        this.conversationHistory.push({ role: 'assistant', content: data.response });
    }

    async sendStreamingMessage() {
        // Add typing indicator
        const typingElement = this.addTypingIndicator();

        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messages: this.conversationHistory,
                stream: true
            })
        });

        if (!response.ok) {
            this.removeTypingIndicator(typingElement);
            throw new Error(`HTTP ${response.status}`);
        }

        // Remove typing indicator and prepare for streaming
        this.removeTypingIndicator(typingElement);
        const messageElement = this.addMessage('bot', '', true);
        const textElement = messageElement.querySelector('.message-text');
        
        let fullResponse = '';
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        break;
                    }
                    
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.content) {
                            fullResponse += parsed.content;
                            textElement.textContent = fullResponse;
                            this.scrollToBottom();
                        }
                    } catch (e) {
                        // Ignore JSON parsing errors for partial chunks
                    }
                }
            }
        }

        this.conversationHistory.push({ role: 'assistant', content: fullResponse });
    }

    addMessage(role, content, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = role === 'bot' ? '<i class="fas fa-magic"></i>' : '<i class="fas fa-user"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.textContent = content;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.formatTime(new Date());

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        
        if (!isStreaming) {
            this.scrollToBottom();
        }

        return messageDiv;
    }

    addTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = '<i class="fas fa-magic"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <span>Wh0Dini-AI is thinking</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        contentDiv.appendChild(typingDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    removeTypingIndicator(element) {
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }

    setTyping(typing) {
        this.isTyping = typing;
        this.updateSendButton();
        
        if (typing) {
            this.sendButton.innerHTML = '<i class="fas fa-circle-notch spinning"></i>';
        } else {
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    }

    clearChat() {
        // Keep only the welcome message
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message').parentElement;
        this.chatMessages.innerHTML = '';
        this.chatMessages.appendChild(welcomeMessage);
        
        // Clear conversation history
        this.conversationHistory = [];
        
        // Update welcome time
        this.setWelcomeTime();
    }

    toggleStreaming() {
        this.isStreaming = !this.isStreaming;
        this.streamToggle.classList.toggle('active');
        
        const icon = this.streamToggle.querySelector('i');
        const text = this.streamToggle.childNodes[1];
        
        if (this.isStreaming) {
            icon.className = 'fas fa-stream';
            text.textContent = ' Streaming: ON';
        } else {
            icon.className = 'fas fa-pause';
            text.textContent = ' Streaming: OFF';
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 10);
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
}

// Initialize the chat when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.wh0diniChat = new Wh0DiniChat();
});

// Auto-refresh status every 30 seconds
setInterval(() => {
    if (window.wh0diniChat) {
        window.wh0diniChat.checkApiStatus();
    }
}, 30000);
