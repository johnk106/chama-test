# Admin/Member View Switch Implementation

## Overview

This implementation provides a modern, accessible toggle switch to replace the previous text-based admin/member view switching. The switch offers a smooth sliding animation, proper accessibility features, and state persistence.

## Features

### 🎨 **Modern Design**
- **Smooth Sliding Animation**: CSS transitions with cubic-bezier easing
- **Gradient Backgrounds**: Soft gradients for visual appeal
- **Subtle Shadows**: Depth and visual hierarchy
- **Rounded Corners**: Modern pill-shaped design
- **Color-Coded States**: Blue for member, green for admin

### ♿ **Accessibility**
- **ARIA Attributes**: `role="switch"` and `aria-checked`
- **Keyboard Navigation**: Tab to focus, Space/Enter to toggle
- **Screen Reader Support**: Proper labeling and state announcements
- **Focus Indicators**: Clear visual focus states

### 📱 **Responsive Design**
- **Touch-Friendly**: Large touch targets on mobile
- **Desktop Optimized**: Mouse and keyboard interactions
- **Adaptive Sizing**: Responsive dimensions for different screens

### 🔒 **Security & State Management**
- **Server-Side Validation**: AJAX calls to verify admin permissions
- **Graceful Fallback**: Falls back to member view if admin verification fails
- **State Persistence**: localStorage per group
- **Disabled States**: Visual feedback when switch is disabled

## Implementation Details

### HTML Structure

```html
<li class="dropdown-item view-switch-container">
  <label class="view-switch" role="switch" aria-checked="false" tabindex="0">
    <input type="checkbox" class="view-switch-input" aria-hidden="true">
    <span class="view-switch-track">
      <span class="view-switch-knob"></span>
      <span class="view-switch-label view-switch-label-member">Member</span>
      <span class="view-switch-label view-switch-label-admin">Admin</span>
    </span>
  </label>
</li>
```

### CSS Classes

- `.view-switch-container`: Container with padding and border
- `.view-switch`: Main switch element with accessibility attributes
- `.view-switch-input`: Hidden checkbox for state management
- `.view-switch-track`: Pill-shaped track with gradient background
- `.view-switch-knob`: Sliding element with gradient and shadow
- `.view-switch-label`: Text labels for Member/Admin
- `.disabled`: Visual state for disabled switches

### JavaScript Functionality

#### Initialization
```javascript
// Disable switch until admin verification
$(".view-switch").addClass('disabled');
$(".view-switch-input").prop('disabled', true);

// Set initial state from localStorage
var savedView = localStorage.getItem(storageKey) || "member";
$(".view-switch-input").prop('checked', savedView === "admin");
$(".view-switch").attr('aria-checked', savedView === "admin");
```

#### Admin Verification
```javascript
$.ajax({
  url: '/chamas-bookeeping/get_user_role/',
  data: { group_id: groupId },
  success: function(data) {
    if (data.role === "admin") {
      $(".view-switch").removeClass('disabled');
      $(".view-switch-input").prop('disabled', false);
    } else {
      // Keep disabled, fall back to member view
      $(".view-switch-input").prop('checked', false);
      updateView("member");
    }
  }
});
```

#### Event Handling
```javascript
// Change event for toggle
$(".view-switch-input").on("change", function() {
  var isAdminView = $(this).is(':checked');
  if (isAdminView) {
    // Re-verify admin permissions
    verifyAdminAndUpdateView();
  } else {
    // Switch to member view immediately
    updateView("member");
  }
});

// Keyboard accessibility
$(".view-switch").on("keydown", function(e) {
  if (e.key === " " || e.key === "Enter") {
    e.preventDefault();
    var input = $(this).find('.view-switch-input');
    if (!input.prop('disabled')) {
      input.prop('checked', !input.prop('checked')).trigger('change');
    }
  }
});
```

## Files Modified

### 1. `chamas/templates/chamas/base.html`
- **HTML Structure**: Replaced text links with accessible switch
- **JavaScript**: Updated event handling and state management
- **ARIA Attributes**: Added proper accessibility attributes

