import json

from pulseapi.tests import PulseStaffTestCase


class TestEntryView(PulseStaffTestCase):
    def test_get_tag_list(self):
        """Make sure we can get a list of tags"""
        tagList = self.client.get('/api/pulse/tags/')
        self.assertEqual(tagList.status_code, 200)

    def test_tag_filtering(self):
        """Filter tags by first letters"""
        payload = self.generatePostPayload(data={
            'title': 'title test_tag_filtering',
            'description': 'description test_tag_filtering',
            'tags': ['test tag'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })

        self.client.post('/api/pulse/entries/', data=payload)
        tagList = self.client.get('/api/pulse/tags/?search=te')
        tagsJson = json.loads(str(tagList.content, 'utf-8'))
        self.assertEqual(len(tagsJson), 1)
