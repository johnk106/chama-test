# Contribution Update Button Fix

## Issue Description
In the Chamas Battery contributions page, when a contribution scheme has records, the create records form correctly disappears, but the "Update Contributions" button remains visible. This creates confusion for users as they can see a button for a form that is no longer accessible.

## Root Cause
The issue was in the JavaScript code in `/workspace/chamas/templates/chamas/contributions.html`. When a contribution has first-round records (`hasFirstRound` is true), the system:

1. ✅ Correctly hides the contribution form card using the `force-hidden` CSS class
2. ✅ Correctly adjusts the layout by adding `full-width` class to the details grid
3. ❌ **Failed to hide the "Update Contributions" button** (ID: `update-contributions`)

The mobile view was correctly implemented and already hides the update button when needed, but the desktop view was missing this functionality.

## Solution Implemented

### 1. Updated Desktop Contribution Details Function
**File:** `/workspace/chamas/templates/chamas/contributions.html`
**Lines:** ~1335-1346

Added logic to hide/show the desktop update button based on whether the contribution has first-round records:

```javascript
// Show/hide the contribution form based on first round records status
const hasFirstRound = response.has_first_round_records;
const contributionFormCard = $(".contribution-form-card");
const detailsGrid = $(".details-grid");
const updateButton = $("#update-contributions");  // Added this line

if (hasFirstRound) {
    contributionFormCard.addClass('force-hidden');
    detailsGrid.addClass('full-width');
    updateButton.hide();  // Added this line
} else {
    contributionFormCard.removeClass('force-hidden');
    detailsGrid.removeClass('full-width');
    updateButton.show();  // Added this line
}
```

### 2. Updated Admin Visibility Function
**File:** `/workspace/chamas/templates/chamas/contributions.html`
**Lines:** ~855-867

Enhanced the `applyAdminVisibility` function to also handle the update button:

```javascript
setTimeout(function() {
    const contributionFormCard = $(".contribution-form-card");
    const detailsGrid = $(".details-grid");
    const updateButton = $("#update-contributions");  // Added this line
    
    if (contributionFormCard.hasClass('force-hidden')) {
        detailsGrid.addClass('full-width');
        updateButton.hide();  // Added this line
    } else if (contributionFormCard.hasClass('admin') && $("body").hasClass("user-is-admin")) {
        detailsGrid.removeClass('full-width');
        updateButton.show();  // Added this line
    }
}, 100);
```

### 3. Updated Initial Page Load Logic
**File:** `/workspace/chamas/templates/chamas/contributions.html**
**Lines:** ~1732-1739

Added update button handling to the initial page load logic:

```javascript
// Also ensure proper layout on initial load
const contributionFormCard = $(".contribution-form-card");
const detailsGrid = $(".details-grid");
const updateButton = $("#update-contributions");  // Added this line
if (contributionFormCard.hasClass('force-hidden')) {
    detailsGrid.addClass('full-width');
    updateButton.hide();  // Added this line
} else {
    detailsGrid.removeClass('full-width');
    updateButton.show();  // Added this line
}
```

## Verification

### Mobile View (Already Working)
- ✅ Update button correctly hides when contribution has records
- ✅ Update button shows when contribution has no records
- ✅ Members list and header also hide/show appropriately

### Desktop View (Now Fixed)
- ✅ Update button now hides when contribution has records
- ✅ Update button shows when contribution has no records
- ✅ Form card continues to hide/show as expected
- ✅ Layout adjusts properly with full-width class

## Behavior Summary

| Contribution State | Form Visibility | Update Button Visibility | Layout |
|-------------------|-----------------|-------------------------|---------|
| **No Records** | ✅ Visible | ✅ Visible | Normal 2-column |
| **Has Records** | ❌ Hidden (`force-hidden`) | ❌ Hidden | Full-width records |

## Files Modified
1. `/workspace/chamas/templates/chamas/contributions.html` - Added JavaScript logic to hide/show update button
2. `/workspace/chamas/static/chamas/contribution.css` - No changes needed (CSS already handles form hiding)

## Testing Recommendations
1. Create a new contribution scheme
2. Verify both form and update button are visible
3. Add some contribution records to the scheme
4. Verify both form and update button are hidden
5. Test on both desktop and mobile views
6. Test with different admin/member view modes

The fix ensures consistent behavior between the contribution form and its associated update button, providing a better user experience by preventing confusion when the form is not accessible.