/**
 * WhiteLabelRAG Frontend Application
 */

class WhiteLabelRAGApp {
    constructor() {
        this.socket = null;
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        this.messageHistory = [];
        
        // Wait for DOM and Socket.IO to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }
    
    initialize() {
        // Check if Socket.IO is available
        if (typeof io === 'undefined') {
            console.error('Socket.IO not loaded. Retrying in 100ms...');
            setTimeout(() => this.initialize(), 100);
            return;
        }
        
        this.initializeElements();
        this.initializeSocket();
        this.bindEvents();
        this.loadFiles();
        this.startHealthCheck();
        
        console.log('WhiteLabelRAG application initialized');
    }
    
    generateSessionId() {
        // Generate a unique session ID using timestamp and random number
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
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
        
        // Workflow elements
        this.workflowWaypoints = document.getElementById('workflowWaypoints');
        this.workflowProgress = document.getElementById('workflowProgress');
        this.taskStepsContainer = document.getElementById('taskStepsContainer');
        this.taskSteps = document.getElementById('taskSteps');
        
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
        
        // Mobile elements
        this.mobileUploadForm = document.getElementById('mobileUploadForm');
        this.mobileFileInput = document.getElementById('mobileFileInput');
        this.mobileUploadStatus = document.getElementById('mobileUploadStatus');
        this.mobileFilesList = document.getElementById('mobileFilesList');
        this.mobileRefreshFiles = document.getElementById('mobileRefreshFiles');
        this.mobileDocCount = document.getElementById('mobileDocCount');
        this.mobileSystemStatus = document.getElementById('mobileSystemStatus');
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
            
            // If we have workflow information, update the waypoints
            if (data.workflow) {
                this.updateWorkflowWaypoints(data.workflow);
            }
            
            // If we have task steps information, update the steps
            if (data.steps) {
                this.updateTaskSteps(data.steps);
            }
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
        
        // Mobile file upload
        if (this.mobileUploadForm) {
            this.mobileUploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                // Use the mobile file input but the same upload method
                this.fileInput = this.mobileFileInput;
                this.uploadStatus = this.mobileUploadStatus;
                this.uploadFiles();
                // Reset to desktop references
                setTimeout(() => {
                    this.fileInput = document.getElementById('fileInput');
                    this.uploadStatus = document.getElementById('uploadStatus');
                }, 500);
            });
            
            // Mobile file input change
            this.mobileFileInput.addEventListener('change', () => {
                this.validateFileSelection();
            });
        }
        
        // Refresh files
        this.refreshFiles.addEventListener('click', () => {
            this.loadFiles();
        });
        
        // Mobile refresh files
        if (this.mobileRefreshFiles) {
            this.mobileRefreshFiles.addEventListener('click', () => {
                this.loadFiles();
            });
        }
        
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
        
        // Show typing indicator if available
        if (window.typingIndicator) {
            window.typingIndicator.show('Processing your request...');
        }
        
        // Send via WebSocket
        this.socket.emit('chat_message', {
            message: message,
            session_id: this.sessionId
        });
        
