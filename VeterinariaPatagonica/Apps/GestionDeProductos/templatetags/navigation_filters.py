from django import template
register = template.Library()


@register.filter(name='page_filter')
def page_filter(self, items):
    current_value = items.number
    valmax = items.paginator.page_range[-1]
    gapval = 4
    valini = current_value - gapval

    if valini <= 0:
        valini = 1

    valend = 1 + current_value + gapval
    if valend > valmax:
        valend = valmax + 1

    return range(valini, valend)