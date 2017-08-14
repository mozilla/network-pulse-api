"""EmailUser Model Generator"""
from pulseapi.users.models import EmailUser

import factory
from faker import Factory

fake = Factory.create()


class EmailUserFactory(factory.Factory):
    """Generate EmailUsers for tests"""
    name = factory.LazyAttribute(lambda o: fake.name())
    email = factory.LazyAttribute(lambda o: fake.email())

    class Meta:
        """Tell factory that it should be generating EmailUsers"""
        model = EmailUser