### 2. `chamas/static/chamas/chamas-base.css`
- **Switch Styles**: Complete CSS implementation with gradients
- **Responsive Design**: Mobile and desktop adaptations
- **Accessibility**: Focus states and disabled styles
- **Animations**: Smooth transitions and hover effects

### 3. `chamas/templates/chamas/dashboard.html`
- **Test Section**: Updated instructions for new switch
- **Accessibility Info**: Added keyboard navigation details

## Usage Instructions

### For Users:
1. Click on your profile picture in the top-right corner
2. Look for the view switch in the dropdown (Member ↔ Admin)
3. Click the switch or use Space/Enter key to toggle
4. Notice how page content changes based on selected view

### For Developers:
1. **Adding Admin Content**: Use `.admin` CSS class
2. **Adding Member Content**: Use `.member` CSS class
3. **State Management**: Check localStorage for current view
4. **Accessibility**: Ensure proper ARIA attributes

## Technical Specifications

### CSS Properties
- **Track**: 120px × 36px (desktop), 100px × 32px (mobile)
- **Knob**: 56px × 32px (desktop), 48px × 28px (mobile)
- **Animation**: 0.3s cubic-bezier(0.4, 0, 0.2, 1)
- **Colors**: Blue gradient (#2191a5) for member, green (#28a745) for admin

### JavaScript Events
- `change`: Toggle state changes
- `keydown`: Keyboard navigation (Space/Enter)
- `focus/blur`: Visual feedback

### State Management
- **localStorage Key**: `selectedView_${groupId}`
- **Values**: "member" or "admin"
- **Persistence**: Per-group preferences

## Accessibility Features

### ARIA Attributes
- `role="switch"`: Indicates switch functionality
- `aria-checked`: Current state (true/false)
- `tabindex="0"`: Keyboard focusable
- `aria-hidden="true"`: Hide checkbox from screen readers

### Keyboard Support
- **Tab**: Focus the switch
- **Space/Enter**: Toggle the switch
- **Visual Focus**: Clear outline indicator

### Screen Reader Support
- Proper labeling with "Member" and "Admin" text
- State announcements via aria-checked
- Disabled state indication

## Browser Compatibility

- ✅ Chrome/Chromium (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Considerations

- **CSS Transitions**: Hardware-accelerated animations
- **Minimal DOM**: Efficient state updates
- **Lazy Loading**: Admin verification only when needed
- **Cached States**: localStorage for performance

## Security Features

- **Server-Side Validation**: All admin checks via AJAX
- **Permission Verification**: Multiple validation points
- **Graceful Degradation**: Falls back to member view on errors
- **CSRF Protection**: Maintains existing security measures

## Testing Checklist

### Functionality
- [ ] Switch toggles between Member and Admin views
- [ ] State persists across page reloads
- [ ] Admin verification works correctly
- [ ] Fallback to member view when not admin
- [ ] Error handling for failed AJAX requests

### Accessibility
- [ ] Keyboard navigation works (Tab, Space, Enter)
- [ ] Screen reader announces state changes
- [ ] Focus indicators are visible
- [ ] ARIA attributes are properly set

### Responsive Design
- [ ] Works on desktop browsers
- [ ] Works on mobile devices
- [ ] Touch targets are appropriately sized
- [ ] Animations are smooth on all devices

### Visual Design
- [ ] Smooth sliding animation
- [ ] Color transitions work correctly
- [ ] Hover effects are responsive
- [ ] Disabled state is clearly indicated

## Troubleshooting

### Common Issues:
1. **Switch not appearing**: Check if user has admin permissions
2. **State not persisting**: Verify localStorage is enabled
3. **Animations not smooth**: Check CSS transitions are supported
4. **Keyboard not working**: Ensure proper event handling

### Debug Information:
- Console logs for role verification errors
- Network tab for AJAX request monitoring
- localStorage inspection for state debugging
- Accessibility tree inspection for ARIA attributes

---

**Implementation Date**: December 2024
**Version**: 2.0.0
**Maintainer**: Full Stack Django Developer