        // Update status
        this.updateAssistantStatus({
            status: 'processing',
            progress: 0,
            details: 'Sending message...',
            workflow: {
                steps: [
                    { label: 'Query' },
                    { label: 'Search Docs' },
                    { label: 'Analyze' },
                    { label: 'Generate' },
                    { label: 'Respond' }
                ],
                currentStep: 0,
                taskSteps: [
                    { 
                        icon: 'bi-search', 
                        title: 'Process Query', 
                        description: 'Analyzing your question for key information'
                    },
                    { 
                        icon: 'bi-database-search', 
                        title: 'Search Documents', 
                        description: 'Finding relevant information in your documents'
                    },
                    { 
                        icon: 'bi-lightbulb', 
                        title: 'Context Building', 
                        description: 'Building context from search results'
                    },
                    { 
                        icon: 'bi-cpu', 
                        title: 'Generate Response', 
                        description: 'Creating an accurate and helpful response'
                    },
                    { 
                        icon: 'bi-check-circle', 
                        title: 'Final Review', 
                        description: 'Reviewing and polishing the response'
                    }
                ],
                currentTaskStep: 0,
                taskProgress: 20
            }
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
        
        // Update document count progress based on sources length
        this.updateDocumentProgress(sources.length);
        
        // Complete the workflow visualization
        this.updateAssistantStatus({
            status: 'completed',
            progress: 100,
            details: 'Response delivered',
            workflow: {
                steps: [
                    { label: 'Query' },
                    { label: 'Search Docs' },
                    { label: 'Analyze' },
                    { label: 'Generate' },
                    { label: 'Respond' }
                ],
                currentStep: 4,  // Last step
                taskSteps: [
                    { 
                        icon: 'bi-search', 
                        title: 'Process Query', 
                        description: 'Analyzing your question for key information'
                    },
                    { 
                        icon: 'bi-database-search', 
                        title: 'Search Documents', 
                        description: 'Finding relevant information in your documents'
                    },
                    { 
                        icon: 'bi-lightbulb', 
                        title: 'Context Building', 
                        description: 'Building context from search results'
                    },
                    { 
                        icon: 'bi-cpu', 
                        title: 'Generate Response', 
                        description: 'Creating an accurate and helpful response'
                    },
                    { 
                        icon: 'bi-check-circle', 
                        title: 'Final Review', 
                        description: 'Reviewing and polishing the response'
                    }
                ],
                currentTaskStep: 4,  // Last task step
                taskProgress: 100
            }
        });
        
        // Clear status
        this.clearAssistantStatus();
    }
    
    updateDocumentProgress(sourceCount) {
        // Update document progress bars
        const docProgress = document.getElementById('docProgress');
        const mobileDocProgress = document.getElementById('mobileDocProgress');
        
        if (docProgress) {
            // Calculate percentage based on sources used vs total docs
            const totalDocs = parseInt(this.docCount.textContent) || 1;
            const percentage = Math.min(100, (sourceCount / totalDocs) * 100);
            docProgress.style.width = `${percentage}%`;
        }
        
        if (mobileDocProgress) {
            const totalDocs = parseInt(this.docCount.textContent) || 1;
            const percentage = Math.min(100, (sourceCount / totalDocs) * 100);
            mobileDocProgress.style.width = `${percentage}%`;
        }
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
            
            // Update typing indicator if available
            if (window.typingIndicator) {
                if (details) {
                    window.typingIndicator.update(details);
                }
                
                // Determine phase based on workflow data
                if (data.workflow && data.workflow.currentStep !== undefined) {
                    const phase = data.workflow.currentStep === 0 ? 'query' :
                                 data.workflow.currentStep === 1 ? 'search' :
                                 data.workflow.currentStep === 2 ? 'analyze' : 
                                 data.workflow.currentStep === 3 ? 'generate' : 'final';
                    window.typingIndicator.showLoadingMessage(phase, progress);
                }
            }
        } else {
            setTimeout(() => {
                this.statusBadge.style.display = 'none';
                
                // Hide typing indicator
                if (window.typingIndicator && status === 'completed') {
                    window.typingIndicator.hide();
                }
            }, 2000);
        }
        
        // Update workflow visualization if available
        this.updateWorkflowVisualization(data);
    }
    
    updateWorkflowVisualization(data) {
        // Check if we have workflow data
        if (data.workflow) {
            // If we have steps, setup the workflow
            if (data.workflow.steps && data.workflow.steps.length > 0) {
                if (typeof window.setupWorkflow === 'function') {
                    window.setupWorkflow(data.workflow.steps);
                }
                
                // If we have a current step, update progress
                if (data.workflow.currentStep !== undefined) {
                    if (typeof window.updateWorkflowProgress === 'function') {
                        window.updateWorkflowProgress(
                            data.workflow.currentStep, 
                            data.workflow.steps.length
                        );
                    }
                }
            }
            
            // If we have task steps, show them
            if (data.workflow.taskSteps && data.workflow.taskSteps.length > 0) {
                if (typeof window.showTaskSteps === 'function') {
                    window.showTaskSteps(data.workflow.taskSteps);
                }
                
                // If we have a current task step and progress, update it
                if (data.workflow.currentTaskStep !== undefined && data.workflow.taskProgress !== undefined) {
                    if (typeof window.updateTaskStepProgress === 'function') {
                        window.updateTaskStepProgress(
                            data.workflow.currentTaskStep, 
                            data.workflow.taskProgress
                        );
                    }
                }
            }
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
        
        // Show upload progress animation
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 5;
            if (progress > 90) clearInterval(progressInterval);
            if (window.showUploadProgress) {
                window.showUploadProgress('uploadStatus', progress);
                window.showUploadProgress('mobileUploadStatus', progress);
            }
        }, 200);
        
