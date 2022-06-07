from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base import AuthProcess
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.exceptions import ImmediateHttpResponse
from allauth.utils import (
    email_address_exists,
    get_user_model,
)
from django.conf import settings
from django.http import HttpResponseRedirect, QueryDict
from django.urls import reverse
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from pulseapi.utility.userpermissions import is_staff_address
from pulseapi.profiles.models import UserProfile


google_provider_id = GoogleProvider.id


class PulseAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return settings.ALLOW_SIGNUP

    def is_safe_url(self, url):
        """
        We override this because the default implementation only
        allows redirects to same origin urls.
        """
        from django.utils.http import is_safe_url
        return is_safe_url(url, allowed_hosts=settings.LOGIN_ALLOWED_REDIRECT_DOMAINS)

    def get_email_confirmation_redirect_url(self, request):
        """
        Override this so that we can redirect to the `?next=` url
        provided since allauth does not do this out of the box
        """
        if request.user.is_authenticated:
            next_url = request.GET.get('next')
            if next_url and self.is_safe_url(next_url):
                return next_url

        return super().get_email_confirmation_redirect_url(request)

    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Override this so that we can set the `?next=` url in the email
        confirmation url so that the user is redirected correctly after
        confirming their email.

        FIXME: This currently does not work because no `?next=` parameter
        is passed to the email confirmation view. Our current workaround
        for this is to set the
        `ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL` to be
        the pulse front-end url via an environment veriable on production.
        """
        url = super().get_email_confirmation_url(request, emailconfirmation)
        next_url = request.GET.get('next')

        if not (next_url and self.is_safe_url(next_url)):
            return url

        # Parse the url and add the `next` url to it as a query string
        url_parts = list(urlparse(url))
        qs = dict(parse_qsl(url_parts[4]))
        qs.update({'next': next_url})
        url_parts[4] = urlencode(qs)

        return urlunparse(url_parts)


class PulseSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Override the default implementation for DefaultSocialAccountAdapter
    for two reasons:
        1. Auto populate our custom EmailUser model with information from
        the social provider
        2. Handle the transition from the old auth system to "upgrade" existing
        accounts to the new allauth system.
    """
    def is_open_for_signup(self, request, socialaccount):
        return settings.ALLOW_SIGNUP

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        name = data.get('name')
        if not name:
            first_name = data.get('first_name') or ''
            last_name = data.get('last_name') or ''
            name = f"{first_name} {last_name}".strip()
        user.name = name if name else 'Unnamed Pulse user'

        if sociallogin.account.provider == google_provider_id and is_staff_address(user_email(user)):
            user.is_staff = True

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        For some reason the signal for creating a user is not triggered
        by allauth, so we manually create a profile when a user first
        logs in.
        """
        user = super().save_user(request, sociallogin, form)

        try:
            UserProfile.objects.get(related_user=user)
        except UserProfile.DoesNotExist:
            
            # Is_active is False by default, so we can hide this 
            # users profile and entries, until set to active by a moderator.
            profile = UserProfile.objects.create(is_active=False)
            user.profile = profile
            user.save()

        return user

    def pre_social_login(self, request, sociallogin):
        email = user_email(sociallogin.user)
        UserModel = get_user_model()
        login_provider_id = sociallogin.account.provider

        if (
                not email or
                not email_address_exists(email) or
                sociallogin.state.get('process') != AuthProcess.LOGIN
        ):
            # This is a new email address, or we're connecting social accounts
            # so we don't need to do anything
            return

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            # This case shouldn't really happen, but even if it does, we
            # don't do anything and let the default behavior kick in.
            return

        social_accounts = list(SocialAccount.objects.filter(
            user=user
        ).values_list('provider', flat=True))

        if len(social_accounts) == 0:
            # This is a hack to associate existing accounts on pulse
            # that were added via Google Auth the old way to the new allauth
            # system. We only do this for new logins into this system.
            request.migrate_user = user
        elif login_provider_id in social_accounts:
            # In this case, the existing user already has a social account
            # and is logging into it using the same provider.
            return
        else:
            # Here the user already has a Pulse social account (e.g. Google)
            # but is logging in through a different social network
            # (e.g. Github) that uses the same email for the first time.
            # We redirect them to the login view where they have to login
            # through their existing social account on Pulse before going to
            # the Social Account Connections view to connect their secondary
            # social account.
            url = reverse('account_login')
            qs = QueryDict(mutable=True)
            next_url = sociallogin.get_redirect_url(request)
            if next_url:
                # We encode the final destination url in the connection
                # view url so that users are correctly rerouted after
                # connecting their accounts.
                qs['next'] = next_url
            next_url = '{url}?{qs}'.format(
                url=reverse('socialaccount_connections'),
                qs=qs.urlencode()
            )
            qs = QueryDict(mutable=True)
            qs['next'] = next_url
            qs['promptconnection'] = True
            qs['provider'] = providers.registry.by_id(login_provider_id).name

            raise ImmediateHttpResponse(
                response=HttpResponseRedirect(f'{url}?{qs.urlencode()}')
            )

    def is_auto_signup_allowed(self, request, sociallogin):
        if hasattr(request, 'migrate_user'):
            # Associate the existing user with the SocialLogin object
            # being created
            sociallogin.user = request.migrate_user
            return True

        return super().is_auto_signup_allowed(request, sociallogin)
