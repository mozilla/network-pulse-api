import json
from urllib.parse import quote
from django.core.exceptions import ValidationError

from pulseapi.profiles.test_models import UserProfileFactory
from pulseapi.creators.models import Creator
from pulseapi.tests import PulseStaffTestCase


class TestCreatorViews(PulseStaffTestCase):
    def test_get_creator_list(self):
        """Make sure we can get a list of creators"""
        creatorList = self.client.get('/api/pulse/creators/')
        self.assertEqual(creatorList.status_code, 200)

    def test_creator_filtering(self):
        """search creators, for autocomplete"""
        last = Creator.objects.last()
        search = last.creator_name

        url = '/api/pulse/creators/?name={search}'.format(
            search=quote(search)
        )

        creatorList = json.loads(
            str(self.client.get(url).content, 'utf-8')
        )

        rest_result = creatorList['results'][0]

        self.assertEqual(last.id, rest_result['creator_id'])


class TestCreatorModel(PulseStaffTestCase):
    def test_require_profile_or_name_on_save(self):
        """
        Make sure that we aren't allowed to save without specifying
        a profile or a name
        """
        creator = Creator()

        with self.assertRaises(ValidationError):
            creator.save()

    def test_auto_create_creator_on_creating_profile(self):
        """
        Make sure that when a profile is created a creator associated with
        that profile is created whose name is set to None and whose
        creator_name is the same as the profile name
        """
        profile = UserProfileFactory()
        profile.save()

        creator_from_db = Creator.objects.get(profile=profile)

        self.assertIsNone(creator_from_db.name)
        self.assertEqual(creator_from_db.creator_name, profile.name)
