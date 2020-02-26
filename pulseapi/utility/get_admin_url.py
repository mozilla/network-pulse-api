from django.urls import reverse
from django.contrib.contenttypes.models import ContentType


def get_admin_url(instance):
    content_type = ContentType.objects.get_for_model(instance.__class__)

    route = 'admin:{}_{}_change'.format(
        content_type.app_label,
        content_type.model
    )

    return reverse(route, args=(instance.id,))
