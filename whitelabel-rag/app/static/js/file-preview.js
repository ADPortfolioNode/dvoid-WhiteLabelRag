/**
 * File Preview Component for WhiteLabelRAG
 * Provides a modal-based file preview functionality
 */

class FilePreviewComponent {
    constructor() {
        this.modalId = 'filePreviewModal';
        this.createModal();
        this.bindEvents();
    }
    
    createModal() {
        // Check if modal already exists
        if (document.getElementById(this.modalId)) {
            return;
        }
        
        // Create modal HTML
        const modalHtml = `
            <div class="modal fade file-preview-modal" id="${this.modalId}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-lg modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header file-preview-header">
                            <h5 class="modal-title">
                                <i class="bi bi-file-earmark"></i>
                                <span id="filePreviewTitle">File Preview</span>
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body file-preview-body p-0">
                            <div class="file-preview-content">
                                <div class="file-preview-info">
                                    <div class="file-meta-item">
                                        <div class="file-meta-icon">
                                            <i class="bi bi-file-earmark"></i>
                                        </div>
                                        <div class="file-meta-label">Type:</div>
                                        <div class="file-meta-value" id="filePreviewType">Unknown</div>
                                    </div>
                                    <div class="file-meta-item">
                                        <div class="file-meta-icon">
                                            <i class="bi bi-rulers"></i>
                                        </div>
                                        <div class="file-meta-label">Size:</div>
                                        <div class="file-meta-value" id="filePreviewSize">Unknown</div>
                                    </div>
                                    <div class="file-meta-item">
                                        <div class="file-meta-icon">
                                            <i class="bi bi-calendar"></i>
                                        </div>
                                        <div class="file-meta-label">Modified:</div>
                                        <div class="file-meta-value" id="filePreviewDate">Unknown</div>
                                    </div>
                                </div>
                                <div class="file-preview-container" id="filePreviewContainer">
                                    <div class="preview-unavailable">
                                        <i class="bi bi-eye-slash"></i>
                                        <p>Preview not available</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer file-preview-footer">
                            <button type="button" class="btn btn-outline-secondary file-action-btn" data-bs-dismiss="modal">
                                <i class="bi bi-x"></i> Close
                            </button>
                            <div>
                                <button type="button" class="btn btn-primary file-action-btn me-2" id="filePreviewAnalyze">
                                    <i class="bi bi-search"></i> Analyze with AI
                                </button>
                                <button type="button" class="btn btn-outline-danger file-action-btn" id="filePreviewDelete">
                                    <i class="bi bi-trash"></i> Delete
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to document
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHtml;
        document.body.appendChild(modalContainer.firstElementChild);
    }
    
    bindEvents() {
        // Listen for file preview events
        document.addEventListener('filePreview', (e) => {
            this.showPreview(e.detail.filename, e.detail.file);
        });
        
        // Analyze button click
        document.getElementById('filePreviewAnalyze')?.addEventListener('click', () => {
            const filename = document.getElementById('filePreviewTitle')?.textContent;
            if (filename && window.app && typeof window.app.sendQuickMessage === 'function') {
                window.app.sendQuickMessage(`Analyze file: ${filename}`);
                this.closeModal();
            }
        });
        
        // Delete button click
        document.getElementById('filePreviewDelete')?.addEventListener('click', () => {
            const filename = document.getElementById('filePreviewTitle')?.textContent;
            if (filename && window.fileNavigation) {
                window.fileNavigation.deleteFile(filename);
                this.closeModal();
            }
        });
    }
    
    showPreview(filename, fileData) {
        if (!filename) return;
        
        // Update modal title and metadata
        document.getElementById('filePreviewTitle').textContent = filename;
        
        // Set file type
        let fileType = 'Unknown';
        let fileIconClass = 'bi-file-earmark';
        
        if (filename.match(/\.pdf$/i)) {
            fileType = 'PDF Document';
            fileIconClass = 'bi-file-earmark-pdf';
        } else if (filename.match(/\.docx?$/i)) {
            fileType = 'Word Document';
            fileIconClass = 'bi-file-earmark-word';
        } else if (filename.match(/\.(txt|md)$/i)) {
            fileType = filename.match(/\.md$/i) ? 'Markdown Document' : 'Text Document';
            fileIconClass = 'bi-file-earmark-text';
        } else if (filename.match(/\.(jpe?g|png|gif|bmp|svg)$/i)) {
            fileType = 'Image';
            fileIconClass = 'bi-file-earmark-image';
        } else if (filename.match(/\.(mp3|wav|ogg|flac)$/i)) {
            fileType = 'Audio';
            fileIconClass = 'bi-file-earmark-music';
        } else if (filename.match(/\.(mp4|mov|avi|mkv|webm)$/i)) {
            fileType = 'Video';
            fileIconClass = 'bi-file-earmark-play';
        } else if (filename.match(/\.csv$/i)) {
            fileType = 'CSV Document';
            fileIconClass = 'bi-file-earmark-spreadsheet';
        }
        
        document.getElementById('filePreviewType').textContent = fileType;
        
        // Update icon in title
        const titleIcon = document.querySelector('.modal-title i');
        if (titleIcon) {
            titleIcon.className = `bi ${fileIconClass}`;
        }
        
        // Set file size
        if (fileData && fileData.size) {
            document.getElementById('filePreviewSize').textContent = this.formatFileSize(fileData.size);
        } else {
            document.getElementById('filePreviewSize').textContent = 'Unknown';
        }
        
        // Set file date
        if (fileData && fileData.modified) {
            document.getElementById('filePreviewDate').textContent = this.formatDate(fileData.modified);
        } else {
            document.getElementById('filePreviewDate').textContent = 'Unknown';
        }
        
        // Generate preview content based on file type
        this.generatePreviewContent(filename, fileData);
        
        // Show modal
        this.openModal();
    }
    
    generatePreviewContent(filename, fileData) {
        const container = document.getElementById('filePreviewContainer');
        
        // Clear previous content
        container.innerHTML = '';
        
        // Default unavailable preview
        let previewContent = `
            <div class="preview-unavailable">
                <i class="bi bi-eye-slash"></i>
                <p>Preview not available for this file type</p>
                <button class="btn btn-sm btn-primary mt-3" id="filePreviewAnalyze">
                    Analyze with AI instead
                </button>
            </div>
        `;
        
        // Generate appropriate preview based on file type
        if (filename.match(/\.(jpe?g|png|gif|bmp|svg)$/i)) {
            // Image preview
            previewContent = `
                <div class="text-center">
                    <img src="/uploads/${filename}" class="preview-image" alt="${filename}">
                </div>
            `;
        } else if (filename.match(/\.(mp3|wav|ogg|flac)$/i)) {
            // Audio preview
            previewContent = `
                <div class="text-center">
                    <audio controls class="preview-audio">
                        <source src="/uploads/${filename}" type="audio/${filename.split('.').pop()}">
                        Your browser does not support the audio element.
                    </audio>
                </div>
            `;
        } else if (filename.match(/\.(mp4|mov|avi|mkv|webm)$/i)) {
            // Video preview
            previewContent = `
                <div class="text-center">
                    <video controls class="preview-video">
                        <source src="/uploads/${filename}" type="video/${filename.split('.').pop()}">
                        Your browser does not support the video element.
                    </video>
                </div>
            `;
        } else if (filename.match(/\.pdf$/i)) {
            // PDF preview
            previewContent = `
                <div class="text-center">
                    <iframe src="/uploads/${filename}" class="preview-pdf" frameborder="0"></iframe>
                </div>
            `;
        } else if (filename.match(/\.(txt|md)$/i)) {
            // Text preview - fetch the file content
            previewContent = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p>Loading file content...</p>
                </div>
            `;
            
            // Fetch text content
            fetch(`/uploads/${filename}`)
                .then(response => response.text())
                .then(text => {
                    container.innerHTML = `<pre class="preview-text">${this.escapeHtml(text)}</pre>`;
                })
                .catch(error => {
                    container.innerHTML = `
                        <div class="preview-unavailable">
                            <i class="bi bi-exclamation-triangle"></i>
                            <p>Error loading file content: ${error.message}</p>
                        </div>
                    `;
                });
        }
        
        // Update container
        if (previewContent) {
            container.innerHTML = previewContent;
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatFileSize(bytes) {
        if (!bytes) return 'Unknown';
        
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        const date = new Date(dateString);
        return date.toLocaleString([], {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    openModal() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }
    
    closeModal() {
        const modal = document.getElementById(this.modalId);
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
}

// Initialize file preview component when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.filePreview = new FilePreviewComponent();
});
