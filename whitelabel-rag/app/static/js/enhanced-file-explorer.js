/**
 * Enhanced File Explorer for WhiteLabelRAG
 * Modern file browsing experience with improved navigation and visualization
 */

class EnhancedFileExplorer {
    constructor(options = {}) {
        // Elements
        this.container = options.container || document.querySelector('.file-explorer-container');
        this.breadcrumbContainer = options.breadcrumbContainer || document.querySelector('.file-breadcrumb');
        this.fileListContainer = options.fileListContainer || document.querySelector('.file-list');
        this.fileGridContainer = options.fileGridContainer || document.querySelector('.file-grid');
        this.searchInput = options.searchInput || document.querySelector('.file-search input');
        this.sortSelect = options.sortSelect || document.querySelector('.file-sort select');
        this.viewToggleButtons = options.viewToggleButtons || document.querySelectorAll('.file-view-toggle button');
        this.uploadDropzone = options.uploadDropzone || document.querySelector('.file-upload-dropzone');
        
        // State
        this.currentPath = '/';
        this.currentView = localStorage.getItem('fileExplorerView') || 'grid';
        this.files = [];
        this.filteredFiles = [];
        this.folders = new Set();
        this.sortMethod = localStorage.getItem('fileExplorerSort') || 'name-asc';
        this.searchTerm = '';
        this.selectedFiles = new Set();
        
        // Bind methods
        this.handleDragOver = this.handleDragOver.bind(this);
        this.handleDragLeave = this.handleDragLeave.bind(this);
        this.handleDrop = this.handleDrop.bind(this);
        
        // Initialize
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.setViewMode(this.currentView);
        this.setSortMethod(this.sortMethod);
    }
    
