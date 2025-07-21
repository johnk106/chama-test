/**
 * Modern Members Page JavaScript
 * Handles search, pagination, modals, and member management
 */

// Global variables
let currentPage = 1;
const membersPerPage = 12;
let filteredMembers = [];
let allMembers = [];
let currentMemberData = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeMembers();
    setupEventListeners();
    initializeAccessibility();
});

/**
 * Initialize members functionality
 */
function initializeMembers() {
    try {
        const memberCards = document.querySelectorAll('.admin-member-card');
        allMembers = Array.from(memberCards);
        filteredMembers = [...allMembers];
        updatePagination();
        
        // Initialize search functionality
        const searchInput = document.getElementById('adminMemberSearch');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(filterMembers, 300));
        }
        
        console.log('Members initialized:', allMembers.length);
    } catch (error) {
        console.error('Error initializing members:', error);
        showAlert('Error loading members page', 'error');
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    try {
        // Modal event listeners
        const memberModal = document.getElementById('adminMemberModal');
        const addMemberModal = document.getElementById('adminAddMemberModal');
        
        if (memberModal) {
            memberModal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeMemberModal();
                }
            });
        }
        
        if (addMemberModal) {
            addMemberModal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeAddMemberModal();
                }
            });
        }
        
        // Keyboard navigation
        document.addEventListener('keydown', handleKeyboardNavigation);
        
        // Form submission
        const addMemberForm = document.getElementById('adminAddMemberForm');
        if (addMemberForm) {
            addMemberForm.addEventListener('submit', submitAddMember);
        }
        
        // Window resize handler for responsive pagination
        window.addEventListener('resize', debounce(updatePagination, 250));
        
    } catch (error) {
        console.error('Error setting up event listeners:', error);
    }
}

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
    try {
        // Add ARIA labels to member cards
        allMembers.forEach((card, index) => {
            const memberName = card.querySelector('.admin-member-name')?.textContent || 'Unknown';
            card.setAttribute('role', 'button');
            card.setAttribute('tabindex', '0');
            card.setAttribute('aria-label', `View details for ${memberName}`);
            
            // Add keyboard support for member cards
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const memberId = this.dataset.memberId;
                    if (memberId) {
                        openMemberModal(memberId);
                    }
                }
            });
        });
        
        // Add ARIA live region for announcements
        if (!document.getElementById('aria-live-region')) {
            const liveRegion = document.createElement('div');
            liveRegion.id = 'aria-live-region';
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }
        
    } catch (error) {
        console.error('Error initializing accessibility:', error);
    }
}

/**
 * Handle keyboard navigation
 */
function handleKeyboardNavigation(e) {
    try {
        if (e.key === 'Escape') {
            closeMemberModal();
            closeAddMemberModal();
        }
        
        // Handle arrow key navigation for member cards
        if (e.key === 'ArrowRight' || e.key === 'ArrowLeft' || e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            const focusedElement = document.activeElement;
            if (focusedElement && focusedElement.classList.contains('admin-member-card')) {
                e.preventDefault();
                navigateMemberCards(focusedElement, e.key);
            }
        }
    } catch (error) {
        console.error('Error in keyboard navigation:', error);
    }
}

/**
 * Navigate between member cards with arrow keys
 */
function navigateMemberCards(currentCard, direction) {
    try {
        const visibleCards = filteredMembers.filter(card => card.style.display !== 'none');
        const currentIndex = visibleCards.indexOf(currentCard);
        
        let nextIndex;
        switch (direction) {
            case 'ArrowRight':
                nextIndex = (currentIndex + 1) % visibleCards.length;
                break;
            case 'ArrowLeft':
                nextIndex = (currentIndex - 1 + visibleCards.length) % visibleCards.length;
                break;
            case 'ArrowDown':
                // Move to next row (assuming 3 cards per row on desktop)
                nextIndex = Math.min(currentIndex + 3, visibleCards.length - 1);
                break;
            case 'ArrowUp':
                // Move to previous row
                nextIndex = Math.max(currentIndex - 3, 0);
                break;
            default:
                return;
        }
        
        if (visibleCards[nextIndex]) {
            visibleCards[nextIndex].focus();
        }
    } catch (error) {
        console.error('Error navigating member cards:', error);
    }
}

