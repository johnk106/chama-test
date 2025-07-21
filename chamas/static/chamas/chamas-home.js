/**
 * Chamas Home Page JavaScript
 * Handles tab switching, coming soon states, and user interactions
 */

class ChamasHomePage {
    constructor() {
        this.options = document.querySelectorAll('.chama-option');
        this.panels = document.querySelectorAll('.content-panel');
        this.bookkeepingButtons = document.querySelectorAll('.btn-primary-custom, .btn-secondary-custom');
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.initializeDefaultState();
        this.setupAccessibility();
    }
    
    /**
     * Bind all event listeners
     */
    bindEvents() {
        // Option click handlers
        this.options.forEach(option => {
            option.addEventListener('click', (e) => this.handleOptionClick(e));
            option.addEventListener('keypress', (e) => this.handleOptionKeypress(e));
            option.addEventListener('mouseenter', (e) => this.handleOptionHover(e));
            option.addEventListener('mouseleave', (e) => this.handleOptionLeave(e));
        });
        
        // Button click handlers
        this.bookkeepingButtons.forEach(button => {
            button.addEventListener('click', (e) => this.handleButtonClick(e));
        });
        
        // Scroll to content when option is selected
        this.options.forEach(option => {
            option.addEventListener('click', () => this.scrollToContent());
        });
    }
    
    /**
     * Handle option click events
     */
    handleOptionClick(event) {
        const option = event.currentTarget;
        const optionType = option.getAttribute('data-option');
        
        // Add click animation
        this.addClickAnimation(option);
        
        // Switch to the selected option
        this.switchOption(optionType);
        
        // Track analytics if available
        this.trackOptionSelection(optionType);
    }
    
    /**
     * Handle keyboard navigation
     */
    handleOptionKeypress(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            event.currentTarget.click();
        }
    }
    
    /**
     * Handle option hover effects
     */
    handleOptionHover(event) {
        const option = event.currentTarget;
        
        // Only apply hover effects if motion is not reduced
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            option.style.transform = 'translateY(-2px)';
        }
        
        // Add hover class for additional styling
        option.classList.add('hovered');
    }
    
    /**
     * Handle option leave effects
     */
    handleOptionLeave(event) {
        const option = event.currentTarget;
        
        // Reset transform if not active
        if (!option.classList.contains('active')) {
            option.style.transform = 'translateY(0)';
        }
        
        // Remove hover class
        option.classList.remove('hovered');
    }
    
    /**
     * Handle button clicks with loading states
     */
    handleButtonClick(event) {
        const button = event.currentTarget;
        
        // Add loading state
        button.classList.add('loading');
        
        // Show loading feedback
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="bx bx-loader-alt bx-spin" aria-hidden="true"></i> Loading...';
        
        // Simulate loading (remove this in production if not needed)
        setTimeout(() => {
            // The actual navigation will happen, so this timeout might not complete
            button.classList.remove('loading');
            button.innerHTML = originalText;
        }, 2000);
    }
    
    /**
     * Switch active option and panel
     */
    switchOption(targetOption) {
        // Remove active class from all options and panels
        this.options.forEach(option => {
            option.classList.remove('active');
            option.setAttribute('aria-selected', 'false');
        });
        
        this.panels.forEach(panel => {
            panel.classList.remove('active');
            panel.setAttribute('aria-hidden', 'true');
        });
        
        // Add active class to selected option and panel
        const selectedOption = document.querySelector(`[data-option="${targetOption}"]`);
        const selectedPanel = document.getElementById(`${targetOption}-panel`);
        
        if (selectedOption && selectedPanel) {
            selectedOption.classList.add('active');
            selectedOption.setAttribute('aria-selected', 'true');
            
            selectedPanel.classList.add('active');
            selectedPanel.setAttribute('aria-hidden', 'false');
            
            // Announce the change to screen readers
            this.announceChange(targetOption);
        }
    }
    
    /**
     * Initialize default state
     */
    initializeDefaultState() {
        // Set bookkeeping as default active option
        this.switchOption('bookkeeping');
    }
    
    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        // Add ARIA roles and properties
        this.options.forEach((option, index) => {
            option.setAttribute('role', 'tab');
            option.setAttribute('aria-selected', 'false');
            option.setAttribute('tabindex', index === 1 ? '0' : '-1'); // Bookkeeping is default
        });
        
        this.panels.forEach(panel => {
            panel.setAttribute('role', 'tabpanel');
            panel.setAttribute('aria-hidden', 'true');
        });
        
        // Add keyboard navigation between tabs
        this.setupKeyboardNavigation();
    }
    
    /**
     * Setup keyboard navigation for tabs
     */
    setupKeyboardNavigation() {
        this.options.forEach((option, index) => {
            option.addEventListener('keydown', (e) => {
                let targetIndex = index;
                
                switch (e.key) {
                    case 'ArrowRight':
                    case 'ArrowDown':
                        e.preventDefault();
                        targetIndex = (index + 1) % this.options.length;
                        break;
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        e.preventDefault();
                        targetIndex = (index - 1 + this.options.length) % this.options.length;
                        break;
                    case 'Home':
                        e.preventDefault();
                        targetIndex = 0;
                        break;
                    case 'End':
                        e.preventDefault();
                        targetIndex = this.options.length - 1;
                        break;
                    default:
                        return;
                }
                
                // Focus and activate the target option
                this.options[targetIndex].focus();
                this.options[targetIndex].click();
            });
        });
    }
    
    /**
     * Add click animation effect
     */
    addClickAnimation(element) {
        element.style.transform = 'scale(0.98)';
        
        setTimeout(() => {
            element.style.transform = element.classList.contains('active') ? 
                'translateY(-2px)' : 'translateY(0)';
        }, 150);
    }
    
    /**
     * Scroll to content area smoothly
     */
    scrollToContent() {
        const contentSection = document.querySelector('.chamas-content');
        if (contentSection) {
            contentSection.scrollIntoView({ 
                behavior: 'smooth',
                block: 'nearest'
            });
        }
    }
    
    /**
     * Announce changes to screen readers
     */
    announceChange(optionType) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        
        let message = '';
        switch (optionType) {
            case 'bookkeeping':
                message = 'Book keeping option selected. This feature is available.';
                break;
            case 'merry-go-round':
                message = 'Merry-go-round chama option selected. This feature is coming soon.';
                break;
            case 'table-banking':
                message = 'Table banking option selected. This feature is coming soon.';
                break;
        }
        
        announcement.textContent = message;
        document.body.appendChild(announcement);
        
        // Remove the announcement after it's been read
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
    
    /**
     * Track option selection for analytics
     */
    trackOptionSelection(optionType) {
        // Implement analytics tracking here if needed
        if (typeof gtag !== 'undefined') {
            gtag('event', 'chama_option_selected', {
                'option_type': optionType,
                'page_title': 'Chamas Home'
            });
        }
        
        // Console log for development
        console.log(`Chama option selected: ${optionType}`);
    }
}

// Utility class for screen reader only content
const srOnlyStyles = `
    .sr-only {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }
`;

// Add screen reader styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = srOnlyStyles;
document.head.appendChild(styleSheet);

// Initialize the chamas home page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ChamasHomePage();
});

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChamasHomePage;
}