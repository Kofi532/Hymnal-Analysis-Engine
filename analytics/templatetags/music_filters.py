from django import template

register = template.Library()

@register.filter
def format_large_number(value):
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value