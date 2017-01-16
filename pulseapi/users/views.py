import os
from httplib2 import Http
from oauth2client import client

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import (HttpResponse, HttpResponseNotFound)
from django.shortcuts import (redirect, render)
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_protect
from apiclient.discovery import build

from .models import EmailUser

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
                redirect_uri=os.getenv('redirect_uris', 'http://test.example.com:8000/oauth2callback').split(',')[0],
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
    """
    if not request.user.is_authenticated():
        return HttpResponseNotFound()

    new_nonce_value(request)
    return render(request, 'users/formprotection.json', {
        'user': request.user,
        'nonce': request.session['nonce']
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
    return redirect("/")


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

        # For now, we only allow mozilla.com, mozilla.org,
        # and mozillafoundation.org accounts.
        domain = email.split("@")[1]
        cleared = [
            'mozilla.com',
            'mozilla.org',
            'mozillafoundation.org'
        ]

        # Any user outside these domains is redirected to the main page.
        if domain not in cleared:
            return redirect('/')

        try:
            # Get the db record for this user and make sure their
            # name matches what google says it should be.
            user = EmailUser.objects.get(email=email)
            # Just to be safe, we rebind the user's name, as this may have
            # changed since last time we saw this user.
            user.name = name
            user.save()
            print("found user in database based on email address.")

        except EmailUser.DoesNotExist:
            # Create a new database entry for this user.
            user = EmailUser.objects.create_user(
                name=name,
                email=email
            )
            print("user not found: created user based on email address.")

        # As this user just authenticated, we mark this user as logged in
        # for the duration of this session.
        login(request, user)

        # Do we need to redirect the user to some explicit URL after login?
        try:
            validator = URLValidator()
            validator(state)
            return redirect(state)

        except ValidationError:
            pass

        # We do not, just redirect them to the main page.
        return redirect('/')

    return HttpResponseNotFound("callback happened without an error or code query argument: this should not be possible.")

