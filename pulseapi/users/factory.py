from factory import (
    DjangoModelFactory,
    Faker,
    Trait,
    LazyAttribute)

from pulseapi.users.models import EmailUser


class BaseEmailUserFactory(DjangoModelFactory):

    class Meta:
        model = EmailUser

    email = Faker('email')
    name = Faker('name')


class MozillaEmailUserFactory(DjangoModelFactory):

    class Meta:
        model = EmailUser

    class Params:
        staff = Trait(
            is_staff=True
        )
        admin = Trait(
            is_superuser=True
        )

    name = Faker('name')
    email = LazyAttribute(lambda o: '%s@mozillafoundation.org' % o.name.replace(' ', ''))
