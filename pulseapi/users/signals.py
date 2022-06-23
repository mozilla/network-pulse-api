from django.dispatch import receiver
from django.db.models.signals import post_delete

from .models import EmailUser
from pulseapi.profiles.models import UserProfile


@receiver(post_delete, sender=EmailUser)
def delete_profile_for_user(sender, **kwargs):
    if kwargs['instance'].profile_id:
        related_profile_id = kwargs['instance'].profile_id
        related_profile = UserProfile.objects.get(id=related_profile_id)
        if related_profile:
            related_profile.delete()
