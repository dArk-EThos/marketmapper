"""Custom template filters for the blog app."""
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
