import json

from django.test import TestCase
from django.test import Client

from pulseapi.users.test_models import EmailUserFactory
from pulseapi.entries.test_models import EntryFactory


class TestEntryView(TestCase):
    def setUp(self):
        self.entries = [EntryFactory() for i in range(2)]
        for entry in self.entries:
            entry.save()

        email = "test@example.org"
        password = "password1234"
        user = EmailUserFactory(email=email, password=password, name="test user")
        user.save()

        self.client = Client()
        self.client.force_login(user);

        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        # Set up with some curated data for all tests to use
        postresponse = self.client.post('/entries/', data={
            'title': 'title setUp1',
            'description': 'description setUp',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': 'Pomax',
            'tags': ['tag1', 'tag2'],
            'interest': 'interest field',
            'issues': 'Open Innovation',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })

    def test_get_tag_list(self):
        """Make sure we can get a list of tags"""
        tagList = self.client.get('/tags/')
        self.assertEqual(tagList.status_code, 200)

    def test_tag_filtering(self):
        """Filter tags by first letters"""
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'title test_tag_filtering',
            'description': 'description test_tag_filtering',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'tags' : 'test tag',
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        tagList = self.client.get('/tags/?search=te')
        tagsJson = json.loads(str(tagList.content, 'utf-8'))
        self.assertEqual(len(tagsJson), 1)
