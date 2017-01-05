import json

from django.test import TestCase
from django.test import Client

from pulseapi.users.test_models import EmailUserFactory
from pulseapi.entries.test_models import EntryFactory


class TestCreators(TestCase):
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

    def test_get_creator_list(self):
        """Make sure we can get a list of creators"""
        creatorList = self.client.get('/creators/')
        self.assertEqual(creatorList.status_code, 200)

    def test_creator_filtering(self):
        """search creators, for autocomplete"""
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'title test_creator_filtering',
            'description': 'description test_creator_filtering',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': ['Pomax','Alan'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        creatorList = json.loads(str(self.client.get('/creators/?search=A').content, 'utf-8'))
        self.assertEqual(creatorList, ['Alan'])