/**
 * Filter members based on search input
 */
function filterMembers() {
    try {
        const searchTerm = document.getElementById('adminMemberSearch')?.value.toLowerCase() || '';
        
        if (!searchTerm) {
            filteredMembers = [...allMembers];
        } else {
            filteredMembers = allMembers.filter(card => {
                const name = card.querySelector('.admin-member-name')?.textContent.toLowerCase() || '';
                const role = card.querySelector('.admin-member-role')?.textContent.toLowerCase() || '';
                
                return name.includes(searchTerm) || role.includes(searchTerm);
            });
        }
        
        currentPage = 1;
        updatePagination();
        displayMembers();
        
        // Announce search results to screen readers
        announceToScreenReader(`Found ${filteredMembers.length} members matching "${searchTerm}"`);
        
    } catch (error) {
        console.error('Error filtering members:', error);
        showAlert('Error filtering members', 'error');
    }
}

/**
 * Display members for current page
 */
function displayMembers() {
    try {
        const start = (currentPage - 1) * membersPerPage;
        const end = start + membersPerPage;
        
        // Hide all members first
        allMembers.forEach(card => {
            card.style.display = 'none';
        });
        
        // Show members for current page
        const membersToShow = filteredMembers.slice(start, end);
        membersToShow.forEach(card => {
            card.style.display = 'block';
        });
        
        // Update empty state
        updateEmptyState(filteredMembers.length === 0);
        
    } catch (error) {
        console.error('Error displaying members:', error);
    }
}

/**
 * Update empty state display
 */
function updateEmptyState(isEmpty) {
    try {
        let emptyState = document.querySelector('.admin-empty-state');
        
        if (isEmpty && !emptyState) {
            const grid = document.getElementById('adminMembersGrid');
            if (grid) {
                emptyState = document.createElement('div');
                emptyState.className = 'admin-empty-state';
                emptyState.innerHTML = `
                    <div class="admin-empty-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h3>No Members Found</h3>
                    <p>Try adjusting your search criteria or add new members.</p>
                `;
                grid.appendChild(emptyState);
            }
        } else if (!isEmpty && emptyState) {
            emptyState.remove();
        }
    } catch (error) {
        console.error('Error updating empty state:', error);
    }
}

/**
 * Update pagination display
 */
