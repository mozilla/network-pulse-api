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
from pulseapi.profiles.factory import BasicUserProfileFactory, ExtendedUserProfileFactory


class BasicEmailUserFactory(DjangoModelFactory):

    class Meta:
        model = EmailUser

    class Params:
        group = Trait(
            profile=SubFactory(BasicUserProfileFactory, group=True),
            name=Faker('sentence', nb_words=3, variable_nb_words=True)
        )
        active = Trait(
            is_active=True
        )
        extended_profile = Trait(
            profile=SubFactory(ExtendedUserProfileFactory)
        )
        use_custom_name = Trait(
            profile=SubFactory(BasicUserProfileFactory, use_custom_name=True)
        )

    email = Faker('email')
    name = Faker('name')
    profile = SubFactory(BasicUserProfileFactory)


class MozillaEmailUserFactory(BasicEmailUserFactory):

    class Meta:
        model = EmailUser

    class Params:
        staff = Trait(
            is_staff=True
        )
        admin = Trait(
            is_superuser=True
        )
        extended_profile = Trait(
            profile=SubFactory(ExtendedUserProfileFactory)
        )

    email = LazyAttribute(lambda o: '%s@mozillafoundation.org' % o.name.replace(' ', ''))
    profile = SubFactory(BasicUserProfileFactory)
