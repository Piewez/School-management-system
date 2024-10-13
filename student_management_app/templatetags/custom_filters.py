from django import template

register = template.Library()

@register.filter(name='get_dynamic_field')
def get_dynamic_field(obj, field_name):
    # field_name doit être une chaîne comme "moyenne_1" ou "moyenne_2"
    return getattr(obj, field_name, 0)
