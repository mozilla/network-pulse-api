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

    def test_profile_searching(self):
        profile_types = ['plain', 'staff', 'grantee']
        program_types = ['first', 'now']
        program_years = ['now', 'before']

        for v1 in profile_types:
            (profile_type, _) = ProfileType.objects.get_or_create(value=v1)
            for v2 in program_types:
                (program_type, _) = ProgramType.objects.get_or_create(value=v2)
                for v3 in program_years:
                    (program_year, _) = ProgramYear.objects.get_or_create(value=v3)
                    profile = UserProfile.objects.create()
                    profile.enable_extended_information = True
                    profile.profile_type = profile_type
                    profile.program_type = program_type
                    profile.program_year = program_year
                    profile.save()

        profile_url = reverse('profile_search')

        # There should be four results for each profile type
        for profile_type in profile_types:
            url = ('{url}?profile_type={type}').format(url=profile_url, type=profile_type)
            response = self.client.get(url)
            entriesjson = json.loads(str(response.content, 'utf-8'))
            self.assertEqual(len(entriesjson), 4)

        # There should be six results for each program type
        for program_type in program_types:
            url = ('{url}?program_type={type}').format(url=profile_url, type=program_type)
            response = self.client.get(url)
            entriesjson = json.loads(str(response.content, 'utf-8'))
            self.assertEqual(len(entriesjson), 6)

        # There should be six results for each program year
        for program_year in program_years:
            url = ('{url}?program_year={type}').format(url=profile_url, type=program_year)
            response = self.client.get(url)
            entriesjson = json.loads(str(response.content, 'utf-8'))
            self.assertEqual(len(entriesjson), 6)

        # There should only be one result for each unique combination
        for v1 in profile_types:
            for v2 in program_types:
                for v3 in program_years:
                    url = ('{url}?profile_type={v1}&program_type={v2}&program_year={v3}').format(
                        url=profile_url,
                        v1=profile_type,
                        v2=program_type,
                        v3=program_year
                    )
                    response = self.client.get(url)
                    entriesjson = json.loads(str(response.content, 'utf-8'))
                    self.assertEqual(len(entriesjson), 1)