function updatePagination() {
    try {
        const totalPages = Math.ceil(filteredMembers.length / membersPerPage);
        const paginationContainer = document.getElementById('adminPagination');
        
        if (!paginationContainer) return;
        
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            displayMembers();
            return;
        }
        
        let paginationHTML = '';
        
        // Previous button
        if (currentPage > 1) {
            paginationHTML += `
                <button class="admin-page-btn" onclick="changePage(${currentPage - 1})" aria-label="Previous page">
                    <i class="fas fa-chevron-left"></i>
                </button>
            `;
        }
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            paginationHTML += `<button class="admin-page-btn" onclick="changePage(1)">1</button>`;
            if (startPage > 2) {
                paginationHTML += `<span class="admin-page-btn" aria-hidden="true">...</span>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const isActive = i === currentPage ? 'active' : '';
            const ariaCurrent = i === currentPage ? 'aria-current="page"' : '';
            paginationHTML += `
                <button class="admin-page-btn ${isActive}" onclick="changePage(${i})" ${ariaCurrent}>
                    ${i}
                </button>
            `;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += `<span class="admin-page-btn" aria-hidden="true">...</span>`;
            }
            paginationHTML += `<button class="admin-page-btn" onclick="changePage(${totalPages})">${totalPages}</button>`;
        }
        
        // Next button
        if (currentPage < totalPages) {
            paginationHTML += `
                <button class="admin-page-btn" onclick="changePage(${currentPage + 1})" aria-label="Next page">
                    <i class="fas fa-chevron-right"></i>
                </button>
            `;
        }
        
        paginationContainer.innerHTML = paginationHTML;
        displayMembers();
        
    } catch (error) {
        console.error('Error updating pagination:', error);
    }
}

/**
 * Change to specific page
 */
function changePage(page) {
    try {
        if (page < 1 || page > Math.ceil(filteredMembers.length / membersPerPage)) {
            return;
        }
        
        currentPage = page;
        updatePagination();
        
        // Scroll to top of members grid
        const membersGrid = document.getElementById('adminMembersGrid');
        if (membersGrid) {
            membersGrid.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        // Announce page change to screen readers
        announceToScreenReader(`Page ${page} loaded`);
        
    } catch (error) {
        console.error('Error changing page:', error);
    }
}

/**
 * Open member details modal
 */
function openMemberModal(memberId) {
    try {
        const modal = document.getElementById('adminMemberModal');
        const modalBody = document.getElementById('adminMemberModalBody');
        const modalTitle = document.getElementById('memberModalTitle');
        
        if (!modal || !modalBody) {
            console.error('Modal elements not found');
            return;
        }
        
        // Show loading state
        modalBody.innerHTML = `
            <div class="admin-loading">
                <div class="admin-spinner"></div>
            </div>
        `;
        
        // Update modal title
        const memberCard = document.querySelector(`[data-member-id="${memberId}"]`);
        const memberName = memberCard?.querySelector('.admin-member-name')?.textContent || 'Member';
        if (modalTitle) {
            modalTitle.textContent = `${memberName} - Details`;
        }
        
        // Show modal
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
        
        // Set focus to close button for accessibility
        const closeBtn = modal.querySelector('.admin-modal-close');
        if (closeBtn) {
            setTimeout(() => closeBtn.focus(), 100);
        }
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Load member details
        setTimeout(() => {
            loadMemberDetails(memberId);
        }, 500);
        
        // Announce modal opening to screen readers
        announceToScreenReader(`Member details modal opened for ${memberName}`);
        
    } catch (error) {
        console.error('Error opening member modal:', error);
        showAlert('Error opening member details', 'error');
    }
}

/**
 * Load member details into modal
 */
function loadMemberDetails(memberId) {
    try {
        const modalBody = document.getElementById('adminMemberModalBody');
        const memberCard = document.querySelector(`[data-member-id="${memberId}"]`);
        
        if (!modalBody || !memberCard) {
            throw new Error('Required elements not found');
        }
        
        // Extract member data from card
        const name = memberCard.querySelector('.admin-member-name')?.textContent || 'Unknown';
        const role = memberCard.querySelector('.admin-member-role')?.textContent || 'Member';
        const avatar = memberCard.querySelector('.admin-member-avatar img')?.src || '';
        const contributions = memberCard.querySelector('.admin-stat-value')?.textContent || 'KSh 0';
        const loans = memberCard.querySelectorAll('.admin-stat-value')[1]?.textContent || '0';
        const memberSince = memberCard.querySelectorAll('.admin-stat-value')[2]?.textContent || 'Unknown';
        
        // In a real application, you would fetch detailed data via AJAX
        // For now, we'll use the available data and simulate additional details
        
        modalBody.innerHTML = `
            <div class="admin-member-details">
                <div class="admin-member-profile">
                    <div class="admin-member-avatar">
                        <img src="${avatar}" alt="${name}" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjEyMCIgdmlld0JveD0iMCAwIDEyMCAxMjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxjaXJjbGUgY3g9IjYwIiBjeT0iNjAiIHI9IjYwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjYwIiBjeT0iNDQiIHI9IjIwIiBmaWxsPSIjOUNBM0FGIi8+CjxwYXRoIGQ9Ik0yMCAxMDBDMjAgODAuNjcxOCAzNC4zMjY2IDY1IDUyIDY1SDY4Qzg1LjY3MzQgNjUgMTAwIDgwLjY3MTggMTAwIDEwMFYxMDBIMjBWMTAwWiIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K'">
                    </div>
                    <h3>${name}</h3>
                    <span class="admin-member-role ${role.toLowerCase()}-bulb">${role}</span>
                </div>
                <div class="admin-contact-info">
                    <h4>Contact Information</h4>
                    <div class="admin-contact-item">
                        <i class="fas fa-envelope admin-contact-icon"></i>
                        <span id="member-email">Loading...</span>
                    </div>
                    <div class="admin-contact-item">
                        <i class="fas fa-phone admin-contact-icon"></i>
                        <span id="member-phone">Loading...</span>
                    </div>
                    <div class="admin-contact-item">
                        <i class="fas fa-calendar admin-contact-icon"></i>
                        <span>Member since: ${memberSince}</span>
                    </div>
                    <div class="admin-contact-item">
                        <i class="fas fa-user-shield admin-contact-icon"></i>
                        <span>Role: ${role}</span>
                    </div>
                </div>
            </div>
            
            <div class="admin-records-section">
                <div class="admin-records-tabs" role="tablist">
                    <button class="admin-tab-button active" onclick="switchTab('contributions')" role="tab" aria-selected="true" aria-controls="contributions-tab" id="contributions-tab-btn">
                        Contributions
                    </button>
                    <button class="admin-tab-button" onclick="switchTab('loans')" role="tab" aria-selected="false" aria-controls="loans-tab" id="loans-tab-btn">
                        Loans
                    </button>
                </div>
                
                <div id="contributions-tab" class="admin-tab-content active" role="tabpanel" aria-labelledby="contributions-tab-btn">
                    <table class="admin-records-table">
                        <thead>
                            <tr>
                                <th scope="col">Date</th>
                                <th scope="col">Type</th>
                                <th scope="col">Amount</th>
                                <th scope="col">Status</th>
                            </tr>
                        </thead>
                        <tbody id="contributions-tbody">
                            <tr>
                                <td colspan="4" style="text-align: center; padding: 2rem; color: var(--admin-gray-500);">
                                    <i class="fas fa-spinner fa-spin" style="margin-right: 0.5rem;"></i>
                                    Loading contribution records...
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div id="loans-tab" class="admin-tab-content" role="tabpanel" aria-labelledby="loans-tab-btn">
                    <table class="admin-records-table">
                        <thead>
                            <tr>
                                <th scope="col">Date</th>
                                <th scope="col">Amount</th>
                                <th scope="col">Status</th>
                                <th scope="col">Balance</th>
                            </tr>
                        </thead>
                        <tbody id="loans-tbody">
                            <tr>
                                <td colspan="4" style="text-align: center; padding: 2rem; color: var(--admin-gray-500);">
                                    <i class="fas fa-spinner fa-spin" style="margin-right: 0.5rem;"></i>
                                    Loading loan records...
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        // Simulate loading member details with AJAX
        setTimeout(() => {
            loadMemberContactDetails(memberId);
            loadMemberContributions(memberId);
            loadMemberLoans(memberId);
        }, 1000);
        
    } catch (error) {
        console.error('Error loading member details:', error);
        modalBody.innerHTML = `
            <div class="admin-empty-state">
                <div class="admin-empty-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Error Loading Details</h3>
                <p>Unable to load member details. Please try again.</p>
            </div>
        `;
    }
}

