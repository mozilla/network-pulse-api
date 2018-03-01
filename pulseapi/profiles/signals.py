from django.dispatch import receiver
from django.db.models.signals import post_save

from pulseapi.profiles.models import UserProfile
from pulseapi.creators.models import Creator


@receiver(post_save, sender=UserProfile)
def create_creator_for_profile(sender, **kwargs):
    """
    Automatically create a corresponding Creator instance for every profile that is created.
    """
    instance = kwargs.get('instance')
    # This will check to see if a creator was passed in and use that
    # to bind to the current profile instead of creating a new one
    creator = instance._creator if hasattr(instance, '_creator') else None

    if kwargs.get('created', False) and not kwargs.get('raw', False):
        if creator is not None:
            creator.profile = instance
            creator.save()
        else:
            Creator.objects.get_or_create(profile=kwargs.get('instance'))
