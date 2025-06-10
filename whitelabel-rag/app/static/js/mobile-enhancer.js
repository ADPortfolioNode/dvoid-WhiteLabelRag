/**
 * WhiteLabelRAG Mobile Enhancements
 * 
 * This script adds mobile-specific optimizations and features
 */

class MobileEnhancer {
    constructor() {
        this.initialize();
    }
    
    initialize() {
        this.detectMobile();
        this.setupMobileOptimizations();
        this.setupHapticFeedback();
        this.fixMobileViewportHeight();
        this.setupMobileCollapsibles();
        this.optimizeForOrientation();
        
        console.log('Mobile enhancements initialized');
    }
    
    detectMobile() {
        // Detect if we're on a mobile device
        this.isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        this.isAndroid = /Android/i.test(navigator.userAgent);
        
        // Add mobile class to body
        if (this.isMobile) {
            document.body.classList.add('mobile-device');
            
            if (this.isIOS) document.body.classList.add('ios-device');
            if (this.isAndroid) document.body.classList.add('android-device');
        }
    }
    
    setupMobileOptimizations() {
        if (!this.isMobile) return;
        
        // Add safe area classes
        document.querySelectorAll('.chat-form').forEach(el => {
            el.classList.add('mobile-safe-area-bottom');
        });
        
        document.querySelectorAll('.navbar').forEach(el => {
            el.classList.add('mobile-safe-area-top');
        });
        
        // Optimize file list scrolling
        document.querySelectorAll('.files-container').forEach(el => {
            el.classList.add('momentum-scroll');
        });
        
        // Improve button feedback
        document.querySelectorAll('button, .btn').forEach(button => {
            button.addEventListener('touchstart', () => {
                button.classList.add('active');
            });
            
            button.addEventListener('touchend', () => {
                button.classList.remove('active');
                this.triggerHapticFeedback();
            });
        });
        
        // Make messages more readable
        document.querySelectorAll('.message-content').forEach(el => {
            el.style.fontSize = '1rem';
        });
    }
    
    setupHapticFeedback() {
        // Setup haptic feedback for mobile devices
        this.canVibrate = 'vibrate' in navigator;
        
        window.triggerHapticFeedback = (intensity = 'medium') => {
            if (!this.canVibrate) return;
            
            // Different intensities
            switch(intensity) {
                case 'light':
                    navigator.vibrate(10);
                    break;
                case 'medium':
                    navigator.vibrate(15);
                    break;
                case 'strong':
                    navigator.vibrate([10, 30, 10]);
                    break;
                case 'error':
                    navigator.vibrate([50, 100, 50]);
                    break;
                case 'success':
                    navigator.vibrate([10, 50, 10, 50]);
                    break;
            }
        };
        
        // Add visual feedback
        document.querySelectorAll('.haptic-feedback').forEach(el => {
            el.addEventListener('click', () => {
                el.classList.add('active');
                setTimeout(() => el.classList.remove('active'), 500);
            });
        });
    }
    
    fixMobileViewportHeight() {
        // Fix the 100vh issue on mobile browsers
        const setVh = () => {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        };
        
        setVh();
        window.addEventListener('resize', setVh);
        
        // Special handling for iOS
        if (this.isIOS) {
            window.addEventListener('orientationchange', () => {
                setTimeout(setVh, 200);
            });
            
            // Fix for iOS keyboard
            const inputs = document.querySelectorAll('input, textarea');
            inputs.forEach(input => {
                input.addEventListener('focus', () => {
                    document.body.classList.add('keyboard-open');
                });
                
                input.addEventListener('blur', () => {
                    document.body.classList.remove('keyboard-open');
                });
            });
        }
    }
    
    setupMobileCollapsibles() {
        // Make mobile sections collapsible for better space usage
        document.querySelectorAll('.mobile-collapsible-trigger').forEach(trigger => {
            trigger.addEventListener('click', () => {
                const target = document.querySelector(trigger.dataset.target);
                if (!target) return;
                
                if (target.classList.contains('show')) {
                    target.classList.remove('show');
                    target.style.maxHeight = '0';
                    trigger.classList.remove('active');
                } else {
                    target.classList.add('show');
                    target.style.maxHeight = target.scrollHeight + 'px';
                    trigger.classList.add('active');
                }
                
                this.triggerHapticFeedback('light');
            });
        });
    }
    
    optimizeForOrientation() {
        // Optimize layout based on device orientation
        const handleOrientationChange = () => {
            const isLandscape = window.matchMedia('(orientation: landscape)').matches;
            
            if (isLandscape) {
                document.body.classList.add('landscape-mode');
                
                // Hide some elements in landscape to maximize chat space
                document.querySelectorAll('.landscape-hidden').forEach(el => {
                    el.style.display = 'none';
                });
                
                // Adjust layouts for landscape
                document.querySelectorAll('.landscape-flex-row').forEach(el => {
                    el.style.display = 'flex';
                    el.style.flexDirection = 'row';
                });
            } else {
                document.body.classList.remove('landscape-mode');
                
                // Restore hidden elements
                document.querySelectorAll('.landscape-hidden').forEach(el => {
                    el.style.display = '';
                });
                
                // Restore layouts
                document.querySelectorAll('.landscape-flex-row').forEach(el => {
                    el.style.display = '';
                    el.style.flexDirection = '';
                });
            }
        };
        
        // Check orientation on load
        handleOrientationChange();
        
        // Listen for orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(handleOrientationChange, 200);
        });
        
        window.addEventListener('resize', handleOrientationChange);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mobileEnhancer = new MobileEnhancer();
});
