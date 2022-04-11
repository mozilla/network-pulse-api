from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import EmailUser


@receiver(pre_save, sender=EmailUser)
def default_to_non_active(sender, instance, **kwargs):
    if settings.TESTING:
        return
    if instance._state.adding is True:
        instance.is_active = False
