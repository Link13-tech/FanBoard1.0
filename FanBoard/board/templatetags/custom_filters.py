from django import template
import re

register = template.Library()


@register.filter
def extract_first_image(content):
    """Extract the URL of the first image from HTML content."""
    match = re.search(r'<img\s+src="([^"]+)"', content)
    if match:
        return match.group(1)
    return None