        try {
            const response = await fetch('/api/documents/upload_and_ingest_document', {
                method: 'POST',
                body: formData
            });
            
            // Complete the progress animation
            clearInterval(progressInterval);
            if (window.showUploadProgress) {
                window.showUploadProgress('uploadStatus', 100);
                window.showUploadProgress('mobileUploadStatus', 100);
            }
            
            const result = await response.json();
            
            if (response.ok) {
                this.showUploadStatus(`✅ ${file.name} uploaded and processed successfully!`, 'success');
                
                // Add a message to chat about the upload
                this.addMessage(`📄 Document "${file.name}" has been uploaded and processed. You can now ask questions about it!`, false);
            } else {
                this.showUploadStatus(`❌ Error uploading ${file.name}: ${result.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            // Clear progress animation on error
            clearInterval(progressInterval);
            console.error('Upload error:', error);
            this.showUploadStatus(`❌ Error uploading ${file.name}: ${error.message || 'Connection error'}`, 'error');
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
        
        // If we have the enhanceFileCards function from our UI enhancer, use it
        if (typeof window.enhanceFileCards === 'function') {
            // First show skeleton loading
            if (typeof window.showSkeletonLoading === 'function') {
                window.showSkeletonLoading('filesList', Math.min(files.length, 5));
            }
            
            // Convert the files to the format expected by enhanceFileCards
            const enhancedFiles = files.map(file => ({
                filename: file.name,
                size: this.formatFileSize(file.size),
                date: this.formatDate(file.modified),
                // Random usage percentage for visual interest - would be replaced with real data in production
                usage: Math.floor(Math.random() * 100)
            }));
            
            // Slight delay to show the skeleton effect
            setTimeout(() => {
                const fileCardsHtml = enhancedFiles.map(file => {
                    // Determine file type icon
                    let iconClass = 'bi-file-earmark';
                    if (file.filename.match(/\.pdf$/i)) {
                        iconClass = 'bi-file-earmark-pdf file-icon-pdf';
                    } else if (file.filename.match(/\.(docx?|rtf|txt|md)$/i)) {
                        iconClass = 'bi-file-earmark-text file-icon-doc';
                    } else if (file.filename.match(/\.(jpe?g|png|gif|bmp|svg)$/i)) {
                        iconClass = 'bi-file-earmark-image file-icon-image';
                    } else if (file.filename.match(/\.(mp3|wav|ogg|flac)$/i)) {
                        iconClass = 'bi-file-earmark-music file-icon-audio';
                    } else if (file.filename.match(/\.(mp4|mov|avi|mkv|webm)$/i)) {
                        iconClass = 'bi-file-earmark-play file-icon-video';
                    }
                    
                    return `
                    <div class="file-card elevation-1 elevation-hover">
                        <div class="d-flex">
                            <div class="file-icon">
                                <i class="bi ${iconClass}"></i>
                            </div>
                            <div class="file-info">
                                <div class="file-name">${file.filename}</div>
                                <div class="file-meta">
                                    ${file.size || 'Unknown size'} • ${file.date || 'Recently added'}
                                </div>
                                <div class="file-stats">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">Usage</small>
                                        <small class="text-muted">${file.usage}%</small>
                                    </div>
                                    <div class="file-stat-bar">
                                        <div class="file-stat-fill" style="width: ${file.usage}%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>`;
                }).join('');
                
                this.filesList.innerHTML = fileCardsHtml;
                
                // Do the same for mobile file list if it exists
                if (this.mobileFilesList) {
                    this.mobileFilesList.innerHTML = fileCardsHtml;
                }
            }, 500);
        } else {
            // Fallback to original implementation
            const filesHtml = files.map(file => `
                <div class="file-item">
                    <div class="file-name">${file.name}</div>
                    <div class="file-meta">${this.formatFileSize(file.size)} • ${this.formatDate(file.modified)}</div>
                </div>
            `).join('');
            
            this.filesList.innerHTML = filesHtml;
            
            // Update mobile file list if it exists
            if (this.mobileFilesList) {
                this.mobileFilesList.innerHTML = filesHtml;
            }
        }
    }
    
    updateStats(fileCount) {
        this.docCount.textContent = fileCount;
        this.systemStatus.textContent = this.isConnected ? 'Ready' : 'Disconnected';
    }
    
    formatFileSize(sizeInBytes) {
        if (sizeInBytes === undefined || sizeInBytes === null) return 'Unknown size';
        
        // Convert to number if it's a string
        const size = typeof sizeInBytes === 'string' ? parseInt(sizeInBytes, 10) : sizeInBytes;
        
        if (isNaN(size) || size === 0) return 'Unknown size';
        
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let i = 0;
        let fileSize = size;
        
        while (fileSize >= 1024 && i < units.length - 1) {
            fileSize /= 1024;
            i++;
        }
        
        return `${fileSize.toFixed(1)} ${units[i]}`;
    }
    
    formatDate(dateStr) {
        if (!dateStr) return 'Unknown date';
        
        try {
            const date = new Date(dateStr);
            
            // Check if date is valid
            if (isNaN(date.getTime())) return 'Unknown date';
            
            // Get current date for comparison
            const now = new Date();
            const yesterday = new Date(now);
            yesterday.setDate(now.getDate() - 1);
            
            // Format based on how recent the date is
            if (date.toDateString() === now.toDateString()) {
                return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
            } else if (date.toDateString() === yesterday.toDateString()) {
                return `Yesterday at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
            } else {
                // For older dates
                return date.toLocaleDateString([], { 
                    year: 'numeric', 
                    month: 'short', 
                    day: 'numeric'
                });
            }
        } catch (e) {
            console.error('Date formatting error:', e);
            return 'Unknown date';
        }
    }
    
    validateFileSelection() {
        const files = this.fileInput.files;
        const allowedTypes = ['.pdf', '.docx', '.txt', '.md', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp3', '.wav', '.mp4', '.avi', '.mov'];
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
    
    // Workflow Waypoints Methods
    updateWorkflowWaypoints(workflow) {
        if (!this.workflowWaypoints || !workflow) return;
        
        // Show the workflow waypoints container
        this.workflowWaypoints.classList.remove('d-none');
        
        // Clear existing waypoints
        const waypointElements = this.workflowWaypoints.querySelectorAll('.waypoint, .waypoint-label');
        waypointElements.forEach(el => el.remove());
        
        const steps = workflow.steps || [];
        const currentStep = workflow.currentStep || 0;
        const totalSteps = steps.length;
        
        if (totalSteps === 0) {
            this.workflowWaypoints.classList.add('d-none');
            return;
        }
        
        // Calculate progress percentage
        const progressPercentage = (currentStep / totalSteps) * 100;
        this.workflowProgress.style.width = `${progressPercentage}%`;
        
        // Add waypoints
        steps.forEach((step, index) => {
            const position = (index / (totalSteps - 1)) * 100;
            
            // Create waypoint dot
            const waypoint = document.createElement('div');
            waypoint.className = 'waypoint';
            if (index < currentStep) {
                waypoint.classList.add('completed');
            } else if (index === currentStep) {
                waypoint.classList.add('active');
            }
            waypoint.style.left = `${position}%`;
            this.workflowWaypoints.querySelector('.workflow-track').appendChild(waypoint);
            
            // Create waypoint label
            const label = document.createElement('div');
            label.className = 'waypoint-label';
            if (index === currentStep) {
                label.classList.add('active');
            }
            label.style.left = `${position}%`;
            label.textContent = step.name || `Step ${index + 1}`;
            label.title = step.description || label.textContent;
            this.workflowWaypoints.appendChild(label);
        });
    }
    
    updateTaskSteps(steps) {
        if (!this.taskStepsContainer || !this.taskSteps || !steps || !steps.length) {
            if (this.taskStepsContainer) {
                this.taskStepsContainer.classList.add('d-none');
            }
            return;
        }
        
        // Show the task steps container
        this.taskStepsContainer.classList.remove('d-none');
        
        // Clear existing steps
        this.taskSteps.innerHTML = '';
        
        // Add task steps
        steps.forEach((step, index) => {
            const stepEl = document.createElement('div');
            stepEl.className = 'task-step';
            
            if (step.status === 'active') {
                stepEl.classList.add('active');
            } else if (step.status === 'completed') {
                stepEl.classList.add('completed');
            }
            
            const iconClass = this.getStepIconClass(step.status, step.type);
            
            stepEl.innerHTML = `
                <div class="step-icon">
                    <i class="${iconClass}"></i>
                </div>
                <div class="step-content">
                    <div class="step-title">${step.title || `Step ${index + 1}`}</div>
                    <div class="step-description">${step.description || ''}</div>
                    <div class="step-progress">
                        <div class="step-progress-bar" style="width: ${step.progress || 0}%"></div>
                    </div>
                </div>
            `;
            
            this.taskSteps.appendChild(stepEl);
        });
    }
    
    getStepIconClass(status, type) {
        // Default icon is a circle
        let iconClass = 'bi bi-circle';
        
        // Determine icon by type
        switch (type) {
            case 'processing':
                iconClass = 'bi bi-gear';
                break;
            case 'search':
                iconClass = 'bi bi-search';
                break;
            case 'document':
                iconClass = 'bi bi-file-text';
                break;
            case 'generation':
                iconClass = 'bi bi-stars';
                break;
            case 'analysis':
                iconClass = 'bi bi-graph-up';
                break;
            case 'completion':
                iconClass = 'bi bi-check-circle';
                break;
            case 'error':
                iconClass = 'bi bi-exclamation-triangle';
                break;
        }
        
        // Add status-specific classes
        if (status === 'completed') {
            iconClass = 'bi bi-check-circle-fill text-success';
        } else if (status === 'error') {
            iconClass = 'bi bi-x-circle-fill text-danger';
        } else if (status === 'active') {
            iconClass += ' text-primary';
        }
        
        return iconClass;
    }
}

// Global functions for quick actions
window.sendQuickMessage = function(message) {
    if (window.app) {
        window.app.sendQuickMessage(message);
    }
};

// Initialize app - the constructor will handle DOM ready checking
window.app = new WhiteLabelRAGApp();
console.log('WhiteLabelRAG application started');
