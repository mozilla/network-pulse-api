import json

from django.core.urlresolvers import reverse

from pulseapi.tests import PulseMemberTestCase
from pulseapi.entries.serializers import EntrySerializer
from pulseapi.creators.models import OrderedCreatorRecord


class TestProfileView(PulseMemberTestCase):
    def test_get_single_profile_data(self):
        """
        Check if we can get a single profile by its `id`
        """
        id = self.users_with_profiles[0].id
        response = self.client.get(reverse('profile', kwargs={'pk': id}))
        self.assertEqual(response.status_code, 200)

    def test_profile_data_serialization(self):
        """
        Make sure profiles have "created_entries" array
        """
        id = self.users_with_profiles[0].id
        response = self.client.get(reverse('profile', kwargs={'pk': id}))
        entriesjson = json.loads(str(response.content, 'utf-8'))

        created_entries = []
        entry_creators = OrderedCreatorRecord.objects.filter(
            creator__profile=self.users_with_profiles[0].id
            )
        for entry_creator in entry_creators:
            created_entries.append(EntrySerializer(entry_creator.entry).data)

        self.assertEqual(entriesjson['created_entries'], created_entries)
