from django import template
from django.urls import reverse
from django.conf import settings


register = template.Library()


@register.assignment_tag(takes_context=True)
def is_next_url_admin(context):
    return context['request'].GET.get('next') == reverse('admin:index')


@register.assignment_tag()
def is_review_app():
    return bool(settings.HEROKU_APP_NAME)
