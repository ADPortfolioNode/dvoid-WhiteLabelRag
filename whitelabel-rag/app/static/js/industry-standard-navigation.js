/**
 * Industry Standard Navigation System
 * Provides modern navigation patterns and interactions for WhiteLabelRAG
 */

class IndustryStandardNavigation {
    constructor() {
        this.sideNav = document.querySelector('.side-nav');
        this.sideNavToggle = document.querySelector('.side-nav-toggle');
        this.sideNavBackdrop = document.querySelector('.side-nav-backdrop');
        this.tabNavItems = document.querySelectorAll('.tab-nav-item');
        this.stepperItems = document.querySelectorAll('.stepper-item');
        
        this.currentStep = 0;
        this.totalSteps = this.stepperItems.length;
        
        this.initSideNav();
        this.initTabNav();
        this.initStepper();
        this.bindEvents();
    }
    
    initSideNav() {
        // Create backdrop if it doesn't exist
        if (!this.sideNavBackdrop && this.sideNav) {
            this.sideNavBackdrop = document.createElement('div');
            this.sideNavBackdrop.className = 'side-nav-backdrop';
            document.body.appendChild(this.sideNavBackdrop);
        }
    }
    
    initTabNav() {
        // Set up tab navigation
        this.tabNavItems.forEach(item => {
            item.addEventListener('click', () => {
                const targetId = item.getAttribute('data-target');
                const targetPane = document.getElementById(targetId);
                
                if (targetPane) {
                    // Remove active class from all tabs and panes
                    this.tabNavItems.forEach(tab => tab.classList.remove('active'));
                    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
                    
                    // Set active tab and pane
                    item.classList.add('active');
                    targetPane.classList.add('active');
                }
            });
        });
        
        // Activate first tab by default if none is active
        if (this.tabNavItems.length > 0 && !Array.from(this.tabNavItems).some(tab => tab.classList.contains('active'))) {
            this.tabNavItems[0].click();
        }
    }
    
    initStepper() {
        // Highlight current step
        this.updateStepper();
    }
    
    bindEvents() {
        // Toggle side navigation
        if (this.sideNavToggle) {
            this.sideNavToggle.addEventListener('click', () => {
                this.toggleSideNav();
            });
        }
        
        // Close side navigation when clicking backdrop
        if (this.sideNavBackdrop) {
            this.sideNavBackdrop.addEventListener('click', () => {
                this.closeSideNav();
            });
        }
        
        // Close side navigation on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sideNav && this.sideNav.classList.contains('active')) {
                this.closeSideNav();
            }
        });
        
        // Handle navigation item clicks
        document.addEventListener('click', (e) => {
            // Side navigation links
            if (e.target.closest('.side-nav-link')) {
                const sideNavLink = e.target.closest('.side-nav-link');
                
                // Remove active class from all links
                document.querySelectorAll('.side-nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                
                // Add active class to clicked link
                sideNavLink.classList.add('active');
                
                // Close side navigation on mobile
                if (window.innerWidth < 992) {
                    this.closeSideNav();
                }
            }
            
            // Top navigation links
            if (e.target.closest('.top-nav-link')) {
                const topNavLink = e.target.closest('.top-nav-link');
                
                // Remove active class from all links
                document.querySelectorAll('.top-nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                
                // Add active class to clicked link
                topNavLink.classList.add('active');
            }
            
            // Context navigation links
            if (e.target.closest('.context-nav-link')) {
                const contextNavLink = e.target.closest('.context-nav-link');
                
                // Remove active class from all links
                document.querySelectorAll('.context-nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                
                // Add active class to clicked link
                contextNavLink.classList.add('active');
            }
        });
        
        // Responsive handling
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 992) {
                // On desktop, show side navigation by default
                if (this.sideNav) {
                    document.body.classList.add('has-side-nav');
                }
            } else {
                // On mobile, hide side navigation by default
                if (this.sideNav) {
                    document.body.classList.remove('has-side-nav');
                    this.closeSideNav();
                }
            }
        });
        
        // Initial responsive setup
        if (window.innerWidth >= 992 && this.sideNav) {
            document.body.classList.add('has-side-nav');
        }
    }
    
    toggleSideNav() {
        if (!this.sideNav) return;
        
        if (this.sideNav.classList.contains('active')) {
            this.closeSideNav();
        } else {
            this.openSideNav();
        }
    }
    
    openSideNav() {
        if (!this.sideNav) return;
        
        this.sideNav.classList.add('active');
        
        if (this.sideNavBackdrop) {
            this.sideNavBackdrop.classList.add('active');
        }
        
        document.body.style.overflow = 'hidden';
    }
    
    closeSideNav() {
        if (!this.sideNav) return;
        
        this.sideNav.classList.remove('active');
        
        if (this.sideNavBackdrop) {
            this.sideNavBackdrop.classList.remove('active');
        }
        
        document.body.style.overflow = '';
    }
    
    goToStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.totalSteps) return;
        
        this.currentStep = stepIndex;
        this.updateStepper();
    }
    
    nextStep() {
        if (this.currentStep < this.totalSteps - 1) {
            this.currentStep++;
            this.updateStepper();
        }
    }
    
    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateStepper();
        }
    }
    
    updateStepper() {
        if (!this.stepperItems.length) return;
        
        this.stepperItems.forEach((item, index) => {
            if (index < this.currentStep) {
                item.classList.add('completed');
                item.classList.remove('active');
            } else if (index === this.currentStep) {
                item.classList.add('active');
                item.classList.remove('completed');
            } else {
                item.classList.remove('active', 'completed');
            }
        });
        
        // Trigger custom event
        const event = new CustomEvent('stepperUpdated', {
            detail: {
                currentStep: this.currentStep,
                totalSteps: this.totalSteps
            }
        });
        document.dispatchEvent(event);
    }
    
    // Helper to create breadcrumbs dynamically
    createBreadcrumbs(items) {
        const breadcrumbNav = document.querySelector('.breadcrumb-nav');
        if (!breadcrumbNav) return;
        
        const breadcrumbList = breadcrumbNav.querySelector('.breadcrumb-list') || document.createElement('ul');
        breadcrumbList.className = 'breadcrumb-list';
        breadcrumbList.innerHTML = '';
        
        items.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'breadcrumb-item';
            
            const link = document.createElement('a');
            link.className = 'breadcrumb-link';
            link.href = item.url || '#';
            link.textContent = item.label;
            
            if (index === 0 && item.icon) {
                link.innerHTML = `<i class="bi bi-${item.icon} me-1"></i> ${item.label}`;
            }
            
            if (index === items.length - 1) {
                link.setAttribute('aria-current', 'page');
            }
            
            li.appendChild(link);
            breadcrumbList.appendChild(li);
        });
        
        breadcrumbNav.appendChild(breadcrumbList);
    }
}

// Initialize navigation when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.industryNavigation = new IndustryStandardNavigation();
    
    // Example: Create breadcrumbs
    if (window.industryNavigation) {
        window.industryNavigation.createBreadcrumbs([
            { label: 'Home', icon: 'house-door', url: '#' },
            { label: 'Documents', url: '#' },
            { label: 'Current Document' }
        ]);
    }
});
