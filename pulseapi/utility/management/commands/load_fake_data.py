"""
Populate the database with fake data. Used for Heroku's review apps and local development.
"""
from itertools import chain, combinations, product

import factory
from random import randint, sample

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import IntegrityError

from pulseapi.entries.models import Entry

# Factories
from pulseapi.creators.factory import EntryCreatorFactory
from pulseapi.entries.factory import BasicEntryFactory, GetInvolvedEntryFactory
from pulseapi.profiles.factory import UserBookmarksFactory, ExtendedUserProfileFactory
from pulseapi.profiles.models import ProgramYear, ProgramType, ProfileType
from pulseapi.tags.factory import TagFactory
from pulseapi.users.factory import BasicEmailUserFactory, MozillaEmailUserFactory


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


# Create a list of dictionaries containing every factory params permutation possible. ex: [{'group': True},
# {'group': True, 'active': True}, ...]
def generate_variations(factory_model):
    for variation in powerset(factory_model._meta.parameters.keys()):
        yield {k: True for k in variation}


# Create fake data for every permutation possible
def generate_fake_data(factory_model, count):
    for kwargs in generate_variations(factory_model):
        for i in range(count):
            factory_model.create(**kwargs)


def generate_fellows(count):
    fellows_profile_type = ProfileType.objects.get(value='fellow')
    program_years = ProgramYear.objects.all()
    program_types = ProgramType.objects.all()

    for (program_year, program_type) in list(product(program_years, program_types)):
        for i in range(count):
            ext_profile = ExtendedUserProfileFactory(
                profile_type=fellows_profile_type,
                program_year=program_year,
                program_type=program_type
            )
            BasicEmailUserFactory.create(
                active=True,
                profile=ext_profile
            )


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
            '-f',
            '--fellows-count',
            action='store',
            type=int,
            default=3,
            dest='fellows_count',
            help='The number of fellows to generate. Default: 3 per program type, per year'
        )

        parser.add_argument(
            '-u',
            '--users-count',
            action='store',
            type=int,
            default=1,
            dest='users_count',
            help='The number of users to generate per possible variations. Default: 1, variations: 80'
        )

        parser.add_argument(
            '-e',
            '--entries-count',
            action='store',
            type=int,
            default=20,
            dest='entries_count',
            help='The number of entries to generate per possible variations. Default: 20, variations: 16'
        )

        parser.add_argument(
            '-t',
            '--tags-count',
            action='store',
            type=int,
            default=6,
            dest='tags_count',
            help='The number of tags to generate. Default: 6'
        )

    def handle(self, *args, **options):
        if options['delete']:
            call_command('flush_data')

        if options['seed']:
            seed = options['seed']
        else:
            seed = randint(0, 5000000)

        print('Seeding Faker with {}'. format(seed))

        faker = factory.faker.Faker._get_faker(locale='en-US')
        faker.random.seed(seed)

        print('Creating tags')
        [TagFactory.create() for i in range(options['tags_count'])]

        print('Creating users')
        generate_fake_data(BasicEmailUserFactory, options['users_count'])

        # Since every Mozilla users' emails must be @mozillafoundation.org, we run into "UNIQUE constraint failed"
        # error from time to time
        try:
            generate_fake_data(MozillaEmailUserFactory, options['users_count'])
        except IntegrityError:
            print('Failed to create user: this email address is already in the database. No more users will be '
                  'created this run.')
            pass

        print('Creating pulse entries')
        generate_fake_data(BasicEntryFactory, options['entries_count'])
        generate_fake_data(GetInvolvedEntryFactory, options['entries_count'])

        print('Creating fellows')
        generate_fellows(options['fellows_count'])

        # Select random published entries and bookmark them for 1 to 10 users
        print('Creating bookmarks')
        approved_entries = Entry.objects.public().with_related()
        for e in sample(list(approved_entries), k=len(approved_entries) // 2):
            [UserBookmarksFactory.create(entry=e) for i in range(randint(1, 10))]

        # Select random entries and link them to 1 to 5 creators
        print('Linking random profiles as creators with random entries')
        all_entries = Entry.objects.all()
        for e in sample(list(all_entries), k=len(all_entries) // 2):
            try:
                [EntryCreatorFactory.create(entry=e) for i in range(randint(1, 5))]
            # That creator and entry might already be linked. If it's the case, skip it and move on:
            except IntegrityError:
                continue

        print(self.style.SUCCESS('Done!'))