/**
 * Simulate loading contact details
 */
function loadMemberContactDetails(memberId) {
    // In a real app, this would be an AJAX call
    setTimeout(() => {
        const emailElement = document.getElementById('member-email');
        const phoneElement = document.getElementById('member-phone');
        
        if (emailElement) {
            emailElement.textContent = 'member@example.com'; // Replace with actual data
        }
        if (phoneElement) {
            phoneElement.textContent = '+254 700 000 000'; // Replace with actual data
        }
    }, 500);
}

/**
 * Simulate loading contributions
 */
function loadMemberContributions(memberId) {
    setTimeout(() => {
        const tbody = document.getElementById('contributions-tbody');
        if (tbody) {
            // In a real app, fetch actual contribution data
            tbody.innerHTML = `
                <tr>
                    <td>Dec 15, 2023</td>
                    <td>Monthly Contribution</td>
                    <td>KSh 5,000</td>
                    <td><span style="color: var(--admin-success); font-weight: 600;">Paid</span></td>
                </tr>
                <tr>
                    <td>Nov 15, 2023</td>
                    <td>Monthly Contribution</td>
                    <td>KSh 5,000</td>
                    <td><span style="color: var(--admin-success); font-weight: 600;">Paid</span></td>
                </tr>
                <tr>
                    <td>Oct 15, 2023</td>
                    <td>Monthly Contribution</td>
                    <td>KSh 5,000</td>
                    <td><span style="color: var(--admin-warning); font-weight: 600;">Partial</span></td>
                </tr>
            `;
        }
    }, 800);
}

