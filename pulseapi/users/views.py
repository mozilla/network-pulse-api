import os
from httplib2 import Http
from oauth2client import client

from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import (HttpResponse, HttpResponseNotFound)
from django.shortcuts import (redirect, render)
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_protect
from apiclient.discovery import build

from .models import EmailUser
from pulseapi.utility.userpermissions import is_staff_address


class FlowHandler:
    """
    To prevent compilation errors due to a missing client_secrets.json,
    especially during "manage.py migrate" and the like, we initialise
    the flow object as None and only assign it once it needs to be used.
    """

    flow = None

    @classmethod
    def get_flow(self):
        """
        get the class-level-bound flow handler
        """
        if self.flow is None:
            self.flow = client.flow_from_clientsecrets(
                # we keep the creds in a separate file that we don't check in.
                'client_secrets.json',

                # we want to be able to get a user's name and email
                scope=' '.join([
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile'
                ]),

                # this url-to-codepath binding is set up in ./users/urls.py
                redirect_uri=os.getenv('redirect_uris', '').split(',')[0],
            )

        return self.flow


def new_state_value(request):
    """
    Set up a random value for the session state, used in authentication validation.
    """

    request.session['state'] = EmailUser.objects.make_random_password()


def new_nonce_value(request):
    """
    set a new random nonce to act as form post identifier
    """

    request.session['nonce'] = EmailUser.objects.make_random_password()

# API ROUTE: /nonce
def nonce(request):
    """
    set a new random nonce to act as form post identifier
    and inform the user what this value is so they can use
    it for signing their POST for a new entry.
    """
    if not request.user.is_authenticated():
        return HttpResponse('Not authorized', status=403)

    new_nonce_value(request)
    return render(request, 'users/nonce.json', {
        'nonce': request.session['nonce']
    }, content_type="application/json")


# API ROUTE: /userstatus
def userstatus(request):
    """
    Get the login status associated with a session. If the
    status is "logged in", also include the user name and
    user email. NOTE: these values should never be persistently
    cached by applications, for obvious reasons.
    """
    name = False
    email = False
    user = request.user
    loggedin = user.is_authenticated()

    # A user is a moderator if they are in the moderator group
    # or if they are a superuser, because superusers can do anything.
    moderator = user.groups.filter(name='moderator')
    is_moderator = len(moderator) > 0

    if is_moderator is False:
        is_moderator = user.is_superuser

    if loggedin:
        name = user.name
        email = user.email

    return render(request, 'users/userstatus.json', {
        'username': name,
        'email': email,
        'loggedin': loggedin,
        'moderator': is_moderator,
    }, content_type="application/json")


# API ROUTE: /
def index(request):
    """
    Initial page with a link that lets us sign in through Google
    """

    # generic state value
    new_state_value(request)
    FlowHandler.get_flow().params['state'] = request.session['state']

    return render(request, 'users/index.html', {
        'user': request.user
    })

# API ROUTE: /login
def start_auth(request):
    """
    Specific login call for logging in through another front-end
    """
    original_url = request.GET.get('original_url', False)

    if original_url is False:
        new_state_value(request)
        original_url = request.session['state']

    else:
        request.session['state'] = original_url

    # record the url to send the user back to post-authentication
    # in the state value.
    FlowHandler.get_flow().params['state'] = original_url
    auth_url = FlowHandler.get_flow().step1_get_authorize_url()
    return redirect(auth_url)

# API Route: /logout (immediately directs to /)
def force_logout(request):
    """
    An explicit logout route.
    """
    user = request.user
    if user.is_authenticated:
        logout(request)
    return HttpResponse("User is no longer logged in.")


def do_final_redirect(state, loggedin, msg):
    """
    As final step in the oauth callback process, redirect the user either to
    the api root, or if there was an original_url to indicate where the user
    was when they started the oauth process, move them back to that url instead.

    This redirect is accompanied by a URL query pair "loggedin=..." which can
    either be 'true' or 'false', and can be used to determine whether the login
    attempd succeeded or not.
    """
    redirectUrl = '/'

    # Do we need to redirect the user to some explicit URL after login?
    try:
        validator = URLValidator()
        validator(state)
        redirectUrl = state
    except ValidationError:
        pass

    # Add the result of the login attempt to the redirect URL as query pair
    if '?' in redirectUrl:
        redirectUrl += '&'
    else:
        redirectUrl += '?'
    redirectUrl += 'loggedin=' + str(loggedin)

    return redirect(redirectUrl)


# API Route: /oauth2callback (Redirects to / on success)
def callback(request):
    """
    The callback route that Google will send the user to when authentication
    finishes (with successfully, or erroneously).
    """

    if 'state' not in request.session:
        msg = '\n'.join([
            'ERROR: No state key found in request.session!',
            'Are you making doubly sure your initial domain and callback domain are the same domain?'
        ])
        print(msg)
        return HttpResponseNotFound(msg)

    error = request.GET.get('error', False)
    auth_code = request.GET.get('code', False)

    if error is not False:
        return HttpResponse("login failed: " + str(error))

    if auth_code is not False:
        state = request.GET.get('state', False)

        if state is False:
            return HttpResponse("Questionable login: missing state value in callback.")

        if state != request.session['state']:
            return HttpResponse("Questionable login: incorrect state value in callback.")

        # get the authenticating user's name and email address from the Google API
        credentials = FlowHandler.get_flow().step2_exchange(auth_code)
        http_auth = credentials.authorize(Http())

        # get a user's full name
        service = build('oauth2', 'v2', http=http_auth)
        userinfo = service.userinfo().get().execute()
        name = userinfo['name']
        email = userinfo['email']

        if settings.ALLOW_UNIVERSAL_LOGIN is None:
            # Any user outside of the cleared mozilla domains is redirected to the main page.
            if not is_staff_address(email):
                return do_final_redirect(state, False, "Domain not in whitelist")

        try:
            # Get the db record for this user and make sure their
            # name matches what google says it should be.
            user = EmailUser.objects.get(email=email)
            # Just to be safe, we rebind the user's name, as this may have
            # changed since last time we saw this user.
            user.name = name
            user.save()

        except EmailUser.DoesNotExist:
            # Create a new database entry for this user.
            user = EmailUser.objects.create_user(
                name=name,
                email=email
            )

        # As this user just authenticated, we mark this user as logged in
        # for the duration of this session.
        login(request, user)

        return do_final_redirect(state, True, "User logged in")

    return HttpResponseNotFound("callback happened without an error or code query argument: this should not be possible.")
