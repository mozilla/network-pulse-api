"""
Create fake users for local development and Heroku's review app.
"""

from factory import (
    DjangoModelFactory,
    Faker,
    Trait,
    LazyAttribute,
    SubFactory)

from pulseapi.users.models import EmailUser
from pulseapi.profiles.factory import UserProfileFactory


class BaseEmailUserFactory(DjangoModelFactory):

    class Meta:
        model = EmailUser

    email = Faker('email')
    name = Faker('name')
    profile = SubFactory(UserProfileFactory)


class MozillaEmailUserFactory(BaseEmailUserFactory):

    class Meta:
        model = EmailUser

    class Params:
        staff = Trait(
            is_staff=True
        )
        admin = Trait(
            is_superuser=True
        )

    email = LazyAttribute(lambda o: '%s@mozillafoundation.org' % o.name.replace(' ', ''))
