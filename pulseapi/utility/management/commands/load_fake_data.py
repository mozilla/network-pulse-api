"""
Populate the database with fake data. Used for Heroku's review apps and local development.
"""
import factory
from random import randint

from django.core.management.base import BaseCommand
from django.core.management import call_command

# Factories
from pulseapi.creators.factory import OrderedCreatorRecordFactory, CreatorFactory
from pulseapi.entries.factory import BasicEntryFactory, GetInvolvedEntryFactory
from pulseapi.profiles.factory import UserBookmarksFactory
from pulseapi.tags.factory import TagFactory
from pulseapi.users.factory import BasicEmailUserFactory, MozillaEmailUserFactory


class Command(BaseCommand):
    help = 'Generate and load fake data for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            help='Delete previous data from the database'
        )

        parser.add_argument(
            '--seed',
            action='store',
            dest='seed',
            help='A seed value to pass to Faker before generating data'
        )

    def handle(self, *args, **options):
        if options['delete']:
            call_command('flush_data')

        if options['seed']:
            seed = options['seed']
        else:
            seed = randint(0, 5000000)

        self.stdout.write('Seeding Faker with {}'. format(seed))

        faker = factory.faker.Faker._get_faker(locale='en-US')
        faker.random.seed(seed)

        self.stdout.write('Creating tags')
        [TagFactory.create() for i in range(6)]

        self.stdout.write('Creating generic users')
        BasicEmailUserFactory.create()
        [BasicEmailUserFactory.create(active=True) for i in range(2)]
        BasicEmailUserFactory.create(extended_profile=True)
        BasicEmailUserFactory.create(group=True)
        BasicEmailUserFactory.create(group=True, active=True)
        BasicEmailUserFactory.create(use_custom_name=True)
        BasicEmailUserFactory.create(use_custom_name=True, active=True)

        self.stdout.write('Creating Mozilla users')
        MozillaEmailUserFactory.create()
        MozillaEmailUserFactory.create(active=True)
        MozillaEmailUserFactory.create(active=True, extended_profile=True)
        MozillaEmailUserFactory.create(active=True, staff=True)
        MozillaEmailUserFactory.create(active=True, staff=True, extended_profile=True)
        MozillaEmailUserFactory.create(active=True, staff=True, admin=True)
        MozillaEmailUserFactory.create(active=True, staff=True, admin=True, extended_profile=True)

        self.stdout.write('Creating pulse entries')
        [BasicEntryFactory.create() for i in range(20)]
        [BasicEntryFactory.create(is_published_by_creator=True) for i in range(20)]
        [BasicEntryFactory.create(mozillauser=True) for i in range(20)]
        [BasicEntryFactory.create(mozillauser=True, is_published_by_creator=True) for i in range(20)]

        self.stdout.write('Creating featured pulse entries')
        [BasicEntryFactory.create(is_featured=True) for i in range(20)]
        [BasicEntryFactory.create(is_featured=True, is_published_by_creator=True) for i in range(20)]
        [BasicEntryFactory.create(mozillauser=True, is_featured=True) for i in range(20)]

        self.stdout.write('Creating "get involved" pulse entries')
        [GetInvolvedEntryFactory.create() for i in range(20)]
        [GetInvolvedEntryFactory.create(is_featured=True) for i in range(20)]
        [GetInvolvedEntryFactory.create(mozillauser=True) for i in range(20)]

        self.stdout.write('Creating bookmarks')
        [UserBookmarksFactory.create() for i in range(100)]

        self.stdout.write('Creating creators')
        [CreatorFactory.create() for i in range(5)]

        self.stdout.write('Linking random creators with random entries')
        [OrderedCreatorRecordFactory.create() for i in range(100)]

        self.stdout.write(self.style.SUCCESS('Done!'))
