import os
from httplib2 import Http
from oauth2client import client

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
    new_state_value(request)
    new_nonce_value(request)

    FlowHandler.get_flow().params['state'] = request.session['state']

    return render(request, 'users/index.html', {
        'user': request.user,
        'auth_url': FlowHandler.get_flow().step1_get_authorize_url(),
        'nonce': request.session['nonce']
    })

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
        service = build('oauth2', 'v2', http=http_auth)
        userinfo = service.userinfo().get().execute()
        name = userinfo['name']
        email = userinfo['email']

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

        return redirect('/')

    return HttpResponseNotFound("callback happened without an error or code query argument: wtf")

