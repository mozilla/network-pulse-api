"""
Create fake creators that are not pulse users for local development and Heroku's review app.
"""

from factory import (
    DjangoModelFactory,
    Iterator,
)

from pulseapi.profiles.models import UserProfile
from pulseapi.creators.models import EntryCreator


# Create a relation between a random profile and a random entry
class EntryCreatorFactory(DjangoModelFactory):

    class Meta:
        model = EntryCreator

    profile = Iterator(UserProfile.objects.all())
