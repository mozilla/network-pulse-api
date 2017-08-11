from django.db import migrations

from pulseapi.users.models import EmailUser
from pulseapi.profiles.models import UserProfile

def ensure_user_profiles(app, schema_editor):
    """
    The only thing this function does is ensure that for every user
    of the system, we have an associated user profile, even if it
    does absolutely nothing (yet).
    """
    users = EmailUser.objects.all()
    for user in users:
        (profile,created) = UserProfile.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
        ('users', '0004_auto_20170616_1131'),
    ]

    operations = [
        migrations.RunPython(ensure_user_profiles),
    ]
