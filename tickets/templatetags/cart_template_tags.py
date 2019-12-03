from django import template
from tickets.models import Added


register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Added.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].tickets.count()

    return 0