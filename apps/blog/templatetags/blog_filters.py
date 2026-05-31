"""Custom template filters for the blog app."""
import re
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdownify")
def markdownify(text):
    """Convert Markdown text to HTML with extensions for tables, fenced code, etc."""
    extensions = [
        "markdown.extensions.tables",
        "markdown.extensions.fenced_code",
        "markdown.extensions.nl2br",
        "markdown.extensions.smarty",
        "markdown.extensions.toc",
    ]
    html = markdown.markdown(text, extensions=extensions)
    return mark_safe(html)


@register.filter(name="enhance_readability")
def enhance_readability(html):
    """Enhance HTML content for better readability and structure."""
    # Add spacing after periods and before capital letters (sentence breaks)
    html = re.sub(r'\.([A-Z])', r'. \1', html)
    
    # Wrap event-like content in cards
    # Look for patterns like "EventName - Date - Location" or "Date: Event"
    event_pattern = r'<p>([^<]*(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2}(?:st|nd|rd|th)?)\b[^<]*(?:Market|Festival|Fair|Event|Show|Sale)[^<]*)</p>'
    html = re.sub(event_pattern, r'<div class="event-card"><p>\1</p></div>', html, flags=re.IGNORECASE)
    
    # Add call-out boxes for important information
    # Look for paragraphs starting with "Note:", "Important:", "Deadline:", etc.
    callout_patterns = {
        'info': r'<p>(?:Note|Info|FYI|Tip):([^<]+)</p>',
        'warning': r'<p>(?:Important|Warning|Deadline|Alert):([^<]+)</p>',
        'success': r'<p>(?:Success|Complete|Done|Approved):([^<]+)</p>'
    }
    
    for callout_type, pattern in callout_patterns.items():
        replacement = f'<div class="callout-box {callout_type}"><p><strong>{callout_type.title()}:</strong>\\1</p></div>'
        html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
    
    # Improve list formatting - add extra spacing
    html = re.sub(r'</li>\s*<li>', '</li><li style="margin-top: 0.5rem;"><', html)
    
    return mark_safe(html)