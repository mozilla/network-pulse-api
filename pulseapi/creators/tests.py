import json
from django.core.exceptions import ValidationError

from pulseapi.creators.models import Creator
from pulseapi.tests import PulseStaffTestCase
from pulseapi.creators.test_models import CreatorFactory


class TestCreatorViews(PulseStaffTestCase):
    def test_get_creator_list(self):
        """Make sure we can get a list of creators"""
        creatorList = self.client.get('/api/pulse/creators/')
        self.assertEqual(creatorList.status_code, 200)

    def test_creator_filtering(self):
        """search creators, for autocomplete"""
        creatorList = json.loads(
            str(self.client.get(
                '/api/pulse/creators/?search=A'
            ).content, 'utf-8')
        )
        db_creators = []
        for creator in self.creators:
            if creator.name and creator.name.startswith('A'):
                db_creators.append(creator.creator_name)

        self.assertEqual(creatorList, db_creators)


class TestCreatorModel(PulseStaffTestCase):
    def test_require_profile_or_name_on_save(self):
        """
        Make sure that we aren't allowed to save without specifying
        a profile or a name
        """
        creator = Creator()

        with self.assertRaises(ValidationError):
            creator.save()

    def test_delete_name_when_given_profile(self):
        """
        Make sure that when we save with a profile and also provide a
        name, the name is set to None and the creator_name is the same
        as the profile name
        """
        profile = self.user.profile

        creator = CreatorFactory(profile=profile)
        creator.save()
        creator_from_db = Creator.objects.get(profile=profile)

        self.assertIsNone(creator_from_db.name)
        self.assertEqual(creator_from_db.creator_name, profile.name)
