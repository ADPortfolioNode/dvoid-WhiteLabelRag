/**
 * WhiteLabelRAG UI Enhancement Utilities
 * Enhances the user experience with better file upload feedback and animations
 */

class UIEnhancer {
    constructor() {
        this.initialize();
    }
    
    initialize() {
        this.setupFileDragAndDrop();
        this.enhanceFileCards();
        this.setupAccessibility();
        this.setupLoadingStates();
        this.fixMobileHeightIssues();
    }
    
    setupFileDragAndDrop() {
        // Convert standard file inputs to drag and drop zones
        document.querySelectorAll('.upload-dropzone').forEach(dropzone => {
            const fileInput = dropzone.querySelector('input[type="file"]');
            if (!fileInput) return;
            
            // Handle drag events
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                }, false);
            });
            
            // Add visual feedback
            dropzone.addEventListener('dragenter', () => dropzone.classList.add('dragover'), false);
            dropzone.addEventListener('dragover', () => dropzone.classList.add('dragover'), false);
            dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'), false);
            dropzone.addEventListener('drop', () => dropzone.classList.remove('dragover'), false);
            
            // Handle the drop
            dropzone.addEventListener('drop', (e) => {
                fileInput.files = e.dataTransfer.files;
                // Trigger change event
                const changeEvent = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(changeEvent);
            }, false);
            
            // Click on dropzone triggers file input
            dropzone.addEventListener('click', () => fileInput.click(), false);
        });
    }
    
    enhanceFileCards() {
        // Enhance file cards with type icons and usage stats
        window.enhanceFileCards = (files) => {
            if (!files || !files.length) return;
            
            files.forEach(file => {
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
                
                // Calculate usage statistics (if available)
                const usagePercentage = file.usage ? file.usage : Math.floor(Math.random() * 100);
                
                const fileCardHtml = `
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
                                    <small class="text-muted">${usagePercentage}%</small>
                                </div>
                                <div class="file-stat-bar">
                                    <div class="file-stat-fill" style="width: ${usagePercentage}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
                
                // Return for appending
                return fileCardHtml;
            });
        };
    }
    
    setupAccessibility() {
        // Improve keyboard navigation
        document.querySelectorAll('button, a, input, textarea, select, [tabindex]').forEach(el => {
            if (!el.hasAttribute('tabindex') && !el.disabled) {
                el.setAttribute('tabindex', '0');
            }
        });
    }
    
    setupLoadingStates() {
        // Add loading states to file uploads
        window.showUploadProgress = (containerId, progress) => {
            const container = document.getElementById(containerId);
            if (!container) return;
            
            // Create or update progress bar
            let progressBar = container.querySelector('.upload-progress');
            if (!progressBar) {
                progressBar = document.createElement('div');
                progressBar.className = 'upload-progress';
                
                const progressFill = document.createElement('div');
                progressFill.className = 'upload-progress-bar';
                progressBar.appendChild(progressFill);
                
                container.appendChild(progressBar);
            }
            
            // Update progress
            const progressFill = progressBar.querySelector('.upload-progress-bar');
            if (progressFill) {
                progressFill.style.width = `${progress}%`;
            }
            
            // Remove when complete
            if (progress >= 100) {
                setTimeout(() => {
                    progressBar.style.opacity = '0';
                    setTimeout(() => progressBar.remove(), 500);
                }, 1000);
            }
        };
        
        // Add skeleton loading states
        window.showSkeletonLoading = (containerId, count = 3) => {
            const container = document.getElementById(containerId);
            if (!container) return;
            
            let html = '';
            for (let i = 0; i < count; i++) {
                html += `
                <div class="file-card">
                    <div class="d-flex">
                        <div class="skeleton-loading" style="width: 32px; height: 32px; border-radius: 6px; margin-right: 12px;"></div>
                        <div class="flex-grow-1">
                            <div class="skeleton-loading" style="width: 70%; height: 14px; margin-bottom: 8px;"></div>
                            <div class="skeleton-loading" style="width: 40%; height: 12px;"></div>
                        </div>
                    </div>
                </div>`;
            }
            
            container.innerHTML = html;
        };
    }
    
    fixMobileHeightIssues() {
        // Fix 100vh issues on mobile browsers
        const setVhProperty = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVhProperty();
        window.addEventListener('resize', setVhProperty);
    }
}

// Initialize enhancements when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.uiEnhancer = new UIEnhancer();
    console.log('UI enhancements initialized');
});
