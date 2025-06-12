/**
 * Main Navigation Functionality for WhiteLabelRAG
 * Enhances the application's navigation system and UI interactions
 */

class MainNavigation {
    constructor() {
        this.hamburgerMenu = document.querySelector('.hamburger-menu');
        this.sidebarCollapse = document.getElementById('sidebarCollapse');
        this.quickClearChat = document.getElementById('quickClearChat');
        this.clearChat = document.getElementById('clearChat');
        
        this.bindEvents();
        this.initMobileNav();
    }
    
    bindEvents() {
        // Hamburger menu animation
        if (this.hamburgerMenu) {
            this.hamburgerMenu.addEventListener('click', () => {
                this.hamburgerMenu.classList.toggle('active');
            });
        }
        
        // Quick clear chat button
        if (this.quickClearChat && this.clearChat) {
            this.quickClearChat.addEventListener('click', () => {
                this.clearChat.click();
            });
        }
        
        // Mobile nav backdrop click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('mobile-nav-menu')) {
                this.closeMobileNav();
            }
        });
        
        // Close sidebar when clicking on nav links on mobile
        document.querySelectorAll('.mobile-nav-link').forEach(link => {
            link.addEventListener('click', () => {
                this.closeMobileNav();
                
                // If the sidebar is shown, hide it
                if (this.sidebarCollapse && this.sidebarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(this.sidebarCollapse);
                    bsCollapse.hide();
                }
                
                // Toggle active state
                document.querySelectorAll('.mobile-nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }
    
    initMobileNav() {
        // Check if the mobile nav menu already exists
        if (document.querySelector('.mobile-nav-menu')) {
            return;
        }
        
        // Create mobile navigation menu
        const mobileNavMenu = document.createElement('div');
        mobileNavMenu.className = 'mobile-nav-menu';
        mobileNavMenu.innerHTML = `
            <div class="mobile-nav-container">
                <div class="mobile-nav-header">
                    <div class="app-brand">
                        <div class="app-logo">
                            <i class="bi bi-robot"></i>
                        </div>
                        <h1 class="app-name">WhiteLabelRAG <span class="version">v1.0</span></h1>
                    </div>
                    <div class="mobile-nav-close">
                        <i class="bi bi-x-lg"></i>
                    </div>
                </div>
                <div class="mobile-nav-body">
                    <ul class="mobile-nav-menu-list">
                        <li class="mobile-nav-menu-item">
                            <a href="#" class="mobile-nav-link active">
                                <i class="bi bi-chat-dots"></i>
                                <span>Chat</span>
                            </a>
                        </li>
                        <li class="mobile-nav-menu-item">
                            <a href="#" class="mobile-nav-link" onclick="app.sendQuickMessage('List my files')">
                                <i class="bi bi-files"></i>
                                <span>Documents</span>
                            </a>
                        </li>
                        <li class="mobile-nav-menu-item">
                            <a href="#" class="mobile-nav-link" onclick="app.sendQuickMessage('Show me system stats')">
                                <i class="bi bi-bar-chart"></i>
                                <span>Stats</span>
                            </a>
                        </li>
                        <li class="mobile-nav-menu-item">
                            <a href="#" class="mobile-nav-link" onclick="app.sendQuickMessage('What can you do?')">
                                <i class="bi bi-question-circle"></i>
                                <span>Help</span>
                            </a>
                        </li>
                        <li class="mobile-nav-menu-item">
                            <a href="#" class="mobile-nav-link text-danger" id="mobileNavClearChat">
                                <i class="bi bi-trash"></i>
                                <span>Clear Chat</span>
                            </a>
                        </li>
                    </ul>
                </div>
                <div class="mobile-nav-footer">
                    WhiteLabelRAG © 2025 - Powered by Azure AI
                </div>
            </div>
        `;
        
        // Add to body
        document.body.appendChild(mobileNavMenu);
        
        // Bind events for mobile nav
        const closeButton = mobileNavMenu.querySelector('.mobile-nav-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                this.closeMobileNav();
            });
        }
        
        // Sync mobile nav clear chat button
        const mobileNavClearChat = document.getElementById('mobileNavClearChat');
        if (mobileNavClearChat && this.clearChat) {
            mobileNavClearChat.addEventListener('click', () => {
                this.clearChat.click();
            });
        }
        
        // Add toggle event to hamburger
        if (this.hamburgerMenu) {
            this.hamburgerMenu.addEventListener('click', () => {
                this.toggleMobileNav();
            });
        }
    }
    
    toggleMobileNav() {
        const mobileNavMenu = document.querySelector('.mobile-nav-menu');
        if (mobileNavMenu) {
            mobileNavMenu.classList.toggle('active');
            document.body.style.overflow = mobileNavMenu.classList.contains('active') ? 'hidden' : '';
        }
    }
    
    closeMobileNav() {
        const mobileNavMenu = document.querySelector('.mobile-nav-menu');
        if (mobileNavMenu) {
            mobileNavMenu.classList.remove('active');
            document.body.style.overflow = '';
            
            if (this.hamburgerMenu) {
                this.hamburgerMenu.classList.remove('active');
            }
        }
    }
    
    updateBreadcrumbs(items) {
        const breadcrumbs = document.querySelector('.page-breadcrumb');
        if (!breadcrumbs || !items || !items.length) return;
        
        let html = '';
        items.forEach((item, index) => {
            const isLast = index === items.length - 1;
            html += `
                <li class="page-breadcrumb-item">
                    <a href="${item.url || '#'}" ${isLast ? 'style="pointer-events: none;"' : ''}>
                        ${index === 0 ? `<i class="bi bi-house-door"></i> ` : ''}${item.label}
                    </a>
                </li>
            `;
        });
        
        breadcrumbs.innerHTML = html;
    }
}

// Initialize navigation when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mainNavigation = new MainNavigation();
    
    // Example breadcrumb update
    if (window.mainNavigation) {
        window.mainNavigation.updateBreadcrumbs([
            { label: 'Home', url: '#' },
            { label: 'Chat', url: '#' },
            { label: 'Assistant', url: '#' }
        ]);
    }
    
    // Connect mobile clear chat button to the main one
    const mobileClearChat = document.getElementById('mobileClearChat');
    const clearChat = document.getElementById('clearChat');
    if (mobileClearChat && clearChat) {
        mobileClearChat.addEventListener('click', () => {
            clearChat.click();
        });
    }
});
