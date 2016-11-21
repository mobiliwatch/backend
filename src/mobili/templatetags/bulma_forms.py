from django import template

register = template.Library()

@register.inclusion_tag('forms/errors.html')
def form_errors(form):
    """
    Display form errors with Bulma
    """
    return {
        'errors': form.non_field_errors,
    }

@register.inclusion_tag('forms/input.html')
def form_input(field, icon):
    """
    Display form input with Bulma
    """
    return {
        'icon' : icon,
        'field': field,
    }

@register.inclusion_tag('forms/select.html')
def form_select(field):
    """
    Display form select with Bulma
    """
    return {
        'field': field,
    }
