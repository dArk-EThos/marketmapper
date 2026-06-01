"""Custom template filters for the blog app."""
import markdown
import re
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


@register.filter(name="enhance_mobile_content")
def enhance_mobile_content(html):
    """Enhanced mobile-first content processing for 2026 standards."""
    if not html:
        return html
    
    # Auto-wrap event/opportunity content in cards
    event_pattern = r'<p>([^<]*(?:Market|Festival|Fair|Event|Opportunity|Vendor)[^<]*)</p>'
    html = re.sub(
        event_pattern, 
        r'<div class="content-card"><div class="flex items-start gap-4"><div class="w-2 h-2 rounded-full bg-prairie-500 mt-3 shrink-0"></div><p class="mb-0">\1</p></div></div>', 
        html, 
        flags=re.IGNORECASE
    )
    
    # Auto-create call-out boxes for important information
    callout_patterns = {
        'warning': (
            r'<p>(?:Important|Warning|Deadline|Alert):([^<]+)</p>',
            r'<div class="callout callout-warning"><div class="flex items-start gap-3"><svg class="w-6 h-6 text-harvest shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg><div><p class="font-semibold text-harvest-700 mb-2">Important</p><p class="mb-0">\1</p></div></div></div>'
        ),
        'info': (
            r'<p>(?:Note|Info|Tip|Pro Tip):([^<]+)</p>',
            r'<div class="callout callout-info"><div class="flex items-start gap-3"><svg class="w-6 h-6 text-prairie-600 shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg><div><p class="font-semibold text-prairie-700 mb-2">Good to know</p><p class="mb-0">\1</p></div></div></div>'
        ),
        'success': (
            r'<p>(?:Success|Approved|Completed|Done):([^<]+)</p>',
            r'<div class="callout callout-success"><div class="flex items-start gap-3"><svg class="w-6 h-6 text-forest-600 shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg><div><p class="font-semibold text-forest-700 mb-2">Success</p><p class="mb-0">\1</p></div></div></div>'
        )
    }
    
    for callout_type, (pattern, replacement) in callout_patterns.items():
        html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
    
    # Enhanced mobile image processing
    img_pattern = r'<img([^>]+)>'
    def process_image(match):
        img_attrs = match.group(1)
        # Add mobile-optimized classes and loading
        if 'class=' not in img_attrs:
            img_attrs += ' class="mobile-image"'
        if 'loading=' not in img_attrs:
            img_attrs += ' loading="lazy"'
        return f'<img{img_attrs}>'
    
    html = re.sub(img_pattern, process_image, html)
    
    # Auto-create visual breaks every few paragraphs
    paragraphs = html.split('</p>')
    enhanced_paragraphs = []
    
    for i, paragraph in enumerate(paragraphs[:-1]):  # Skip last empty item
        enhanced_paragraphs.append(paragraph + '</p>')
        
        # Add visual break every 3-4 paragraphs
        if (i + 1) % 4 == 0 and i < len(paragraphs) - 3:
            enhanced_paragraphs.append('<hr class="my-12 border-gray-200">')
    
    # Add the last paragraph if it exists
    if paragraphs and paragraphs[-1].strip():
        enhanced_paragraphs.append(paragraphs[-1])
    
    html = ''.join(enhanced_paragraphs)
    
    # Enhanced link styling
    link_pattern = r'<a([^>]*)>([^<]+)</a>'
    html = re.sub(
        link_pattern,
        r'<a\1 class="text-prairie-600 hover:text-prairie-800 font-medium underline underline-offset-2 decoration-prairie-300 hover:decoration-prairie-600 transition-colors">\2</a>',
        html
    )
    
    # Add reading anchors for long content (mobile navigation)
    heading_pattern = r'<h([23])([^>]*)>([^<]+)</h[23]>'
    def add_anchor(match):
        level = match.group(1)
        attrs = match.group(2)
        text = match.group(3)
        anchor_id = re.sub(r'[^a-zA-Z0-9]+', '-', text.lower()).strip('-')
        
        if 'id=' not in attrs:
            attrs += f' id="{anchor_id}"'
        
        return f'<h{level}{attrs} class="group relative"><a href="#{anchor_id}" class="absolute -left-8 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-prairie-600 no-underline" aria-label="Link to {text}"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.1m0 0l4-4a4 4 0 105.656-5.656l-1.1 1.102m0 0L8.364 16.364"></path></svg></a>{text}</h{level}>'
    
    html = re.sub(heading_pattern, add_anchor, html)
    
    return mark_safe(html)