/**
 * Simulate loading loans
 */
function loadMemberLoans(memberId) {
    setTimeout(() => {
        const tbody = document.getElementById('loans-tbody');
        if (tbody) {
            // In a real app, fetch actual loan data
            tbody.innerHTML = `
                <tr>
                    <td>Nov 01, 2023</td>
                    <td>KSh 50,000</td>
                    <td><span style="color: var(--admin-warning); font-weight: 600;">Active</span></td>
                    <td>KSh 25,000</td>
                </tr>
                <tr>
                    <td>Aug 15, 2023</td>
                    <td>KSh 30,000</td>
                    <td><span style="color: var(--admin-success); font-weight: 600;">Paid</span></td>
                    <td>KSh 0</td>
                </tr>
            `;
        }
    }, 1200);
}

/**
 * Switch between tabs in modal
 */
function switchTab(tabName) {
    try {
        // Remove active class from all tabs and contents
        document.querySelectorAll('.admin-tab-button').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.admin-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Add active class to selected tab and content
        const activeTabBtn = document.querySelector(`#${tabName}-tab-btn`);
        const activeTabContent = document.getElementById(`${tabName}-tab`);
        
        if (activeTabBtn) {
            activeTabBtn.classList.add('active');
            activeTabBtn.setAttribute('aria-selected', 'true');
            activeTabBtn.focus();
        }
        
        if (activeTabContent) {
            activeTabContent.classList.add('active');
        }
        
        // Announce tab change to screen readers
        announceToScreenReader(`${tabName} tab selected`);
        
    } catch (error) {
        console.error('Error switching tab:', error);
    }
}

/**
 * Close member modal
 */
function closeMemberModal() {
    try {
        const modal = document.getElementById('adminMemberModal');
        if (modal) {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', 'true');
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            // Return focus to the member card that opened the modal
            if (currentMemberData && currentMemberData.cardElement) {
                currentMemberData.cardElement.focus();
            }
            
            // Announce modal closing to screen readers
            announceToScreenReader('Member details modal closed');
        }
    } catch (error) {
        console.error('Error closing member modal:', error);
    }
}

/**
 * Open add member modal
 */
function openAddMemberModal() {
    try {
        const modal = document.getElementById('adminAddMemberModal');
        if (modal) {
            modal.classList.add('active');
            modal.setAttribute('aria-hidden', 'false');
            
            // Prevent body scroll
            document.body.style.overflow = 'hidden';
            
            // Focus on first input
            setTimeout(() => {
                const firstInput = document.getElementById('memberName');
                if (firstInput) {
                    firstInput.focus();
                }
            }, 100);
            
            // Announce modal opening to screen readers
            announceToScreenReader('Add member form opened');
        }
    } catch (error) {
        console.error('Error opening add member modal:', error);
    }
}

/**
 * Close add member modal
 */
function closeAddMemberModal() {
    try {
        const modal = document.getElementById('adminAddMemberModal');
        if (modal) {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', 'true');
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            // Reset form
            const form = document.getElementById('adminAddMemberForm');
            if (form) {
                form.reset();
                
                // Clear any validation errors
                const errorElements = form.querySelectorAll('.error-message');
                errorElements.forEach(el => el.remove());
            }
            
            // Return focus to add button
            const addButton = document.querySelector('.admin-add-member');
            if (addButton) {
                addButton.focus();
            }
            
            // Announce modal closing to screen readers
            announceToScreenReader('Add member form closed');
        }
    } catch (error) {
        console.error('Error closing add member modal:', error);
    }
}

