from django import template
from django.urls import reverse
from django.conf import settings


register = template.Library()


@register.simple_tag(takes_context=True)
def is_next_url_admin(context):
    return context['request'].GET.get('next') == reverse('admin:index')


@register.simple_tag()
def is_review_app():
    return bool(settings.HEROKU_APP_NAME)


@register.simple_tag()
def get_pulse_contact_url():
    return settings.PULSE_CONTACT_URL


@register.simple_tag(takes_context=True)
def signin_before_connect(context):
    return bool(context['request'].GET.get('promptconnection'))


@register.simple_tag(takes_context=True)
def get_login_attempt_provider_name(context):
    return context['request'].GET.get('provider', '')


@register.simple_tag()
def get_email_verification_sender():
    return settings.EMAIL_VERIFICATION_FROM
