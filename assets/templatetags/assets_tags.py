from django import template
from ..models import Asset, Software

register = template.Library()


@register.simple_tag
def get_recent_asset(num=6):
    asset = Asset.objects.filter()
    return asset.order_by('-c_time')[:num]


@register.simple_tag
def get_recent_software(num=6):
    software = Software.objects.filter()
    return software.order_by('-c_time')[:num]

@register.simple_tag
def get_is_admin(request):
    if request.session.get('isAdmin', False):
        return True
    else:
        return False