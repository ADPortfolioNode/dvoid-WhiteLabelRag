/**
 * WhiteLabelRAG Typing Indicator
 * 
 * Provides visual feedback when the assistant is typing
 */

class TypingIndicator {
    constructor() {
        this.initialize();
    }
    
    initialize() {
        this.createIndicator();
        this.bindEvents();
    }
    
    createIndicator() {
        // Create the typing indicator element
        this.indicator = document.createElement('div');
        this.indicator.className = 'typing-indicator message message-assistant';
        this.indicator.innerHTML = `
            <div class="message-content typing-indicator-content">
                <div class="typing-animation">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <div class="typing-label">Assistant is thinking...</div>
            </div>
        `;
        
        // Hide initially
        this.indicator.style.display = 'none';
        
        // Add to chat container
        const chatContainer = document.getElementById('chatContainer');
        if (chatContainer) {
            chatContainer.appendChild(this.indicator);
        }
    }
    
    bindEvents() {
        // Expose methods globally
        window.typingIndicator = {
            show: this.show.bind(this),
            hide: this.hide.bind(this),
            update: this.update.bind(this),
            showLoadingMessage: this.showLoadingMessage.bind(this)
        };
        
        // Listen for socket events
        if (window.app && window.app.socket) {
            window.app.socket.on('assistant_status', (data) => {
                if (data.status === 'processing' || data.status === 'running') {
                    this.show(data.details || 'Processing...');
                } else if (data.status === 'completed' || data.status === 'idle') {
                    this.hide();
                } else if (data.status === 'error') {
                    this.hide();
                }
            });
            
            window.app.socket.on('chat_response', () => {
                this.hide();
            });
        }
    }
    
    show(message = 'Assistant is thinking...') {
        this.indicator.style.display = 'block';
        this.update(message);
        this.scrollIntoView();
    }
    
    hide() {
        this.indicator.style.display = 'none';
    }
    
    update(message) {
        const label = this.indicator.querySelector('.typing-label');
        if (label) {
            label.textContent = message;
        }
    }
    
    scrollIntoView() {
        const chatContainer = document.getElementById('chatContainer');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    showLoadingMessage(phase, progress) {
        let message = 'Assistant is thinking...';
        
        switch (phase) {
            case 'query':
                message = 'Processing your question...';
                break;
            case 'search':
                message = 'Searching through documents...';
                break;
            case 'analyze':
                message = 'Analyzing relevant information...';
                break;
            case 'generate':
                message = 'Generating a response...';
                break;
            case 'final':
                message = 'Finalizing response...';
                break;
            default:
                message = 'Working on your request...';
        }
        
        // Add progress if provided
        if (progress !== undefined && progress !== null) {
            message += ` (${Math.round(progress)}%)`;
        }
        
        this.update(message);
        this.show();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.typingIndicatorInstance = new TypingIndicator();
});
