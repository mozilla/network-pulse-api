"""UserProfile Model Generator"""
from pulseapi.profiles.models import UserProfile

import factory
from faker import Factory

fake = Factory.create()


class UserProfileFactory(factory.Factory):
    """Generate UserProfiles for tests"""
    is_active = True
    user_bio = factory.LazyAttribute(
        lambda o: 'user_bio {fake_bio}'.format(
            fake_bio=''.join(fake.text(max_nb_chars=130))
        )
    )

    class Meta:
        """Tell factory that it should be generating UserProfiles"""
        model = UserProfile
