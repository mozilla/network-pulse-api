import json

from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.generic.base import RedirectView

from requests import post
from requests.exceptions import RequestException

# see https://developers.google.com/recaptcha/docs/verify
RECAPTCHA_VERIFICATION_URL = 'https://www.google.com/recaptcha/api/siteverify'


def verify_recaptcha(response_token):
    """
    Ask google to verify a client-generated recaptcha token
    against what it supposedly generated.
    """
    try:
        response = post(RECAPTCHA_VERIFICATION_URL, timeout=5, data={
            'response': response_token,
            'secret': settings.RECAPTCHA_SECRET,
        })
        response.raise_for_status()

    except RequestException:
        return False

    data = json.loads(response.text)
    
    if data.get('success') is not True:
        return False

    return True


class LoginRedirectView(RedirectView):
    """
    A utility view that redirects requests to the real
    login route, but only if recaptcha validation passes
    (provided recaptcha is enabled). If recaptcha fails,
    we send an http 403 response.
    """

    permanent = False
    query_string = True
    url = '/accounts/login'

    def get(self, request, *args, **kwargs):
        if settings.USE_RECAPTCHA:
            response_token = request.GET.get('token', None)

            if response_token is None:
                return HttpResponseForbidden() 

            if not verify_recaptcha(response_token):
                return HttpResponseForbidden()
        
        return super().get(request, *args, **kwargs)
