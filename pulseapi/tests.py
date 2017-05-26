from django.test import TestCase
from pulseapi.users.test_models import EmailUserFactory
from pulseapi.entries.test_models import EntryFactory
from django.test import Client
import json


# Create your tests here.
class PulseStaffTestCase(TestCase):
    def setUp(self):
        self.entries = [EntryFactory() for i in range(2)]
        for entry in self.entries:
            entry.set_moderation_state("Approved")
            entry.save()

        email = "test@mozilla.org"
        password = "password1234"
        user = EmailUserFactory(email=email, password=password, name="test user")
        user.save()

        self.client = Client()
        self.client.force_login(user);

        # Set up with some curated data for all tests to use
        postresponse = self.client.post('/entries/', data=self.generatePostPayload())

    def generatePostPayload(self, data={}):

        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        payload = {
            'title': 'default title',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'content_url': 'http://example.com/',
            'tags': ['tag1', 'tag2']
        }
        for key in data:
            payload[key] = data[key]

        return payload

class PulseMemberTestCase(TestCase):
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

            # Set up with some curated data for all tests to use
            postresponse = self.client.post('/entries/', data=self.generatePostPayload())

    def generatePostPayload(self, data={}):

        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        payload = {
            'title': 'default title',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'content_url': 'http://example.com/',
            'tags': ['tag1', 'tag2']
        }
        for key in data:
            payload[key] = data[key]

        return payload
