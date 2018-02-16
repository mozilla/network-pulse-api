from factory import (
    DjangoModelFactory,
    Faker,
    Trait,
)

from pulseapi.users.models import EmailUser


class EmailUserFactory(DjangoModelFactory):

    class Meta:
        model = EmailUser

    class Params:
        staff = Trait(
            is_staff=True
        )

    # TODO: profile + moar emails variety (@mozilla, etc)
    email = Faker('email')
    name = Faker('name')
