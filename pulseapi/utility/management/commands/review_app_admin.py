"""
Management command called during Heroku Review App post-deployment phase: create an admin user and print its random
password in the logs.
"""

from django.core.management.base import BaseCommand

from pulseapi.users.models import EmailUser


class Command(BaseCommand):
    help = "Create a superuser to use on Heroku Review App"

    def handle(self, *args, **options):
        password = EmailUser.objects.make_random_password()
        admin = EmailUser.objects.create_superuser('test', 'test@mozillafoundation.org', password)
        admin.save()
        self.stdout.write('Admin user created. Password: {}'.format(password))
