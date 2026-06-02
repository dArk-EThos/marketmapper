"""Template tags and filters for the opportunities app."""

from datetime import date

from django import template

register = template.Library()

# Map internal category keys to display names
CATEGORY_LABELS = {
    "food": "Food",
    "craft": "Craft",
    "art": "Art",
    "farm": "Farm",
    "vintage": "Vintage",
    "wellness": "Wellness",
    "other": "Other",
}


@register.filter
def deadline_urgency(deadline):
    """Return urgency level string for a deadline date.

    Returns 'urgent' (<7 days), 'soon' (<30 days), 'normal', or 'past'.
    """
    if not deadline:
        return "normal"
    delta = (deadline - date.today()).days
    if delta < 0:
        return "past"
    if delta < 7:
        return "urgent"
    if delta < 30:  # Changed from 14 to 30 days
        return "soon"
    return "normal"


@register.filter
def days_until(deadline):
    """Return a human-readable string for days until a deadline."""
    if not deadline:
        return ""
    delta = (deadline - date.today()).days
    if delta < 0:
        return "Deadline passed"
    if delta == 0:
        return "Today!"
    if delta == 1:
        return "1 day left"
    return f"{delta} days left"


@register.filter
def vendor_category_display(categories):
    """Turn a JSON list of category keys into a comma-separated display string."""
    if not categories:
        return ""
    if isinstance(categories, str):
        return categories
    return ", ".join(CATEGORY_LABELS.get(c, c.title()) for c in categories)


@register.filter
def vendor_category_list(categories):
    """Turn a JSON list of category keys into a list of display name strings."""
    if not categories:
        return []
    if isinstance(categories, str):
        return [categories]
    return [CATEGORY_LABELS.get(c, c.title()) for c in categories]


@register.simple_tag
def query_transform(request, **kwargs):
    """Build a query string preserving existing params but overriding with kwargs."""
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            updated[k] = v
        else:
            updated.pop(k, None)
    return updated.urlencode()


# Badge display configuration
BADGE_CONFIG = {
    "verified": {"label": "Verified", "icon": "✓", "color": "blue"},
    "vendor_favorite": {"label": "Vendor Favorite", "icon": "★", "color": "harvest"},
    "new_market": {"label": "New Market", "icon": "✦", "color": "forest"},
    "returning_annual": {"label": "Returning Annual", "icon": "↻", "color": "prairie"},
    "high_demand": {"label": "High Demand", "icon": "🔥", "color": "red"},
    "family_friendly": {"label": "Family Friendly", "icon": "👨‍👩‍👧", "color": "prairie"},
    "accessible": {"label": "Accessible", "icon": "♿", "color": "prairie"},
}


@register.filter
def badge_list(badges):
    """Turn a JSON list of badge keys into a list of badge config dicts."""
    if not badges:
        return []
    return [BADGE_CONFIG[b] for b in badges if b in BADGE_CONFIG]
