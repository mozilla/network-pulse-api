import json
from pulseapi.tests import PulseStaffTestCase


class TestCreators(PulseStaffTestCase):
    def test_get_creator_list(self):
        """Make sure we can get a list of creators"""
        creatorList = self.client.get('/api/pulse/creators/')
        self.assertEqual(creatorList.status_code, 200)

    def test_creator_filtering(self):
        """search creators, for autocomplete"""
        payload = {
            'title': 'title test_creator_filtering',
            'content_url': 'http://example.com/test_creator_filtering',
            'description': 'description test_creator_filtering',
            'creators': ['Alice', 'Bob', 'Carol']
        }
        json.loads(str(self.client.get('/api/pulse/nonce/').content, 'utf-8'))
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        creatorList = json.loads(
            str(self.client.get(
                '/api/pulse/creators/?search=A'
            ).content, 'utf-8')
        )
        self.assertEqual(creatorList, ['Alice'])
