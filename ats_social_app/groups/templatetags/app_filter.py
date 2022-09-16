from django import template

register = template.Library()


@register.filter(name='percentage')
def percentage(value, arg):
    result = (int(value) / int(arg) * 100)
    formatted_string = "{:.2f}".format(result)
    float_value = float(formatted_string)
    return float_value
