import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.views.generic.base import RedirectView
from allauth.account.views import LoginView

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


__old_get_context_data = LoginView.get_context_data


def augmented_get_context_data(self, **kwargs):
    """
    Patch allauth's LoginView.get_context_data class function
    so that we can check for a recaptcha-related session value
    if we're using recaptcha. Allauth only has post-processing
    signals, so we're kind of left with monkey patching as the
    only way to pre-process the login route.
    """

    if settings.USE_RECAPTCHA:
        request = self.request
        session = request.session

        if 'recaptcha_token' not in session:
            raise PermissionDenied()

        session_token = session['recaptcha_token']

        # clear the token after reading it so someone can't just set a valid session and then
        # bulk-load the allauth route with a hundred tabs.
        session['recaptcha_token'] = None
        if session_token is None:
            raise PermissionDenied()

        client_token = request.GET.get('token', None)
        if client_token is None:
            raise PermissionDenied()

        if client_token != session_token:
            raise PermissionDenied()

    return __old_get_context_data(self, **kwargs)


LoginView.get_context_data = augmented_get_context_data


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
            client_token = request.GET.get('token', None)

            if client_token is None:
                return HttpResponseForbidden()

            if not verify_recaptcha(client_token):
                return HttpResponseForbidden()

            """
            note the token in the session, so that the redirect
            to `accounts/login` works. This allows us to write code
            that prevents users from directly accessing the allauth
            login route, thus preventing recaptcha circumvention.
            """
            request.session['recaptcha_token'] = client_token

        return super().get(request, *args, **kwargs)
