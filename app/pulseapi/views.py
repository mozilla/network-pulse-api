import os
from httplib2 import Http
from oauth2client import client

from django.http import (HttpResponse, HttpResponseNotFound)
from django.shortcuts import (redirect, render)
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_protect
from apiclient.discovery import build

from .models import EmailUser

"""
The flow variable is used to run through oauth2 workflows.
"""
FLOW = client.flow_from_clientsecrets(
    # we keep the creds in a separate file that we don't check in.
    'client_secrets.json',

    # we want to be able to get a user's name and email
    scope=' '.join([
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]),

    # this url-to-codepath binding is set up in ./users/urls.py
    redirect_uri=os.getenv('redirect_uris', 'http://test.stuff.com:8000/oauth2callback').split(',')[0],
)


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


def index(request):
    """
    Initial page with a link that lets us sign in through Google
    """
    new_state_value(request)
    new_nonce_value(request)

    FLOW.params['state'] = request.session['state']

    return render(request, 'users/index.html', {
        'user': request.user,
        'auth_url': FLOW.step1_get_authorize_url(),
        'nonce': request.session['nonce']
    })


def force_logout(request):
    """
    An explicit logout route.
    """

    user = request.user
    if user.is_authenticated:
        logout(request)
    return redirect("/")


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
        print msg
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
        credentials = FLOW.step2_exchange(auth_code)
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

def post_validate(request):
    """
    Security helper function to ensure that a post request is session, CSRF, and nonce protected
    """

    user = request.user
    csrf_token = request.POST.get('csrfmiddlewaretoken', False)
    nonce = request.POST.get('nonce', False)

    # ignore post attempts without a CSRF token
    if csrf_token is False:
        return "No CSRF token in POST data."

    # ignore post attempts without a known form id
    if nonce is False:
        return "No form identifier in POST data."

    # ignore post attempts by clients that are not logged in
    if not user.is_authenticated:
        return "Anonymous posting is not supported."

    # ignore unexpected post attempts (i.e. missing the session-based unique form id)
    if nonce != request.session['nonce']:
        # invalidate the nonce entirely, so people can't retry until there's an id collision
        request.session['nonce'] = False
        return "Forms cannot be auto-resubmitted (e.g. by reloading)."

    return True


@csrf_protect
def post_test(request):
    """
    Testing route for POSTing to the Django database
    """
    validation_result = post_validate(request)

    if validation_result is True:
        # invalidate the nonce, so this form cannot be resubmitted with the current id
        request.session['nonce'] = False

        context = {
            'user': request.user,
            'name': request.POST['name'],
            'url': request.POST['url'],
        }

        return render(request, 'users/submissions.html', context)

    else:
        return HttpResponseNotFound(validation_result)
