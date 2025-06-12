/**
 * WhiteLabelRAG Frontend Application
 */

class WhiteLabelRAGApp {
    constructor() {
        this.socket = null;
        this.sessionId = this.generateSessionId();
        this.isConnected = false;
        this.messageHistory = [];
        this.statusMinimized = false; // Track minimize state
        
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
        
        // Add minimize button to status badge
        this.addStatusMinimizeButton();
        
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
    
    addStatusMinimizeButton() {
        if (!this.statusBadge) return;
        
        // Create minimize button element
        const btn = document.createElement('button');
        btn.id = 'statusMinimizeBtn';
        btn.textContent = '−'; // Unicode minus sign
        btn.title = 'Minimize status display';
        btn.style.marginLeft = '10px';
        btn.style.background = 'transparent';
        btn.style.border = 'none';
        btn.style.color = '#333';
        btn.style.fontSize = '1.2rem';
        btn.style.cursor = 'pointer';
        btn.style.userSelect = 'none';
        
        // Add click event to toggle minimize
        btn.addEventListener('click', () => {
            this.statusMinimized = !this.statusMinimized;
            if (this.statusMinimized) {
                this.statusBadge.style.height = '24px';
                this.statusText.style.display = 'none';
                this.progressBar.style.display = 'none';
                btn.textContent = '+';
                btn.title = 'Restore status display';
            } else {
                this.statusBadge.style.height = '';
                this.statusText.style.display = '';
                this.progressBar.style.display = '';
                btn.textContent = '−';
                btn.title = 'Minimize status display';
            }
        });
        
        // Append button to status badge
        this.statusBadge.appendChild(btn);
    }
    
    updateAssistantStatus(data) {
        const status = data.status || 'idle';
        const progress = data.progress || 0;
        const details = data.details || '';
        
        if (this.statusMinimized) {
            // If minimized, only update statusText content but keep hidden
            this.statusText.textContent = details || status;
            return;
        }
        
        this.statusText.textContent = details || status;
        this.progressBar.style.width = `${progress}%`;
        
        // Update indicator
        this.statusIndicator.className = 'status-indicator';
        if (status === 'processing' || status === 'running') {
            this.statusIndicator.classList.add('processing');
        } else if (status === 'completed') {
            this.statusIndicator.classList.add('active');
            // Fade out after 5 seconds
            setTimeout(() => {
                this.statusBadge.style.transition = 'opacity 1s ease';
                this.statusBadge.style.opacity = '0';
                this.progressBar.style.transition = 'opacity 1s ease';
                this.progressBar.style.opacity = '0';
                setTimeout(() => {
                    this.statusBadge.style.display = 'none';
                    this.statusBadge.style.opacity = '';
                    this.progressBar.style.opacity = '';
                    this.clearAssistantStatus();
                }, 1000);
            }, 5000);
        } else if (status === 'failed' || status === 'error') {
            this.statusIndicator.classList.add('error');
        }
        
        // Show/hide status badge
        if (status !== 'idle' && status !== 'completed') {
            this.statusBadge.style.display = 'flex';
            this.statusBadge.style.opacity = '1';
            
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
        }
        
        // Update workflow visualization if available
        this.updateWorkflowVisualization(data);
    }
    
    // ... rest of the class unchanged ...
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

// Add method to fetch and display accuracy and regression metrics
WhiteLabelRAGApp.prototype.fetchAndDisplayMetrics = async function() {
    try {
        const response = await fetch('/api/metrics/accuracy_regression');
        if (!response.ok) {
            console.error('Failed to fetch accuracy and regression metrics');
            return;
        }
        const data = await response.json();
        const accuracy = data.accuracy_percent;
        const regression = data.regression_percent;
        
        // Display metrics in status badge or create a dedicated element
        let metricsEl = document.getElementById('accuracyRegressionMetrics');
        if (!metricsEl) {
            metricsEl = document.createElement('div');
            metricsEl.id = 'accuracyRegressionMetrics';
            metricsEl.style.fontSize = '0.9rem';
            metricsEl.style.marginLeft = '15px';
            metricsEl.style.color = '#444';
            this.statusBadge.appendChild(metricsEl);
        }
        metricsEl.textContent = `Accuracy: ${accuracy}% | Regression: ${regression}%`;
    } catch (error) {
        console.error('Error fetching accuracy and regression metrics:', error);
    }
};

// Call fetchAndDisplayMetrics periodically, e.g., every 60 seconds
setInterval(() => {
    if (window.app) {
        window.app.fetchAndDisplayMetrics();
    }
}, 60000);

// Initial call on load
if (window.app) {
    window.app.fetchAndDisplayMetrics();
}
</create_file>
