from django.db import migrations
from django.conf import settings


def match_profile_isactive_to_user_isactive(apps, schema):
    EmailUser = apps.get_model('users', 'EmailUser')
    UserProfile = apps.get_model('profiles', 'UserProfile')

    network_pulse_users = EmailUser.objects.all()

    for user in network_pulse_users:

        user_profile, created = UserProfile.objects.get_or_create(related_user=user)

        user_profile.is_active = user.is_active

        user_profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0024_delete_orphan_profiles'),
    ]

    operations = [
        migrations.RunPython(code=match_profile_isactive_to_user_isactive, reverse_code=migrations.RunPython.noop)
    ]
