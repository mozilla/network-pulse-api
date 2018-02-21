"""
Create fake profiles for local development and Heroku's review app.
"""

from factory import (
    DjangoModelFactory,
    Trait,
    Faker,
)

from pulseapi.profiles.models import UserProfile


class UserProfileFactory(DjangoModelFactory):

    class Meta:
        model = UserProfile

    class Params:
        active = Trait(
            is_active=True
        )
        use_custom_name = Trait(
            custom_name=Faker('user_name')
        )
        group = Trait(
            is_group=True
        )

    # TODO: finish missing base fields
    location = Faker('city')
    twitter = Faker('url')

    # TODO: use factory.Maybe with extended flag to add extended info
