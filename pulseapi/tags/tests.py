import json

from pulseapi.tests import PulseStaffTestCase


class TestEntryView(PulseStaffTestCase):
    def test_get_tag_list(self):
        """Make sure we can get a list of tags"""
        tagList = self.client.get('/api/pulse/tags/')
        self.assertEqual(tagList.status_code, 200)

    def test_tag_filtering(self):
        """Filter tags by first letters"""
        values = json.loads(
            str(self.client.get('/api/pulse/nonce/').content, 'utf-8')
        )
        self.client.post('/api/pulse/entries/', data={
            'title': 'title test_tag_filtering',
            'description': 'description test_tag_filtering',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'tags': 'test tag',
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        tagList = self.client.get('/api/pulse/tags/?search=te')
        tagsJson = json.loads(str(tagList.content, 'utf-8'))
        self.assertEqual(len(tagsJson), 1)
