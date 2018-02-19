"""
Can be used with load_fake_data script. Flush models to make sure that the database is empty before loading a new
set of fake data.
"""
from django.core.management.base import BaseCommand

from pulseapi.entries.models import Entry
from pulseapi.users.models import EmailUser


class Command(BaseCommand):
    help = "Flush models from the database"

    def handle(self, *args, **options):
        self.stdout.write('Flushing models from the database')

        self.stdout.write('Dropping Entry objects')
        Entry.objects.all().delete()

        self.stdout.write('Dropping EmailUser objects')
        EmailUser.objects.all().delete()
