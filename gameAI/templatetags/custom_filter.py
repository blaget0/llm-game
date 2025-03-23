from django import template

register = template.Library()

@register.filter
def get_by_index(lst, index):
    try:
        return lst[index]
    except (IndexError, TypeError, KeyError):
        return None
    
@register.filter
def get_name(obj):
    try:
        return obj.name
    except (IndexError, TypeError, KeyError):
        return None