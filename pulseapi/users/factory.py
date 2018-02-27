"""
Create fake users for local development and Heroku's review app.
"""

from factory import (
    DjangoModelFactory,
    Faker,
    Trait,
    LazyAttribute,
    SubFactory,
)

from pulseapi.users.models import EmailUser
from pulseapi.profiles.factory import BasicUserProfileFactory, ExtendedUserProfileFactory


class BasicEmailUserFactory(DjangoModelFactory):

    class Meta:
        model = EmailUser
        exclude = ('email_domain',)

    class Params:
        group = Trait(
            profile=SubFactory(BasicUserProfileFactory, group=True),
            name=Faker('color_name')
        )
        active = Trait(
            profile=SubFactory(BasicUserProfileFactory, is_active=True)
        )
        extended_profile = Trait(
            profile=SubFactory(ExtendedUserProfileFactory)
        )
        use_custom_name = Trait(
            profile=SubFactory(BasicUserProfileFactory, use_custom_name=True)
        )

    email = LazyAttribute(lambda o: o.name.replace(' ', '') + '@' + o.email_domain)
    name = Faker('name')
    profile = SubFactory(BasicUserProfileFactory)

    # LazyAttribute helper value
    email_domain = Faker('domain_name')


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
