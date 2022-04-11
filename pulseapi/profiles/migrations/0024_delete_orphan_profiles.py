from django.db import migrations
from django.conf import settings


def find_and_delete_orphan_profiles(apps, schema):
    UserProfile = apps.get_model('profiles', 'UserProfile')

    orphan_profiles = UserProfile.objects.filter(
            related_user=None
    )

    for orphan in orphan_profiles:
        orphan.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0023_auto_20190807_1733'),
    ]

    operations = [
        migrations.RunPython(
            find_and_delete_orphan_profiles
        ),
    ]
