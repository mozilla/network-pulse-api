from django.dispatch import receiver
from django.db.models.signals import post_save

from pulseapi.profiles.models import UserProfile
from pulseapi.creators.models import Creator


@receiver(post_save, sender=UserProfile)
def create_creator_for_profile(sender, **kwargs):
    """
    Automatically create a corresponding Creator instance for every profile that is created.
    """
    if kwargs.get('created', False) and not kwargs.get('raw', False):
        Creator.objects.get_or_create(profile=kwargs.get('instance'))
