from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

from .models import EmailUser
from pulseapi.profiles.models import UserProfile


@receiver(pre_save, sender=EmailUser)
def default_to_non_active(sender, instance, **kwargs):
    if settings.TESTING:
        return
    if instance._state.adding is True:
        instance.is_active = False

@receiver(post_delete, sender=EmailUser)
def delete_profile_for_user(sender, **kwargs):
    related_profile_id = kwargs['instance'].profile_id
    related_profile = UserProfile.objects.get(id=related_profile_id)
    related_profile.delete()
