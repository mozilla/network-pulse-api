import json

from django.test import TestCase
from django.test import Client
from pulseapi.tests import PulseStaffTestCase

from pulseapi.users.test_models import EmailUserFactory
from pulseapi.entries.test_models import EntryFactory


class TestCreators(PulseStaffTestCase):
    def test_get_creator_list(self):
        """Make sure we can get a list of creators"""
        creatorList = self.client.get('/creators/')
        self.assertEqual(creatorList.status_code, 200)

    def test_creator_filtering(self):
        """search creators, for autocomplete"""
        payload = {
            'title': 'title test_creator_filtering',
            'description': 'description test_creator_filtering',
            'creators': ['Pomax','Alan'],
        }
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
        creatorList = json.loads(str(self.client.get('/creators/?search=A').content, 'utf-8'))
        self.assertEqual(creatorList, ['Alan'])
