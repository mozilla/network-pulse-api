import factory
from faker import Factory as FakerFactory

from pulseapi.entries.models import Entry
from pulseapi.users.test_models import EmailUserFactory


faker = FakerFactory.create()


class EntryFactory(factory.DjangoModelFactory):
    title = factory.LazyAttribute(lambda o: ' '.join(faker.words(nb=4)))
    description = factory.LazyAttribute(lambda o: ' '.join(faker.sentence(nb_words=20)))
    content_url = 'http://mozilla.org/image.png'

    # tags = []
    # for _ in range(0, 2):
    #     factory.LazyAttribute("tag")

    # get_involved = factory.LazyAttribute(lambda o: ' '.join(faker.sentence(nb_words=20)))
    # get_involved_url = factory.LazyAttribute(lambda o: '{a}.com'.format(a=o.name.lower()))
    # thumbnail_url = factory.LazyAttribute(
    #     lambda o: 'http://{a}.com/{a}.png'.format(a=o.name.lower())
    # )
    # interest = factory.LazyAttribute(
    #     lambda o: 'Long description for {a}'.format(a=o.name.lower())
    # )
    # short_description = factory.LazyAttribute(
    #     lambda o: 'Short description for {a}'.format(a=o.name.lower())
    # )

    featured = False
    # internal_notes = "some notes"
    # issues = ["Decentralization"]
    # creators = "Alan, Pomax"
    published_by_id = 1

    # @factory.post_generation
    # def events(self, create, extracted, **kwargs):
    #     if not create:
    #         # Simple build, do nothing.
    #         return

    #     if extracted:
    #         # A list of groups were passed in, use them
    #         for event in extracted:
    #             self.events.add(event)
    class Meta:
        model = Entry


# class UserProjectFactory(factory.Factory):
#     user = factory.SubFactory(UserFactory)
#     project = factory.SubFactory(ProjectFactory)
#     role = 'Contributor'

#     class Meta:
#         model = UserProject


# class ResourceLinkFactory(factory.Factory):
#     url = factory.LazyAttribute(lambda o: faker.url())
#     title = factory.LazyAttribute(lambda o: ' '.join(faker.words(nb=4)))
#     project = factory.SubFactory(ProjectFactory)

#     class Meta:
#         model = ResourceLink
