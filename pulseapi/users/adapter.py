from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from allauth.utils import email_address_exists, get_user_model
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.provider import GoogleProvider
from django.db.models import Model
from django.conf import settings

from pulseapi.utility.userpermissions import is_staff_address
from pulseapi.profiles.models import UserProfile


google_provider_id = GoogleProvider.id


class PulseAccountAdapter(DefaultAccountAdapter):
    def is_safe_url(self, url):
        """
        We override this because the default implementation only
        allows redirects to same origin urls.
        """
        from django.utils.http import is_safe_url
        return is_safe_url(url, allowed_hosts=settings.LOGIN_ALLOWED_REDIRECT_DOMAINS)


class PulseSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Override the default implementation for DefaultSocialAccountAdapter
    for two reasons:
        1. Auto populate our custom EmailUser model with information from
        the social provider
        2. Handle the transition from the old auth system to "upgrade" existing
        accounts to the new allauth system.
    """
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        name = data.get('name')
        user.name = ' '.join([
            data.get('first_name', ''),
            data.get('last_name', '')
        ]).strip() if not name else name

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
            profile = UserProfile.objects.create(is_active=True)
            user.profile = profile
            user.save()

        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        email = user_email(sociallogin.user)
        print(f'auto signup for {email} using {sociallogin.account.provider}' )

        if (
                sociallogin.account.provider == google_provider_id and
                email and
                email_address_exists(email)
        ):
            # This is a hack to associate existing accounts on pulse
            # that were added via Google Auth the old way.
            # This associates the existing User model instance with the new
            # SocialLogin instance being created here the first time a user
            # logs into the allauth system. Subsequent logins bypass this flow.
            try:
                user = get_user_model().objects.get(email=email)

                # Make sure that there is no other social account with the same
                # email. This is a security check to make sure that if a
                # malicious user creates a pulse account through a non-google
                # provider using a gmail address, the real owner of that gmail
                # account doesn't get auto-linked to that same pulse account
                # when they login for the first time.
                if SocialAccount.objects.filter(user=user).exclude(provider=google_provider_id).exists():
                    return False

                # Associate the existing user with the SocialLogin object
                # being created
                sociallogin.user = user

            except Model.DoesNotExist:
                return False

            return True

        return super().is_auto_signup_allowed(request, sociallogin)