    bindEvents() {
        // View toggle
        this.viewToggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                const view = button.dataset.view;
                this.setViewMode(view);
            });
        });
        
        // Sort selector
        if (this.sortSelect) {
            this.sortSelect.addEventListener('change', () => {
                this.setSortMethod(this.sortSelect.value);
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
        
        // File upload dropzone
        if (this.uploadDropzone) {
            this.uploadDropzone.addEventListener('dragover', this.handleDragOver);
            this.uploadDropzone.addEventListener('dragleave', this.handleDragLeave);
            this.uploadDropzone.addEventListener('drop', this.handleDrop);
            this.uploadDropzone.addEventListener('click', () => {
                // Trigger hidden file input click
                const fileInput = document.querySelector('input[type="file"]');
                if (fileInput) fileInput.click();
            });
        }
        
        // Document event delegation for file/folder interactions
        document.addEventListener('click', (e) => {
            // Folder navigation
            if (e.target.closest('.file-type-folder')) {
                const item = e.target.closest('.file-type-folder');
                const folderPath = item.dataset.path;
                if (folderPath) this.navigateToFolder(folderPath);
            }
            
            // Breadcrumb navigation
            if (e.target.closest('.file-breadcrumb-item')) {
                const crumb = e.target.closest('.file-breadcrumb-item');
                const path = crumb.dataset.path;
                if (path) this.navigateToFolder(path);
            }
            
            // File selection
            if (e.target.closest('.file-grid-item:not(.file-type-folder), .file-list-item:not(.file-type-folder)')) {
                const item = e.target.closest('.file-grid-item, .file-list-item');
                
                // Ignore if clicking on an action button
                if (e.target.closest('.file-action-btn')) return;
                
                const fileId = item.dataset.id;
                this.toggleFileSelection(fileId, item);
            }
            
            // File actions
            if (e.target.closest('.file-action-view')) {
                e.preventDefault();
                const item = e.target.closest('.file-grid-item, .file-list-item');
                const fileId = item.dataset.id;
                this.previewFile(fileId);
            }
            
            if (e.target.closest('.file-action-delete')) {
                e.preventDefault();
                const item = e.target.closest('.file-grid-item, .file-list-item');
                const fileId = item.dataset.id;
                this.deleteFile(fileId);
            }
        });
    }
    
    // Set the view mode (grid or list)
    setViewMode(mode) {
        if (mode !== 'grid' && mode !== 'list') return;
        
        this.currentView = mode;
        localStorage.setItem('fileExplorerView', mode);
        
        // Update toggle buttons
        this.viewToggleButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.view === mode);
        });
        
        // Show appropriate container
        if (this.fileGridContainer) {
            this.fileGridContainer.style.display = mode === 'grid' ? 'grid' : 'none';
        }
        
        if (this.fileListContainer) {
            this.fileListContainer.style.display = mode === 'list' ? 'flex' : 'none';
        }
        
        // Render files in the new view
        this.renderFiles();
    }
    
    // Set sort method and update display
    setSortMethod(method) {
        this.sortMethod = method;
        localStorage.setItem('fileExplorerSort', method);
        
        // Update sort selector
        if (this.sortSelect) {
            this.sortSelect.value = method;
        }
        
        this.sortFiles();
        this.renderFiles();
    }
    
    // Set files from external source
    setFiles(files) {
        this.files = Array.isArray(files) ? files : [];
        this.extractFolders();
        this.filterFiles();
        this.renderBreadcrumbs();
        this.renderFiles();
    }
    
    // Extract folder structure from file paths
    extractFolders() {
        this.folders.clear();
        
        // Add root folder
        this.folders.add('/');
        
        this.files.forEach(file => {
            if (file.name.includes('/')) {
                const parts = file.name.split('/');
                // Remove the last part (filename)
                parts.pop();
                
                let currentPath = '';
                parts.forEach(part => {
                    currentPath += part + '/';
                    this.folders.add(currentPath);
                });
            }
        });
    }
    
    // Navigate to a folder
    navigateToFolder(path) {
        this.currentPath = path;
        this.filterFiles();
        this.renderBreadcrumbs();
        this.renderFiles();
    }
    
    // Filter files based on current path and search term
    filterFiles() {
        this.filteredFiles = this.files.filter(file => {
            // Filter by path
            const inCurrentPath = this.isFileInCurrentPath(file.name);
            
            // Filter by search term
            const matchesSearch = this.searchTerm === '' || 
                file.name.toLowerCase().includes(this.searchTerm);
            
            return inCurrentPath && matchesSearch;
        });
        
        this.sortFiles();
    }
    
    // Check if a file is in the current path
    isFileInCurrentPath(filename) {
        // Files directly in root
        if (this.currentPath === '/' && !filename.includes('/')) {
            return true;
        }
        
        // Files in subfolders
        if (filename.startsWith(this.currentPath) && 
            filename.substring(this.currentPath.length).split('/').length === 1) {
            return true;
        }
        
        return false;
    }
    
    // Get display name for a file or folder
    getDisplayName(path) {
        // For root
        if (path === '/') return 'Home';
        
        // For files or folders
        const parts = path.split('/');
        return parts[parts.length - 1] || parts[parts.length - 2];
    }
    
    // Sort the filtered files
    sortFiles() {
        const [property, direction] = this.sortMethod.split('-');
        const multiplier = direction === 'asc' ? 1 : -1;
        
        this.filteredFiles.sort((a, b) => {
            let valueA, valueB;
            
            switch (property) {
                case 'name':
                    valueA = this.getDisplayName(a.name);
                    valueB = this.getDisplayName(b.name);
                    break;
                case 'date':
                    valueA = new Date(a.date || 0);
                    valueB = new Date(b.date || 0);
                    break;
                case 'size':
                    valueA = a.size || 0;
                    valueB = b.size || 0;
                    break;
                case 'type':
                    valueA = a.type || '';
                    valueB = b.type || '';
                    break;
                default:
                    valueA = a.name;
                    valueB = b.name;
            }
            
            if (valueA < valueB) return -1 * multiplier;
            if (valueA > valueB) return 1 * multiplier;
            return 0;
        });
    }
    
    // Render breadcrumb navigation
    renderBreadcrumbs() {
        if (!this.breadcrumbContainer) return;
        
        const pathParts = this.currentPath.split('/').filter(part => part !== '');
        let html = `
            <div class="file-breadcrumb-item" data-path="/">
                <i class="bi bi-house-door"></i>
                <span>Home</span>
            </div>
        `;
        
        let currentPath = '/';
        pathParts.forEach((part, index) => {
            currentPath += part + '/';
            const isLast = index === pathParts.length - 1;
            
            html += `
                <div class="file-breadcrumb-item ${isLast ? 'active' : ''}" data-path="${currentPath}">
                    <span>${part}</span>
                </div>
            `;
        });
        
        this.breadcrumbContainer.innerHTML = html;
    }
    
    // Render files in current view mode
    renderFiles() {
        // Get current subfolders
        const currentSubfolders = Array.from(this.folders)
            .filter(folder => {
                if (folder === this.currentPath) return false;
                
                if (this.currentPath === '/' && !folder.substring(1).includes('/')) {
                    return true;
                }
                
                return folder.startsWith(this.currentPath) && 
                       folder.substring(this.currentPath.length).split('/').filter(p => p).length === 1;
            })
            .map(folder => ({
                id: folder,
                name: folder,
                isFolder: true,
                type: 'folder'
            }));
        
        // Combine folders and files
        const items = [...currentSubfolders, ...this.filteredFiles];
        
        // Render based on view mode
        if (this.currentView === 'grid') {
            this.renderGridView(items);
        } else {
            this.renderListView(items);
        }
    }
    
    // Render grid view
    renderGridView(items) {
        if (!this.fileGridContainer) return;
        
        if (items.length === 0) {
            this.fileGridContainer.innerHTML = this.getEmptyStateHTML();
            return;
        }
        
        let html = '';
        
        items.forEach(item => {
            const isFolder = item.isFolder;
            const fileType = isFolder ? 'folder' : this.getFileTypeClass(item.name);
            const displayName = this.getDisplayName(item.name);
            const selected = this.selectedFiles.has(item.id);
            
            html += `
                <div class="file-grid-item file-type-${fileType} ${selected ? 'selected' : ''}" 
                     data-id="${item.id}" data-path="${item.name}">
                    <div class="file-grid-icon">
                        ${this.getFileIconHTML(fileType)}
                    </div>
                    <div class="file-grid-name" title="${displayName}">
                        ${displayName}
                    </div>
                    <div class="file-grid-meta">
                        ${!isFolder ? this.getFileMeta(item) : ''}
                    </div>
                </div>
            `;
        });
        
        this.fileGridContainer.innerHTML = html;
    }
    
    // Render list view
    renderListView(items) {
        if (!this.fileListContainer) return;
        
        if (items.length === 0) {
            this.fileListContainer.innerHTML = this.getEmptyStateHTML();
            return;
        }
        
        let html = '';
        
        items.forEach(item => {
            const isFolder = item.isFolder;
            const fileType = isFolder ? 'folder' : this.getFileTypeClass(item.name);
            const displayName = this.getDisplayName(item.name);
            const selected = this.selectedFiles.has(item.id);
            
            html += `
                <div class="file-list-item file-type-${fileType} ${selected ? 'selected' : ''}" 
                     data-id="${item.id}" data-path="${item.name}">
                    <div class="file-list-icon">
                        ${this.getFileIconHTML(fileType)}
                    </div>
                    <div class="file-list-content">
                        <div class="file-list-name" title="${displayName}">
                            ${displayName}
                        </div>
                        <div class="file-list-meta">
                            ${!isFolder ? this.getFileMeta(item) : 'Folder'}
                        </div>
                    </div>
                    ${!isFolder ? `
                    <div class="file-list-actions">
                        <button class="file-action-btn file-action-view" title="Preview">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="file-action-btn btn-danger file-action-delete" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                    ` : ''}
                </div>
            `;
        });
        
        this.fileListContainer.innerHTML = html;
    }
    
    // Get empty state HTML
    getEmptyStateHTML() {
        const isSearch = this.searchTerm !== '';
        
        return `
            <div class="file-explorer-empty">
                <i class="bi bi-${isSearch ? 'search' : 'folder-x'}"></i>
                <h5>${isSearch ? 'No matching files found' : 'This folder is empty'}</h5>
                <p class="text-muted">
                    ${isSearch 
                        ? 'Try another search term or clear your search' 
                        : 'Upload a file to get started'}
                </p>
            </div>
        `;
    }
    
    // Get file type class based on extension
    getFileTypeClass(filename) {
        if (!filename) return 'unknown';
        
        const ext = filename.split('.').pop().toLowerCase();
        
        if (['doc', 'docx', 'txt', 'md', 'rtf'].includes(ext)) return 'doc';
        if (['xls', 'xlsx', 'csv'].includes(ext)) return 'sheet';
        if (['pdf'].includes(ext)) return 'pdf';
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'].includes(ext)) return 'image';
        if (['mp3', 'wav', 'ogg', 'flac'].includes(ext)) return 'audio';
        if (['mp4', 'avi', 'mov', 'wmv', 'webm'].includes(ext)) return 'video';
        
        return 'unknown';
    }
    
    // Get file icon HTML based on type
    getFileIconHTML(fileType) {
        const iconMap = {
            folder: '<i class="bi bi-folder"></i>',
            doc: '<i class="bi bi-file-text"></i>',
            sheet: '<i class="bi bi-file-spreadsheet"></i>',
            pdf: '<i class="bi bi-file-pdf"></i>',
            image: '<i class="bi bi-file-image"></i>',
            audio: '<i class="bi bi-file-music"></i>',
            video: '<i class="bi bi-file-play"></i>',
            unknown: '<i class="bi bi-file"></i>'
        };
        
        return iconMap[fileType] || iconMap.unknown;
    }
    
    // Get file metadata HTML
    getFileMeta(file) {
        const sizeStr = file.size ? this.formatFileSize(file.size) : '';
        const dateStr = file.date ? new Date(file.date).toLocaleDateString() : '';
        const typeStr = file.type || this.getFileTypeClass(file.name).toUpperCase();
        
        let metaStr = '';
        
        if (sizeStr) metaStr += `<span>${sizeStr}</span>`;
        if (dateStr) metaStr += `<span>${dateStr}</span>`;
        if (typeStr) metaStr += `<span>${typeStr}</span>`;
        
        return metaStr || 'Unknown';
    }
    
    // Format file size
    formatFileSize(sizeInBytes) {
        if (sizeInBytes < 1024) return `${sizeInBytes} B`;
        if (sizeInBytes < 1024 * 1024) return `${(sizeInBytes / 1024).toFixed(1)} KB`;
        if (sizeInBytes < 1024 * 1024 * 1024) return `${(sizeInBytes / (1024 * 1024)).toFixed(1)} MB`;
        return `${(sizeInBytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
    }
    
    // Toggle file selection
    toggleFileSelection(fileId, element) {
        if (this.selectedFiles.has(fileId)) {
            this.selectedFiles.delete(fileId);
            element.classList.remove('selected');
        } else {
            this.selectedFiles.add(fileId);
            element.classList.add('selected');
        }
        
        // Trigger selection change event
        this.triggerEvent('selectionChange', {
            selectedFiles: Array.from(this.selectedFiles),
            count: this.selectedFiles.size
        });
    }
    
    // Preview a file
    previewFile(fileId) {
        const file = this.files.find(f => f.id === fileId);
        if (!file) return;
        
        // Trigger preview event
        this.triggerEvent('filePreview', { file });
    }
    
    // Delete a file
    deleteFile(fileId) {
        if (confirm('Are you sure you want to delete this file?')) {
            // Trigger delete event
            this.triggerEvent('fileDelete', { fileId });
        }
    }
    
    // Handle drag over
    handleDragOver(e) {
        e.preventDefault();
        this.uploadDropzone.classList.add('active');
    }
    
    // Handle drag leave
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadDropzone.classList.remove('active');
    }
    
    // Handle file drop
    handleDrop(e) {
        e.preventDefault();
        this.uploadDropzone.classList.remove('active');
        
        if (e.dataTransfer.files.length) {
            // Trigger upload event
            this.triggerEvent('fileUpload', { files: e.dataTransfer.files });
        }
    }
    
    // Custom event trigger
    triggerEvent(eventName, detail) {
        const event = new CustomEvent(`fileExplorer:${eventName}`, { 
            detail,
            bubbles: true 
        });
        this.container.dispatchEvent(event);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Create file explorer instance if container exists
    const fileExplorerContainer = document.querySelector('.file-explorer-container');
    if (fileExplorerContainer) {
        window.fileExplorer = new EnhancedFileExplorer();
    }
});
