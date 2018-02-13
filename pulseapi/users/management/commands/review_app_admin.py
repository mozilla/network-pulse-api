"""
Management command called during Heroku Review App post-deployment phase: create an admin user and print its random
password in the logs.
"""

from django.core.management.base import BaseCommand

from pulseapi.users.models import EmailUser


class Command(BaseCommand):
    help = "Create a super admin user to use on Heroku Review App"

    def handle(self, *args, **options):
        password = EmailUser.objects.make_random_password()
        self.stdout.write('Your admin password is: {}'.format(password))
        user = EmailUser.objects.create_superuser('test', 'test@test.org', password)
        user.save()
