"""
Populate the database with fake data. Used for Heroku's review apps and local development.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command

# Factories
from pulseapi.entries.factory import EntryFactory
from pulseapi.users.factory import BaseEmailUserFactory, MozillaEmailUserFactory


class Command(BaseCommand):
    help = 'Generate and load fake data for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete previous data from the database'
        )

    def handle(self, *args, **options):
        if options['delete']:
            call_command('flush_data')

        self.stdout.write('Creating users')
        [BaseEmailUserFactory.create() for i in range(2)]
        [MozillaEmailUserFactory.create() for i in range(2)]
        [MozillaEmailUserFactory.create(staff=True, admin=True) for i in range(2)]
        [MozillaEmailUserFactory.create(staff=True) for i in range(2)]

        self.stdout.write('Creating pulse entries')
        [EntryFactory.create() for i in range(10)]
        [EntryFactory.create(mozillauser=True) for i in range(10)]
