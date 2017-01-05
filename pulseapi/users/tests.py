import json

from django.test import TestCase
from django.test import Client

from pulseapi.entries.test_models import EntryFactory


class TestUnauthedUserPost(TestCase):
    def test_unauthenticated_user_posting(self):
        """Assert that unauthenticated users can't get a nonce"""
        self.entries = [EntryFactory() for i in range(2)]
        for entry in self.entries:
            entry.save()

        self.client = Client()

        values = self.client.get('/nonce/')
        self.assertEqual(values.status_code, 404)