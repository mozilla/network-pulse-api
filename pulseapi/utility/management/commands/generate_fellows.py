"""
Insert a configurable number of fellowship profiles into the database
"""
from django.core.management.base import BaseCommand

from pulseapi.profiles.models import ProgramYear, ProgramType, ProfileType
from pulseapi.profiles.factory import ExtendedUserProfileFactory
from pulseapi.users.factory import BasicEmailUserFactory

class Command(BaseCommand):
    help = 'Generate fellowship profiles for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fellowsCount',
            action='store',
            type=int,
            default=3,
            dest='fellows_count',
            help='The number of fellows to generate per program type, per year'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating Fellows')
        fellows_profile_type = ProfileType.objects.get(value='fellow')
        program_years = ProgramYear.objects.all()
        program_types = ProgramType.objects.all()

        for program_year in program_years:
            for program_type in program_types:
                for i in range(options['fellows_count']):
                    ext_profile = ExtendedUserProfileFactory(
                        profile_type=fellows_profile_type,
                        program_year=program_year,
                        program_type=program_type
                    )
                    BasicEmailUserFactory.create(
                        active=True,
                        profile=ext_profile
                    )