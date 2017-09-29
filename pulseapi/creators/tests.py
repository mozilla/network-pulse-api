import json
from pulseapi.tests import PulseStaffTestCase


class TestCreators(PulseStaffTestCase):
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
            if creator.name.startswith('A'):
                db_creators.append(creator.name)

        self.assertEqual(creatorList, db_creators)
