/**
 * File Navigation System for WhiteLabelRAG
 * Provides folder navigation, breadcrumbs, and enhanced file interactions
 */

class FileNavigationSystem {
    constructor() {
        this.currentPath = '/';
        this.fileListElement = document.getElementById('filesList');
        this.mobileFileListElement = document.getElementById('mobileFilesList');
        this.breadcrumbsElement = document.getElementById('fileBreadcrumbs');
        this.mobileBreadcrumbsElement = document.getElementById('mobileFileBreadcrumbs');
        this.sortSelector = document.getElementById('fileSortSelector');
        this.searchInput = document.getElementById('fileSearchInput');
        this.files = [];
        this.folders = new Set();
        this.filteredFiles = [];
        this.sortMethod = 'name-asc'; // Default sort
        this.searchTerm = '';
        
        this.bindEvents();
    }
    
    bindEvents() {
        // Sort selector
        if (this.sortSelector) {
            this.sortSelector.addEventListener('change', () => {
                this.sortMethod = this.sortSelector.value;
                this.renderFiles();
            });
        }
        
        // Search input
        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => {
                this.searchTerm = this.searchInput.value.toLowerCase().trim();
                this.filterFiles();
                this.renderFiles();
            });
        }
        
        // Document event listener for file actions
        document.addEventListener('click', (e) => {
            // Handle file card clicks
            if (e.target.closest('.file-action-view')) {
                e.preventDefault();
                const fileCard = e.target.closest('.file-card');
                if (fileCard) {
                    const filename = fileCard.dataset.filename;
                    this.previewFile(filename);
                }
            }
            
            // Handle file delete
            if (e.target.closest('.file-action-delete')) {
                e.preventDefault();
                const fileCard = e.target.closest('.file-card');
                if (fileCard) {
                    const filename = fileCard.dataset.filename;
                    this.deleteFile(filename);
                }
            }
            
            // Handle folder navigation
            if (e.target.closest('.folder-card')) {
                e.preventDefault();
                const folderCard = e.target.closest('.folder-card');
                if (folderCard) {
                    const folderPath = folderCard.dataset.path;
                    this.navigateToFolder(folderPath);
                }
            }
            
            // Handle breadcrumb navigation
            if (e.target.closest('.breadcrumb-item')) {
                e.preventDefault();
                const breadcrumbItem = e.target.closest('.breadcrumb-item');
                if (breadcrumbItem) {
                    const path = breadcrumbItem.dataset.path;
                    this.navigateToFolder(path);
                }
            }
        });
    }
    
    setFiles(files) {
        this.files = files;
        this.extractFolders();
        this.filterFiles();
        this.renderBreadcrumbs();
        this.renderFiles();
    }
    
    extractFolders() {
        this.folders.clear();
        this.files.forEach(file => {
            // Check if the filename contains path separators
            if (file.name.includes('/')) {
                const parts = file.name.split('/');
                let currentPath = '';
                
                // Add each folder in the path
                for (let i = 0; i < parts.length - 1; i++) {
                    currentPath += parts[i] + '/';
                    this.folders.add(currentPath);
                }
            }
        });
    }
    
    filterFiles() {
        // Filter files by current path and search term
        this.filteredFiles = this.files.filter(file => {
            const inCurrentPath = this.currentPath === '/' 
                ? !file.name.includes('/') 
                : file.name.startsWith(this.currentPath) && !file.name.substring(this.currentPath.length).includes('/');
                
            const matchesSearch = this.searchTerm === '' || 
                file.name.toLowerCase().includes(this.searchTerm);
                
            return inCurrentPath && matchesSearch;
        });
        
        // Sort the filtered files
        this.sortFiles();
    }
    
    sortFiles() {
        switch (this.sortMethod) {
            case 'name-asc':
                this.filteredFiles.sort((a, b) => {
                    const aName = a.name.substring(this.currentPath.length);
                    const bName = b.name.substring(this.currentPath.length);
                    return aName.localeCompare(bName);
                });
                break;
            case 'name-desc':
                this.filteredFiles.sort((a, b) => {
                    const aName = a.name.substring(this.currentPath.length);
                    const bName = b.name.substring(this.currentPath.length);
                    return bName.localeCompare(aName);
                });
                break;
            case 'date-desc':
                this.filteredFiles.sort((a, b) => new Date(b.modified) - new Date(a.modified));
                break;
            case 'date-asc':
                this.filteredFiles.sort((a, b) => new Date(a.modified) - new Date(b.modified));
                break;
            case 'size-desc':
                this.filteredFiles.sort((a, b) => b.size - a.size);
                break;
            case 'size-asc':
                this.filteredFiles.sort((a, b) => a.size - b.size);
                break;
        }
    }
    
    renderBreadcrumbs() {
        if (!this.breadcrumbsElement && !this.mobileBreadcrumbsElement) return;
        
        // Create breadcrumb HTML
        let html = `
            <li class="breadcrumb-item ${this.currentPath === '/' ? 'active' : ''}" data-path="/">
                <i class="bi bi-house-door"></i> Home
            </li>
        `;
        
        if (this.currentPath !== '/') {
            const parts = this.currentPath.split('/').filter(p => p);
            let path = '/';
            
            parts.forEach((part, index) => {
                path += part + '/';
                const isLast = index === parts.length - 1;
                
                html += `
                    <li class="breadcrumb-item ${isLast ? 'active' : ''}" data-path="${path}">
                        ${part}
                    </li>
                `;
            });
        }
        
        // Update breadcrumbs
        if (this.breadcrumbsElement) {
            this.breadcrumbsElement.innerHTML = html;
        }
        
        if (this.mobileBreadcrumbsElement) {
            this.mobileBreadcrumbsElement.innerHTML = html;
        }
    }
    
    renderFiles() {
        if (!this.fileListElement && !this.mobileFileListElement) return;
        
        // Get current folders for this path
        const currentFolders = Array.from(this.folders)
            .filter(folder => 
                folder.startsWith(this.currentPath) && 
                folder !== this.currentPath &&
                !folder.substring(this.currentPath.length).includes('/'));
        
        // No files or folders to display
        if (this.filteredFiles.length === 0 && currentFolders.length === 0) {
            const emptyStateHtml = `
                <div class="file-empty-state text-center p-4">
                    <i class="bi bi-folder-x display-5 text-muted"></i>
                    <p class="mt-3 mb-1">No files found</p>
                    <p class="text-muted small">
                        ${this.searchTerm ? 'Try a different search term' : 'Upload some files to get started'}
                    </p>
                </div>
            `;
            
            if (this.fileListElement) {
                this.fileListElement.innerHTML = emptyStateHtml;
            }
            
            if (this.mobileFileListElement) {
                this.mobileFileListElement.innerHTML = emptyStateHtml;
            }
            
            return;
        }
        
        // Build HTML for folders
        let foldersHtml = '';
        if (currentFolders.length > 0) {
            foldersHtml = currentFolders.map(folder => {
                const folderName = folder.substring(this.currentPath.length).replace('/', '');
                return `
                    <div class="folder-card elevation-1 elevation-hover" data-path="${folder}">
                        <div class="d-flex">
                            <div class="file-icon">
                                <i class="bi bi-folder-fill text-warning"></i>
                            </div>
                            <div class="file-info">
                                <div class="file-name">${folderName}</div>
                                <div class="file-meta text-muted">
                                    <small>Folder</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        // Build HTML for files
        let filesHtml = '';
        if (this.filteredFiles.length > 0) {
            filesHtml = this.filteredFiles.map(file => {
                // Extract the visible filename without the path
                const visibleFilename = file.name.substring(this.currentPath.length);
                
                // Determine file type icon
                let iconClass = 'bi-file-earmark';
                let fileTypeClass = 'text-secondary';
                
                if (visibleFilename.match(/\.pdf$/i)) {
                    iconClass = 'bi-file-earmark-pdf';
                    fileTypeClass = 'text-danger';
                } else if (visibleFilename.match(/\.(docx?|rtf|txt|md)$/i)) {
                    iconClass = 'bi-file-earmark-text';
                    fileTypeClass = 'text-primary';
                } else if (visibleFilename.match(/\.(jpe?g|png|gif|bmp|svg)$/i)) {
                    iconClass = 'bi-file-earmark-image';
                    fileTypeClass = 'text-success';
                } else if (visibleFilename.match(/\.(mp3|wav|ogg|flac)$/i)) {
                    iconClass = 'bi-file-earmark-music';
                    fileTypeClass = 'text-info';
                } else if (visibleFilename.match(/\.(mp4|mov|avi|mkv|webm)$/i)) {
                    iconClass = 'bi-file-earmark-play';
                    fileTypeClass = 'text-warning';
                }
                
                return `
                    <div class="file-card elevation-1 elevation-hover" data-filename="${file.name}">
                        <div class="d-flex">
                            <div class="file-icon">
                                <i class="bi ${iconClass} ${fileTypeClass}"></i>
                            </div>
                            <div class="file-info">
                                <div class="file-name">${visibleFilename}</div>
                                <div class="file-meta">
                                    ${this.formatFileSize(file.size)} • ${this.formatDate(file.modified)}
                                </div>
                                <div class="file-actions mt-2">
                                    <button class="btn btn-sm btn-outline-primary file-action-view">
                                        <i class="bi bi-eye"></i> View
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger file-action-delete">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        const html = foldersHtml + filesHtml;
        
        // Update file lists
        if (this.fileListElement) {
            this.fileListElement.innerHTML = html;
        }
        
        if (this.mobileFileListElement) {
            this.mobileFileListElement.innerHTML = html;
        }
    }
    
    navigateToFolder(path) {
        this.currentPath = path;
        this.filterFiles();
        this.renderBreadcrumbs();
        this.renderFiles();
    }
    
    formatFileSize(bytes) {
        if (!bytes) return 'Unknown size';
        
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
        if (!dateString) return 'Unknown date';
        
        const date = new Date(dateString);
        const now = new Date();
        const yesterday = new Date(now);
        yesterday.setDate(now.getDate() - 1);
        
        // Format date based on how recent it is
        if (date.toDateString() === now.toDateString()) {
            return `Today ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        } else if (date.toDateString() === yesterday.toDateString()) {
            return `Yesterday ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        } else {
            return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
        }
    }
    
    previewFile(filename) {
        // Find the file in our data
        const file = this.files.find(f => f.name === filename);
        if (!file) return;
        
        // Send message to chat
        if (window.app && typeof window.app.sendQuickMessage === 'function') {
            window.app.sendQuickMessage(`Analyze file: ${filename}`);
        }
        
        // Trigger custom event for file preview
        const event = new CustomEvent('filePreview', {
            detail: { filename, file }
        });
        document.dispatchEvent(event);
    }
    
    async deleteFile(filename) {
        if (!confirm(`Are you sure you want to delete ${filename}?`)) {
            return;
        }
        
        try {
            const response = await fetch('/api/files', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Refresh the file list
                if (window.app && typeof window.app.loadFiles === 'function') {
                    window.app.loadFiles();
                }
                
                // Show success notification
                this.showNotification('File deleted successfully', 'success');
            } else {
                this.showNotification(`Error: ${data.error || 'Failed to delete file'}`, 'danger');
            }
        } catch (error) {
            console.error('Error deleting file:', error);
            this.showNotification('Error deleting file. Please try again.', 'danger');
        }
    }
    
    showNotification(message, type = 'info') {
        // Create a Bootstrap toast notification
        const toastId = `toast-${Date.now()}`;
        const toast = document.createElement('div');
        toast.className = `toast align-items-center border-0 bg-${type} text-white`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.setAttribute('id', toastId);
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add to notifications container or create one if it doesn't exist
        let notificationsContainer = document.getElementById('toastContainer');
        if (!notificationsContainer) {
            notificationsContainer = document.createElement('div');
            notificationsContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            notificationsContainer.setAttribute('id', 'toastContainer');
            document.body.appendChild(notificationsContainer);
        }
        
        notificationsContainer.appendChild(toast);
        
        // Initialize and show the toast
        const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
        bsToast.show();
        
        // Remove from DOM after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
}

// Initialize navigation system when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.fileNavigation = new FileNavigationSystem();
    
    // Connect to the app's file loading system
    if (window.app) {
        const originalDisplayFiles = window.app.displayFiles;
        window.app.displayFiles = function(files) {
            // Let the navigation system handle file display
            if (window.fileNavigation) {
                window.fileNavigation.setFiles(files);
            }
            
            // Also call the original method to maintain compatibility
            originalDisplayFiles.call(this, files);
        };
    }
});
