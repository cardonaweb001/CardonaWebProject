from django import template
from django.template.defaultfilters import stringfilter
import os

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def filename(value):
    """Returns just the filename from a file path"""
    return os.path.basename(value)