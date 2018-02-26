"""
Create fake profiles for local development and Heroku's review app.
"""

from factory import (
    DjangoModelFactory,
    Trait,
    Faker,
    post_generation,
    Iterator,
    LazyAttribute)

from pulseapi.issues.models import Issue
from pulseapi.profiles.models import (
    UserProfile,
    ProfileType,
    ProgramType,
    ProgramYear,
    UserBookmarks,
)
from pulseapi.utility.factories_utility import get_random_items, ImageProvider

Faker.add_provider(ImageProvider)


class UserBookmarksFactory(DjangoModelFactory):

    class Meta:
        model = UserBookmarks

    profile = Iterator(UserProfile.objects.all())


class BasicUserProfileFactory(DjangoModelFactory):

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

    location = Faker('city')
    twitter = Faker('url')
    linkedin = Faker('url')
    github = Faker('url')
    website = Faker('url')

    @post_generation
    def issues(self, create, extracted, **kwargs):
        self.issues.add(*(get_random_items(Issue)))

    @post_generation
    def set_thumbnail(self, create, extracted, **kwargs):
        self.thumbnail.name = Faker('people_image').generate({})


class ExtendedUserProfileFactory(BasicUserProfileFactory):

    class Meta:
        exclude = ('affiliation_sentence',)

    is_active = True
    enable_extended_information = True
    affiliation = LazyAttribute(lambda o: o.affiliation_sentence.rstrip('.'))
    user_bio = Faker('sentence', nb_words=4, variable_nb_words=True)
    user_bio_long = Faker('paragraphs', nb=3)
    # Used default values from the database
    profile_type = Iterator(ProfileType.objects.all())
    program_type = Iterator(ProgramType.objects.all())
    program_year = Iterator(ProgramYear.objects.all())

    affiliation_sentence = Faker('sentence', nb_words=2, variable_nb_words=True)
