/**
 * Enhanced Navigation System for WhiteLabelRAG
 * Provides modern, responsive navigation interactions and UI behaviors
 */

class EnhancedNavigation {
    constructor() {
        // Main navigation elements
        this.navbar = document.querySelector('.app-navbar');
        this.sidenav = document.querySelector('.app-sidenav');
        this.sidenavToggle = document.querySelector('.app-sidenav-toggle');
        this.sidenavClose = document.querySelector('.app-sidenav-close');
        this.sidenavBackdrop = document.querySelector('.app-sidenav-backdrop');
        
        // Tab navigation
        this.tabs = document.querySelectorAll('.app-tab');
        this.tabPanes = document.querySelectorAll('.app-tab-pane');
        
        // Stepper navigation
        this.stepper = document.querySelector('.app-stepper');
        this.stepperItems = document.querySelectorAll('.app-stepper-item');
        this.stepperProgress = document.querySelector('.app-stepper-progress');
        
        // Current state
        this.currentStep = 0;
        this.totalSteps = this.stepperItems ? this.stepperItems.length : 0;
        
        // Initialize components
        this.init();
    }
    
    init() {
        this.createSidenavBackdrop();
        this.bindEvents();
        this.initTabs();
        this.updateStepper();
    }
    
    createSidenavBackdrop() {
        // Create backdrop if it doesn't exist but sidenav does
        if (!this.sidenavBackdrop && this.sidenav) {
            this.sidenavBackdrop = document.createElement('div');
            this.sidenavBackdrop.className = 'app-sidenav-backdrop';
            document.body.appendChild(this.sidenavBackdrop);
        }
    }
    
    bindEvents() {
        // Toggle sidenav
        if (this.sidenavToggle) {
            this.sidenavToggle.addEventListener('click', () => {
                this.toggleSidenav();
            });
        }
        
        // Close sidenav
        if (this.sidenavClose) {
            this.sidenavClose.addEventListener('click', () => {
                this.closeSidenav();
            });
        }
        
        // Close sidenav on backdrop click
        if (this.sidenavBackdrop) {
            this.sidenavBackdrop.addEventListener('click', () => {
                this.closeSidenav();
            });
        }
        
        // Close sidenav on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sidenav && this.sidenav.classList.contains('active')) {
                this.closeSidenav();
            }
        });
        
        // Tab click handler
        this.tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.target;
                this.activateTab(target);
            });
        });
        
        // Navigation link handlers for active states
        document.addEventListener('click', (e) => {
            // Navbar links
            if (e.target.closest('.app-nav-link')) {
                const navLinks = document.querySelectorAll('.app-nav-link');
                navLinks.forEach(link => link.classList.remove('active'));
                e.target.closest('.app-nav-link').classList.add('active');
            }
            
            // Sidenav links
            if (e.target.closest('.app-sidenav-link')) {
                const sidenavLinks = document.querySelectorAll('.app-sidenav-link');
                sidenavLinks.forEach(link => link.classList.remove('active'));
                e.target.closest('.app-sidenav-link').classList.add('active');
                
                // Close sidenav on mobile after link click
                if (window.innerWidth < 992) {
                    this.closeSidenav();
                }
            }
        });
        
        // Window resize handler for responsive behavior
        window.addEventListener('resize', () => {
            // Close sidenav on larger screens if window is resized
            if (window.innerWidth >= 992 && this.sidenav && this.sidenav.classList.contains('active')) {
                this.closeSidenav();
            }
        });
    }
    
    toggleSidenav() {
        if (this.sidenav) {
            this.sidenav.classList.toggle('active');
            if (this.sidenavBackdrop) {
                this.sidenavBackdrop.classList.toggle('active');
            }
            
            // Prevent body scrolling when sidenav is open
            document.body.style.overflow = this.sidenav.classList.contains('active') ? 'hidden' : '';
        }
    }
    
    openSidenav() {
        if (this.sidenav && !this.sidenav.classList.contains('active')) {
            this.sidenav.classList.add('active');
            if (this.sidenavBackdrop) {
                this.sidenavBackdrop.classList.add('active');
            }
            document.body.style.overflow = 'hidden';
        }
    }
    
    closeSidenav() {
        if (this.sidenav && this.sidenav.classList.contains('active')) {
            this.sidenav.classList.remove('active');
            if (this.sidenavBackdrop) {
                this.sidenavBackdrop.classList.remove('active');
            }
            document.body.style.overflow = '';
        }
    }
    
    initTabs() {
        // Activate first tab by default if none is active
        if (this.tabs.length > 0 && !Array.from(this.tabs).some(tab => tab.classList.contains('active'))) {
            const firstTabTarget = this.tabs[0].dataset.target;
            this.activateTab(firstTabTarget);
        }
    }
    
    activateTab(targetId) {
        // Deactivate all tabs and panes
        this.tabs.forEach(tab => tab.classList.remove('active'));
        this.tabPanes.forEach(pane => pane.classList.remove('active'));
        
        // Activate the selected tab and pane
        const selectedTab = document.querySelector(`.app-tab[data-target="${targetId}"]`);
        const selectedPane = document.getElementById(targetId);
        
        if (selectedTab) selectedTab.classList.add('active');
        if (selectedPane) selectedPane.classList.add('active');
    }
    
    updateStepper() {
        if (!this.stepper || !this.stepperItems.length) return;
        
        // Update progress bar width
        if (this.stepperProgress) {
            const progressWidth = this.currentStep === 0 ? 0 : 
                                (this.currentStep / (this.totalSteps - 1)) * 100;
            this.stepperProgress.style.width = `${progressWidth}%`;
        }
        
        // Update stepper item states
        this.stepperItems.forEach((item, index) => {
            // Remove all state classes
            item.classList.remove('active', 'completed', 'error');
            
            // Add appropriate state class
            if (index < this.currentStep) {
                item.classList.add('completed');
            } else if (index === this.currentStep) {
                item.classList.add('active');
            }
        });
    }
    
    // Public methods for stepper control
    nextStep() {
        if (this.currentStep < this.totalSteps - 1) {
            this.currentStep++;
            this.updateStepper();
            return true;
        }
        return false;
    }
    
    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateStepper();
            return true;
        }
        return false;
    }
    
    goToStep(stepIndex) {
        if (stepIndex >= 0 && stepIndex < this.totalSteps) {
            this.currentStep = stepIndex;
            this.updateStepper();
            return true;
        }
        return false;
    }
    
    markStepComplete(stepIndex) {
        if (stepIndex >= 0 && stepIndex < this.totalSteps) {
            const stepItem = this.stepperItems[stepIndex];
            stepItem.classList.add('completed');
            stepItem.classList.remove('active', 'error');
            return true;
        }
        return false;
    }
    
    markStepError(stepIndex) {
        if (stepIndex >= 0 && stepIndex < this.totalSteps) {
            const stepItem = this.stepperItems[stepIndex];
            stepItem.classList.add('error');
            stepItem.classList.remove('active', 'completed');
            return true;
        }
        return false;
    }
}

// Initialize enhanced navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Make navigation instance globally available
    window.enhancedNav = new EnhancedNavigation();
});
