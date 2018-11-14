from django.dispatch import receiver
from django.core.signals import post_save

from pulseapi.users.models import EmailUser
from pulseapi.profiles.models import UserProfile


@receiver(post_save, sender=EmailUser)
def create_profile_for_user(sender, **kwargs):
    if kwargs.get('created', False):
        UserProfile.objects.get_or_create(
            user=kwargs.get('instance'),
            is_active=True,
        )
