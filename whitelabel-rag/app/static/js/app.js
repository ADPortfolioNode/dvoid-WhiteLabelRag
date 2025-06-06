/**
 * WhiteLabelRAG Frontend Application
 */

class WhiteLabelRAGApp {
    constructor() {
        this.socket = null;
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        this.messageHistory = [];
        
        this.initializeElements();
        this.initializeSocket();
        this.bindEvents();
        this.loadFiles();
    }
    
    initializeElements() {
        // Chat elements
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        
        // Status elements
        this.statusBadge = document.getElementById('statusBadge');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        this.progressBar = document.getElementById('progressBar');
        this.connectionStatus = document.getElementById('connectionStatus');
        
        // File elements
        this.uploadForm = document.getElementById('uploadForm');
        this.fileInput = document.getElementById('fileInput');
        this.uploadStatus = document.getElementById('uploadStatus');
        this.filesList = document.getElementById('filesList');
        this.refreshFiles = document.getElementById('refreshFiles');
        
        // Control elements
        this.clearChat = document.getElementById('clearChat');
        
        // Stats elements
        this.docCount = document.getElementById('docCount');
        this.systemStatus = document.getElementById('systemStatus');
    }
    
    initializeSocket() {
        const socketOptions = {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: 15,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 8000,
            timeout: 30000,
            autoConnect: true,
            forceNew: false,
            upgrade: true,
            rememberUpgrade: true,
            pingInterval: 15000,
            pingTimeout: 10000
        };
        
        this.socket = io(socketOptions);
        
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.isConnected = true;
            this.updateConnectionStatus('connected');
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log('Disconnected from server:', reason);
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.updateConnectionStatus('error');
        });
        
        // Message events
        this.socket.on('chat_response', (data) => {
            this.handleChatResponse(data);
        });
        
        this.socket.on('assistant_status', (data) => {
            this.updateAssistantStatus(data);
        });
        
        this.socket.on('assistant_status_update', (data) => {
            this.updateAssistantStatus(data);
        });
        
        // Health check
        this.socket.on('health_check_response', (data) => {
            console.log('Health check response:', data);
        });
        
        // Error handling
        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.addMessage('System error occurred. Please try again.', false, true);
        });
    }
    
    bindEvents() {
        // Chat form submission
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // File upload
        this.uploadForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.uploadFiles();
        });
        
        // Refresh files
        this.refreshFiles.addEventListener('click', () => {
            this.loadFiles();
        });
        
        // Clear chat
        this.clearChat.addEventListener('click', () => {
            this.clearChatHistory();
        });
        
        // Enter key handling
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize input
        this.messageInput.addEventListener('input', () => {
            this.autoResizeInput();
        });
        
        // File input change
        this.fileInput.addEventListener('change', () => {
            this.validateFileSelection();
        });
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        if (!this.isConnected) {
            this.showError('Not connected to server. Please wait for reconnection.');
            return;
        }
        
        // Add user message to chat
        this.addMessage(message, true);
        
        // Clear input
        this.messageInput.value = '';
        this.autoResizeInput();
        
        // Send via WebSocket
        this.socket.emit('chat_message', {
            message: message,
            session_id: this.sessionId
        });
        
        // Update status
        this.updateAssistantStatus({
            status: 'processing',
            progress: 0,
            details: 'Sending message...'
        });
    }
    
    handleChatResponse(data) {
        const text = data.text || 'No response received';
        const sources = data.sources || [];
        const error = data.error || false;
        
        this.addMessage(text, false, error, sources);
        
        // Update message history
        this.messageHistory.push({
            user: this.messageInput.value,
            assistant: text,
            timestamp: new Date().toISOString(),
            sources: sources
        });
        
        // Clear status
        this.clearAssistantStatus();
    }
    
    addMessage(content, isUser = false, isError = false, sources = []) {
        // Remove welcome message if it exists
        const welcomeMessage = this.chatContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'message-user' : 'message-assistant'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (isError) {
            contentDiv.style.backgroundColor = '#f8d7da';
            contentDiv.style.color = '#721c24';
            contentDiv.style.borderColor = '#f5c6cb';
        }
        
        // Format content (basic markdown-like formatting)
        const formattedContent = this.formatMessageContent(content);
        contentDiv.innerHTML = formattedContent;
        
        messageDiv.appendChild(contentDiv);
        
        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            sourcesDiv.innerHTML = '<strong>Sources:</strong> ' + 
                sources.map(source => `<span class="source-tag">${source}</span>`).join('');
            contentDiv.appendChild(sourcesDiv);
        }
        
        // Add timestamp
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        metaDiv.textContent = new Date().toLocaleTimeString();
        messageDiv.appendChild(metaDiv);
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessageContent(content) {
        // Basic formatting for better readability
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Italic
            .replace(/`(.*?)`/g, '<code>$1</code>')            // Code
            .replace(/\n/g, '<br>')                            // Line breaks
            .replace(/#{1,6}\s*(.*)/g, '<h6>$1</h6>')         // Headers
            .replace(/•\s*(.*)/g, '• $1')                      // Bullet points
            .replace(/(\d+\.)\s*(.*)/g, '$1 $2');             // Numbered lists
    }
    
    updateAssistantStatus(data) {
        const status = data.status || 'idle';
        const progress = data.progress || 0;
        const details = data.details || '';
        
        this.statusText.textContent = details || status;
        this.progressBar.style.width = `${progress}%`;
        
        // Update indicator
        this.statusIndicator.className = 'status-indicator';
        if (status === 'processing' || status === 'running') {
            this.statusIndicator.classList.add('processing');
        } else if (status === 'completed') {
            this.statusIndicator.classList.add('active');
        } else if (status === 'failed' || status === 'error') {
            this.statusIndicator.classList.add('error');
        }
        
        // Show/hide status badge
        if (status !== 'idle' && status !== 'completed') {
            this.statusBadge.style.display = 'flex';
        } else {
            setTimeout(() => {
                this.statusBadge.style.display = 'none';
            }, 2000);
        }
    }
    
    clearAssistantStatus() {
        setTimeout(() => {
            this.statusBadge.style.display = 'none';
            this.statusText.textContent = 'Ready';
            this.progressBar.style.width = '0%';
            this.statusIndicator.className = 'status-indicator';
        }, 1500);
    }
    
    updateConnectionStatus(status) {
        this.connectionStatus.className = `connection-status ${status}`;
        
        const statusText = this.connectionStatus.querySelector('span');
        const statusIcon = this.connectionStatus.querySelector('i');
        
        switch (status) {
            case 'connected':
                statusText.textContent = 'Connected';
                statusIcon.className = 'bi bi-circle-fill text-success';
                break;
            case 'disconnected':
                statusText.textContent = 'Disconnected';
                statusIcon.className = 'bi bi-circle-fill text-danger';
                break;
            case 'connecting':
                statusText.textContent = 'Connecting...';
                statusIcon.className = 'bi bi-circle-fill text-warning';
                break;
            case 'error':
                statusText.textContent = 'Connection Error';
                statusIcon.className = 'bi bi-circle-fill text-danger';
                break;
        }
    }
    
    async uploadFiles() {
        const files = this.fileInput.files;
        if (!files || files.length === 0) {
            this.showUploadStatus('Please select files to upload.', 'error');
            return;
        }
        
        this.showUploadStatus('Uploading files...', 'processing');
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            await this.uploadSingleFile(file);
        }
        
        // Clear file input
        this.fileInput.value = '';
        
        // Refresh file list
        this.loadFiles();
    }
    
    async uploadSingleFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/documents/upload_and_ingest_document', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showUploadStatus(`✅ ${file.name} uploaded and processed successfully!`, 'success');
                
                // Add a message to chat about the upload
                this.addMessage(`📄 Document "${file.name}" has been uploaded and processed. You can now ask questions about it!`, false);
            } else {
                this.showUploadStatus(`❌ Error uploading ${file.name}: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showUploadStatus(`❌ Error uploading ${file.name}: ${error.message}`, 'error');
        }
    }
    
    showUploadStatus(message, type) {
        this.uploadStatus.innerHTML = `<div class="upload-status ${type}">${message}</div>`;
        
        if (type === 'success') {
            setTimeout(() => {
                this.uploadStatus.innerHTML = '';
            }, 5000);
        }
    }
    
    async loadFiles() {
        try {
            const response = await fetch('/api/files');
            const data = await response.json();
            
            if (response.ok) {
                this.displayFiles(data.files || []);
                this.updateStats(data.files ? data.files.length : 0);
            } else {
                console.error('Error loading files:', data.error);
                this.filesList.innerHTML = '<div class="text-muted small">Error loading files</div>';
            }
        } catch (error) {
            console.error('Error loading files:', error);
            this.filesList.innerHTML = '<div class="text-muted small">Error loading files</div>';
        }
    }
    
    displayFiles(files) {
        if (!files || files.length === 0) {
            this.filesList.innerHTML = '<div class="text-muted small">No files uploaded yet</div>';
            return;
        }
        
        const filesHtml = files.map(file => `
            <div class="file-item">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">${this.formatFileSize(file.size)} • ${this.formatDate(file.modified)}</div>
            </div>
        `).join('');
        
        this.filesList.innerHTML = filesHtml;
    }
    
    updateStats(fileCount) {
        this.docCount.textContent = fileCount;
        this.systemStatus.textContent = this.isConnected ? 'Ready' : 'Disconnected';
    }
    
    validateFileSelection() {
        const files = this.fileInput.files;
        const allowedTypes = ['.pdf', '.docx', '.txt', '.md', '.csv'];
        const maxSize = 16 * 1024 * 1024; // 16MB
        
        for (let file of files) {
            const extension = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!allowedTypes.includes(extension)) {
                this.showUploadStatus(`❌ File type not supported: ${file.name}`, 'error');
                this.fileInput.value = '';
                return false;
            }
            
            if (file.size > maxSize) {
                this.showUploadStatus(`❌ File too large: ${file.name} (max 16MB)`, 'error');
                this.fileInput.value = '';
                return false;
            }
        }
        
        return true;
    }
    
    clearChatHistory() {
        // Remove all messages except welcome message
        const messages = this.chatContainer.querySelectorAll('.message');
        messages.forEach(message => message.remove());
        
        // Add welcome message back
        this.chatContainer.innerHTML = `
            <div class="welcome-message">
                <div class="text-center">
                    <i class="bi bi-robot display-4 text-primary"></i>
                    <h4>Welcome to WhiteLabelRAG!</h4>
                    <p class="text-muted">
                        I'm your AI assistant with document search capabilities. 
                        Upload documents and ask me questions about them, or just have a conversation!
                    </p>
                    <div class="quick-actions">
                        <button class="btn btn-outline-primary btn-sm me-2" onclick="app.sendQuickMessage('What can you do?')">
                            What can you do?
                        </button>
                        <button class="btn btn-outline-primary btn-sm me-2" onclick="app.sendQuickMessage('Show me system stats')">
                            System Stats
                        </button>
                        <button class="btn btn-outline-primary btn-sm" onclick="app.sendQuickMessage('List my files')">
                            List Files
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Clear message history
        this.messageHistory = [];
    }
    
    sendQuickMessage(message) {
        this.messageInput.value = message;
        this.sendMessage();
    }
    
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    autoResizeInput() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
    
    showError(message) {
        this.addMessage(message, false, true);
    }
    
    // Health check
    startHealthCheck() {
        setInterval(() => {
            if (this.isConnected) {
                this.socket.emit('health_check');
            }
        }, 30000); // Every 30 seconds
    }
}

// Global functions for quick actions
window.sendQuickMessage = function(message) {
    if (window.app) {
        window.app.sendQuickMessage(message);
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.app = new WhiteLabelRAGApp();
    window.app.startHealthCheck();
    
    console.log('WhiteLabelRAG application initialized');
});