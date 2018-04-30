"""
Call this command to fetch data from Github about contribution activity on public repos and save it to S3
"""

from django.core.management.base import BaseCommand

from pulseapi.utility import contributions_data

class Command(BaseCommand):
    help = "Run the GitHub contribution data task"

    def handle(self, *args, **options):
        contributions_data.run()
