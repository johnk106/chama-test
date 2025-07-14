# UI Implementation Guide - Chamas Platform

## Quick Start for Other Pages

### 1. Header Pattern
Use this header pattern consistently across all pages:

```html
<!-- Mobile Header -->
<div class="mobile-header d-block d-md-none">
    <div class="d-flex justify-content-between align-items-center">
        <button class="btn-hamburger" onclick="openNav()">
            <i class='bx bx-menu'></i>
        </button>
        <h1 class="header-title">Page Title</h1>
        <div class="notification-badge-container">
            <button class="btn-notification">
                <i class='bx bx-bell'></i>
                {% if notifications.count > 0 %}
                    <span class="notification-badge">{{ notifications.count }}</span>
                {% endif %}
            </button>
        </div>
    </div>
</div>

<!-- Desktop Header -->
<div class="desktop-header d-none d-md-block">
    <div class="d-flex justify-content-between align-items-center">
        <h1 class="header-title">Page Title</h1>
        <div class="notification-badge-container">
            <button class="btn-notification">
                <i class='bx bx-bell'></i>
                {% if notifications.count > 0 %}
                    <span class="notification-badge">{{ notifications.count }}</span>
                {% endif %}
            </button>
        </div>
    </div>
</div>
```

### 2. Card Component Pattern
Use this card pattern for content sections:

```html
<div class="content-card">
    <div class="card-header">
        <h3 class="card-title">Section Title</h3>
        <button class="btn-action">
            <i class='bx bx-plus'></i>
            Add New
        </button>
    </div>
    <div class="card-content">
        <!-- Your content here -->
    </div>
</div>
```

### 3. List Item Pattern
For lists of items (members, transactions, etc.):

```html
<div class="list-container">
    <div class="list-item">
        <div class="item-icon">
            <i class='bx bx-user'></i>
        </div>
        <div class="item-content">
            <h4 class="item-title">Item Title</h4>
            <p class="item-subtitle">Item Description</p>
        </div>
        <div class="item-action">
            <span class="item-value">$500</span>
            <i class='bx bx-chevron-right'></i>
        </div>
    </div>
</div>
```

### 4. CSS Classes to Use

#### Layout Classes
- `.modern-page` - Wrap the entire page content
- `.page-content` - Main content container
- `.content-card` - Individual content sections
- `.section-grid` - Grid layout for multiple cards

#### Component Classes
- `.mobile-header` / `.desktop-header` - Headers
- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary action buttons
- `.btn-notification` - Notification bell button
- `.list-container` - Container for lists
- `.list-item` - Individual list items

#### Color Classes
- `.text-primary` - Primary text color (#06b6d4)
- `.text-secondary` - Secondary text color (#64748b)
- `.text-success` - Success color (#059669)
- `.text-danger` - Danger color (#dc2626)
- `.bg-primary` - Primary background
- `.bg-card` - Card background (white)

### 5. Common CSS Patterns

```css
/* Page Container */
.modern-page {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
    min-height: 100vh;
    padding: 0;
    margin: 0;
}

/* Content Cards */
.content-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}

.content-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* List Items */
.list-item {
    display: flex;
    align-items: center;
    padding: 16px 12px;
    border-radius: 12px;
    transition: background-color 0.2s;
    border-bottom: 1px solid #f1f5f9;
}

.list-item:hover {
    background-color: #f8fafc;
}

.list-item:last-child {
    border-bottom: none;
}

/* Buttons */
.btn-primary {
    background: linear-gradient(135deg, #06b6d4, #0891b2);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.2s;
    cursor: pointer;
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
}
```

### 6. Responsive Breakpoints

```css
/* Mobile First */
.content-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
}

/* Tablet */
@media (min-width: 768px) {
    .content-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 24px;
    }
}

/* Desktop */
@media (min-width: 1024px) {
    .content-grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 32px;
    }
}
```

### 7. Page-Specific Implementations

#### Contributions Page
- Use card pattern for contribution schemes
- List pattern for individual contributions
- Add floating action button for new contributions

#### Members Page
- Grid layout for member cards on desktop
- List layout for mobile
- Search and filter functionality

#### Loans Page
- Status badges for loan applications
- Progress bars for repayment status
- Action buttons for approve/decline

#### Reports Page
- Chart containers for data visualization
- Download buttons for reports
- Filter controls

### 8. JavaScript Interactions

```javascript
// Standard hover effects
document.querySelectorAll('.content-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Mobile navigation
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    document.getElementById("main").style.marginLeft = "150px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
}
```

### 9. Template Structure

```html
{% extends 'chamas/base.html' %}
{% load static %}

{% block head %}
<title>Page Title</title>
<link rel="stylesheet" href="{% static 'chamas/dashboard.css' %}">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
{% endblock %}

{% block body %}
<div class="modern-page">
    <!-- Include header pattern -->
    
    <div class="page-content">
        <!-- Your page content -->
    </div>
</div>
{% endblock %}
```

### 10. Quick Copy-Paste Sections

#### Action Bar
```html
<div class="action-bar">
    <div class="search-container">
        <input type="text" placeholder="Search..." class="search-input">
        <i class='bx bx-search search-icon'></i>
    </div>
    <div class="action-buttons">
        <button class="btn-secondary">
            <i class='bx bx-filter'></i>
            Filter
        </button>
        <button class="btn-primary">
            <i class='bx bx-plus'></i>
            Add New
        </button>
    </div>
</div>
```

#### Status Badge
```html
<span class="status-badge status-success">Active</span>
<span class="status-badge status-warning">Pending</span>
<span class="status-badge status-danger">Overdue</span>
```

This guide provides a consistent design system that can be applied across all pages in the chamas platform, ensuring a unified and professional user experience.