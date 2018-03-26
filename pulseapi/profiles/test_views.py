import json

from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q

from .models import UserProfile, ProfileType, ProgramType, ProgramYear

from pulseapi.tests import PulseMemberTestCase
from pulseapi.entries.models import Entry
from pulseapi.entries.serializers import EntrySerializer
from pulseapi.creators.models import OrderedCreatorRecord
from pulseapi.profiles.serializers import (
    UserProfileEntriesSerializer,
    UserProfilePublicSerializer,
    UserProfilePublicWithEntriesSerializer,
)


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
        user = self.users_with_profiles[0]
        profile = user.profile
        location = "Springfield, IL"
        profile.location = location
        profile.save()

        id = profile.id
        response = self.client.get(reverse('profile', kwargs={'pk': id}))
        entriesjson = json.loads(str(response.content, 'utf-8'))

        self.assertEqual(entriesjson['location'], location)

        created_entries = []
        entry_creators = OrderedCreatorRecord.objects.filter(
            creator__profile=id
        ).order_by('-id')

        created_entries = [EntrySerializer(x.entry).data for x in entry_creators]
        self.assertEqual(entriesjson['profile_id'], id)
        self.assertEqual(entriesjson['created_entries'], created_entries)

        # make sure extended profile data does not show
        self.assertEqual('program_type' in entriesjson, False)

    def test_v2_profile_data_serialization(self):
        """
        Make sure profiles do not have "created_entries" array for API version 2
        """
        profile = OrderedCreatorRecord.objects.filter(creator__profile__isnull=False)[:1].get().creator.profile
        response = self.client.get(reverse('profile', args=[
            settings.API_VERSIONS['version_2'] + '/',
            profile.id
        ]))
        profile_json = json.loads(str(response.content, 'utf-8'))

        self.assertEqual(profile_json['profile_id'], profile.id)
        self.assertNotIn('created_entries', profile_json)

    def test_profile_entries_created(self):
        """
        Get the created entries for a profile
        """
        profile = OrderedCreatorRecord.objects.filter(creator__profile__isnull=False)[:1].get().creator.profile
        entries = [
            UserProfileEntriesSerializer.serialize_entry(ocr.entry)
            for ocr in OrderedCreatorRecord.objects.filter(creator__profile=profile)
        ]

        response = self.client.get(
            '{url}?created'.format(
                url=reverse('profile-entries', kwargs={'pk': profile.id})
            )
        )
        profile_json = json.loads(str(response.content, 'utf-8'))
        self.assertListEqual(profile_json['created'], entries)

    def test_profile_entries_published(self):
        """
        Get the published entries for a profile
        """
        profile = UserProfile.objects.filter(related_user__entries__isnull=False)[:1].get()
        entries = [
            UserProfileEntriesSerializer.serialize_entry(entry)
            for entry in Entry.objects.public().filter(published_by=profile.user)
        ]

        response = self.client.get(
            '{url}?published'.format(
                url=reverse('profile-entries', kwargs={'pk': profile.id})
            )
        )
        profile_json = json.loads(str(response.content, 'utf-8'))
        self.assertListEqual(profile_json['published'], entries)

    def test_profile_entries_favorited(self):
        """
        Get the favorited entries for a profile
        """
        profile = self.user.profile
        entries = Entry.objects.public()[:2]
        serialized_entries = []

        for entry in entries:
            self.client.put(reverse('bookmark', kwargs={'entryid': entry.id}))
            serialized_entries.append(UserProfileEntriesSerializer.serialize_entry(entry))

        response = self.client.get(
            '{url}?favorited'.format(
                url=reverse('profile-entries', kwargs={'pk': profile.id})
            )
        )
        profile_json = json.loads(str(response.content, 'utf-8'))
        self.assertListEqual(profile_json['favorited'], serialized_entries)

    def test_profile_entries_count(self):
        """
        Get the number of entries associated with a profile
        """
        profile = OrderedCreatorRecord.objects.filter(creator__profile__isnull=False)[:1].get().creator.profile
        published_entry = profile.related_creator.related_entries.last().entry
        published_entry.published_by = profile.user
        published_entry.save()
        favorited_entries = Entry.objects.public()[:2]

        self.client.force_login(user=profile.user)

        for entry in favorited_entries:
            self.client.put(reverse('bookmark', kwargs={'entryid': entry.id}))

        entry_count = Entry.objects.public().filter(
            Q(related_creators__creator__profile=profile) |
            Q(published_by=profile.user) |
            Q(bookmarked_by__profile=profile)
        ).distinct().count()

        response = self.client.get(reverse('profile-entries', kwargs={'pk': profile.id}))
        profile_json = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(profile_json['entry_count'], entry_count)

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

    def test_updating_readonly_profile_type(self):
        profile = self.user.profile
        current_profile_type = profile.profile_type.value
        new_profile_type = ProfileType.objects.exclude(value=current_profile_type)[0].value

        response = self.client.put(reverse('myprofile'), json.dumps({'profile_type': new_profile_type}))
        self.assertEqual(response.status_code, 200)

        # Make sure that the profile type was not changed since
        # it is a readonly field
        profile.refresh_from_db()
        self.assertEqual(profile.profile_type.value, current_profile_type)

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

    def test_profile_list_v1(self):
        (profile_type, _) = ProfileType.objects.get_or_create(value='test-type')
        for profile in UserProfile.objects.all()[:3]:
            profile.enable_extended_information = True
            profile.profile_type = profile_type
            profile.save()

        url = reverse('profile_list', args=[
            settings.API_VERSIONS['version_1'] + '/'
        ])
        response = self.client.get('{url}?profile_type={type}'.format(url=url, type=profile_type.value))
        response_profiles = json.loads(str(response.content, 'utf-8'))

        profile_list = [
            UserProfilePublicWithEntriesSerializer(
                profile,
                context={'request': response.wsgi_request}
            ).data
            for profile in UserProfile.objects.filter(profile_type=profile_type)
        ]

        self.assertListEqual(response_profiles, profile_list)

    def test_profile_list_v2(self):
        (profile_type, _) = ProfileType.objects.get_or_create(value='test-type')
        for profile in UserProfile.objects.all()[:3]:
            profile.enable_extended_information = True
            profile.profile_type = profile_type
            profile.save()

        url = reverse('profile_list', args=[
            settings.API_VERSIONS['version_2'] + '/'
        ])
        response = self.client.get('{url}?profile_type={type}'.format(url=url, type=profile_type.value))
        response_profiles = json.loads(str(response.content, 'utf-8'))

        profile_list = [
            UserProfilePublicSerializer(
                profile,
                context={'request': response.wsgi_request}
            ).data
            for profile in UserProfile.objects.filter(profile_type=profile_type)
        ]

        self.assertListEqual(response_profiles, profile_list)

    def test_profile_list_filtering(self):
        profile_types = ['a', 'b', 'c']
        program_types = ['a', 'b']
        program_years = ['a', 'b']

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

        profile_url = reverse('profile_list')

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

    def test_invalid_profile_list_filtering_argument(self):
        profile_url = reverse('profile_list')
        url = ('{url}?unsupported_arg=should_be_empty_response').format(url=profile_url)
        response = self.client.get(url)
        entriesjson = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(len(entriesjson), 0)
