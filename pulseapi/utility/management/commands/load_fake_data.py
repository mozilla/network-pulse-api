"""
Populate the database with fake data. Used for Heroku's review apps and local development.
"""
import factory
from random import randint, sample

from django.core.management.base import BaseCommand
from django.core.management import call_command

from pulseapi.entries.models import Entry

# Factories
from pulseapi.creators.factory import EntryCreatorFactory
from pulseapi.entries.factory import BasicEntryFactory, GetInvolvedEntryFactory
from pulseapi.profiles.factory import UserBookmarksFactory
from pulseapi.tags.factory import TagFactory
from pulseapi.users.factory import BasicEmailUserFactory, MozillaEmailUserFactory

# Number of fake objects created by default
fake_objects = {'tag': 5, 'user': 2}


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

        parser.add_argument(
            '--fellows-count',
            action='store',
            type=int,
            default=3,
            dest='fellows_count',
            help='The number of fellows to generate per program type, per year'
        )

        parser.add_argument(
            '--interactive',
            action='store_true',
            dest='interactive',
            help='Generate a custom number of entries, tags, fellows, etc'
        )

    def handle(self, *args, **options):
        if options['delete']:
            call_command('flush_data')

        if options['seed']:
            seed = options['seed']
        else:
            seed = randint(0, 5000000)

        # Ask user for how much entries, tags, etc, they want or use default values
        if options['interactive']:
            print("Welcome to the interactive mode. For each factories, I will ask you how many elements you want."
                  "If you don't provide any value, I will use the default one.")
            for o in fake_objects:
                while True:
                    try:
                        fake_objects[o] = int(
                            input(f'How many {o} do you want? [default is {fake_objects[o]}]: ') or fake_objects[o]
                        )
                        break
                    except ValueError:
                        print("Value error: I'm excepting an integer!")

        self.stdout.write('Seeding Faker with {}'. format(seed))

        faker = factory.faker.Faker._get_faker(locale='en-US')
        faker.random.seed(seed)

        self.stdout.write('Creating tags')
        [TagFactory.create() for i in range(6)]

        self.stdout.write('Creating generic users')
        BasicEmailUserFactory.create()
        [BasicEmailUserFactory.create(active=True) for i in range(2)]
        BasicEmailUserFactory.create(group=True)
        BasicEmailUserFactory.create(group=True, active=True)
        BasicEmailUserFactory.create(use_custom_name=True)
        BasicEmailUserFactory.create(use_custom_name=True, active=True)

        # Call the generate_fellows command to handle fellows generation
        fellows_count = options['fellows_count']
        call_command('generate_fellows', f'--fellowsCount={fellows_count}')

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

        # Select random published entries and bookmark them for 1 to 10 users
        self.stdout.write('Creating bookmarks')
        approved_entries = Entry.objects.public().with_related()
        for e in sample(list(approved_entries), k=len(approved_entries) // 2):
            [UserBookmarksFactory.create(entry=e) for i in range(randint(1, 10))]

        # Select random entries and link them to 1 to 5 creators
        self.stdout.write('Linking random profiles as creators with random entries')
        for e in sample(list(Entry.objects.all()), k=100):
            [EntryCreatorFactory.create(entry=e) for i in range(randint(1, 5))]

        self.stdout.write(self.style.SUCCESS('Done!'))
