import json
from urllib.parse import urlencode
from django.core.urlresolvers import reverse
from django.conf import settings

from .models import UserProfile, ProfileType, ProgramType, ProgramYear

from pulseapi.tests import PulseMemberTestCase
from pulseapi.entries.models import Entry, ModerationState
from pulseapi.entries.serializers import (
    EntrySerializerWithV1Creators,
    EntrySerializerWithCreators,
)
from pulseapi.entries.factory import BasicEntryFactory
from pulseapi.users.factory import BasicEmailUserFactory
from pulseapi.creators.models import EntryCreator
from pulseapi.creators.factory import EntryCreatorFactory
from pulseapi.profiles.serializers import (
    UserProfileEntriesSerializer,
    UserProfilePublicSerializer,
    UserProfilePublicWithEntriesSerializer,
    UserProfileBasicSerializer,
)
from pulseapi.profiles.factory import UserBookmarksFactory, ExtendedUserProfileFactory


class TestProfileView(PulseMemberTestCase):
    def test_get_single_profile_data(self):
        """
        Check if we can get a single profile by its `id`
        """
        id = self.users_with_profiles[0].profile.id
        response = self.client.get(reverse('profile', kwargs={'pk': id}))
        self.assertEqual(response.status_code, 200)

    def test_v1_profile_data_serialization(self):
        """
        Make sure v1 profiles have "created_entries" array
        """
        location = 'Springfield, IL'
        profile = ExtendedUserProfileFactory(location=location)
        id = profile.id

        response = self.client.get(reverse('profile', args=[
            settings.API_VERSIONS['version_1'] + '/',
            id
        ]))
        response_entries = json.loads(str(response.content, 'utf-8'))

        self.assertEqual(response_entries['location'], location)

        created_entries = []
        entry_creators = EntryCreator.objects.filter(profile=profile).order_by('-id')

        created_entries = [EntrySerializerWithV1Creators(x.entry).data for x in entry_creators]
        self.assertEqual(response_entries['profile_id'], id)
        self.assertEqual(response_entries['created_entries'], created_entries)

        # make sure extended profile data does not show
        self.assertIn('program_type', response_entries)

    def test_v2_profile_data_serialization(self):
        """
        Make sure profiles do not have "created_entries" array for API version 2
        """
        profile = EntryCreator.objects.first().profile
        response = self.client.get(reverse('profile', args=[
            settings.API_VERSIONS['version_2'] + '/',
            profile.id
        ]))
        profile_json = json.loads(str(response.content, 'utf-8'))

        self.assertEqual(profile_json['profile_id'], profile.id)
        self.assertNotIn('created_entries', profile_json)

    def run_test_profile_entries(self, version, entry_type):
        entry_serializer_class = EntrySerializerWithCreators
        if version == settings.API_VERSIONS['version_1']:
            entry_serializer_class = EntrySerializerWithV1Creators

        user = self.user
        # "Created" entry_type profile used as default
        profile = EntryCreator.objects.first().profile

        if entry_type is 'published':
            profile = user.profile
            approved = ModerationState.objects.get(name='Approved')
            for _ in range(0, 3):
                BasicEntryFactory.create(published_by=user, moderation_state=approved)
        elif entry_type is 'favorited':
            profile = user.profile
            for entry in Entry.objects.all()[:4]:
                self.client.put(reverse('bookmark', kwargs={'entryid': entry.id}))

        expected_entries = UserProfileEntriesSerializer(
            instance=profile,
            context={
                'created': entry_type is 'created',
                'published': entry_type is 'published',
                'favorited': entry_type is 'favorited',
                'EntrySerializerClass': entry_serializer_class
            },
        ).data[entry_type]

        response = self.client.get(
            '{url}?{entry_type}'.format(
                url=reverse(
                    'profile-entries',
                    args=[version + '/', profile.id]
                ),
                entry_type=entry_type
            )
        )
        profile_json = json.loads(str(response.content, 'utf-8'))
        self.assertListEqual(profile_json[entry_type], expected_entries)

    def test_profile_v1_entries_created(self):
        """
        Get the created entries for a profile (v1)
        """
        self.run_test_profile_entries(
            version=settings.API_VERSIONS['version_1'],
            entry_type='created',
        )

    def test_profile_v2_entries_created(self):
        """
        Get the created entries for a profile (v2)
        """
        self.run_test_profile_entries(
            version=settings.API_VERSIONS['version_2'],
            entry_type='created',
        )

    def test_profile_v1_entries_published(self):
        """
        Get the published entries for a profile (v1)
        """
        self.run_test_profile_entries(
            version=settings.API_VERSIONS['version_1'],
            entry_type='published',
        )

    def test_profile_v2_entries_published(self):
        """
        Get the published entries for a profile (v2)
        """
        self.run_test_profile_entries(
            version=settings.API_VERSIONS['version_2'],
            entry_type='published',
        )

    def test_profile_v1_entries_favorited(self):
        """
        Get the favorited entries for a profile (v1)
        """
        self.run_test_profile_entries(
            version=settings.API_VERSIONS['version_1'],
            entry_type='favorited',
        )

    def test_profile_v2_entries_favorited(self):
        """
        Get the favorited entries for a profile (v2)
        """
        self.run_test_profile_entries(
            version=settings.API_VERSIONS['version_2'],
            entry_type='favorited',
        )

    def test_profile_entries_count(self):
        """
        Get the number of entries associated with a profile
        """
        user = BasicEmailUserFactory()
        profile = user.profile

        approved = ModerationState.objects.get(name='Approved')
        BasicEntryFactory(published_by=user, moderation_state=approved)
        published_entry_2 = BasicEntryFactory(published_by=user, moderation_state=approved, published_by_creator=True)

        created_entry = BasicEntryFactory(published_by=self.user, moderation_state=approved)
        EntryCreatorFactory(profile=profile, entry=created_entry)

        favorited_entry_1 = BasicEntryFactory(published_by=self.user, moderation_state=approved)
        favorited_entry_2 = BasicEntryFactory(published_by=self.user, moderation_state=approved)
        UserBookmarksFactory(profile=profile, entry=favorited_entry_1)
        UserBookmarksFactory(profile=profile, entry=favorited_entry_2)

        # Overlapping entries (entries that belong to more than one of created, published, or favorited)
        # These entries should not be duplicated in the entry count
        EntryCreatorFactory(profile=profile, entry=published_entry_2)
        UserBookmarksFactory(profile=profile, entry=created_entry)

        response = self.client.get(reverse('profile-entries', kwargs={'pk': profile.id}))
        response_profile = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(response_profile['entry_count'], 5)

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

    def run_test_profile_list(self, api_version, profile_serializer_class, query_dict=''):
        (profile_type, _) = ProfileType.objects.get_or_create(value='temporary-type')
        for _ in range(3):
            profile = ExtendedUserProfileFactory(profile_type=profile_type)
            profile.thumbnail = None
            profile.save()

        url = reverse('profile_list', args=[api_version + '/'])
        response = self.client.get('{url}?profile_type={type}&{qs}'.format(
            url=url,
            type=profile_type.value,
            qs=urlencode(query_dict)
        ))
        response_profiles = json.loads(str(response.content, 'utf-8'))

        profile_list = profile_serializer_class(
            UserProfile.objects.filter(profile_type=profile_type),
            many=True,
        ).data

        self.assertListEqual(response_profiles, profile_list)

    def test_profile_list_v1(self):
        self.run_test_profile_list(
            api_version=settings.API_VERSIONS['version_1'],
            profile_serializer_class=UserProfilePublicWithEntriesSerializer
        )

    def test_profile_list_v2(self):
        self.run_test_profile_list(
            api_version=settings.API_VERSIONS['version_2'],
            profile_serializer_class=UserProfilePublicSerializer
        )

    def test_profile_list_basic_v2(self):
        self.run_test_profile_list(
            api_version=settings.API_VERSIONS['version_2'],
            profile_serializer_class=UserProfileBasicSerializer,
            query_dict={'basic': ''}
        )

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