/**
 * Submit add member form
 */
function submitAddMember(event) {
    event.preventDefault();
    
    try {
        const form = event.target;
        const formData = new FormData(form);
        const memberData = Object.fromEntries(formData.entries());
        
        // Validate form data
        if (!validateMemberForm(memberData)) {
            return;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Adding...';
        submitBtn.disabled = true;
        
        // Add loading spinner
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
        
        // Simulate API call
        setTimeout(() => {
            // In real app, make AJAX call to add member
            const success = Math.random() > 0.2; // 80% success rate for demo
            
            if (success) {
                showAlert('Member added successfully!', 'success');
                closeAddMemberModal();
                
                // In a real app, you would refresh the member list or add the new member to the DOM
                announceToScreenReader('New member added successfully');
                
                // Optionally reload the page to show the new member
                // location.reload();
            } else {
                showAlert('Failed to add member. Please try again.', 'error');
            }
            
            // Reset button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('Error submitting add member form:', error);
        showAlert('Error adding member. Please try again.', 'error');
    }
}

/**
 * Validate member form data
 */
function validateMemberForm(data) {
    try {
        const errors = [];
        
        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        
        // Validate name
        if (!data.name || data.name.trim().length < 2) {
            errors.push({ field: 'memberName', message: 'Name must be at least 2 characters long' });
        }
        
        // Validate email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!data.email || !emailRegex.test(data.email)) {
            errors.push({ field: 'memberEmail', message: 'Please enter a valid email address' });
        }
        
        // Validate phone
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        if (!data.mobile || !phoneRegex.test(data.mobile)) {
            errors.push({ field: 'memberPhone', message: 'Please enter a valid phone number' });
        }
        
        // Validate role
        if (!data.role) {
            errors.push({ field: 'memberRole', message: 'Please select a role' });
        }
        
        // Display errors
        errors.forEach(error => {
            const field = document.getElementById(error.field);
            if (field) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.style.color = 'var(--admin-error)';
                errorDiv.style.fontSize = '0.875rem';
                errorDiv.style.marginTop = '0.25rem';
                errorDiv.textContent = error.message;
                errorDiv.setAttribute('role', 'alert');
                
                field.parentNode.appendChild(errorDiv);
                
                // Add error styling to field
                field.style.borderColor = 'var(--admin-error)';
                
                // Remove error styling on input
                field.addEventListener('input', function() {
                    this.style.borderColor = '';
                    const errorMsg = this.parentNode.querySelector('.error-message');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }, { once: true });
            }
        });
        
        // Focus on first error field
        if (errors.length > 0) {
            const firstErrorField = document.getElementById(errors[0].field);
            if (firstErrorField) {
                firstErrorField.focus();
            }
            
            announceToScreenReader(`Form has ${errors.length} error${errors.length > 1 ? 's' : ''}`);
        }
        
        return errors.length === 0;
        
    } catch (error) {
        console.error('Error validating form:', error);
        return false;
    }
}

/**
 * Confirm member removal
 */
function confirmRemoveMember(memberId, memberName) {
    try {
        const confirmed = confirm(
            `Are you sure you want to remove ${memberName} from this chama?\n\nThis action cannot be undone and will remove all associated records.`
        );
        
        if (confirmed) {
            removeMember(memberId);
        }
    } catch (error) {
        console.error('Error confirming member removal:', error);
    }
}

/**
 * Remove member
 */
function removeMember(memberId) {
    try {
        const memberCard = document.querySelector(`[data-member-id="${memberId}"]`);
        const memberName = memberCard?.querySelector('.admin-member-name')?.textContent || 'Member';
        
        if (memberCard) {
            // Show loading state
            memberCard.style.opacity = '0.5';
            memberCard.style.pointerEvents = 'none';
            
            // Add loading overlay
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.style.position = 'absolute';
            loadingOverlay.style.top = '0';
            loadingOverlay.style.left = '0';
            loadingOverlay.style.right = '0';
            loadingOverlay.style.bottom = '0';
            loadingOverlay.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
            loadingOverlay.style.display = 'flex';
            loadingOverlay.style.alignItems = 'center';
            loadingOverlay.style.justifyContent = 'center';
            loadingOverlay.style.borderRadius = 'inherit';
            loadingOverlay.innerHTML = '<i class="fas fa-spinner fa-spin" style="color: var(--admin-primary);"></i>';
            
            memberCard.style.position = 'relative';
            memberCard.appendChild(loadingOverlay);
        }
        
        // Simulate API call
        setTimeout(() => {
            const success = Math.random() > 0.1; // 90% success rate for demo
            
            if (success) {
                showAlert(`${memberName} has been removed from the chama.`, 'warning');
                
                if (memberCard) {
                    // Animate removal
                    memberCard.style.transform = 'scale(0.8)';
                    memberCard.style.opacity = '0';
                    
                    setTimeout(() => {
                        memberCard.remove();
                        
                        // Update member arrays
                        allMembers = allMembers.filter(card => card !== memberCard);
                        filteredMembers = filteredMembers.filter(card => card !== memberCard);
                        
                        // Refresh pagination
                        updatePagination();
                        
                        announceToScreenReader(`${memberName} removed from chama`);
                    }, 300);
                }
            } else {
                showAlert('Failed to remove member. Please try again.', 'error');
                
                if (memberCard) {
                    // Restore card state
                    memberCard.style.opacity = '1';
                    memberCard.style.pointerEvents = 'auto';
                    
                    const overlay = memberCard.querySelector('.loading-overlay');
                    if (overlay) {
                        overlay.remove();
                    }
                }
            }
        }, 1500);
        
    } catch (error) {
        console.error('Error removing member:', error);
        showAlert('Error removing member. Please try again.', 'error');
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    try {
        const alertsContainer = document.getElementById('admin-alerts-container');
        if (!alertsContainer) return;
        
        const alertId = 'alert-' + Date.now();
        const iconMap = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        const alertHTML = `
            <div id="${alertId}" class="admin-alert admin-alert-${type}" role="alert" aria-live="polite">
                <i class="fas fa-${iconMap[type] || 'info-circle'}"></i>
                <span>${message}</span>
                <button onclick="closeAlert('${alertId}')" aria-label="Close alert" style="background: none; border: none; font-size: 1.2rem; cursor: pointer; color: inherit; opacity: 0.7;">
                    &times;
                </button>
            </div>
        `;
        
        alertsContainer.insertAdjacentHTML('beforeend', alertHTML);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            closeAlert(alertId);
        }, 5000);
        
        // Announce to screen readers
        announceToScreenReader(message);
        
    } catch (error) {
        console.error('Error showing alert:', error);
    }
}

