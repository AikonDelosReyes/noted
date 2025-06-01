from django import template

register = template.Library()

@register.filter
def unique(value):
    """Return unique values from a list."""
    if value:
        return set(value)
    return [] 