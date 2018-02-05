import json

from django.core.urlresolvers import reverse

from .models import UserProfile, ProfileType, ProgramType, ProgramYear

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

        created_entries = [EntrySerializer(x.entry).data for x in entry_creators]
        self.assertEqual(entriesjson['created_entries'], created_entries)

        # make sure extended profile data does not show
        self.assertEqual('program_type' in entriesjson, False)

    def test_extended_profile_data(self):
        (profile, created) = UserProfile.objects.get_or_create(related_user=self.user)
        profile.enable_extended_information = True
        test_program = ProgramType.objects.all().first()
        profile.program_type = test_program
        profile.save()

        profile_url = reverse('profile', kwargs={'pk': profile.id})

        # extended profile data should show in API responses
        response = self.client.get(profile_url)
        entriesjson = json.loads(str(response.content, 'utf-8'))
        self.assertEqual('program_type' in entriesjson, True)
        self.assertEqual(entriesjson['program_type'], test_program.value)

    def test_updating_extended_profile_data(self):
        (profile, created) = UserProfile.objects.get_or_create(related_user=self.user)
        profile.enable_extended_information = True
        profile.program_type = ProgramType.objects.all().first()
        profile.save()

        profile_url = reverse('myprofile')

        # authentication is absolutely required
        self.client.logout()
        response = self.client.put(profile_url, json.dumps({'affiliation': 'Mozilla'}))
        self.assertEqual(response.status_code, 403)

        # with authentication, updates should work
        self.client.force_login(user=self.user)
        response = self.client.put(profile_url, json.dumps({'affiliation': 'Mozilla'}))
        profile.refresh_from_db()
        self.assertEqual(profile.affiliation, 'Mozilla')

        response = self.client.get(profile_url)
        entriesjson = json.loads(str(response.content, 'utf-8'))
        self.assertEqual('affiliation' in entriesjson, True)
        self.assertEqual(entriesjson['affiliation'], 'Mozilla')

    def test_updating_disabled_extended_profile_data(self):
        (profile, created) = UserProfile.objects.get_or_create(related_user=self.user)
        profile.enable_extended_information = False
        profile.affiliation = 'untouched'
        profile.save()

        profile_url = reverse('myprofile')

        # With authentication, "updates" should work, but
        # enable_extened_information=False should prevent
        # an update from occurring.
        self.client.put(profile_url, {'affiliation': 'Mozilla'})
        profile.refresh_from_db()
        self.assertEqual(profile.affiliation, 'untouched')

    def test_profile_type_uniqueness(self):
        # as found in the bootstrap migration:
        (profile, created) = ProfileType.objects.get_or_create(value='plain')
        self.assertEqual(created, False)

    def test_program_type_uniqueness(self):
        # as found in the bootstrap migration:
        (profile, created) = ProgramType.objects.get_or_create(value='senior fellow')
        self.assertEqual(created, False)

    def test_program_year_uniqueness(self):
        # as found in the bootstrap migration:
        (profile, created) = ProgramYear.objects.get_or_create(value='2018')
        self.assertEqual(created, False)