/**
 * Close alert
 */
function closeAlert(alertId) {
    try {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                alert.remove();
            }, 300);
        }
    } catch (error) {
        console.error('Error closing alert:', error);
    }
}

/**
 * Announce message to screen readers
 */
function announceToScreenReader(message) {
    try {
        const liveRegion = document.getElementById('aria-live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    } catch (error) {
        console.error('Error announcing to screen reader:', error);
    }
}

/**
 * Get CSRF token for Django
 */
function getCsrfToken() {
    try {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    } catch (error) {
        console.error('Error getting CSRF token:', error);
        return '';
    }
}

/**
 * Debounce function to limit function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to format currency
 */
function formatCurrency(amount) {
    try {
        return new Intl.NumberFormat('en-KE', {
            style: 'currency',
            currency: 'KES',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    } catch (error) {
        return `KSh ${amount.toLocaleString()}`;
    }
}

/**
 * Utility function to format date
 */
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(date);
    } catch (error) {
        return dateString;
    }
}

// Export functions for testing (if in a module environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        filterMembers,
        changePage,
        openMemberModal,
        closeMemberModal,
        openAddMemberModal,
        closeAddMemberModal,
        submitAddMember,
        confirmRemoveMember,
        removeMember,
        showAlert,
        closeAlert
    };
}


